import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../api';
import { Play, Terminal, FileCode2, Copy, CheckCircle2, Box, Cpu, AlertCircle, FileJson } from 'lucide-react';

export default function ProjectDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [deployments, setDeployments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [deploying, setDeploying] = useState(false);
  const [activeTab, setActiveTab] = useState('dockerfile');
  const [copied, setCopied] = useState('');

  useEffect(() => {
    fetchProject();
    fetchDeployments();
  }, [id]);

  const fetchProject = async () => {
    try {
      const response = await api.get(`/projects/${id}`);
      setProject(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDeployments = async () => {
    try {
      const response = await api.get(`/projects/${id}/deployments`);
      setDeployments(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    setGenerating(true);
    try {
      const response = await api.post(`/projects/${id}/generate`);
      setProject(prev => ({ ...prev, generated_configs: response.data }));
    } catch (err) {
      alert('Failed to generate configurations.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDeploy = async () => {
    setDeploying(true);
    try {
      const response = await api.post(`/projects/${id}/deploy`);
      navigate(`/deployments/${response.data.id}`);
    } catch (err) {
      alert('Failed to trigger deployment.');
      setDeploying(false);
    }
  };

  const handleCopy = (text, type) => {
    navigator.clipboard.writeText(text);
    setCopied(type);
    setTimeout(() => setCopied(''), 2000);
  };

  if (loading) return <div className="animate-pulse flex space-x-4 p-8">Loading...</div>;
  if (!project) return <div>Project not found</div>;

  const configs = project.generated_configs;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="glass-panel p-6 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <Box className="w-8 h-8 text-primary" />
            <h1 className="text-2xl font-bold">{project.repo_url ? project.repo_url.split('/').pop() : 'Unknown Repository'}</h1>
          </div>
          <p className="text-text_muted text-sm">{project.repo_url || 'No URL available'}</p>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-800 rounded-lg text-sm border border-slate-700">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span className="font-medium">{project.tech_stack?.primary_language || 'Unknown'}</span>
          </div>
          <button 
            onClick={handleGenerate} 
            disabled={generating}
            className="btn-secondary flex items-center gap-2"
          >
            <FileCode2 className="w-4 h-4" />
            {generating ? 'Generating...' : 'Regenerate AI Configs'}
          </button>
        </div>
      </div>

      {/* Configurations Section */}
      {!configs ? (
        <div className="glass-panel p-12 text-center flex flex-col items-center">
          <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mb-4">
            <Terminal className="w-8 h-8 text-blue-500" />
          </div>
          <h2 className="text-xl font-bold mb-2">No DevOps Configurations Found</h2>
          <p className="text-text_muted max-w-md mb-6">Let the AI engine analyze your codebase and automatically generate the perfect Dockerfile and CI/CD pipelines.</p>
          <button onClick={handleGenerate} disabled={generating} className="btn-primary flex items-center gap-2">
            <Cpu className="w-5 h-5" />
            {generating ? 'Analyzing Codebase...' : 'Generate AI DevOps Configs'}
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-6">
            {/* Tabs */}
            <div className="glass-panel overflow-hidden">
              <div className="flex border-b border-slate-700 bg-slate-800/50 overflow-x-auto">
                {['dockerfile', 'docker-compose.yml', 'deploy.yml'].map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveTab(tab)}
                    className={`px-6 py-3 text-sm font-medium transition-colors border-b-2 whitespace-nowrap ${
                      activeTab === tab 
                        ? 'border-primary text-white bg-slate-800' 
                        : 'border-transparent text-text_muted hover:text-white hover:bg-slate-800/50'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>
              
              <div className="relative group">
                <button 
                  onClick={() => handleCopy(configs[activeTab === 'deploy.yml' ? 'github_actions' : activeTab.replace('.yml', '_compose')], activeTab)}
                  className="absolute top-4 right-4 p-2 bg-slate-800 rounded-md border border-slate-700 text-slate-400 hover:text-white opacity-0 group-hover:opacity-100 transition-all z-10"
                >
                  {copied === activeTab ? <CheckCircle2 className="w-4 h-4 text-green-400" /> : <Copy className="w-4 h-4" />}
                </button>
                <pre className="p-6 overflow-x-auto bg-[#0d1117] text-sm text-slate-300 font-mono">
                  <code>
                    {activeTab === 'dockerfile' && configs.dockerfile}
                    {activeTab === 'docker-compose.yml' && configs.docker_compose}
                    {activeTab === 'deploy.yml' && configs.github_actions}
                  </code>
                </pre>
              </div>
            </div>
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            <div className="glass-panel p-6">
              <h3 className="font-bold mb-4 flex items-center gap-2">
                <Play className="w-5 h-5 text-green-400" />
                Actions
              </h3>
              <button 
                onClick={handleDeploy} 
                disabled={deploying}
                className="w-full py-3 bg-green-500 hover:bg-green-600 text-white font-bold rounded-lg transition-colors flex items-center justify-center gap-2 shadow-lg shadow-green-500/20 active:scale-95"
              >
                {deploying ? 'Initializing...' : 'Deploy to Local Engine'}
              </button>
            </div>

            <div className="glass-panel p-6 border-l-4 border-l-blue-500">
              <h3 className="font-bold mb-3 flex items-center gap-2">
                <FileJson className="w-5 h-5 text-blue-400" />
                AI Explanation
              </h3>
              <p className="text-sm text-text_muted leading-relaxed">
                {configs.explanation}
              </p>
            </div>

            <div className="glass-panel p-6">
              <h3 className="font-bold mb-4 text-sm uppercase tracking-wider text-text_muted">Deployment History</h3>
              {deployments.length === 0 ? (
                <p className="text-sm text-slate-500">No deployments yet.</p>
              ) : (
                <div className="space-y-3">
                  {deployments.map((dep) => (
                    <div 
                      key={dep.id} 
                      onClick={() => navigate(`/deployments/${dep.id}`)}
                      className="flex items-center justify-between p-3 rounded-lg bg-slate-800/50 border border-slate-700/50 hover:bg-slate-800 cursor-pointer transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        {dep.status === 'success' ? <CheckCircle2 className="w-4 h-4 text-green-400" /> :
                         dep.status === 'failed' ? <AlertCircle className="w-4 h-4 text-red-400" /> :
                         <Loader2 className="w-4 h-4 text-blue-400 animate-spin" />}
                        <span className="text-sm font-medium">{new Date(dep.created_at).toLocaleDateString()}</span>
                      </div>
                      <span className="text-xs text-text_muted capitalize">{dep.status}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
