const API_BASE = import.meta.env.VITE_API_URL || '/api';

const getHeaders = () => {
  const token = localStorage.getItem('token');
  return {
    'Content-Type': 'application/json',
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
  };
};

const handleResponse = async (res) => {
  if (res.status === 401) {
    localStorage.removeItem('token');
    window.location.reload();
  }
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Something went wrong' }));
    throw new Error(err.detail || 'API Error');
  }
  return res.json();
};

export const api = {
  // Auth
  login: async (username, password) => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const res = await fetch(`${API_BASE}/auth/token`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData.toString(),
    });
    return handleResponse(res);
  },
  
  register: async (email, password) => {
    const res = await fetch(`${API_BASE}/auth/register`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ email, password }),
    });
    return handleResponse(res);
  },
  
  me: async () => {
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Profile & Resume
  getProfile: async () => {
    const res = await fetch(`${API_BASE}/profile/`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  updateProfile: async (data) => {
    const res = await fetch(`${API_BASE}/profile/`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  uploadResume: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const token = localStorage.getItem('token');
    const res = await fetch(`${API_BASE}/profile/resume`, {
      method: 'POST',
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
      body: formData,
    });
    return handleResponse(res);
  },

  // Companies
  researchCompany: async (name, website) => {
    const res = await fetch(`${API_BASE}/companies/research`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ name, website }),
    });
    return handleResponse(res);
  },

  listCompanies: async () => {
    const res = await fetch(`${API_BASE}/companies/`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Jobs
  searchJobs: async (params = {}) => {
    const query = new URLSearchParams(params).toString();
    const res = await fetch(`${API_BASE}/jobs/search?${query}`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  importJob: async (jobData) => {
    const res = await fetch(`${API_BASE}/jobs/import`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(jobData),
    });
    return handleResponse(res);
  },

  // Applications
  listApplications: async () => {
    const res = await fetch(`${API_BASE}/applications/`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  getApplication: async (id) => {
    const res = await fetch(`${API_BASE}/applications/${id}`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  updateApplication: async (id, data) => {
    const res = await fetch(`${API_BASE}/applications/${id}`, {
      method: 'PUT',
      headers: getHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(res);
  },

  // Emails & Approvals
  getPendingEmails: async () => {
    const res = await fetch(`${API_BASE}/emails/pending`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  generateEmail: async (applicationId) => {
    const res = await fetch(`${API_BASE}/emails/generate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ application_id: applicationId }),
    });
    return handleResponse(res);
  },

  regenerateEmail: async (emailId, style, additionalInstructions) => {
    const res = await fetch(`${API_BASE}/emails/${emailId}/regenerate`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ style, additional_instructions: additionalInstructions }),
    });
    return handleResponse(res);
  },

  approveEmail: async (emailId) => {
    const res = await fetch(`${API_BASE}/emails/${emailId}/approve`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  sendEmail: async (emailId) => {
    const res = await fetch(`${API_BASE}/emails/${emailId}/send`, {
      method: 'POST',
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Replies
  listReplies: async () => {
    const res = await fetch(`${API_BASE}/replies/`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Assistant
  askAssistant: async (message) => {
    const res = await fetch(`${API_BASE}/assistant/chat`, {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify({ message }),
    });
    return handleResponse(res);
  },

  // Dashboard
  getStats: async () => {
    const res = await fetch(`${API_BASE}/dashboard/stats`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  },

  // Gmail OAuth Setup
  getGmailAuthUrl: async () => {
    const res = await fetch(`${API_BASE}/gmail/auth-url`, {
      headers: getHeaders(),
    });
    return handleResponse(res);
  }
};
export default api;
