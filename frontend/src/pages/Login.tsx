import React, { useState } from 'react';
import { Activity, LogIn } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';

const API_BASE_URL = 'http://localhost:8000';

export default function Login() {
  const [username, setUsername] = useState('testuser');
  const [password, setPassword] = useState('TestPass123!');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        throw new Error('Invalid username or password');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      navigate('/');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-card animate-fade-up" style={{ width: '100%', maxWidth: '400px', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <Activity color="var(--accent-cyan)" size={48} style={{ margin: '0 auto 1rem' }} />
          <h1 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>FitTrack</h1>
          <p style={{ color: 'var(--text-muted)' }}>Sign in to continue</p>
        </div>

        {error && (
          <div style={{ padding: '0.8rem', background: 'rgba(255,0,85,0.1)', color: 'var(--accent-danger)', borderRadius: '8px', marginBottom: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}

        <form onSubmit={handleLogin}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input 
              type="text" 
              className="form-input" 
              value={username} 
              onChange={(e) => setUsername(e.target.value)}
              required 
            />
          </div>
          <div className="form-group" style={{ marginBottom: '2rem' }}>
            <label className="form-label">Password</label>
            <input 
              type="password" 
              className="form-input" 
              value={password} 
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Signing in...' : <><LogIn size={18} /> Sign In</>}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--text-muted)' }}>
          Don’t have an account? <Link to="/signup" style={{ color: 'var(--accent-cyan)' }}>Create one</Link>
        </p>
      </div>
    </div>
  );
}
