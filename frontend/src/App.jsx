import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({ errorInfo: `${error.toString()} \n ${errorInfo.componentStack}` });
    console.error("ErrorBoundary caught:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{ padding: '2rem', color: 'red', background: '#fee2e2', borderRadius: '8px', margin: '2rem' }}>
          <h2>Something went wrong in the UI.</h2>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: '12px' }}>{this.state.errorInfo}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}

const API_URL = 'http://localhost:8000';

function getToken() {
  return localStorage.getItem('ats_token');
}

function setToken(token) {
  localStorage.setItem('ats_token', token);
}

function clearToken() {
  localStorage.removeItem('ats_token');
}

function api() {
  const token = getToken();
  const client = axios.create({ baseURL: API_URL });
  if (token) {
    client.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  }
  client.interceptors.response.use(
    (r) => r,
    (err) => {
      // If we get a 401 from a protected route (not login), we might want to log out
      // However, we shouldn't reload automatically as it breaks the login/register flow.
      if (err.response?.status === 401 && err.config.url !== '/login') {
        clearToken();
        localStorage.removeItem('ats_role');
        // Let the component handle the redirect based on token state
      }
      return Promise.reject(err);
    }
  );
  return client;
}

// SVG Icons
const Icons = {
  Dashboard: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="9" rx="1"></rect><rect x="14" y="3" width="7" height="5" rx="1"></rect><rect x="14" y="12" width="7" height="9" rx="1"></rect><rect x="3" y="16" width="7" height="5" rx="1"></rect></svg>,
  Briefcase: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="7" width="20" height="14" rx="2" ry="2"></rect><path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"></path></svg>,
  Upload: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>,
  CheckCircle: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>,
  XCircle: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>,
  Clock: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>,
  User: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>,
  Logout: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>,
  Settings: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>,
  Play: () => <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>,
  FileText: () => <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
};

