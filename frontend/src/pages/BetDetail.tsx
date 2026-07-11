import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import PlatformBadge from '../components/PlatformBadge';
import ScoreRangeBadge from '../components/ScoreRangeBadge';

const mockChartData = [
  { name: 'Self Score', value: 4.1, color: '#3b82f6' },
  { name: 'Market Score', value: 3.8, color: '#8b5cf6' },
  { name: 'Lifecycle Wt', value: 1.5, color: '#10b981' },
  { name: 'Cross-Platform', value: 1.0, color: '#f59e0b' },
];

const BetDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div className="container animate-fade-in">
      <div className="mb-4">
        <Link to="/" className="btn btn-ghost">&larr; Back to Dashboard</Link>
      </div>
      
      <div className="flex items-center gap-4 mb-6">
        <PlatformBadge platform="polymarket" />
        <h1 className="page-title" style={{ margin: 0, fontSize: '1.5rem' }}>
          Will the Fed cut rates in September 2026? (Bet #{id})
        </h1>
      </div>

      <div className="dashboard-grid">
        <div className="flex-col gap-6">
          
          <div className="glass-card mb-6">
            <h3 className="mb-4">"Explain This Flag" Breakdown</h3>
            <div className="flex items-center gap-4 mb-6">
              <span className="text-muted" style={{ width: '120px' }}>Composite Score:</span>
              <ScoreRangeBadge score={7.7} />
              <span className="badge badge-sentiment-positive ml-2">High Confidence</span>
            </div>
            
            <div style={{ height: '250px', width: '100%' }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mockChartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <XAxis type="number" hide />
                  <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} width={100} />
                  <Tooltip cursor={{fill: 'rgba(255,255,255,0.05)'}} contentStyle={{ backgroundColor: 'var(--color-surface)', border: 'none', borderRadius: '8px' }} />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                    {mockChartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
            <p className="text-sm text-muted mt-4">
              <strong>Formula:</strong> ((Self * 0.6) + (Market * 0.4)) * Lifecycle + Cross-Platform
            </p>
          </div>

          <div className="glass-card mb-6">
            <h3 className="mb-4">News Context</h3>
            <div style={{ borderLeft: '2px solid var(--color-border)', paddingLeft: '1rem' }}>
              <div className="mb-4">
                <span className="badge badge-sentiment-positive mb-2">Positive (0.78)</span>
                <span className="badge badge-neutral ml-2 mb-2">Economic Data</span>
                <p><strong>WSJ:</strong> "Inflation cools faster than expected in July report."</p>
              </div>
              <div>
                <span className="badge badge-sentiment-neutral mb-2">Neutral (0.12)</span>
                <p><strong>Bloomberg:</strong> "Fed officials signal readiness to adjust policy."</p>
              </div>
            </div>
          </div>
        </div>

        <div>
          <div className="glass-card mb-6" style={{ borderLeft: '4px solid var(--color-accent-blue)' }}>
            <h3 className="mb-2">Cross-Platform Corroboration</h3>
            <p className="text-sm mb-4">Similar markets on Kalshi are showing correlated anomalous activity.</p>
            <div className="flex items-center gap-2 text-sm text-muted mb-2">
              <PlatformBadge platform="kalshi" /> 
              <span>Will the Fed cut rates in Q3?</span>
            </div>
            <div className="flex justify-between items-center bg-black/20 p-2 rounded">
              <span className="text-sm">Similarity Score:</span>
              <span className="font-bold text-accent-blue">0.89</span>
            </div>
          </div>

          <div className="glass-card mb-6" style={{ borderLeft: '4px solid var(--color-accent-amber)' }}>
            <h3 className="mb-2">Trader Reputation</h3>
            <div className="flex items-center gap-2 mb-4">
              <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-text-primary)' }}>84.2</span>
              <span className="text-muted text-sm">Score</span>
            </div>
            
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted">Win Rate:</span>
              <strong>68.5%</strong>
            </div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-muted">Large Bet Win Rate:</span>
              <strong className="text-accent-amber">74.1%</strong>
            </div>
            <div className="flex justify-between items-center mt-4">
              <span className="badge badge-neutral">Resolved Bets: n=420</span>
            </div>
          </div>

          <div className="glass-card mb-6">
            <h3 className="mb-2">Historical Calibration</h3>
            <div className="flex items-center gap-2 mb-2">
              <span style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--color-text-primary)' }}>72%</span>
              <span className="text-muted">Hit Rate</span>
            </div>
            <p className="text-sm text-muted">
              Historically, <strong>High Confidence</strong> anomaly flags for <strong>Polymarket</strong> have been directionally correct 72% of the time.
            </p>
            <div className="mt-4">
              <span className="badge badge-neutral">Sample Size: n=142</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BetDetail;
