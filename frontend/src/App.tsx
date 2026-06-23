import React from 'react';
import { BrowserRouter, Routes, Route, NavLink, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { LayoutDashboard, Activity, Target, Droplets, Scale, LogOut } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Workouts from './pages/Workouts';
import Goals from './pages/Goals';
import Weight from './pages/Weight';
import Water from './pages/Water';
import Login from './pages/Login';
import Signup from './pages/Signup';
import './index.css';

function Sidebar() {
  const navigate = useNavigate();

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  return (
    <aside className="sidebar">
      <div style={{ marginBottom: '3rem', padding: '0 1rem' }}>
        <h2 style={{ fontSize: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Activity color="var(--accent-cyan)" />
          <span className="text-gradient">FitTrack</span>
        </h2>
      </div>

      <nav style={{ flex: 1 }}>
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`} end>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/workouts" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Activity size={20} />
          <span>Workouts</span>
        </NavLink>
        <NavLink to="/goals" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Target size={20} />
          <span>Goals</span>
        </NavLink>
        <NavLink to="/weight" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Scale size={20} />
          <span>Weight</span>
        </NavLink>
        <NavLink to="/water" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <Droplets size={20} />
          <span>Water Logs</span>
        </NavLink>
      </nav>

      <div style={{ marginTop: 'auto', paddingTop: '2rem', borderTop: '1px solid var(--border-color)' }}>
        <div className="nav-item" style={{ cursor: 'pointer', color: 'var(--accent-danger)' }} onClick={handleLogout}>
          <LogOut size={20} />
          <span>Logout</span>
        </div>
      </div>
    </aside>
  );
}

function PrivateRoute({ children }: { children: React.ReactNode }) {
  const token = localStorage.getItem('token');
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return <>{children}</>;
}

function MainLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="app-container">
      <Sidebar />
      <main className="main-content">
        {children}
      </main>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/signup" element={<Signup />} />
        
        {/* Protected Routes */}
        <Route path="/" element={<PrivateRoute><MainLayout><Dashboard /></MainLayout></PrivateRoute>} />
        <Route path="/workouts" element={<PrivateRoute><MainLayout><Workouts /></MainLayout></PrivateRoute>} />
        <Route path="/goals" element={<PrivateRoute><MainLayout><Goals /></MainLayout></PrivateRoute>} />
        <Route path="/weight" element={<PrivateRoute><MainLayout><Weight /></MainLayout></PrivateRoute>} />
        <Route path="/water" element={<PrivateRoute><MainLayout><Water /></MainLayout></PrivateRoute>} />
        
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
