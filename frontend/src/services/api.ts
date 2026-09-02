import axios from 'axios';
import { Project, TestRun, TestReport, IssueItem, TestConfig } from '../types';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const ProjectService = {
  list: async (): Promise<Project[]> => {
    const res = await api.get('/projects');
    return res.data;
  },
  create: async (data: { name: string; base_url: string; description?: string }): Promise<Project> => {
    const res = await api.post('/projects', data);
    return res.data;
  },
  get: async (id: string): Promise<Project> => {
    const res = await api.get(`/projects/${id}`);
    return res.data;
  },
  delete: async (id: string): Promise<void> => {
    await api.delete(`/projects/${id}`);
  },
};

export const TestService = {
  create: async (data: { target_url: string; target_type?: 'live' | 'localhost'; project_id?: string; config?: Partial<TestConfig> }): Promise<TestRun> => {
    const res = await api.post('/tests', data);
    return res.data;
  },
  list: async (projectId?: string): Promise<TestRun[]> => {
    const params = projectId ? { project_id: projectId } : {};
    const res = await api.get('/tests', { params });
    return res.data;
  },
  get: async (id: string): Promise<TestRun> => {
    const res = await api.get(`/tests/${id}`);
    return res.data;
  },
  getStatus: async (id: string): Promise<TestRun> => {
    const res = await api.get(`/tests/${id}/status`);
    return res.data;
  },
  getReport: async (id: string): Promise<TestReport> => {
    const res = await api.get(`/tests/${id}/report`);
    return res.data;
  },
  getIssues: async (id: string, params?: { category?: string; severity?: string; page_url?: string }): Promise<IssueItem[]> => {
    const res = await api.get(`/tests/${id}/issues`, { params });
    return res.data;
  },
  updateIssueStatus: async (issueId: string, status: 'open' | 'resolved' | 'ignored'): Promise<IssueItem> => {
    const res = await api.patch(`/issues/${issueId}`, { status });
    return res.data;
  },
  getStreamUrl: (testId: string): string => {
    return `/api/tests/${testId}/stream`;
  }
};

export default api;
