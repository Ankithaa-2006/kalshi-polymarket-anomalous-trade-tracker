import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { LeaderboardTrader } from '../types/api';
import PlatformBadge from '../components/PlatformBadge';

export default function Leaderboard() {
  const [platform, setPlatform] = useState<string>('all');
  const { data: traders, loading, error } = useApi<LeaderboardTrader[]>(
    `/api/traders/leaderboard?platform=${platform}&limit=50`,
    [platform]
  );

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>Trader Reputation Leaderboard</h1>
        <div className="filters">
          <select value={platform} onChange={e => setPlatform(e.target.value)}>
            <option value="all">All Platforms</option>
            <option value="polymarket">Polymarket</option>
            <option value="kalshi">Kalshi</option>
          </select>
        </div>
      </header>

      {loading && <div>Loading...</div>}
      {error && <div className="error">{error}</div>}

      {!loading && !error && traders && (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Rank</th>
                <th>Trader</th>
                <th>Platform</th>
                <th>Win Rate</th>
                <th>Large Bet Win Rate</th>
                <th>Reputation Score</th>
                <th>Sample Size</th>
              </tr>
            </thead>
            <tbody>
              {traders.map((trader, index) => (
                <tr key={trader.id}>
                  <td>#{index + 1}</td>
                  <td className="mono">{trader.external_trader_id.slice(0, 8)}...</td>
                  <td><PlatformBadge platform={trader.platform} /></td>
                  <td>{trader.win_rate ? (trader.win_rate * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>{trader.large_bet_win_rate ? (trader.large_bet_win_rate * 100).toFixed(1) + '%' : 'N/A'}</td>
                  <td>
                    <strong>
                      {trader.reputation_score ? (trader.reputation_score * 100).toFixed(1) : 'N/A'}
                    </strong>
                  </td>
                  <td>{trader.total_resolved_bets}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
