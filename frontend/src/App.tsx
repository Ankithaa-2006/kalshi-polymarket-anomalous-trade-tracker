import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import BetDetail from './pages/BetDetail';
import CalibrationView from './pages/CalibrationView';
import Leaderboard from './pages/Leaderboard';
import Watchlists from './pages/Watchlists';
import Methodology from './pages/Methodology';
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
          <Route path="/leaderboard" element={<Leaderboard />} />
          <Route path="/watchlists" element={<Watchlists />} />
          <Route path="/methodology" element={<Methodology />} />
        </Routes>
        <DisclaimerBanner />
      </div>
    </BrowserRouter>
  );
}

export default App;
