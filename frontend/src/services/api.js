import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api/v1";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// ========================================
// REQUEST INTERCEPTOR
// ========================================

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

// ========================================
// RESPONSE INTERCEPTOR
// ========================================

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
    }

    return Promise.reject(error);
  }
);

// ========================================
// AUTH
// ========================================

export const login = async (email, password) => {
  const response = await api.post("/auth/login", {
    email: String(email || "").trim(),
    password: String(password || ""),
  });

  const accessToken = response.data?.access_token;

  if (!accessToken) {
    throw new Error("No access token received from server.");
  }

  localStorage.setItem("access_token", accessToken);

  return response.data;
};

export const logout = () => {
  localStorage.removeItem("access_token");
};

// ========================================
// MONITORING
// ========================================

export const getMonitoringSummary = async () => {
  const response = await api.get("/monitoring/summary");
  return response.data;
};

// ========================================
// REQUESTS
// ========================================

export const getRequests = async () => {
  const response = await api.get("/requests");
  return response.data;
};

export const createRequest = async (requestData) => {
  const response = await api.post("/requests", requestData);
  return response.data;
};

// ========================================
// WORKFLOWS
// ========================================

export const getWorkflowExecutions = async () => {
  const response = await api.get("/workflows/executions");
  return response.data;
};

export const getWorkflowExecution = async (executionId) => {
  const response = await api.get(
    `/workflows/executions/${executionId}`
  );

  return response.data;
};

export const executeWorkflow = async (
  workflowName,
  requestId
) => {
  const response = await api.post(
    `/workflows/${workflowName}/execute`,
    null,
    {
      params: {
        request_id: requestId,
      },
    }
  );

  return response.data;
};

export const retryWorkflowExecution = async (
  executionId
) => {
  const response = await api.post(
    `/workflows/executions/${executionId}/retry`
  );

  return response.data;
};

// ========================================
// APPROVALS
// ========================================

export const getApprovals = async () => {
  const response = await api.get("/approvals");
  return response.data;
};

export const approveApproval = async (
  approvalId,
  reviewerComment = ""
) => {
  const response = await api.patch(
    `/approvals/${approvalId}`,
    {
      decision: "approved",
      reviewer_comment: reviewerComment || null,
    }
  );

  return response.data;
};

export const rejectApproval = async (
  approvalId,
  reviewerComment = ""
) => {
  const response = await api.patch(
    `/approvals/${approvalId}`,
    {
      decision: "rejected",
      reviewer_comment: reviewerComment || null,
    }
  );

  return response.data;
};

// ========================================
// DOCUMENTS
// ========================================

export const uploadDocument = async (file) => {
  const formData = new FormData();

  formData.append("file", file);

  const response = await api.post(
    "/documents/ingest",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const searchDocuments = async (
  query,
  limit = 5
) => {
  const response = await api.get(
    "/documents/search",
    {
      params: {
        query,
        limit,
      },
    }
  );

  return response.data;
};

// ========================================
// AGENTS
// ========================================

export const getAgents = async () => {
  const response = await api.get("/agents");
  return response.data;
};

// ========================================
// TOOLS
// ========================================

export const getTools = async () => {
  const response = await api.get("/tools");
  return response.data;
};

// ========================================
// AUDIT LOGS
// ========================================

export const getAuditLogs = async () => {
  const response = await api.get("/audit-logs");
  return response.data;
};

export default api;