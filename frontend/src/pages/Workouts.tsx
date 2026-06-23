import React, { useState, useEffect } from 'react';
import { Plus, Flame, Clock, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface Workout {
  id: number;
  workout_name: string;
  category: string;
  duration_minutes: number;
  calories_burned: number;
  workout_date: string;
}

export default function Workouts() {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  // Form state
  const [name, setName] = useState('');
  const [category, setCategory] = useState('Cardio');
  const [duration, setDuration] = useState('');
  const [calories, setCalories] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchWorkouts = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/workouts/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.status === 401) {
        navigate('/login');
        return;
      }
      if (response.ok) {
        const data = await response.json();
        // data could be paginated or an array
        setWorkouts(Array.isArray(data) ? data : data.items || []);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWorkouts();
  }, []);

  const handleLogWorkout = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/workouts/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          workout_name: name,
          category,
          duration_minutes: parseInt(duration),
          calories_burned: parseInt(calories),
          workout_date: date
        })
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchWorkouts();
        // Reset form
        setName('');
        setDuration('');
        setCalories('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="animate-fade-up">
      <header className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2.5rem' }}>Workouts</h1>
          <p style={{ color: 'var(--text-muted)' }}>Track your recent physical activities.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} /> Log Workout
        </button>
      </header>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading workouts...</div>
      ) : (
        <div className="grid-cols-3">
          {workouts.length === 0 ? (
            <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '3rem', color: 'var(--text-muted)', background: 'var(--bg-card)', borderRadius: '16px' }}>
              No workouts logged yet. Click "Log Workout" to get started!
            </div>
          ) : (
            workouts.map((w) => (
              <div key={w.id} className="glass-card">
                <div className="flex-between" style={{ marginBottom: '1rem' }}>
                  <span className={`badge ${w.category === 'Cardio' ? 'badge-green' : 'badge-purple'}`}>
                    {w.category}
                  </span>
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{w.workout_date}</span>
                </div>
                <h3 style={{ fontSize: '1.2rem', marginBottom: '1.5rem' }}>{w.workout_name}</h3>
                
                <div className="flex-between" style={{ borderTop: '1px solid var(--border-color)', paddingTop: '1rem' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--text-muted)' }}>
                    <Clock size={16} />
                    <span style={{ fontSize: '0.9rem' }}>{w.duration_minutes} min</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--accent-danger)' }}>
                    <Flame size={16} />
                    <span style={{ fontSize: '0.9rem', fontWeight: 'bold' }}>{w.calories_burned} kcal</span>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.5rem' }}>Log Workout</h2>
              <button className="btn-outline" style={{ padding: '0.4rem', border: 'none' }} onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleLogWorkout}>
              <div className="form-group">
                <label className="form-label">Workout Name</label>
                <input type="text" className="form-input" value={name} onChange={(e) => setName(e.target.value)} required placeholder="e.g. Morning Run" />
              </div>
              <div className="form-group">
                <label className="form-label">Category</label>
                <select className="form-input" value={category} onChange={(e) => setCategory(e.target.value)}>
                  <option value="Cardio">Cardio</option>
                  <option value="Strength">Strength</option>
                  <option value="HIIT">HIIT</option>
                  <option value="Flexibility">Flexibility</option>
                  <option value="Other">Other</option>
                </select>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Duration (min)</label>
                  <input type="number" className="form-input" value={duration} onChange={(e) => setDuration(e.target.value)} required min="1" />
                </div>
                <div className="form-group" style={{ flex: 1 }}>
                  <label className="form-label">Calories Burned</label>
                  <input type="number" className="form-input" value={calories} onChange={(e) => setCalories(e.target.value)} required min="0" />
                </div>
              </div>
              <div className="form-group" style={{ marginBottom: '2rem' }}>
                <label className="form-label">Date</label>
                <input type="date" className="form-input" value={date} onChange={(e) => setDate(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Save Workout</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
