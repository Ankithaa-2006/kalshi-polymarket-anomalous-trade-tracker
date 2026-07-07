import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import PlatformBadge from '../components/PlatformBadge';
import ScoreRangeBadge from '../components/ScoreRangeBadge';

// Mock data until API is ready
const MOCK_BETS = [
  {
    id: 1,
    market_title: "Will the Fed cut rates in September 2026?",
    platform: "polymarket",
    side: "yes",
    size: 250000,
    time_to_resolution_hours: 4.5,
    composite_score: 5.2,
    scoring_mode: 'full',
    trader_win_rate: 0.65,
    calibration_hit_rate: 0.72,
    calibration_sample_size: 142
  },
  {
    id: 2,
    market_title: "Who will win the 2026 Midterms?",
    platform: "kalshi",
    side: "no",
    size: 50000,
    time_to_resolution_hours: 72,
    composite_score: 3.8,
    scoring_mode: 'market_only',
    trader_win_rate: null,
    calibration_hit_rate: 0.58,
    calibration_sample_size: 45
  }
];

const Dashboard: React.FC = () => {
  const [platformFilter, setPlatformFilter] = useState('all');

  return (
    <div className="container animate-fade-in">
      <h1 className="page-title">Prediction Market Anomaly Tracker</h1>
      <p className="page-subtitle">Detecting anomalous betting patterns across Kalshi & Polymarket</p>

      <div className="filter-bar">
        <div className="filter-group">
          <label>Platform:</label>
          <select value={platformFilter} onChange={(e) => setPlatformFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="kalshi">Kalshi</option>
            <option value="polymarket">Polymarket</option>
          </select>
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
          <h2 className="mb-4">Flagged Bets</h2>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Score</th>
                  <th>Platform</th>
                  <th>Market</th>
                  <th>Side</th>
                  <th>Size</th>
                  <th>Timing</th>
                  <th>Win Rate</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_BETS.map(bet => (
                  <tr key={bet.id}>
                    <td><ScoreRangeBadge score={bet.composite_score} /></td>
                    <td><PlatformBadge platform={bet.platform} /></td>
                    <td>
                      <Link to={`/bets/${bet.id}`}>
                        {bet.market_title}
                      </Link>
                    </td>
                    <td>
                      <span className={`badge ${bet.side === 'yes' ? 'badge-sentiment-positive' : 'badge-sentiment-negative'}`}>
                        {bet.side.toUpperCase()}
                      </span>
                    </td>
                    <td>${bet.size.toLocaleString()}</td>
                    <td>{bet.time_to_resolution_hours}h before close</td>
                    <td>{bet.trader_win_rate ? `${(bet.trader_win_rate * 100).toFixed(1)}%` : '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
