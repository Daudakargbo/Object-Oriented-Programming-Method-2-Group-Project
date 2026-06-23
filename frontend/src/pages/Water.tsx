import React, { useState, useEffect } from 'react';
import { Plus, Droplets, X } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';

export default function Water() {
  const [data, setData] = useState<{name: string, ml: number}[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  // Form state
  const [amount, setAmount] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchWaterLogs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/water/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.status === 401) {
        navigate('/login');
        return;
      }
      if (response.ok) {
        const json = await response.json();
        const items = Array.isArray(json) ? json : json.items || [];
        
        // Group by date for the chart
        const grouped: Record<string, number> = {};
        items.forEach((item: any) => {
          const d = new Date(item.log_date).toLocaleDateString('en-US', { weekday: 'short' });
          grouped[d] = (grouped[d] || 0) + item.amount_ml;
        });
        
        const chartData = Object.keys(grouped).map(k => ({ name: k, ml: grouped[k] }));
        setData(chartData);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWaterLogs();
  }, []);

  const handleLogWater = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/water/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          amount_ml: parseFloat(amount),
          log_date: date
        })
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchWaterLogs();
        setAmount('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="animate-fade-up">
      <header className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2.5rem' }}>Water Intake</h1>
          <p style={{ color: 'var(--text-muted)' }}>Stay hydrated. Track your daily water consumption.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} /> Log Water
        </button>
      </header>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading water logs...</div>
      ) : (
        <div className="glass-card">
          <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Droplets size={20} color="var(--accent-cyan)" />
              Weekly Hydration
            </h3>
            <span style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Daily Target: <strong style={{color:'var(--text-main)'}}>2500 ml</strong></span>
          </div>
          
          <div style={{ height: '350px', width: '100%' }}>
            {data.length === 0 ? (
               <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                 No water data logged yet.
               </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }} barSize={30}>
                  <XAxis dataKey="name" stroke="var(--text-muted)" axisLine={false} tickLine={false} />
                  <YAxis stroke="var(--text-muted)" axisLine={false} tickLine={false} />
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <Tooltip 
                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--accent-cyan)' }}
                  />
                  <Bar dataKey="ml" fill="var(--accent-cyan)" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.5rem' }}>Log Water Intake</h2>
              <button className="btn-outline" style={{ padding: '0.4rem', border: 'none' }} onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleLogWater}>
              <div className="form-group">
                <label className="form-label">Amount (ml)</label>
                <input type="number" className="form-input" value={amount} onChange={(e) => setAmount(e.target.value)} required min="0" step="10" placeholder="e.g. 250" />
              </div>
              <div className="form-group" style={{ marginBottom: '2rem' }}>
                <label className="form-label">Date</label>
                <input type="date" className="form-input" value={date} onChange={(e) => setDate(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Save Water Log</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
