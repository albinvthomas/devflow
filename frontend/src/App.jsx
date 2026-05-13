import { useState, useEffect } from 'react';
import { AlertCircle, X } from 'lucide-react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Connect from './pages/Connect';
import ProjectDetails from './pages/ProjectDetails';
import DeploymentLogs from './pages/DeploymentLogs';

// Protected Route Wrapper
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('devflow_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const Toast = () => {
  const [toast, setToast] = useState(null);

  useEffect(() => {
    const handleToast = (e) => {
      setToast(e.detail);
      setTimeout(() => setToast(null), 5000);
    };
    window.addEventListener('devflow-toast', handleToast);
    return () => window.removeEventListener('devflow-toast', handleToast);
  }, []);

  if (!toast) return null;

  return (
    <div className="fixed bottom-4 right-4 z-[100] animate-in slide-in-from-bottom-5">
      <div className="glass-panel border-red-500/30 bg-slate-900/90 p-4 rounded-xl shadow-xl shadow-red-500/10 flex items-start gap-3 max-w-md">
        <AlertCircle className="w-5 h-5 text-red-400 shrink-0 mt-0.5" />
        <p className="text-sm text-slate-200 flex-1">{toast}</p>
        <button onClick={() => setToast(null)} className="text-slate-400 hover:text-white transition-colors">
          <X className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen relative">
        <Toast />
        {/* Simple Global Header */}
        <nav className="glass-panel border-x-0 border-t-0 rounded-none sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex-shrink-0 flex items-center gap-2 cursor-pointer" onClick={() => window.location.href='/dashboard'}>
                <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center text-white font-bold shadow-lg shadow-blue-500/50">D</div>
                <span className="font-bold text-xl tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-400">DevFlow</span>
              </div>
              <div>
                {localStorage.getItem('devflow_token') && (
                  <button 
                    onClick={() => { localStorage.removeItem('devflow_token'); window.location.href='/login'; }}
                    className="text-sm text-text_muted hover:text-white transition-colors"
                  >
                    Sign Out
                  </button>
                )}
              </div>
            </div>
          </div>
        </nav>

        {/* Page Content */}
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/connect" element={<ProtectedRoute><Connect /></ProtectedRoute>} />
            <Route path="/projects/:id" element={<ProtectedRoute><ProjectDetails /></ProtectedRoute>} />
            <Route path="/deployments/:id" element={<ProtectedRoute><DeploymentLogs /></ProtectedRoute>} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
