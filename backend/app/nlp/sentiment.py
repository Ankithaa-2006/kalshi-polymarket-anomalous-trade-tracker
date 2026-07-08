import logging
import asyncio
from typing import Dict, Tuple

from ..config import settings

logger = logging.getLogger(__name__)

_models_loaded = False
_sentence_model = None
_sentiment_pipe = None
_zeroshot_pipe = None

def _load_models():
    global _models_loaded, _sentence_model, _sentiment_pipe, _zeroshot_pipe
    if _models_loaded:
        return
    
    if settings.NLP_BACKEND == 'huggingface':
        logger.info("Loading HuggingFace models... this may take a while.")
        from sentence_transformers import SentenceTransformer
        from transformers import pipeline

        # Relevancy Model
        _sentence_model = SentenceTransformer('all-MiniLM-L6-v2', cache_folder=settings.MODELS_CACHE_DIR)
        
        # Sentiment Model (FinBERT)
        _sentiment_pipe = pipeline("sentiment-analysis", model="ProsusAI/finbert", cache_folder=settings.MODELS_CACHE_DIR)
        
        # Zero-shot classification (BART)
        _zeroshot_pipe = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", cache_folder=settings.MODELS_CACHE_DIR)
        
        logger.info("HuggingFace models loaded successfully.")
    else:
        logger.info("Using VADER for sentiment, skipping heavy model load.")
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        _sentiment_pipe = SentimentIntensityAnalyzer()
        
    _models_loaded = True

def _analyze_news_sync(market_title: str, text: str) -> Tuple[float, str, float, str]:
    """Sync function to perform NLP tasks. Returns (relevance, sentiment_label, sentiment_score, category)."""
    _load_models()
    
    relevance = 0.5
    sentiment_label = "neutral"
    sentiment_score = 0.0
    category = "general"
    
    if settings.NLP_BACKEND == 'huggingface':
        from sentence_transformers import util
        
        # Relevance
        emb1 = _sentence_model.encode(market_title, convert_to_tensor=True)
        emb2 = _sentence_model.encode(text, convert_to_tensor=True)
        relevance = float(util.cos_sim(emb1, emb2)[0][0])
        
        # Sentiment
        if relevance > 0.3:
            sent_result = _sentiment_pipe(text[:512])[0]
            sentiment_label = sent_result['label'].lower()
            sentiment_score = sent_result['score']
            if sentiment_label == 'negative':
                sentiment_score = -sentiment_score
                
            # Category
            candidate_labels = ["politics", "economics", "sports", "technology", "crypto", "world news"]
            cat_result = _zeroshot_pipe(text[:512], candidate_labels)
            category = cat_result['labels'][0]
    else:
        # VADER fallback
        vs = _sentiment_pipe.polarity_scores(text)
        sentiment_score = vs['compound']
        if sentiment_score >= 0.05:
            sentiment_label = 'positive'
        elif sentiment_score <= -0.05:
            sentiment_label = 'negative'
            
    return relevance, sentiment_label, sentiment_score, category

async def analyze_news_async(market_title: str, text: str) -> Tuple[float, str, float, str]:
    """Wrapper to run NLP analysis in a separate thread so it doesn't block the event loop."""
    return await asyncio.to_thread(_analyze_news_sync, market_title, text)
