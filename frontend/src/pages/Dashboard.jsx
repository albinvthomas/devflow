import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { Plus, GitBranch, FolderGit2, Cpu, ExternalLink } from 'lucide-react';

export default function Dashboard() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/projects');
      setProjects(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-400">Your Projects</h1>
          <p className="text-text_muted mt-1">Manage and deploy your automated environments</p>
        </div>
        <button onClick={() => navigate('/connect')} className="btn-primary flex items-center gap-2">
          <Plus className="w-5 h-5" />
          Connect Repository
        </button>
      </div>

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map((n) => (
            <div key={n} className="glass-panel p-6 h-48"></div>
          ))}
        </div>
      ) : projects.length === 0 ? (
        <div className="glass-panel p-12 text-center flex flex-col items-center justify-center">
          <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mb-4">
            <GitBranch className="w-8 h-8 text-slate-400" />
          </div>
          <h3 className="text-xl font-bold mb-2">No projects connected</h3>
          <p className="text-text_muted max-w-md mb-6">Connect your first GitHub repository to start generating DevOps configurations and deploying instantly.</p>
          <button onClick={() => navigate('/connect')} className="btn-primary">Connect Repository</button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <div 
              key={project.id} 
              className="glass-panel p-6 hover:border-primary/50 cursor-pointer transition-all hover:-translate-y-1 group relative overflow-hidden"
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              <div className="absolute top-0 left-0 w-1 h-full bg-primary/0 group-hover:bg-primary transition-colors"></div>
              
              <div className="flex items-start justify-between mb-4">
                <div className="p-3 bg-slate-800/50 rounded-lg text-primary">
                  <FolderGit2 className="w-6 h-6" />
                </div>
                <ExternalLink className="w-5 h-5 text-slate-600 group-hover:text-primary transition-colors" />
              </div>
              
              <h3 className="font-bold text-lg mb-1 truncate" title={project.repo_url || 'Unknown'}>
                {project.repo_url ? project.repo_url.split('/').pop() : 'Unknown Repository'}
              </h3>
              
              <div className="flex items-center gap-2 text-sm text-text_muted mb-4 truncate">
                <GitBranch className="w-4 h-4" />
                {project.repo_url ? project.repo_url.replace('https://github.com/', '') : 'Unknown URL'}
              </div>

                <div className="flex items-center gap-2 flex-wrap mt-auto">
                  <div className="flex items-center gap-1 px-2.5 py-1 bg-blue-500/10 text-blue-400 border border-blue-500/20 rounded-full text-xs font-medium">
                    <Cpu className="w-3 h-3" />
                    {project.tech_stack?.primary_language || 'Unknown'}
                  </div>
                  {project.latest_deployment_status && (
                    <div className={`px-2 py-1 rounded-full text-xs font-medium border ${
                      project.latest_deployment_status === 'success' ? 'bg-green-500/10 text-green-400 border-green-500/20' :
                      project.latest_deployment_status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                      project.latest_deployment_status === 'queued' ? 'bg-slate-500/10 text-slate-400 border-slate-500/20' :
                      'bg-blue-500/10 text-blue-400 border-blue-500/20'
                    }`}>
                      <span className="capitalize">{project.latest_deployment_status}</span>
                    </div>
                  )}
                </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
