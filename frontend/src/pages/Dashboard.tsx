import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Activity, Zap, Clock, TrendingUp } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export default function Dashboard() {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/api/v1/users/dashboard', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.status === 401) {
          localStorage.removeItem('token');
          navigate('/login');
          return;
        }
        
        if (response.ok) {
          const json = await response.json();
          setData(json);
        }
      } catch (err) {
        console.error(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchDashboard();
  }, [navigate]);

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>Loading dashboard...</div>;
  }

  // Fallback if data fails or is empty
  const calories = data?.total_calories_burned || 0;
  const workouts = data?.total_workouts || 0;
  const goalProgress = data?.active_goals_count ? Math.round((data.achieved_goals_count / data.active_goals_count) * 100) : 0;
  
  // Create a placeholder chart data if recent_workouts is empty
  const chartData = data?.recent_workouts?.length > 0 
    ? [...data.recent_workouts].reverse().map((w: any) => ({
        name: new Date(w.workout_date).toLocaleDateString('en-US', { weekday: 'short' }),
        calories: w.calories_burned
      }))
    : [
        { name: 'Mon', calories: 0 },
        { name: 'Tue', calories: 0 },
        { name: 'Wed', calories: 0 },
        { name: 'Thu', calories: 0 },
        { name: 'Fri', calories: 0 },
        { name: 'Sat', calories: 0 },
        { name: 'Sun', calories: 0 },
      ];

  return (
    <div className="animate-fade-up">
      <header className="flex-between" style={{ marginBottom: '2rem' }}>
        <div>
          <h1 className="text-gradient" style={{ fontSize: '2.5rem' }}>Overview</h1>
          <p style={{ color: 'var(--text-muted)' }}>Welcome back to your fitness journey.</p>
        </div>
        <button className="btn btn-primary" onClick={() => navigate('/workouts')}>
          <Activity size={18} /> New Activity
        </button>
      </header>

      <div className="grid-cols-3" style={{ marginBottom: '2rem' }}>
        <div className="glass-card flex-between">
          <div>
            <h3 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Calories Burned</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{calories} <span style={{fontSize: '1rem', color: 'var(--accent-cyan)'}}>kcal</span></p>
          </div>
          <div style={{ background: 'rgba(0, 240, 255, 0.1)', padding: '1rem', borderRadius: '50%' }}>
            <Zap size={24} color="var(--accent-cyan)" />
          </div>
        </div>
        
        <div className="glass-card flex-between">
          <div>
            <h3 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Total Workouts</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{workouts} <span style={{fontSize: '1rem', color: 'var(--accent-purple)'}}>sessions</span></p>
          </div>
          <div style={{ background: 'rgba(176, 0, 255, 0.1)', padding: '1rem', borderRadius: '50%' }}>
            <Clock size={24} color="var(--accent-purple)" />
          </div>
        </div>

        <div className="glass-card flex-between">
          <div>
            <h3 style={{ color: 'var(--text-muted)', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Goal Progress</h3>
            <p style={{ fontSize: '2rem', fontWeight: 'bold' }}>{goalProgress} <span style={{fontSize: '1rem', color: 'var(--accent-green)'}}>%</span></p>
          </div>
          <div style={{ background: 'rgba(0, 255, 136, 0.1)', padding: '1rem', borderRadius: '50%' }}>
            <TrendingUp size={24} color="var(--accent-green)" />
          </div>
        </div>
      </div>

      <div className="glass-card">
        <h3 style={{ marginBottom: '1.5rem', fontWeight: '600' }}>Recent Activity</h3>
        <div style={{ height: '300px', width: '100%' }}>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorCalories" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--accent-cyan)" stopOpacity={0.4}/>
                  <stop offset="95%" stopColor="var(--accent-cyan)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <XAxis dataKey="name" stroke="var(--text-muted)" />
              <YAxis stroke="var(--text-muted)" />
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border-color)" vertical={false} />
              <Tooltip 
                contentStyle={{ background: 'var(--bg-card)', border: '1px solid var(--border-color)', borderRadius: '8px' }}
                itemStyle={{ color: 'var(--accent-cyan)' }}
              />
              <Area type="monotone" dataKey="calories" stroke="var(--accent-cyan)" fillOpacity={1} fill="url(#colorCalories)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
