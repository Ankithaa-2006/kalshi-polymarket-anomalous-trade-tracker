import React, { useState } from 'react';
import { useApi } from '../hooks/useApi';
import { Watchlist } from '../types/api';

// Hardcoded for demo purposes
const USER_ID = 1;

export default function Watchlists() {
  const { data: watchlists, loading, error, refetch } = useApi<Watchlist[]>(`/api/watchlists/${USER_ID}`);
  
  const [watchType, setWatchType] = useState('category');
  const [watchValue, setWatchValue] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!watchValue) return;
    setSubmitting(true);
    
    try {
      await fetch('/api/watchlists/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_id: USER_ID,
          watch_type: watchType,
          watch_value: watchValue
        })
      });
      setWatchValue('');
      refetch();
    } catch (err) {
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <h1>My Watchlists</h1>
      </header>
      
      <div className="card">
        <h3>Create New Watchlist</h3>
        <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
          <select value={watchType} onChange={e => setWatchType(e.target.value)}>
            <option value="category">Category</option>
            <option value="trader">Trader ID</option>
          </select>
          <input 
            type="text" 
            placeholder="e.g. politics"
            value={watchValue}
            onChange={e => setWatchValue(e.target.value)}
          />
          <button type="submit" disabled={submitting}>Add Watchlist</button>
        </form>
      </div>

      <h3 style={{ marginTop: '2rem' }}>Active Watchlists</h3>
      {loading && <div>Loading...</div>}
      {error && <div className="error">{error}</div>}
      
      {!loading && watchlists && (
        <div className="table-container" style={{ marginTop: '1rem' }}>
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Value</th>
                <th>Created At</th>
              </tr>
            </thead>
            <tbody>
              {watchlists.map(w => (
                <tr key={w.id}>
                  <td>{w.watch_type}</td>
                  <td><strong>{w.watch_value}</strong></td>
                  <td>{new Date(w.created_at).toLocaleString()}</td>
                </tr>
              ))}
              {watchlists.length === 0 && (
                <tr>
                  <td colSpan={3} style={{ textAlign: 'center' }}>No watchlists found.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
