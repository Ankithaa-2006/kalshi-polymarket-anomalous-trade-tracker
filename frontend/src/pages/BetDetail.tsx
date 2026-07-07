import React from 'react';
import { useParams, Link } from 'react-router-dom';
import PlatformBadge from '../components/PlatformBadge';
import ScoreRangeBadge from '../components/ScoreRangeBadge';

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
            <h3 className="mb-4">Anomaly Breakdown</h3>
            <div className="flex items-center gap-4 mb-2">
              <span className="text-muted" style={{ width: '120px' }}>Composite Score:</span>
              <ScoreRangeBadge score={5.2} />
            </div>
            <div className="flex items-center gap-4 mb-2">
              <span className="text-muted" style={{ width: '120px' }}>Self Score:</span>
              <strong>4.1</strong>
            </div>
            <div className="flex items-center gap-4 mb-2">
              <span className="text-muted" style={{ width: '120px' }}>Market Score:</span>
              <strong>3.8</strong>
            </div>
            <div className="flex items-center gap-4 mb-2">
              <span className="text-muted" style={{ width: '120px' }}>Lifecycle Wt:</span>
              <strong>1.5x</strong>
            </div>
          </div>

          <div className="glass-card">
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
          <div className="glass-card mb-6" style={{ borderLeft: '4px solid var(--color-accent-amber)' }}>
            <h3 className="mb-2">Historical Calibration</h3>
            <div className="flex items-center gap-2 mb-2">
              <span style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--color-text-primary)' }}>72%</span>
              <span className="text-muted">Hit Rate</span>
            </div>
            <p className="text-sm text-muted">
              Historically, anomaly flags in the <strong>5.0+</strong> score range for <strong>Polymarket</strong> have been directionally correct 72% of the time.
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
