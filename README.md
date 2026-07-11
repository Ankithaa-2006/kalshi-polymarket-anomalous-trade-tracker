# Prediction Market Anomaly & Signal Tracker

A full-featured research tool that monitors prediction markets (Kalshi and Polymarket) for anomalous betting activity. It adds real-world news context using NLP, tracks trader reputation via Empirical Bayesian Shrinkage, and corroborates signals across platforms to help you judge signal quality.

## Features

- **Cross-Platform Corroboration**: Uses `sentence-transformers` to automatically match similar markets between Polymarket and Kalshi and boosts confidence scores when anomalous activity is corroborated on both platforms.
- **Trader Reputation Tracking**: Computes trader win rates and "large bet win rates", applying Bayesian shrinkage to rank the most profitable and accurate traders on a global leaderboard.
- **Smart Anomaly Scoring**: Categorizes anomalous bets into Confidence Tiers (High, Medium, Low) based on market score, self score (historical baseline), lifecycle weight, and cross-platform corroboration.
- **Automated Alerts (SMTP)**: Create custom watchlists by category or specific trader IDs. The system will email you immediately when a matching high-confidence anomaly is detected.
- **News Context**: Integrates with NewsAPI to fetch the latest headlines around the time of the bet and performs sentiment analysis to contextualize the trade.
- **Historical Calibration**: Transparently tracks its own accuracy, showing you how often a "High Confidence" flag actually predicted the correct outcome.

## Architecture

The project is split into a modern decoupled stack:

### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Database**: SQLite (via SQLAlchemy + Alembic for migrations)
- **Background Jobs**: APScheduler (for fetching market data, computing reputations, and matching markets periodically)
- **NLP / ML**: HuggingFace `sentence-transformers` for market title matching, `vaderSentiment` for news context.

### Frontend
- **Framework**: React + Vite (TypeScript)
- **Routing**: React Router DOM
- **Charts**: Recharts (for the "Explain this Flag" visual breakdown)
- **Styling**: Custom CSS with CSS Variables for a modern, dark-mode glassmorphic aesthetic.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/Ankithaa-2006/kalshi-polymarket-anomalous-trade-tracker.git
cd kalshi-polymarket-anomalous-trade-tracker
```

### 2. Backend Setup
Navigate to the backend directory and install the requirements:
```bash
cd backend
pip install -r requirements.txt
```

Set up your environment variables. Copy the example `.env` file or create a new one:
```bash
cp ../.env.example .env
```

Edit the `.env` file to include your API keys. *Note: Kalshi is disabled by default. If you wish to use it, set `ENABLE_KALSHI=True`.*
```env
# backend/.env
NEWS_API_KEY=your_news_api_key_here
ENABLE_KALSHI=False
# KALSHI_API_KEY_ID=
# KALSHI_PRIVATE_KEY_PATH=

# SMTP Configuration (Optional, for email alerts)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASS=your_app_password
SMTP_FROM=your_email@gmail.com
```

Apply database migrations:
```bash
python -m alembic upgrade head
```

Run the FastAPI server:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
Open a new terminal, navigate to the frontend directory, and install dependencies:
```bash
cd frontend
npm install
```

Start the Vite development server:
```bash
npm run dev
```
The dashboard will be available at `http://localhost:5173`.

## Usage
Once the backend and frontend are running, the backend's APScheduler will automatically begin polling for active markets every 15 minutes. 
Navigate to the **Watchlists** tab on the frontend to set up alerts for specific market categories (e.g., `politics` or `crypto`) and receive emails when anomalous activity occurs!

## Methodology
The anomaly scoring system uses Median Absolute Deviation (MAD) to detect outliers against a trader's personal baseline and the overall market baseline. A full explanation of the math, Bayesian shrinkage, and NLP pipelines can be found in the **Methodology** tab of the dashboard.
