import React from 'react';
import { Link } from 'react-router-dom';

const CalibrationView: React.FC = () => {
  return (
    <div className="container animate-fade-in">
      <div className="mb-4">
        <Link to="/" className="btn btn-ghost">&larr; Back to Dashboard</Link>
      </div>
      
      <h1 className="page-title">Calibration Analysis</h1>
      <p className="page-subtitle">Historical accuracy of anomaly flags</p>

      <div className="glass-card mb-6 text-center" style={{ padding: '3rem' }}>
        <h2 className="text-muted mb-4">Under Construction</h2>
        <p>This view will contain Recharts visualizations showing hit rates across score bands and platforms.</p>
      </div>
    </div>
  );
};

export default CalibrationView;
