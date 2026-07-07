import React from 'react';

const DisclaimerBanner: React.FC = () => {
  return (
    <div className="disclaimer-banner">
      <div>
        <strong>⚠️ Research Tool</strong> — This dashboard flags statistical anomalies and shows historical patterns. It does not predict outcomes and is not betting or financial advice.
      </div>
      <button className="btn btn-ghost" style={{ padding: '0.25rem 0.5rem', fontSize: '0.75rem' }}>
        Methodology
      </button>
    </div>
  );
};

export default DisclaimerBanner;