function App() {
  const [token, setTokenState] = useState(getToken());
  const [role, setRole] = useState(localStorage.getItem('ats_role') || 'student');

  const handleLogin = (newToken, newRole) => {
    setToken(newToken);
    setTokenState(newToken);
    localStorage.setItem('ats_role', newRole);
    setRole(newRole);
  };

  const handleLogout = () => {
    clearToken();
    setTokenState(null);
    localStorage.removeItem('ats_role');
  };

  if (!token) {
    return <AuthPage onLogin={handleLogin} />;
  }

  return (
    <ErrorBoundary>
      <div className="app-container">
        <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo-icon">AI</div>
          <h2>AI-ATS</h2>
        </div>
        
        <nav className="sidebar-nav">
          <div className="nav-item active">
            <Icons.Dashboard />
            <span>Dashboard</span>
          </div>
          {role === 'admin' && (
            <div className="nav-item">
              <Icons.Settings />
              <span>Settings</span>
            </div>
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="avatar">
              <Icons.User />
            </div>
            <div className="user-info">
              <span className="user-role">{role === 'student' ? 'Candidate' : 'Administrator'}</span>
            </div>
          </div>
          <button className="logout-btn" onClick={handleLogout}>
            <Icons.Logout />
          </button>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="page-title">
            <h1>{role === 'student' ? 'Candidate Portal' : 'Admin Console'}</h1>
            <p className="subtitle">Welcome back. Here is your overview.</p>
          </div>
        </header>
        
        <div className="content-scroll">
          {role === 'student' ? <StudentPage /> : <AdminPage />}
        </div>
      </main>
    </div>
    </ErrorBoundary>
  );
}

function AuthPage({ onLogin }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [isLogin, setIsLogin] = useState(true);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      if (isLogin) {
        // Just try to login
        const res = await api().post('/login', { email, password });
        onLogin(res.data.access_token, res.data.role);
      } else {
        // Try to register
        try {
          await api().post('/register', { email, password });
          // If successful, log them in
          const res = await api().post('/login', { email, password });
          onLogin(res.data.access_token, res.data.role);
        } catch (regErr) {
          setError(regErr.response?.data?.detail || regErr.message || 'Registration failed');
        }
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || (isLogin ? 'Login failed' : 'Registration failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-split">
        <div className="auth-hero">
          <div className="hero-content">
            <div className="logo-icon large">AI</div>
            <h1>Next-Gen AI Recruiting</h1>
            <p>Streamline your hiring process with advanced machine learning algorithms and role-based agent architecture.</p>
          </div>
        </div>
        <div className="auth-form-wrapper">
          <div className="auth-card">
            <h2>{isLogin ? 'Welcome Back' : 'Create Account'}</h2>
            <p className="auth-subtitle">
              {isLogin 
                ? 'Enter your credentials to access your account.' 
                : 'Sign up to apply for roles or publish new pipelines.'}
            </p>
            
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label>Email Address</label>
                <div className="input-with-icon">
                  <Icons.User />
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="name@company.com"
                    required
                  />
                </div>
              </div>
              
              <div className="input-group">
                <label>Password</label>
                <div className="input-with-icon">
                  <Icons.Settings />
                  <input
                    type="password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    required
                  />
                </div>
              </div>
              
              {error && <div className="feedback error-feedback"><Icons.XCircle/> {error}</div>}
              
              <button type="submit" className="btn-primary full-width" disabled={loading}>
                {loading ? <span className="spinner"></span> : (isLogin ? 'Sign In' : 'Sign Up')}
              </button>
            </form>
            
            <div className="auth-footer">
              <p>
                {isLogin ? "Don't have an account?" : "Already have an account?"} 
                <button 
                  type="button" 
                  className="btn-link" 
                  onClick={() => setIsLogin(!isLogin)}
                >
                  {isLogin ? 'Sign Up' : 'Log In'}
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StudentPage() {
  const [file, setFile] = useState(null);
  const [jds, setJds] = useState([]);
  const [selectedJd, setSelectedJd] = useState(null);
  const [myResumes, setMyResumes] = useState([]);
  const [checkJdId, setCheckJdId] = useState('');
  const [checkFilename, setCheckFilename] = useState('');
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');
  const [checkingStatus, setCheckingStatus] = useState(false);

  const fetchJds = async () => {
    try {
      const res = await api().get('/jds');
      setJds(res.data.jds || []);
    } catch (_) {}
  };

  const fetchMyResumes = async () => {
    try {
      const res = await api().get('/my-resumes');
      setMyResumes(res.data.resumes || []);
      if (res.data.resumes?.length && !checkFilename) {
        setCheckFilename(res.data.resumes[0].filename);
        const jd = jds.find(j => j.title === res.data.resumes[0].jd_title);
        if (jd) setCheckJdId(jd.id);
      }
    } catch (_) {}
  };

  useEffect(() => {
    fetchJds();
  }, []);

  useEffect(() => {
    if (jds.length) fetchMyResumes();
  }, [jds, successMsg, checkFilename]);

  const handleUpload = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    if (!file) {
      setError('Please select a PDF file.');
      return;
    }
    if (!selectedJd) {
      setError('Please select a job for your application.');
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('resume', file);
      const res = await api().post(`/upload-resume?jd_id=${selectedJd}`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setSuccessMsg(`Successfully applied with ${res.data.filename}`);
      setCheckFilename(res.data.filename);
      setCheckJdId(selectedJd);
      setFile(null);
      if (document.getElementById('resume-input')) {
        document.getElementById('resume-input').value = '';
      }
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Upload failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleCheckStatus = async (e) => {
    e.preventDefault();
    setCheckingStatus(true);
    try {
      const res = await api().get(`/status/${checkJdId}/${encodeURIComponent(checkFilename)}`);
      setStatus(res.data);
    } catch (err) {
      // ignore
    } finally {
      setCheckingStatus(false);
    }
  };

  const selectedJobDetail = selectedJd ? jds.find(j => j.id === selectedJd) : null;

  return (
    <div className="dashboard-grid">
      <div className="main-column">
        <section className="glass-panel">
          <div className="panel-header">
            <h3><Icons.Briefcase /> Available Opportunities</h3>
            <span className="badge-count">{jds.length} Jobs</span>
          </div>
          
          <div className="cards-grid">
            {jds.length > 0 ? (
              jds.map(jd => (
                <div key={jd.id} className={`job-card ${selectedJd === jd.id ? 'selected' : ''}`} onClick={() => setSelectedJd(jd.id)}>
                  <div className="job-card-header">
                    <h4>{jd.title}</h4>
                  </div>
                  <div className="job-card-body">
                    <p className="description-preview">
                      {jd.description_text 
                        ? jd.description_text.slice(0, 150) + "..." 
                        : "Click to view full description."}
                    </p>
                  </div>
                  <div className="job-card-meta">
                    <span className="meta-tag"><Icons.FileText /> Description loaded</span>
                  </div>
                  <button className={`select-btn ${selectedJd === jd.id ? 'active' : ''}`}>
                    {selectedJd === jd.id ? 'Selected to Apply' : 'View & Apply'}
                  </button>
                </div>
              ))
            ) : (
              <div className="empty-state">
                <Icons.Briefcase />
                <p>No open positions at the moment.</p>
              </div>
            )}
          </div>
        </section>

        {selectedJd && (
          <section className="glass-panel slide-up">
            <div className="panel-header">
              <h3><Icons.FileText /> Job Details: {selectedJobDetail?.title}</h3>
            </div>
            <div className="job-full-description">
              <div className="description-content">
                {selectedJobDetail?.description_text ? (
                   selectedJobDetail.description_text.split('\n').map((line, i) => (
                     <p key={i}>{line}</p>
                   ))
                ) : (
                  <p className="dim">No detailed description available for this role.</p>
                )}
              </div>
            </div>
          </section>
        )}

        {selectedJd && (
          <section className="glass-panel slide-up">
            <div className="panel-header">
              <h3><Icons.Upload /> Apply for {selectedJobDetail?.title}</h3>
            </div>
            
            <form onSubmit={handleUpload} className="modern-form">
              <div className="file-upload-zone">
                <input
                  id="resume-input"
                  type="file"
                  accept=".pdf"
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="file-input-hidden"
                />
                <label htmlFor="resume-input" className="file-upload-label">
                  <div className="upload-icon-large"><Icons.Upload /></div>
                  <span className="upload-title">{file ? file.name : "Click to select or drag PDF here"}</span>
                  <span className="upload-subtitle">Only .pdf files are accepted. Max 5MB.</span>
                </label>
              </div>
              
              {error && <div className="feedback error-feedback"><Icons.XCircle/> {error}</div>}
              {successMsg && <div className="feedback success-feedback"><Icons.CheckCircle/> {successMsg}</div>}
              
              <div className="form-actions">
                <button type="submit" disabled={loading || !file} className="btn-primary">
                  {loading ? <span className="spinner"></span> : 'Submit Application'}
                </button>
              </div>
            </form>
          </section>
        )}
      </div>

      <div className="side-column">
        <section className="glass-panel">
          <div className="panel-header">
            <h3>Track Status</h3>
          </div>
          
          <form onSubmit={handleCheckStatus} className="status-form">
            <div className="input-group">
              <label>Select Your Application</label>
              {myResumes.length > 0 ? (
                <select className="premium-select" value={`${checkJdId}|${checkFilename}`} onChange={(e) => {
                  const [jid, fn] = e.target.value.split('|');
                  setCheckJdId(jid);
                  setCheckFilename(fn);
                  setStatus(null);
                }}>
                  {myResumes.map(r => (
                    <option key={`${r.jd_title}|${r.filename}`} value={`${jds.find(j => j.title === r.jd_title)?.id}|${r.filename}`}>
                      {r.jd_title} ({r.filename})
                    </option>
                  ))}
                </select>
              ) : (
                <div className="empty-select">You haven't applied yet.</div>
              )}
            </div>
            
            <button type="submit" disabled={checkingStatus || !myResumes.length} className="btn-secondary full-width">
              {checkingStatus ? <span className="spinner"></span> : 'Check Analysis Result'}
            </button>
          </form>

          {status && (
            <div className={`status-result-card ${status.passed === true ? 'approved' : status.passed === false ? 'rejected' : 'pending'}`}>
              <div className="status-icon">
                {status.passed === true ? <Icons.CheckCircle /> : status.passed === false ? <Icons.XCircle /> : <Icons.Clock />}
              </div>
              <div className="status-body">
                <h4>{status.filename}</h4>
                <p className="status-message">{status.message}</p>
                {status.score != null && (
                  <div className="status-metrics">
                    <div className="metric">
                      <span className="metric-label">AI Score</span>
                      <span className="metric-value">{(status.score * 100).toFixed(0)}%</span>
                    </div>
                    <div className="metric">
                      <span className="metric-label">Rank</span>
                      <span className="metric-value">#{status.rank}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

function AdminPage() {
  const [title, setTitle] = useState('');
  const [jdFile, setJdFile] = useState(null);
  const [deadline, setDeadline] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [jds, setJds] = useState([]);
  const [selectedJdId, setSelectedJdId] = useState(Number(localStorage.getItem('ats_last_jd')) || null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [jdStats, setJdStats] = useState({});
  const [runningAnalysis, setRunningAnalysis] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');

  const fetchJds = async () => {
    try {
      const res = await api().get('/jds');
      setJds(res.data.jds || []);
      if (!selectedJdId && res.data.jds?.length > 0) {
        const firstId = res.data.jds[0].id;
        setSelectedJdId(firstId);
        localStorage.setItem('ats_last_jd', firstId);
      }
    } catch (_) {}
  };

  const fetchDeadline = async () => {
    try {
      const res = await api().get('/deadline');
      setDeadline(res.data.deadline ? res.data.deadline.slice(0, 16) : '');
    } catch (_) {}
  };

  const fetchJdStats = async (jdId) => {
    try {
      const res = await api().get(`/stats/${jdId}`);
      setJdStats(prev => ({ ...prev, [jdId]: res.data }));
    } catch (_) {}
  };

  const fetchAnalysisResult = async (jdId) => {
    try {
      const res = await api().get(`/results/${jdId}`);
      setAnalysisResult(res.data);
    } catch (_) {}
  };

  useEffect(() => {
    fetchJds();
    fetchDeadline();
  }, []);

  useEffect(() => {
    if (selectedJdId) {
      localStorage.setItem('ats_last_jd', selectedJdId);
      fetchJdStats(selectedJdId);
      fetchAnalysisResult(selectedJdId);
    }
  }, [selectedJdId]);

  const handleAddJd = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMsg('');
    if (!jdFile || !title) {
      setError('Please provide a title and upload a JD doc.');
      return;
    }
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('title', title);
      formData.append('jd_document', jdFile);
      const res = await api().post('/submit-jd', formData);
      setTitle('');
      setJdFile(null);
      if (document.getElementById('jd-input')) {
         document.getElementById('jd-input').value = '';
      }
      setSuccessMsg('Role published successfully!');
      setTimeout(() => setSuccessMsg(''), 5000);
      await fetchJds();
      setSelectedJdId(res.data.jd_id);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Submission failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async (jdId) => {
    setRunningAnalysis(true);
    try {
      const res = await api().post(`/run-analysis/${jdId}`);
      setAnalysisResult(res.data);
      fetchJdStats(jdId);
    } catch (err) {
      alert(err.response?.data?.detail || err.message || 'Analysis failed.');
    } finally {
      setRunningAnalysis(false);
    }
  };

  const handleSetDeadline = async () => {
    try {
      await api().post('/deadline', { deadline: deadline ? `${deadline}:00` : null });
      alert("Deadline updated");
    } catch (err) {
      alert(err.response?.data?.detail || 'Failed to set deadline');
    }
  };

  return (
    <div className="dashboard-grid admin-grid">
      <div className="main-column">
        <section className="glass-panel">
          <div className="panel-header">
            <h3>Recruitment Pipelines</h3>
            <button className="btn-secondary text-sm" onClick={fetchJds}>Refresh Data</button>
          </div>
          
          <div className="pipeline-list">
            {(jds || []).map(jd => (
              <div key={jd?.id} className={`pipeline-item ${selectedJdId === jd?.id ? 'active' : ''}`} onClick={() => setSelectedJdId(jd?.id)}>
                <div className="pipeline-info">
                  <h4>{jd?.title || 'Untitled'}</h4>
                  <div className="pipeline-stats">
                    <span className="stat-pill"><Icons.User /> {jdStats?.[jd?.id]?.resume_count || 0} Candidates</span>
                    {jdStats?.[jd?.id]?.has_analysis && <span className="stat-pill success"><Icons.CheckCircle /> Analyzed</span>}
                  </div>
                </div>
                <div className="pipeline-actions" onClick={e => e.stopPropagation()}>
                  <button 
                    onClick={() => handleRunAnalysis(jd?.id)} 
                    disabled={runningAnalysis || (jdStats?.[jd?.id]?.resume_count === 0)}
                    className="btn-primary sm round"
                    title="Run AI Analysis"
                  >
                    {runningAnalysis && selectedJdId === jd?.id ? <span className="spinner xs"></span> : <Icons.Play />}
                  </button>
                </div>
              </div>
            ))}
            {(jds || []).length === 0 && (
              <div className="empty-state">
                <Icons.Briefcase />
                <p>No job descriptions posted yet.</p>
              </div>
            )}
          </div>
        </section>

        {selectedJdId && (
          <section className="glass-panel results-panel fade-in">
            <div className="panel-header">
              <h3>AI Screening Results: {jds?.find(j => j?.id === selectedJdId)?.title || 'Selected Job'}</h3>
            </div>

            {analysisResult?.jd_skills?.length > 0 && (
              <div className="jd-skills-view section-divider-top">
                <span className="label">Target Technologies (from JD):</span>
                <div className="skill-tags">
                  {analysisResult.jd_skills.map((s, i) => (
                    <span key={i} className="tag target">{s}</span>
                  ))}
                </div>
              </div>
            )}

            {analysisResult?.candidates?.length > 0 ? (
              <div className="premium-table-wrapper">
                <table className="premium-table">
                  <thead>
                    <tr>
                      <th>Candidate Details</th>
                      <th>AI Score</th>
                      <th>Match Status</th>
                      <th>Extracted Skills</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(analysisResult?.candidates || [])?.map((c, i) => (
                      <tr key={c?.filename || i} className={i < 3 && c?.status === "Shortlisted" ? 'top-match' : ''}>
                        <td className="candidate-cell">
                          <div className="rank-badge">#{i + 1}</div>
                          <div className="candidate-name-info">
                            <span className="name">{c?.name || 'Unknown'}</span>
                            <span className="filename">{c?.filename || 'Unknown File'}</span>
                          </div>
                        </td>
                        <td>
                          <div className="score-wrapper">
                            <span className="score-text">{(c?.score != null ? c.score * 100 : 0).toFixed(0)}%</span>
                            <div className="progress-bar">
                              <div className="progress-fill" style={{ width: `${Math.max(0, (c?.score || 0) * 100)}%`, backgroundColor: (c?.score || 0) > 0.7 ? '#10b981' : (c?.score || 0) > 0.4 ? '#f59e0b' : '#ef4444' }}></div>
                            </div>
                          </div>
                        </td>
                        <td>
                          <span className={`status-pill ${c?.status?.toLowerCase() || 'pending'}`}>{c?.status || 'Pending'}</span>
                          {c?.skill_match_perc != null && (
                            <div style={{fontSize: '0.7rem', color: 'var(--text-secondary)', marginTop: '0.2rem'}}>
                              {(c.skill_match_perc * 100).toFixed(0)}% skill match
                            </div>
                          )}
                        </td>
                        <td>
                          <div className="skill-tags">
                            {(c?.skills || [])?.slice(0, 3)?.map((s, idx) => <span key={`${s}-${idx}`} className="tag">{s}</span>)}
                            {(c?.skills || []).length === 0 && <span>-</span>}
                            {(c?.skills || []).length > 3 && <span className="tag dim">+{(c?.skills || []).length - 3}</span>}
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="empty-state">
                <p>{analysisResult?.message || "No results available. Run the analysis above."}</p>
              </div>
            )}
            
             {analysisResult?.logs?.length > 0 && (
              <details className="logs-disclosure">
                <summary>View Agent Reasoning Logs</summary>
                <div className="logs-content">
                  {analysisResult.logs.map((log, i) => (
                    <div key={i} className="log-line">{log}</div>
                  ))}
                </div>
              </details>
            )}
          </section>
        )}
      </div>

      <div className="side-column">
        <section className="glass-panel">
          <div className="panel-header">
            <h3>Publish New Job</h3>
          </div>
          <form onSubmit={handleAddJd} className="modern-form">
            <div className="input-group">
              <label>Role / Title</label>
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="Software Engineer"
                required
              />
            </div>
            
            <div className="file-upload-zone small-zone">
              <input
                id="jd-input"
                type="file"
                accept=".pdf,.docx"
                onChange={(e) => setJdFile(e.target.files?.[0] || null)}
                className="file-input-hidden"
              />
              <label htmlFor="jd-input" className="file-upload-label">
                <div className="upload-icon-small"><Icons.FileText /></div>
                <span className="upload-title">{jdFile ? jdFile.name : "Select JD File (PDF/DOCX)"}</span>
              </label>
            </div>
            
            {error && <div className="feedback error-feedback"><Icons.XCircle /> {error}</div>}
            
            <button type="submit" disabled={loading} className="btn-primary full-width">
              {loading ? <span className="spinner"></span> : 'Publish Role'}
            </button>
          </form>
        </section>

        <section className="glass-panel">
          <div className="panel-header">
            <h3>Global Settings</h3>
          </div>
          <div className="setting-block">
            <label>Application Deadline</label>
            <div className="input-with-button">
              <input
                type="datetime-local"
                value={deadline}
                onChange={(e) => setDeadline(e.target.value)}
                className="deadline-input"
              />
              <button onClick={handleSetDeadline} className="btn-secondary">Save</button>
            </div>
            <p className="setting-hint">Applies to all job roles in UTC.</p>
          </div>
        </section>
      </div>
    </div>
  );
}

export default App;
