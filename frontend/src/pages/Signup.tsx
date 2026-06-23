import React, { useState } from 'react';
import { Activity, UserPlus } from 'lucide-react';
import { useNavigate, Link } from 'react-router-dom';

const API_BASE_URL = 'http://localhost:8000';

export default function Signup() {
  const [form, setForm] = useState({
    username: '',
    email: '',
    full_name: '',
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (field: string, value: string) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (form.password !== form.confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/users/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: form.username,
          email: form.email,
          full_name: form.full_name,
          password: form.password,
        }),
      });

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        throw new Error(data.detail || 'Registration failed. Please try again.');
      }

      setSuccess('Account created successfully. You can sign in now.');
      setTimeout(() => navigate('/login'), 900);
    } catch (err: any) {
      setError(err.message || 'Registration failed.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center' }}>
      <div className="glass-card animate-fade-up" style={{ width: '100%', maxWidth: '460px', padding: '2.5rem' }}>
        <div style={{ textAlign: 'center', marginBottom: '1.5rem' }}>
          <Activity color="var(--accent-cyan)" size={48} style={{ margin: '0 auto 1rem' }} />
          <h1 className="text-gradient" style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Create your account</h1>
          <p style={{ color: 'var(--text-muted)' }}>Start tracking your fitness journey</p>
        </div>

        {error && (
          <div style={{ padding: '0.8rem', background: 'rgba(255,0,85,0.1)', color: 'var(--accent-danger)', borderRadius: '8px', marginBottom: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
            {error}
          </div>
        )}

        {success && (
          <div style={{ padding: '0.8rem', background: 'rgba(0,255,136,0.12)', color: 'var(--accent-green)', borderRadius: '8px', marginBottom: '1rem', textAlign: 'center', fontSize: '0.9rem' }}>
            {success}
          </div>
        )}

        <form onSubmit={handleSignup}>
          <div className="form-group">
            <label className="form-label">Username</label>
            <input className="form-input" value={form.username} onChange={(e) => handleChange('username', e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Full Name</label>
            <input className="form-input" value={form.full_name} onChange={(e) => handleChange('full_name', e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Email</label>
            <input type="email" className="form-input" value={form.email} onChange={(e) => handleChange('email', e.target.value)} required />
          </div>
          <div className="form-group">
            <label className="form-label">Password</label>
            <input type="password" className="form-input" value={form.password} onChange={(e) => handleChange('password', e.target.value)} required />
          </div>
          <div className="form-group" style={{ marginBottom: '1rem' }}>
            <label className="form-label">Confirm Password</label>
            <input type="password" className="form-input" value={form.confirmPassword} onChange={(e) => handleChange('confirmPassword', e.target.value)} required />
          </div>

          <button type="submit" className="btn btn-primary" style={{ width: '100%' }} disabled={loading}>
            {loading ? 'Creating account...' : <><UserPlus size={18} /> Create account</>}
          </button>
        </form>

        <p style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--accent-cyan)' }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
