import React, { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import PlatformBadge from '../components/PlatformBadge';
import ScoreRangeBadge from '../components/ScoreRangeBadge';
import { FlaggedBet } from '../types/api';

const CONFIDENCE_COLORS: Record<string, string> = {
  high: '#10b981',
  medium: '#f59e0b',
  low: '#6b7280',
};

const Dashboard: React.FC = () => {
  const [platformFilter, setPlatformFilter] = useState('all');
  const [confidenceFilter, setConfidenceFilter] = useState('all');
  const [bets, setBets] = useState<FlaggedBet[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ limit: '50' });
      if (platformFilter !== 'all') params.set('platform', platformFilter);
      if (confidenceFilter !== 'all') params.set('confidence_tier', confidenceFilter);
      
      const res = await fetch(`/api/bets/flagged?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: FlaggedBet[] = await res.json();
      setBets(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [platformFilter, confidenceFilter]);

  useEffect(() => {
    fetchBets();
  }, [fetchBets]);

  return (
    <div className="container animate-fade-in">
      <h1 className="page-title">Prediction Market Anomaly Tracker</h1>
      <p className="page-subtitle">Detecting anomalous betting patterns across Kalshi &amp; Polymarket</p>

      <nav style={{ display: 'flex', gap: '1rem', marginBottom: '1.5rem', flexWrap: 'wrap' }}>
        <Link to="/" className="btn btn-ghost" style={{ fontSize: '0.85rem' }}>Dashboard</Link>
        <Link to="/leaderboard" className="btn btn-ghost" style={{ fontSize: '0.85rem' }}>Leaderboard</Link>
        <Link to="/calibration" className="btn btn-ghost" style={{ fontSize: '0.85rem' }}>Calibration</Link>
        <Link to="/watchlists" className="btn btn-ghost" style={{ fontSize: '0.85rem' }}>Watchlists</Link>
        <Link to="/methodology" className="btn btn-ghost" style={{ fontSize: '0.85rem' }}>Methodology</Link>
      </nav>

      <div className="filter-bar">
        <div className="filter-group">
          <label>Platform:</label>
          <select value={platformFilter} onChange={(e) => setPlatformFilter(e.target.value)}>
            <option value="all">All</option>
            <option value="kalshi">Kalshi</option>
            <option value="polymarket">Polymarket</option>
          </select>
        </div>
        <div className="filter-group">
          <label>Confidence:</label>
          <select value={confidenceFilter} onChange={(e) => setConfidenceFilter(e.target.value)}>
            <option value="all">All Tiers</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
        <button onClick={fetchBets} className="btn btn-ghost" style={{ marginLeft: 'auto' }}>Refresh</button>
      </div>

      <div className="dashboard-grid">
        <div className="glass-card" style={{ gridColumn: '1 / -1' }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '1rem' }}>
            <h2>Flagged Bets</h2>
            {loading && <span className="text-muted" style={{ fontSize: '0.85rem' }}>Loading…</span>}
            {error && <span style={{ color: 'var(--color-accent-red)', fontSize: '0.85rem' }}>Error: {error}</span>}
          </div>

          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Score</th>
                  <th>Tier</th>
                  <th>Platform</th>
                  <th>Market</th>
                  <th>Side</th>
                  <th>Size</th>
                  <th>Timing</th>
                  <th>Win Rate</th>
                  <th>Cross-Platform</th>
                </tr>
              </thead>
              <tbody>
                {!loading && bets.length === 0 && (
                  <tr>
                    <td colSpan={9} style={{ textAlign: 'center', padding: '2rem', color: 'var(--color-text-muted)' }}>
                      No flagged bets yet. Start the backend to ingest market data.
                    </td>
                  </tr>
                )}
                {bets.map(bet => (
                  <tr key={bet.id}>
                    <td><ScoreRangeBadge score={bet.composite_score} /></td>
                    <td>
                      {bet.confidence_tier && (
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '999px',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          background: `${CONFIDENCE_COLORS[bet.confidence_tier] || '#6b7280'}22`,
                          color: CONFIDENCE_COLORS[bet.confidence_tier] || '#6b7280',
                          border: `1px solid ${CONFIDENCE_COLORS[bet.confidence_tier] || '#6b7280'}44`,
                        }}>
                          {bet.confidence_tier.charAt(0).toUpperCase() + bet.confidence_tier.slice(1)}
                        </span>
                      )}
                    </td>
                    <td><PlatformBadge platform={bet.platform} /></td>
                    <td>
                      <Link to={`/bets/${bet.id}`}>
                        {bet.market_title ?? `Market #${bet.market_id}`}
                      </Link>
                    </td>
                    <td>
                      <span className={`badge ${bet.side === 'yes' ? 'badge-sentiment-positive' : 'badge-sentiment-negative'}`}>
                        {bet.side.toUpperCase()}
                      </span>
                    </td>
                    <td>${Number(bet.size).toLocaleString()}</td>
                    <td>{bet.time_to_resolution_hours != null ? `${bet.time_to_resolution_hours.toFixed(1)}h` : '—'}</td>
                    <td>{bet.trader_win_rate != null ? `${(bet.trader_win_rate * 100).toFixed(1)}%` : '—'}</td>
                    <td>
                      {bet.cross_platform_corroboration != null && bet.cross_platform_corroboration > 0 ? (
                        <span style={{ color: '#f59e0b', fontWeight: 600 }}>✓ Corroborated</span>
                      ) : '—'}
                    </td>
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
