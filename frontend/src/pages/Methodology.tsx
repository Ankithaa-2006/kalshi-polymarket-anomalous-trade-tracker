import React from 'react';

export default function Methodology() {
  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Methodology & Track Record</h1>
      </header>

      <div className="card" style={{ marginTop: '2rem' }}>
        <h2>Anomaly Scoring (MAD)</h2>
        <p>
          We calculate anomalies using Median Absolute Deviation (MAD), a robust statistic that is less sensitive to extreme outliers than standard deviation. 
          For each bet, we compare its size against both the trader's historical baseline and the market's historical baseline.
        </p>

        <h2 style={{ marginTop: '1.5rem' }}>Trader Reputation & Empirical Bayesian Shrinkage</h2>
        <p>
          Instead of just ranking traders by raw win rate, we use empirical Bayesian shrinkage. A trader with a 100% win rate on 2 bets will be shrunk heavily towards the global average, whereas a trader with a 65% win rate on 10,000 bets will have a reputation score very close to 65%. 
          This ensures the leaderboard highlights statistically significant performance.
        </p>

        <h2 style={{ marginTop: '1.5rem' }}>Cross-Platform Corroboration</h2>
        <p>
          We use <code>sentence-transformers</code> (specifically <code>all-MiniLM-L6-v2</code>) to compute embedding similarity between market titles across Kalshi and Polymarket. 
          If a bet is flagged as anomalous on one platform, we check its paired market on the other platform. If anomalous activity is detected on both platforms independently, the confidence tier of the signal is boosted.
        </p>
        
        <h2 style={{ marginTop: '1.5rem', color: '#ff4444' }}>Disclaimer: Not Betting Advice</h2>
        <p>
          This tool identifies statistical anomalies, cross-platform corroboration, and historical patterns. It does not predict future outcomes and is strictly for research purposes.
        </p>
      </div>
    </div>
  );
}
