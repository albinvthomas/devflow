import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';
import { GitBranch, Loader2 } from 'lucide-react';

export default function Connect() {
  const [repoUrl, setRepoUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleConnect = async (e) => {
    e.preventDefault();
    setError('');
    
    let repoFullName = repoUrl.trim();
    // Extract owner/repo if user pasted a full URL
    if (repoFullName.startsWith('http')) {
      repoFullName = repoFullName.replace(/\/$/, '');
      const parts = repoFullName.split('/');
      repoFullName = `${parts[parts.length - 2]}/${parts[parts.length - 1]}`;
    }

    setLoading(true);
    try {
      const response = await api.post('/projects', { repo_full_name: repoFullName });
      navigate(`/projects/${response.data.id}`);
    } catch (err) {
      const detail = err.response?.data?.detail;
      const errorMessage = typeof detail === 'string' ? detail : 'Failed to connect repository. Make sure it is public and valid.';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-12">
      <div className="glass-panel p-8 relative overflow-hidden">
        {/* Glow effect */}
        <div className="absolute top-0 right-0 w-64 h-64 bg-primary/10 rounded-full blur-3xl pointer-events-none"></div>

        <div className="relative z-10">
          <div className="flex items-center gap-4 mb-6">
            <div className="p-3 bg-slate-800 rounded-xl">
              <GitBranch className="w-8 h-8 text-white" />
            </div>
            <div>
              <h2 className="text-2xl font-bold">Connect Repository</h2>
              <p className="text-text_muted">Link a public GitHub repository to DevFlow</p>
            </div>
          </div>

          <form onSubmit={handleConnect} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-text_muted mb-2">Repository URL or Format (owner/repo)</label>
              <div className="flex gap-3">
                <input
                  type="text"
                  className="input-field flex-1"
                  placeholder="e.g., albinvthomas/SmartPhoneDoctor"
                  value={repoUrl}
                  onChange={(e) => setRepoUrl(e.target.value)}
                  required
                />
                <button type="submit" disabled={loading || !repoUrl} className="btn-primary whitespace-nowrap min-w-[120px] flex justify-center">
                  {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : 'Analyze'}
                </button>
              </div>
              {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
            </div>
          </form>

          <div className="mt-8 p-4 bg-slate-800/50 rounded-lg border border-slate-700/50">
            <h4 className="text-sm font-medium mb-2 flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-blue-500"></span>
              What happens next?
            </h4>
            <ul className="text-sm text-text_muted space-y-2 pl-4 list-disc marker:text-slate-600">
              <li>DevFlow will fetch the repository structure from GitHub.</li>
              <li>The AI engine will analyze the files to determine the tech stack.</li>
              <li>You can then generate custom Docker & CI/CD configurations.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
