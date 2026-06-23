import React, { useState, useEffect } from 'react';
import { Plus, Scale, X } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useNavigate } from 'react-router-dom';

export default function Weight() {
  const [data, setData] = useState<{name: string, weight: number}[]>([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const navigate = useNavigate();

  // Form state
  const [weight, setWeight] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);

  const fetchWeightLogs = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/weight/', {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      if (response.status === 401) {
        navigate('/login');
        return;
      }
      if (response.ok) {
        const json = await response.json();
        const items = Array.isArray(json) ? json : json.items || [];
        // Format for Recharts
        const chartData = items.map((item: any) => ({
          name: new Date(item.log_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          weight: item.weight_kg
        })).reverse(); // Assuming descending from API, reverse for chronological chart
        setData(chartData);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchWeightLogs();
  }, []);

  const handleLogWeight = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/v1/weight/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          weight_kg: parseFloat(weight),
          log_date: date
        })
      });

      if (response.ok) {
        setIsModalOpen(false);
        fetchWeightLogs();
        setWeight('');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Calculate trend
  const weightTrend = data.length >= 2 ? (data[data.length - 1].weight - data[0].weight).toFixed(1) : 0;
  const trendColor = Number(weightTrend) <= 0 ? 'var(--accent-green)' : 'var(--accent-danger)';

  return (
    <div className="animate-fade-up">
      <header className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2.5rem' }}>Weight Logs</h1>
          <p style={{ color: 'var(--text-muted)' }}>Monitor your body weight progress.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} /> Log Weight
        </button>
      </header>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading weight data...</div>
      ) : (
        <div className="glass-card">
          <div className="flex-between" style={{ marginBottom: '1.5rem' }}>
            <h3 style={{ fontWeight: '600', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Scale size={20} color="var(--accent-cyan)" />
              Weight Trend
            </h3>
            {data.length >= 2 && (
              <span style={{ color: trendColor, fontWeight: 'bold' }}>
                {Number(weightTrend) > 0 ? '+' : ''}{weightTrend} kg since start
              </span>
            )}
          </div>
          
          <div style={{ height: '400px', width: '100%' }}>
            {data.length === 0 ? (
               <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)' }}>
                 No weight data logged yet.
               </div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                  <defs>
                    <linearGradient id="colorWeight" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.4}/>
                      <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <XAxis dataKey="name" stroke="var(--text-muted)" />
                  <YAxis domain={['dataMin - 1', 'dataMax + 1']} stroke="var(--text-muted)" />
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
                  <Tooltip 
                    contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                    itemStyle={{ color: 'var(--accent-cyan)' }}
                  />
                  <Area type="monotone" dataKey="weight" stroke="var(--accent-cyan)" fillOpacity={1} fill="url(#colorWeight)" />
                </AreaChart>
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
              <h2 style={{ fontSize: '1.5rem' }}>Log Weight</h2>
              <button className="btn-outline" style={{ padding: '0.4rem', border: 'none' }} onClick={() => setIsModalOpen(false)}>
                <X size={20} />
              </button>
            </div>
            
            <form onSubmit={handleLogWeight}>
              <div className="form-group">
                <label className="form-label">Weight (kg)</label>
                <input type="number" className="form-input" value={weight} onChange={(e) => setWeight(e.target.value)} required min="0" step="0.1" />
              </div>
              <div className="form-group" style={{ marginBottom: '2rem' }}>
                <label className="form-label">Date</label>
                <input type="date" className="form-input" value={date} onChange={(e) => setDate(e.target.value)} required />
              </div>
              <button type="submit" className="btn btn-primary" style={{ width: '100%' }}>Save Weight</button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
