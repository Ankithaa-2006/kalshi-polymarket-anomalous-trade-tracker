import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..database import async_session_maker
from ..models.user import User, Watchlist, AlertSent
from ..models.bet import Bet
from ..models.market import Market
from ..models.anomaly import AnomalyScore
from ..config import settings

logger = logging.getLogger(__name__)

async def dispatch_alerts(bet_id: int):
    """
    Checks active watchlists and sends SMTP alerts if a new flagged bet matches.
    """
    async with async_session_maker() as session:
        # Fetch the flagged bet
        stmt = select(Bet).join(AnomalyScore).join(Market).where(
            Bet.id == bet_id,
            AnomalyScore.flagged == True
        )
        res = await session.execute(stmt)
        bet = res.scalar_one_or_none()
        
        if not bet:
            return
            
        market_category = bet.market.category
        
        # Find matching watchlists
        # 1. Category watchlists
        stmt_watch = select(Watchlist).join(User).where(
            (Watchlist.watch_type == 'category') & (Watchlist.watch_value == market_category)
        )
        # We could also add trader watchlists logic here
        
        res_watch = await session.execute(stmt_watch)
        watchlists = res_watch.scalars().all()
        
        for w in watchlists:
            # Check if alert already sent
            stmt_sent = select(AlertSent).where(
                AlertSent.watchlist_id == w.id,
                AlertSent.bet_id == bet.id
            )
            res_sent = await session.execute(stmt_sent)
            if res_sent.scalar_one_or_none():
                continue
                
            # Send email
            user_email = w.user.email if w.user else None
            if user_email and settings.SMTP_HOST:
                try:
                    msg = MIMEMultipart()
                    msg['From'] = settings.SMTP_FROM
                    msg['To'] = user_email
                    msg['Subject'] = f"Alert: Anomalous Bet Detected in {market_category}"
                    
                    body = f"A new anomalous bet was detected on {bet.market.platform} in the market: {bet.market.title}.\n"
                    body += f"Bet Size: {bet.size} | Side: {bet.side} | Price: {bet.price}\n"
                    
                    msg.attach(MIMEText(body, 'plain'))
                    
                    server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
                    server.starttls()
                    if settings.SMTP_USER and settings.SMTP_PASS:
                        server.login(settings.SMTP_USER, settings.SMTP_PASS)
                        
                    server.send_message(msg)
                    server.quit()
                    logger.info(f"Sent email alert to {user_email} for bet {bet.id}")
                except Exception as e:
                    logger.error(f"Failed to send email alert: {e}")
                    
            # Record alert sent
            alert = AlertSent(watchlist_id=w.id, bet_id=bet.id)
            session.add(alert)
            
        await session.commit()
