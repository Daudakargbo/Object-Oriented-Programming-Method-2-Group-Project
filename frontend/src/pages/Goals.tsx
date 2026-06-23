import React, { useState, useEffect } from 'react';
import { Plus, Target, CheckCircle, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Goal {
  id: number;
  goal_name: string;
  target_value: number;
  current_value: number;
  deadline: string;
  is_achieved: boolean;
}

export default function Goals() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  // Form state
  const [name, setName] = useState('');
  const [target, setTarget] = useState('');
  const [deadline, setDeadline] = useState('');

  const fetchGoals = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/goals/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.status === 401) {
        navigate('/login');
        return;
      }
      if (response.ok) {
        const data = await response.json();
        setGoals(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGoals();
  }, []);

  const handleCreateGoal = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/goals/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          goal_name: name,
          target_value: parseFloat(target),
          deadline: deadline
        })
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchGoals();
        setName('');
        setTarget('');
        setDeadline('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="animate-fade-up">
      <header className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2.5rem' }}>Goals</h1>
          <p style={{ color: 'var(--text-muted)' }}>Track your long-term fitness milestones.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} /> New Goal
        </button>
      </header>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading goals...</div>
      ) : (
        <div className="grid-cols-3">
          {goals.length === 0 ? (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', background: 'var(--bg-card)', borderRadius: '16px' }}>
              No goals set yet. Click "New Goal" to get started!
            </div>
          ) : (
            goals.map((g) => {
              const progress = Math.min((g.current_value / g.target_value) * 100, 100);
              return (
                <div key={g.id} className="glass-card" style={{ position: 'relative', overflow: 'hidden' }}>
                  <div className="flex-between" style={{ marginBottom: '1rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: g.is_achieved ? 'var(--accent-green)' : 'var(--accent-cyan)' }}>
                      {g.is_achieved ? <CheckCircle size={20} /> : <Target size={20} />}
                      <span style={{ fontWeight: '600' }}>{g.is_achieved ? 'Completed' : 'Active'}</span>
                    </div>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Due: {g.deadline}</span>
                  </div>
                  
                  <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem' }}>{g.goal_name}</h3>
                  
                  <div style={{ marginBottom: '0.5rem', display: 'flex', justifyContent: 'space-between', fontSize: '0.9rem' }}>
                    <span style={{ color: 'var(--text-main)' }}>{g.current_value}</span>
                    <span style={{ color: 'var(--text-muted)' }}>{g.target_value} target</span>
                  </div>
                  
                  {/* Progress Bar */}
                  <div style={{ width: '100%', height: '8px', background: 'rgba(255,255,255,0.1)', borderRadius: '4px', overflow: 'hidden' }}>
                    <div style={{ 
                      width: `${progress}%`, 
                      height: '100%', 
                      background: g.is_achieved ? 'var(--accent-green)' : 'linear-gradient(90deg, var(--accent-cyan), var(--accent-purple))',
                      transition: 'width 1s ease-in-out'
                    }} />
                  </div>
                </div>
              );
            })
          )}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.5rem' }}>Create New Goal</h2>
              <button className="btn-outline" style={{ padding: '0.4rem', border: 'none' }} onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleCreateGoal}>
              <div className="form-group">
                <label className="form-label">Goal Name</label>
                <input type="text" className="form-input" value={name} onChange={(e) => setName(e.target.value)} required placeholder="e.g. Lose 5kg" />
              </div>
              <div className="form-group">
                <label className="form-label">Target Value</label>
                <input type="number" className="form-input" value={target} onChange={(e) => setTarget(e.target.value)} required min="0" step="0.1" />
              </div>
              <div className="form-group" style={{ marginBottom: '2rem' }}>
                <label className="form-label">Deadline</label>
                <input type="date" className="form-input" value={deadline} onChange={(e) => setDeadline(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Create Goal</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
