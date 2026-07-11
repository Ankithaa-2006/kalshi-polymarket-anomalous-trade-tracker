import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sentence_transformers import SentenceTransformer, util
from decimal import Decimal

from ..database import async_session_maker
from ..models.market import Market
from ..models.market_match import MarketMatch

# Global model instance
model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('all-MiniLM-L6-v2')
    return model

async def compute_market_matches(similarity_threshold=0.8):
    """
    Computes cross-platform market matches using embeddings of the market title.
    """
    async with async_session_maker() as session:
        # Fetch all kalshi and polymarket markets
        stmt_k = select(Market).where(Market.platform == 'kalshi')
        res_k = await session.execute(stmt_k)
        kalshi_markets = res_k.scalars().all()
        
        stmt_p = select(Market).where(Market.platform == 'polymarket')
        res_p = await session.execute(stmt_p)
        poly_markets = res_p.scalars().all()
        
        if not kalshi_markets or not poly_markets:
            return

        # Prepare embeddings
        embedder = get_model()
        kalshi_texts = [m.title for m in kalshi_markets if m.title]
        poly_texts = [m.title for m in poly_markets if m.title]
        
        if not kalshi_texts or not poly_texts:
            return

        # Run embedding in a thread pool to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        k_embeddings = await loop.run_in_executor(None, embedder.encode, kalshi_texts)
        p_embeddings = await loop.run_in_executor(None, embedder.encode, poly_texts)
        
        cosine_scores = util.cos_sim(k_embeddings, p_embeddings)
        
        # Identify matches above threshold
        matches_found = []
        for i in range(len(kalshi_texts)):
            for j in range(len(poly_texts)):
                score = cosine_scores[i][j].item()
                if score >= similarity_threshold:
                    matches_found.append((kalshi_markets[i].id, poly_markets[j].id, score))
                    
        # Store matches in database
        for m_id_a, m_id_b, score in matches_found:
            # Check if match already exists
            stmt_check = select(MarketMatch).where(
                (MarketMatch.market_id_a == m_id_a) & (MarketMatch.market_id_b == m_id_b)
            )
            res_check = await session.execute(stmt_check)
            existing = res_check.scalar_one_or_none()
            
            if not existing:
                new_match = MarketMatch(
                    market_id_a=m_id_a,
                    market_id_b=m_id_b,
                    similarity_score=Decimal(str(score)),
                    confirmed=False
                )
                session.add(new_match)
                
        await session.commit()
