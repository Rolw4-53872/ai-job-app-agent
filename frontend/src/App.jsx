import React, { useState, useEffect, useRef } from 'react';
import { 
  Briefcase, User, Send, CheckSquare, MessageSquare, AlertCircle, 
  Search, ShieldAlert, Award, FileText, Check, AlertTriangle, Play,
  SendHorizontal, Clock, ArrowRight, RefreshCw, BarChart2, Layers, LogOut, ChevronRight
} from 'lucide-react';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import api from './services/api';

const STATUS_COLORS = {
  'Draft': '#64748b',
  'Ready': '#3b82f6',
  'Approved': '#8b5cf6',
  'Sent': '#06b6d4',
  'Delivered': '#0284c7',
  'Replied': '#eab308',
  'Interview': '#10b981',
  'Assessment': '#f97316',
  'Offer': '#ec4899',
  'Rejected': '#ef4444',
  'Closed': '#475569'
};

const PRIORITY_COLORS = {
  'Low': '#64748b',
  'Medium': '#3b82f6',
  'High': '#f59e0b',
  'Urgent': '#ef4444'
};

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [authError, setAuthError] = useState('');
  const [currentTab, setCurrentTab] = useState('dashboard');
  
  // App States
  const [stats, setStats] = useState(null);
  const [applications, setApplications] = useState([]);
  const [pendingEmails, setPendingEmails] = useState([]);
  const [replies, setReplies] = useState([]);
  const [profile, setProfile] = useState(null);
  const [jobs, setJobs] = useState([]);
  
  // Job Search Filters
  const [jobQuery, setJobQuery] = useState('');
  const [jobCountry, setJobCountry] = useState('');
  const [jobType, setJobType] = useState('Remote');
  const [searchLoading, setSearchLoading] = useState(false);

  // Email Approval State
  const [selectedEmail, setSelectedEmail] = useState(null);
  const [emailStyle, setEmailStyle] = useState('professional');
  const [emailInstructions, setEmailInstructions] = useState('');
  const [emailActionLoading, setEmailActionLoading] = useState(false);
  
  // Assistant State
  const [isAssistantOpen, setIsAssistantOpen] = useState(false);
  const [assistantMessage, setAssistantMessage] = useState('');
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', text: 'Hello! I am your AI Job Application Assistant. How can I help you manage your applications today?', actions: [] }
  ]);
  const [chatLoading, setChatLoading] = useState(false);
  
  // Profile Form States
  const [fullName, setFullName] = useState('');
  const [phone, setPhone] = useState('');
  const [country, setCountry] = useState('');
  const [linkedin, setLinkedin] = useState('');
  const [skillsText, setSkillsText] = useState('');
  const [profileLoading, setProfileLoading] = useState(false);
  const [resumeFile, setResumeFile] = useState(null);
  
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (token) {
      loadAllData();
    }
  }, [token]);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatHistory, isAssistantOpen]);

  const loadAllData = async () => {
    try {
      const [statsData, appsData, emailsData, repliesData, profileData] = await Promise.all([
        api.getStats().catch(() => null),
        api.listApplications().catch(() => []),
        api.getPendingEmails().catch(() => []),
        api.listReplies().catch(() => []),
        api.getProfile().catch(() => null)
      ]);

      if (statsData) setStats(statsData);
      setApplications(appsData);
      setPendingEmails(emailsData);
      setReplies(repliesData);
      
      if (profileData) {
        setProfile(profileData);
        setFullName(profileData.full_name || '');
        setPhone(profileData.phone_number || '');
        setCountry(profileData.country || '');
        setLinkedin(profileData.linkedin_url || '');
        setSkillsText(profileData.skills ? profileData.skills.join(', ') : '');
      }
    } catch (e) {
      console.error("Error loading data", e);
    }
  };

  const handleAuth = async (e) => {
    e.preventDefault();
    setAuthError('');
    try {
      if (isLogin) {
        const res = await api.login(email, password);
        localStorage.setItem('token', res.access_token);
        setToken(res.access_token);
      } else {
        await api.register(email, password);
        const res = await api.login(email, password);
        localStorage.setItem('token', res.access_token);
        setToken(res.access_token);
      }
    } catch (err) {
      setAuthError(err.message || 'Authentication failed');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
  };

  // Job Board Search
  const handleJobSearch = async () => {
    setSearchLoading(true);
    try {
      const res = await api.searchJobs({
        query: jobQuery,
        country: jobCountry,
        workplace_type: jobType
      });
      setJobs(res);
    } catch (err) {
      alert("Failed to search jobs: " + err.message);
    } finally {
      setSearchLoading(false);
    }
  };

  // Job Import
  const handleImportJob = async (job) => {
    try {
      await api.importJob({
        company_name: job.company_name,
        company_website: job.company_website,
        title: job.title,
        description: job.description,
        location: job.location,
        workplace_type: job.workplace_type,
        source: job.source,
        url: job.url
      });
      alert(`Imported ${job.title} at ${job.company_name} successfully! Check Applications.`);
      loadAllData();
    } catch (err) {
      alert("Failed to import job: " + err.message);
    }
  };

  // Profile Save
  const handleProfileSave = async (e) => {
    e.preventDefault();
    setProfileLoading(true);
    try {
      const skillsArr = skillsText.split(',').map(s => s.trim()).filter(Boolean);
      await api.updateProfile({
        full_name: fullName,
        phone_number: phone,
        country,
        linkedin_url: linkedin,
        skills: skillsArr
      });
      alert("Profile updated successfully!");
      loadAllData();
    } catch (err) {
      alert("Failed to update profile: " + err.message);
    } finally {
      setProfileLoading(false);
    }
  };

  // Resume PDF Upload
  const handleResumeUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    
    const formData = new FormData();
    formData.append('file', file);
    
    setProfileLoading(true);
    try {
      await api.uploadResume(file);
      alert("Resume uploaded and parsed successfully by AI! Profile fields synced.");
      loadAllData();
    } catch (err) {
      alert("Failed parsing resume: " + err.message);
    } finally {
      setProfileLoading(false);
    }
  };

  // Generate Email Draft
  const handleGenerateEmail = async (appId) => {
    try {
      await api.generateEmail(appId);
      alert("AI personalized email draft generated! Review in 'Approvals'.");
      setCurrentTab('approvals');
      loadAllData();
    } catch (err) {
      alert("Failed generating email: " + err.message);
    }
  };

  // Approve & Send Email
  const handleEmailAction = async (action, emailId) => {
    setEmailActionLoading(true);
    try {
      if (action === 'approve') {
        await api.approveEmail(emailId);
        alert("Email approved! Ready to send.");
      } else if (action === 'send') {
        await api.sendEmail(emailId);
        alert("Email successfully sent via Gmail API!");
        setSelectedEmail(null);
      } else if (action === 'regenerate') {
        await api.regenerateEmail(emailId, emailStyle, emailInstructions);
        alert("Email draft regenerated with new style parameter.");
      }
      loadAllData();
    } catch (err) {
      alert(`Action '${action}' failed: ` + err.message);
    } finally {
      setEmailActionLoading(false);
    }
  };

  // Assistant Chat
  const handleAssistantSend = async (e) => {
    e.preventDefault();
    if (!assistantMessage.trim()) return;
    
    const userMsg = assistantMessage;
    setAssistantMessage('');
    setChatHistory(prev => [...prev, { role: 'user', text: userMsg }]);
    setChatLoading(true);
    
    try {
      const res = await api.askAssistant(userMsg);
      setChatHistory(prev => [...prev, { 
        role: 'assistant', 
        text: res.response,
        actions: res.suggested_actions || []
      }]);
    } catch (err) {
      setChatHistory(prev => [...prev, { role: 'assistant', text: 'Sorry, I couldn\'t process that message right now.' }]);
    } finally {
      setChatLoading(false);
    }
  };

  // Auth Redirect Google Link
  const handleGmailLink = async () => {
    try {
      const res = await api.getGmailAuthUrl();
      window.open(res.url, '_blank', 'width=600,height=700');
    } catch (err) {
      alert("Gmail link failure: " + err.message);
    }
  };

  if (!token) {
    return (
      <div style={{ display: 'flex', minHeight: '100vh', alignItems: 'center', justifyContent: 'center', padding: '20px' }}>
        <div className="glass-card" style={{ width: '100%', maxWidth: '420px', padding: '40px', background: 'rgba(15, 21, 36, 0.9)' }}>
          <div style={{ textAlign: 'center', marginBottom: '30px' }}>
            <div style={{ display: 'inline-flex', padding: '12px', borderRadius: '12px', background: 'var(--primary-glow)', color: 'var(--primary)', marginBottom: '16px' }}>
              <Briefcase size={36} />
            </div>
            <h2 style={{ fontSize: '28px', marginBottom: '6px' }}>AI Application Agent</h2>
            <p style={{ color: 'var(--muted)', fontSize: '14px' }}>Human-in-the-loop application orchestrator</p>
          </div>
          
          <form onSubmit={handleAuth} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '8px', fontWeight: '500' }}>Email Address</label>
              <input 
                type="email" 
                required 
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com" 
                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
              />
            </div>
            
            <div>
              <label style={{ display: 'block', fontSize: '13px', color: '#94a3b8', marginBottom: '8px', fontWeight: '500' }}>Password</label>
              <input 
                type="password" 
                required 
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••" 
                style={{ width: '100%', padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
              />
            </div>
            
            {authError && (
              <div style={{ color: 'var(--danger)', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <AlertCircle size={16} />
                <span>{authError}</span>
              </div>
            )}
            
            <button 
              type="submit" 
              style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '14px', borderRadius: '8px', fontWeight: '600', fontSize: '15px', marginTop: '10px' }}
            >
              {isLogin ? 'Sign In' : 'Create Account'}
            </button>
          </form>
          
          <div style={{ textAlign: 'center', marginTop: '24px' }}>
            <span style={{ fontSize: '13px', color: 'var(--muted)' }}>
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button 
                onClick={() => setIsLogin(!isLogin)} 
                style={{ background: 'none', border: 'none', color: 'var(--primary)', fontWeight: '600', padding: 0 }}
              >
                {isLogin ? 'Sign Up' : 'Log In'}
              </button>
            </span>
          </div>
        </div>
      </div>
    );
  }

  // Set selected email template if navigating from approvals tab list
  const currentApprovalEmail = selectedEmail || pendingEmails[0];

  return (
    <div style={{ display: 'flex', minHeight: '100vh', position: 'relative' }}>
      
      {/* Sidebar Navigation */}
      <aside style={{ width: '260px', borderRight: '1px solid var(--border-glass)', background: 'rgba(11, 15, 25, 0.9)', padding: '24px', display: 'flex', flexDirection: 'column', gap: '30px', flexShrink: 0 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{ background: 'var(--primary-glow)', color: 'var(--primary)', padding: '8px', borderRadius: '8px' }}>
            <Briefcase size={22} />
          </div>
          <div>
            <h3 style={{ fontSize: '16px', margin: 0, fontWeight: '700' }}>Job Agent</h3>
            <span style={{ fontSize: '11px', color: 'var(--muted)', fontWeight: '600' }}>HI-IN-THE-LOOP</span>
          </div>
        </div>
        
        <nav style={{ display: 'flex', flexDirection: 'column', gap: '6px', flexGrow: 1 }}>
          {[
            { id: 'dashboard', label: 'Dashboard', icon: BarChart2 },
            { id: 'profile', label: 'Profile & Resume', icon: User },
            { id: 'jobs', label: 'Search Jobs', icon: Search },
            { id: 'applications', label: 'Pipeline', icon: Layers },
            { id: 'approvals', label: 'Approvals', icon: CheckSquare, badge: pendingEmails.length },
            { id: 'replies', label: 'Replies Monitor', icon: MessageSquare, badge: replies.length }
          ].map(tab => {
            const Icon = tab.icon;
            const active = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => { setCurrentTab(tab.id); if(tab.id==='approvals') setSelectedEmail(null); }}
                style={{
                  display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', border: 'none', borderRadius: '10px',
                  background: active ? 'var(--primary-glow)' : 'transparent',
                  color: active ? 'var(--primary)' : '#94a3b8',
                  fontWeight: active ? '600' : '500', fontSize: '14px', textAlign: 'left', width: '100%'
                }}
              >
                <Icon size={18} />
                <span style={{ flexGrow: 1 }}>{tab.label}</span>
                {tab.badge > 0 && (
                  <span style={{ background: tab.id==='approvals' ? 'var(--danger)' : 'var(--primary)', color: 'white', fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '99px' }}>
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
        
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <button 
            onClick={handleGmailLink}
            style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px', padding: '10px', borderRadius: '8px', border: '1px solid #dc2626', background: 'rgba(220, 38, 38, 0.05)', color: '#ef4444', fontSize: '13px', fontWeight: '600', width: '100%' }}
          >
            <RefreshCw size={14} /> Link Gmail Account
          </button>
          
          <button 
            onClick={handleLogout}
            style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '12px 16px', borderRadius: '10px', border: 'none', background: 'transparent', color: '#94a3b8', fontSize: '14px', fontWeight: '500', textAlign: 'left', width: '100%' }}
          >
            <LogOut size={18} /> Logout
          </button>
        </div>
      </aside>

      {/* Main Content Area */}
      <main style={{ flexGrow: 1, padding: '40px', overflowY: 'auto', maxHeight: '100vh', boxSizing: 'border-box' }}>
        
        {/* TAB 1: DASHBOARD */}
        {currentTab === 'dashboard' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h1 style={{ fontSize: '32px', marginBottom: '6px' }}>Dashboard Overview</h1>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Performance, status distributions, and active logs</p>
            </div>
            
            {/* Stat Cards */}
            <div className="dashboard-grid">
              {[
                { title: 'Total Applications', count: stats?.total_applications || 0, color: 'var(--primary)', icon: Layers },
                { title: 'Interviews Invited', count: stats?.interviews_count || 0, color: 'var(--success)', icon: Award },
                { title: 'Pending Replies', count: stats?.pending_replies || 0, color: 'var(--warning)', icon: Clock },
                { title: 'Offers Received', count: stats?.offers_count || 0, color: 'var(--accent)', icon: Check },
                { title: 'Rejected Applications', count: stats?.rejected_count || 0, color: 'var(--danger)', icon: AlertTriangle }
              ].map((card, idx) => {
                const Icon = card.icon;
                return (
                  <div key={idx} className="glass-card" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
                    <div style={{ background: `${card.color}15`, color: card.color, padding: '12px', borderRadius: '12px' }}>
                      <Icon size={24} />
                    </div>
                    <div>
                      <span style={{ color: 'var(--muted)', fontSize: '13px', fontWeight: '600' }}>{card.title}</span>
                      <h2 style={{ fontSize: '28px', margin: '4px 0 0 0', fontWeight: '800' }}>{card.count}</h2>
                    </div>
                  </div>
                );
              })}
            </div>
            
            {/* Charts Row */}
            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '24px' }}>
              
              {/* Area Chart - Activity Timeline */}
              <div className="glass-card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '18px', marginBottom: '20px' }}>Application Funnel (Timeline)</h3>
                <div style={{ width: '100%', height: '260px' }}>
                  {stats?.monthly_activity?.length > 0 ? (
                    <ResponsiveContainer>
                      <AreaChart data={stats.monthly_activity}>
                        <defs>
                          <linearGradient id="colorApps" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.2}/>
                            <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                          </linearGradient>
                          <linearGradient id="colorInts" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="var(--success)" stopOpacity={0.2}/>
                            <stop offset="95%" stopColor="var(--success)" stopOpacity={0}/>
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="month" stroke="var(--muted)" fontSize={11} />
                        <YAxis stroke="var(--muted)" fontSize={11} />
                        <Tooltip contentStyle={{ background: '#0f1524', border: '1px solid var(--border-glass)', borderRadius: '8px' }} />
                        <Area type="monotone" dataKey="applications_sent" stroke="var(--primary)" strokeWidth={2} fillOpacity={1} fill="url(#colorApps)" name="Applications Sent" />
                        <Area type="monotone" dataKey="interviews" stroke="var(--success)" strokeWidth={2} fillOpacity={1} fill="url(#colorInts)" name="Interviews Scheduled" />
                      </AreaChart>
                    </ResponsiveContainer>
                  ) : (
                    <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--muted)' }}>No chart data. Complete an application import to visualize.</div>
                  )}
                </div>
              </div>
              
              {/* Pie Chart - Status Distribution */}
              <div className="glass-card" style={{ padding: '24px' }}>
                <h3 style={{ fontSize: '18px', marginBottom: '20px' }}>Current Status Split</h3>
                <div style={{ width: '100%', height: '260px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  {stats?.status_distribution?.length > 0 ? (
                    <ResponsiveContainer>
                      <PieChart>
                        <Pie
                          data={stats.status_distribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={60}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="count"
                          nameKey="status"
                        >
                          {stats.status_distribution.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.status] || '#cbd5e1'} />
                          ))}
                        </Pie>
                        <Tooltip contentStyle={{ background: '#0f1524', border: '1px solid var(--border-glass)', borderRadius: '8px' }} />
                      </PieChart>
                    </ResponsiveContainer>
                  ) : (
                    <div style={{ color: 'var(--muted)' }}>No distribution split.</div>
                  )}
                </div>
              </div>
              
            </div>
            
            {/* Activity Logs */}
            <div className="glass-card" style={{ padding: '24px' }}>
              <h3 style={{ fontSize: '18px', marginBottom: '20px' }}>Recent Logs & Events</h3>
              <div className="timeline-line" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                {stats?.recent_activities?.length > 0 ? (
                  stats.recent_activities.map((log) => (
                    <div key={log.id} style={{ display: 'flex', gap: '16px', zIndex: 1 }}>
                      <div style={{ width: '32px', height: '32px', borderRadius: '99px', background: 'rgba(99, 102, 241, 0.1)', color: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                        <Play size={12} />
                      </div>
                      <div>
                        <div style={{ fontSize: '14px', fontWeight: '600' }}>{log.action.replace('_', ' ').toUpperCase()}</div>
                        <div style={{ fontSize: '12px', color: 'var(--muted)' }}>{new Date(log.created_at).toLocaleString()}</div>
                      </div>
                    </div>
                  ))
                ) : (
                  <div style={{ paddingLeft: '40px', color: 'var(--muted)', fontSize: '14px' }}>Activity history is empty. Start using the pipeline to log actions.</div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* TAB 2: PROFILE & RESUME */}
        {currentTab === 'profile' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h1 style={{ fontSize: '32px', marginBottom: '6px' }}>Profile Management</h1>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Upload resume PDF to parse profile details using GPT models</p>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
              
              {/* PDF Resume Uploader */}
              <div className="glass-card" style={{ padding: '24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
                <h3 style={{ fontSize: '18px', margin: 0 }}>Resume (PDF)</h3>
                
                <div style={{ border: '2px dashed var(--border-glass)', borderRadius: '12px', padding: '30px 20px', textAlign: 'center', background: 'rgba(0,0,0,0.1)' }}>
                  <FileText size={40} style={{ color: 'var(--muted)', marginBottom: '12px' }} />
                  <p style={{ fontSize: '13px', color: 'var(--muted)', margin: '0 0 16px 0' }}>Upload your current resume in PDF format</p>
                  
                  <input 
                    type="file" 
                    id="resume-file" 
                    accept=".pdf" 
                    onChange={handleResumeUpload} 
                    style={{ display: 'none' }}
                  />
                  <label 
                    htmlFor="resume-file"
                    style={{ background: 'var(--primary)', color: 'white', padding: '10px 20px', borderRadius: '8px', fontWeight: '600', fontSize: '13px', cursor: 'pointer', display: 'inline-block' }}
                  >
                    Select File
                  </label>
                </div>
                
                {profile?.years_of_experience > 0 && (
                  <div style={{ background: 'rgba(16, 185, 129, 0.05)', border: '1px solid rgba(16, 185, 129, 0.1)', padding: '16px', borderRadius: '8px' }}>
                    <div style={{ color: 'var(--success)', fontWeight: '600', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <CheckSquare size={16} /> Resume Loaded Successfully
                    </div>
                    <span style={{ fontSize: '12px', color: 'var(--muted)', display: 'block', marginTop: '6px' }}>
                      Estimated Experience: {profile.years_of_experience} years
                    </span>
                  </div>
                )}
              </div>
              
              {/* Profile Details Form */}
              <div className="glass-card" style={{ padding: '30px' }}>
                <h3 style={{ fontSize: '18px', marginBottom: '24px' }}>Candidate Details</h3>
                
                <form onSubmit={handleProfileSave} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--muted)', marginBottom: '8px', fontWeight: '600' }}>Full Name</label>
                      <input 
                        type="text" 
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--muted)', marginBottom: '8px', fontWeight: '600' }}>Phone Number</label>
                      <input 
                        type="text" 
                        value={phone}
                        onChange={(e) => setPhone(e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
                      />
                    </div>
                  </div>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--muted)', marginBottom: '8px', fontWeight: '600' }}>Country</label>
                      <input 
                        type="text" 
                        value={country}
                        onChange={(e) => setCountry(e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
                      />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '12px', color: 'var(--muted)', marginBottom: '8px', fontWeight: '600' }}>LinkedIn URL</label>
                      <input 
                        type="text" 
                        value={linkedin}
                        onChange={(e) => setLinkedin(e.target.value)}
                        style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label style={{ display: 'block', fontSize: '12px', color: 'var(--muted)', marginBottom: '8px', fontWeight: '600' }}>Skills (comma-separated)</label>
                    <textarea 
                      rows={3}
                      value={skillsText}
                      onChange={(e) => setSkillsText(e.target.value)}
                      placeholder="Python, FastAPI, Machine Learning, PostgreSQL"
                      style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box', resize: 'vertical' }}
                    />
                  </div>
                  
                  <button 
                    type="submit" 
                    disabled={profileLoading}
                    style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '8px', fontWeight: '600', width: 'fit-content', marginTop: '10px' }}
                  >
                    {profileLoading ? 'Saving...' : 'Save Profile'}
                  </button>
                </form>
              </div>
              
            </div>
          </div>
        )}

        {/* TAB 3: SEARCH JOBS */}
        {currentTab === 'jobs' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h1 style={{ fontSize: '32px', marginBottom: '6px' }}>Job Board Search</h1>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Filter, search, and import listings to your application tracker</p>
            </div>
            
            {/* Filter Bar */}
            <div className="glass-card" style={{ padding: '24px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
              <input 
                type="text" 
                placeholder="Title/Keywords (e.g. AI Engineer, Python)"
                value={jobQuery}
                onChange={(e) => setJobQuery(e.target.value)}
                style={{ flexGrow: 2, padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white' }}
              />
              
              <input 
                type="text" 
                placeholder="Country"
                value={jobCountry}
                onChange={(e) => setJobCountry(e.target.value)}
                style={{ flexGrow: 1, padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white' }}
              />
              
              <select 
                value={jobType} 
                onChange={(e) => setJobType(e.target.value)}
                style={{ padding: '12px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', minWidth: '120px' }}
              >
                <option value="Remote">Remote</option>
                <option value="Hybrid">Hybrid</option>
                <option value="On-site">On-site</option>
              </select>
              
              <button 
                onClick={handleJobSearch} 
                disabled={searchLoading}
                style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '12px 24px', borderRadius: '8px', fontWeight: '600' }}
              >
                {searchLoading ? 'Searching...' : 'Search'}
              </button>
            </div>
            
            {/* Listings Grid */}
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
              {jobs.length > 0 ? (
                jobs.map(job => (
                  <div key={job.id} className="glass-card" style={{ padding: '24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div style={{ maxWidth: '80%' }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                        <span style={{ fontSize: '14px', color: 'var(--primary)', fontWeight: '600' }}>{job.company_name}</span>
                        <span style={{ fontSize: '11px', color: 'var(--muted)', background: 'rgba(255,255,255,0.05)', padding: '2px 8px', borderRadius: '99px' }}>{job.workplace_type}</span>
                        <span style={{ fontSize: '11px', color: 'var(--success)', background: 'rgba(16, 185, 129, 0.05)', padding: '2px 8px', borderRadius: '99px' }}>{job.salary_range}</span>
                      </div>
                      <h3 style={{ fontSize: '18px', margin: '0 0 10px 0' }}>{job.title}</h3>
                      <p style={{ color: 'var(--muted)', fontSize: '13px', margin: 0, whiteSpace: 'pre-line' }}>{job.description.split('\n')[0]}</p>
                    </div>
                    
                    <button 
                      onClick={() => handleImportJob(job)}
                      style={{ background: 'none', border: '1px solid var(--border-glass)', color: 'white', padding: '10px 20px', borderRadius: '8px', fontWeight: '600', fontSize: '13px' }}
                    >
                      Import Role
                    </button>
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '60px', color: 'var(--muted)', fontSize: '14px' }}>
                  No job search results loaded. Try searching with keyword filters.
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: APPLICATIONS PIPELINE */}
        {currentTab === 'applications' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h1 style={{ fontSize: '32px', marginBottom: '6px' }}>Applications Tracker</h1>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Review pipeline status logs, update candidate files, and trigger drafts</p>
            </div>
            
            <div className="glass-card" style={{ overflow: 'hidden' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
                <thead>
                  <tr style={{ background: 'rgba(255,255,255,0.02)', borderBottom: '1px solid var(--border-glass)' }}>
                    <th style={{ padding: '16px 24px', color: 'var(--muted)', fontSize: '12px', fontWeight: '700' }}>COMPANY</th>
                    <th style={{ padding: '16px 24px', color: 'var(--muted)', fontSize: '12px', fontWeight: '700' }}>POSITION</th>
                    <th style={{ padding: '16px 24px', color: 'var(--muted)', fontSize: '12px', fontWeight: '700' }}>STATUS</th>
                    <th style={{ padding: '16px 24px', color: 'var(--muted)', fontSize: '12px', fontWeight: '700' }}>DATE ADDED</th>
                    <th style={{ padding: '16px 24px', color: 'var(--muted)', fontSize: '12px', fontWeight: '700' }}>ACTIONS</th>
                  </tr>
                </thead>
                <tbody>
                  {applications.length > 0 ? (
                    applications.map(app => (
                      <tr key={app.id} style={{ borderBottom: '1px solid var(--border-glass)' }}>
                        <td style={{ padding: '20px 24px', fontWeight: '600' }}>{app.company.name}</td>
                        <td style={{ padding: '20px 24px' }}>{app.job ? app.job.title : 'General Outreach'}</td>
                        <td style={{ padding: '20px 24px' }}>
                          <span style={{ 
                            background: `${STATUS_COLORS[app.status] || '#cbd5e1'}15`, 
                            color: STATUS_COLORS[app.status] || '#cbd5e1', 
                            fontSize: '12px', fontWeight: '700', padding: '4px 10px', borderRadius: '99px' 
                          }}>
                            {app.status}
                          </span>
                        </td>
                        <td style={{ padding: '20px 24px', color: 'var(--muted)', fontSize: '13px' }}>{new Date(app.created_at).toLocaleDateString()}</td>
                        <td style={{ padding: '20px 24px' }}>
                          <button
                            onClick={() => handleGenerateEmail(app.id)}
                            style={{ 
                              background: 'var(--primary-glow)', border: 'none', color: 'var(--primary)',
                              padding: '8px 16px', borderRadius: '6px', fontSize: '12px', fontWeight: '600'
                            }}
                          >
                            Draft Email
                          </button>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={5} style={{ padding: '40px', textAlign: 'center', color: 'var(--muted)', fontSize: '14px' }}>
                        Pipeline is empty. Import a job to start the application track.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* TAB 5: APPROVALS HUB */}
        {currentTab === 'approvals' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h1 style={{ fontSize: '32px', marginBottom: '6px' }}>Approvals Control Hub</h1>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Human-in-the-loop validation page. Review, regenerate style, and confirm dispatch.</p>
            </div>
            
            {pendingEmails.length > 0 ? (
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '24px' }}>
                
                {/* Approvals Queue */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {pendingEmails.map(mail => (
                    <div 
                      key={mail.id} 
                      onClick={() => setSelectedEmail(mail)}
                      className="glass-card" 
                      style={{ 
                        padding: '16px', cursor: 'pointer',
                        borderColor: currentApprovalEmail?.id === mail.id ? 'var(--primary)' : 'var(--border-glass)',
                        background: currentApprovalEmail?.id === mail.id ? 'var(--primary-glow)' : 'var(--bg-surface-glass)'
                      }}
                    >
                      <h4 style={{ fontSize: '14px', margin: '0 0 6px 0' }}>{mail.subject}</h4>
                      <span style={{ fontSize: '11px', color: 'var(--muted)' }}>To: {mail.recipient_email}</span>
                    </div>
                  ))}
                </div>
                
                {/* Email Template Preview details */}
                {currentApprovalEmail && (
                  <div className="glass-card" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    <div style={{ borderBottom: '1px solid var(--border-glass)', paddingBottom: '20px' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                        <span style={{ fontSize: '13px', color: 'var(--muted)' }}>Recipient: <strong style={{ color: 'white' }}>{currentApprovalEmail.recipient_email}</strong></span>
                        <span style={{ background: '#f59e0b15', color: '#f59e0b', fontSize: '11px', fontWeight: '700', padding: '3px 8px', borderRadius: '4px' }}>PENDING HUMAN APPROVAL</span>
                      </div>
                      <h3 style={{ margin: 0, fontSize: '18px' }}>{currentApprovalEmail.subject}</h3>
                    </div>
                    
                    {/* Why written this way box */}
                    {currentApprovalEmail.rationale && (
                      <div style={{ background: 'rgba(99, 102, 241, 0.05)', border: '1px solid rgba(99, 102, 241, 0.1)', padding: '16px', borderRadius: '8px' }}>
                        <h4 style={{ color: 'var(--primary)', margin: '0 0 6px 0', fontSize: '13px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                          <AlertCircle size={14} /> AI Approach Rationale
                        </h4>
                        <p style={{ margin: 0, fontSize: '12px', color: '#cbd5e1' }}>{currentApprovalEmail.rationale}</p>
                      </div>
                    )}
                    
                    {/* Editable/Preview Body */}
                    <div style={{ background: '#090d16', border: '1px solid var(--border-glass)', borderRadius: '10px', padding: '20px', fontFamily: 'monospace', fontSize: '13px', whiteSpace: 'pre-wrap', color: '#e2e8f0', minHeight: '180px' }}>
                      {currentApprovalEmail.body}
                    </div>
                    
                    {/* Regeneration Settings */}
                    <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', borderTop: '1px solid var(--border-glass)', paddingTop: '20px' }}>
                      <div style={{ flexGrow: 1 }}>
                        <label style={{ display: 'block', fontSize: '11px', color: 'var(--muted)', marginBottom: '6px', fontWeight: '600' }}>Tonal Writing Style</label>
                        <select 
                          value={emailStyle}
                          onChange={(e) => setEmailStyle(e.target.value)}
                          style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white' }}
                        >
                          <option value="professional">Professional</option>
                          <option value="bold">Bold & Creative</option>
                          <option value="warm">Warm & Conversational</option>
                          <option value="concise">Concise & Quick</option>
                          <option value="technical">Highly Technical</option>
                        </select>
                      </div>
                      
                      <div style={{ flexGrow: 2 }}>
                        <label style={{ display: 'block', fontSize: '11px', color: 'var(--muted)', marginBottom: '6px', fontWeight: '600' }}>Additional Adjustments / Prompt Instructions</label>
                        <input 
                          type="text"
                          value={emailInstructions}
                          onChange={(e) => setEmailInstructions(e.target.value)}
                          placeholder="e.g. emphasize my backend skill with PostgreSQL, write shorter"
                          style={{ width: '100%', padding: '10px', borderRadius: '6px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', boxSizing: 'border-box' }}
                        />
                      </div>
                    </div>
                    
                    {/* Actions Bar */}
                    <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                      <button
                        onClick={() => handleEmailAction('regenerate', currentApprovalEmail.id)}
                        disabled={emailActionLoading}
                        style={{ background: 'none', border: '1px solid var(--border-glass)', color: 'white', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontWeight: '600' }}
                      >
                        Regenerate
                      </button>
                      
                      {currentApprovalEmail.status !== 'Approved' && (
                        <button
                          onClick={() => handleEmailAction('approve', currentApprovalEmail.id)}
                          disabled={emailActionLoading}
                          style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontWeight: '600' }}
                        >
                          Approve Draft
                        </button>
                      )}
                      
                      {currentApprovalEmail.status === 'Approved' && (
                        <button
                          onClick={() => handleEmailAction('send', currentApprovalEmail.id)}
                          disabled={emailActionLoading}
                          style={{ background: 'var(--success)', color: 'white', border: 'none', padding: '10px 20px', borderRadius: '8px', fontSize: '13px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' }}
                        >
                          <Send size={14} /> Send via Gmail
                        </button>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ) : (
              <div className="glass-card" style={{ padding: '60px', textAlign: 'center', color: 'var(--muted)' }}>
                <CheckSquare size={48} style={{ margin: '0 auto 16px auto', display: 'block', opacity: 0.5 }} />
                <h3>No pending approvals found</h3>
                <p style={{ fontSize: '14px', maxWidth: '380px', margin: '8px auto 0 auto' }}>Generate email templates for imported roles inside the Applications Pipeline first.</p>
              </div>
            )}
          </div>
        )}

        {/* TAB 6: REPLIES MONITOR */}
        {currentTab === 'replies' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '30px' }}>
            <div>
              <h1 style={{ fontSize: '32px', marginBottom: '6px' }}>Replies Monitor</h1>
              <p style={{ color: 'var(--muted)', margin: 0 }}>Classify responses, review summary priority, and copy suggested responses</p>
            </div>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '20px' }}>
              {replies.length > 0 ? (
                replies.map(rep => (
                  <div key={rep.id} className="glass-card" style={{ padding: '24px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
                      <div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '6px' }}>
                          <span style={{ fontSize: '14px', fontWeight: '700' }}>{rep.sender}</span>
                          <span style={{ background: `${PRIORITY_COLORS[rep.priority]}15`, color: PRIORITY_COLORS[rep.priority], fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '4px' }}>
                            {rep.priority} PRIORITY
                          </span>
                          <span style={{ background: 'rgba(255,255,255,0.05)', color: 'white', fontSize: '11px', fontWeight: '700', padding: '2px 8px', borderRadius: '4px' }}>
                            {rep.classification}
                          </span>
                        </div>
                        <h4 style={{ margin: 0, fontSize: '16px' }}>{rep.subject}</h4>
                      </div>
                      <span style={{ fontSize: '12px', color: 'var(--muted)' }}>{new Date(rep.processed_at).toLocaleString()}</span>
                    </div>
                    
                    {/* Summary */}
                    <p style={{ fontSize: '13px', background: 'rgba(255,255,255,0.02)', padding: '12px', borderRadius: '6px', margin: '0 0 16px 0', borderLeft: '3px solid var(--primary)' }}>
                      <strong>AI Summary:</strong> {rep.summary}
                    </p>
                    
                    {/* Suggested Reply */}
                    {rep.suggested_reply && (
                      <div style={{ background: '#090d16', border: '1px solid var(--border-glass)', padding: '16px', borderRadius: '8px' }}>
                        <span style={{ display: 'block', fontSize: '11px', color: 'var(--muted)', marginBottom: '8px', fontWeight: '600' }}>SUGGESTED REPLY (CLICK TO COPY)</span>
                        <pre 
                          onClick={() => { navigator.clipboard.writeText(rep.suggested_reply); alert("Suggested reply copied to clipboard!"); }}
                          style={{ margin: 0, fontSize: '12.5px', fontFamily: 'monospace', whiteSpace: 'pre-wrap', color: '#cbd5e1', cursor: 'pointer' }}
                        >
                          {rep.suggested_reply}
                        </pre>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div style={{ textAlign: 'center', padding: '60px', color: 'var(--muted)' }}>
                  No recruiter responses have been processed yet. Monitoring sandbox logs.
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* FLOATING AI ASSISTANT CHATBOT */}
      <div style={{ position: 'fixed', bottom: '24px', right: '24px', zIndex: 100, display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
        
        {isAssistantOpen && (
          <div className="glass-card animate-pulse-slow" style={{ width: '380px', height: '500px', display: 'flex', flexDirection: 'column', background: 'rgba(15, 21, 36, 0.95)', border: '1px solid rgba(255, 255, 255, 0.1)', boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5)', borderRadius: '16px', overflow: 'hidden', marginBottom: '16px', animation: 'none' }}>
            {/* Header */}
            <div style={{ background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)', padding: '16px 20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', color: 'white' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <Briefcase size={18} />
                <h3 style={{ margin: 0, fontSize: '14px', fontWeight: '700' }}>AI Assistant</h3>
              </div>
              <button 
                onClick={() => setIsAssistantOpen(false)}
                style={{ background: 'none', border: 'none', color: 'white', padding: 0, fontSize: '18px', fontWeight: '600' }}
              >
                ×
              </button>
            </div>
            
            {/* Messages Screen */}
            <div style={{ flexGrow: 1, padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {chatHistory.map((chat, idx) => (
                <div 
                  key={idx} 
                  style={{ 
                    alignSelf: chat.role === 'user' ? 'flex-end' : 'flex-start',
                    maxWidth: '80%',
                    background: chat.role === 'user' ? 'var(--primary)' : 'rgba(255,255,255,0.05)',
                    padding: '10px 14px',
                    borderRadius: chat.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                    fontSize: '13px',
                    whiteSpace: 'pre-line'
                  }}
                >
                  {chat.text}
                  {/* Assistant custom Action buttons */}
                  {chat.actions?.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '10px' }}>
                      {chat.actions.map((act, aIdx) => (
                        <button
                          key={aIdx}
                          onClick={() => {
                            if (act.action === 'redirect_approvals') setCurrentTab('approvals');
                            else if (act.action === 'redirect_applications') setCurrentTab('applications');
                            else if (act.action === 'redirect_jobs') setCurrentTab('jobs');
                            setIsAssistantOpen(false);
                          }}
                          style={{ background: 'rgba(255,255,255,0.1)', color: 'white', border: 'none', padding: '4px 10px', borderRadius: '4px', fontSize: '11px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '4px' }}
                        >
                          {act.label} <ArrowRight size={10} />
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              ))}
              {chatLoading && (
                <div style={{ alignSelf: 'flex-start', background: 'rgba(255,255,255,0.05)', padding: '10px 14px', borderRadius: '12px 12px 12px 2px', fontSize: '12px', color: 'var(--muted)' }}>
                  Thinking...
                </div>
              )}
              <div ref={chatEndRef} />
            </div>
            
            {/* Input Bar */}
            <form onSubmit={handleAssistantSend} style={{ padding: '12px', borderTop: '1px solid var(--border-glass)', display: 'flex', gap: '8px' }}>
              <input 
                type="text" 
                value={assistantMessage}
                onChange={(e) => setAssistantMessage(e.target.value)}
                placeholder="Ask me: 'How many interviews do I have?'"
                style={{ flexGrow: 1, padding: '8px 12px', borderRadius: '8px', border: '1px solid var(--border-glass)', background: '#090d16', color: 'white', fontSize: '12.5px' }}
              />
              <button 
                type="submit"
                style={{ background: 'var(--primary)', color: 'white', border: 'none', padding: '8px', borderRadius: '8px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                <SendHorizontal size={16} />
              </button>
            </form>
          </div>
        )}
        
        {/* Toggle Button */}
        <button
          onClick={() => setIsAssistantOpen(!isAssistantOpen)}
          style={{
            background: 'linear-gradient(135deg, #4f46e5 0%, #6366f1 100%)',
            color: 'white', border: 'none', width: '56px', height: '56px', borderRadius: '99px',
            boxShadow: '0 10px 25px -5px rgba(99, 102, 241, 0.4)',
            display: 'flex', alignItems: 'center', justifyContent: 'center'
          }}
        >
          <MessageSquare size={24} />
        </button>
      </div>

    </div>
  );
}
