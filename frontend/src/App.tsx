import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import BetDetail from './pages/BetDetail';
import CalibrationView from './pages/CalibrationView';
import DisclaimerBanner from './components/DisclaimerBanner';
import './index.css';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/bets/:id" element={<BetDetail />} />
          <Route path="/calibration" element={<CalibrationView />} />
        </Routes>
        <DisclaimerBanner />
      </div>
    </BrowserRouter>
  );
}

export default App;
