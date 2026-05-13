import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { Terminal, ArrowLeft, Loader2, CheckCircle2, XCircle } from 'lucide-react';

export default function DeploymentLogs() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [deployment, setDeployment] = useState(null);
  const [logs, setLogs] = useState('');
  const logsEndRef = useRef(null);

  useEffect(() => {
    fetchDeployment();
    
    const token = localStorage.getItem('devflow_token');
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const eventSource = new EventSource(`${baseUrl}/deployments/${id}/stream?token=${token}`);
    
    eventSource.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setLogs(data.logs || 'Waiting for logs...');
      setDeployment(prev => prev ? { ...prev, status: data.status } : null);
      scrollToBottom();
      
      if (data.status === 'success' || data.status === 'failed') {
        eventSource.close();
      }
    };

    eventSource.onerror = (error) => {
      console.error("SSE Error:", error);
      eventSource.close();
    };

    return () => eventSource.close();
  }, [id]);

  const fetchDeployment = async () => {
    try {
      const response = await api.get(`/deployments/${id}`);
      setDeployment(response.data);
      const logRes = await api.get(`/deployments/${id}/logs`);
      setLogs(logRes.data.logs || 'Waiting for logs...');
      scrollToBottom();
    } catch (err) {
      console.error(err);
    }
  };

  const scrollToBottom = () => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  if (!deployment) return <div className="p-8">Loading logs...</div>;

  return (
    <div className="max-w-5xl mx-auto h-[80vh] flex flex-col">
      <div className="flex items-center justify-between mb-4">
        <button onClick={() => navigate(-1)} className="flex items-center gap-2 text-text_muted hover:text-white transition-colors">
          <ArrowLeft className="w-4 h-4" />
          Back to Project
        </button>
        
        <div className="flex items-center gap-3">
          <span className="text-sm font-mono text-slate-400">ID: {deployment.id.split('-')[0]}</span>
          <div className={`px-3 py-1 rounded-full text-sm font-medium flex items-center gap-2 border ${
            deployment.status === 'success' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
            deployment.status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
            'bg-blue-500/10 text-blue-400 border-blue-500/20'
          }`}>
            {deployment.status === 'success' && <CheckCircle2 className="w-4 h-4" />}
            {deployment.status === 'failed' && <XCircle className="w-4 h-4" />}
            {(deployment.status === 'queued' || deployment.status === 'running') && <Loader2 className="w-4 h-4 animate-spin" />}
            <span className="capitalize">{deployment.status}</span>
          </div>
        </div>
      </div>

      <div className="flex-1 glass-panel overflow-hidden flex flex-col rounded-xl border-slate-700 shadow-2xl">
        <div className="bg-slate-900 px-4 py-3 border-b border-slate-800 flex items-center gap-2 rounded-t-xl">
          <Terminal className="w-5 h-5 text-slate-400" />
          <span className="text-sm font-medium text-slate-300">Live Deployment Output</span>
        </div>
        
        <div className="flex-1 p-4 bg-[#0d1117] overflow-y-auto text-sm font-mono whitespace-pre-wrap">
          {logs.split('\n').map((line, i) => {
            // Very simple color highlighting for docker logs
            let colorClass = "text-slate-300";
            if (line.includes("ERROR:") || line.toLowerCase().includes("failed")) colorClass = "text-red-400 font-bold";
            if (line.includes("Done.") || line.includes("Successfully")) colorClass = "text-green-400";
            if (line.startsWith("Step ")) colorClass = "text-blue-300";
            if (line.includes("Cloning repository")) colorClass = "text-purple-400";

            return <div key={i} className={`mb-1 ${colorClass}`}>{line}</div>;
          })}
          <div ref={logsEndRef} />
        </div>
      </div>
    </div>
  );
}
