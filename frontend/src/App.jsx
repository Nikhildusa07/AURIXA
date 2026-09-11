// frontend/src/App.jsx

import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import api, {
  getMonitoringSummary,
  getRequests,
  getWorkflowExecutions,
  getApprovals,
  getAuditLogs,
  approveApproval,
  rejectApproval,
} from "./services/api";

import "./App.css";

// ========================================
// HELPERS
// ========================================

const normalizeStatus = (status) =>
  String(status || "").toLowerCase().trim();

const getArrayData = (data) => {
  if (Array.isArray(data)) return data;

  if (Array.isArray(data?.items)) return data.items;

  if (Array.isArray(data?.data)) return data.data;

  if (Array.isArray(data?.records)) return data.records;

  if (Array.isArray(data?.results)) return data.results;

  return [];
};

const getErrorMessage = (
  error,
  fallback = "Something went wrong."
) => {
  const detail = error?.response?.data?.detail;

  if (!detail) {
    return error?.message || fallback;
  }

  if (typeof detail === "string") {
    return detail;
  }

  if (Array.isArray(detail)) {
    return detail
      .map(
        (item) =>
          item?.msg ||
          item?.message ||
          "Validation error"
      )
      .join(", ");
  }

  if (typeof detail === "object") {
    return (
      detail?.msg ||
      detail?.message ||
      fallback
    );
  }

  return String(detail);
};

const formatDate = (dateValue) => {
  if (!dateValue) return "-";

  const date = new Date(dateValue);

  if (Number.isNaN(date.getTime())) {
    return String(dateValue);
  }

  return date.toLocaleString();
};

const formatText = (value, fallback = "-") => {
  if (
    value === null ||
    value === undefined ||
    value === ""
  ) {
    return fallback;
  }

  if (
    typeof value === "string" ||
    typeof value === "number"
  ) {
    return String(value);
  }

  return fallback;
};

const formatRecommendation = (recommendation) => {
  if (!recommendation) {
    return "No AI recommendation available.";
  }

  if (
    typeof recommendation === "string" ||
    typeof recommendation === "number"
  ) {
    return String(recommendation);
  }

  if (Array.isArray(recommendation)) {
    if (!recommendation.length) {
      return "No AI recommendation available.";
    }

    return recommendation
      .map((item) =>
        typeof item === "object"
          ? Object.values(item).join(" • ")
          : String(item)
      )
      .join(", ");
  }

  if (typeof recommendation === "object") {
    const entries = Object.entries(
      recommendation
    );

    if (!entries.length) {
      return "No AI recommendation available.";
    }

    return entries
      .map(([key, value]) => {
        const label = key
          .replaceAll("_", " ")
          .replace(/\b\w/g, (char) =>
            char.toUpperCase()
          );

        const text =
          value !== null &&
          typeof value === "object"
            ? JSON.stringify(value)
            : String(value);

        return `${label}: ${text}`;
      })
      .join(" • ");
  }

  return String(recommendation);
};

const getWorkflowName = (workflow) =>
  workflow?.workflow ||
  workflow?.workflow_name ||
  workflow?.name ||
  workflow?.state?.workflow_name ||
  workflow?.state?.workflow ||
  "Unknown Workflow";

const getWorkflowStep = (workflow) =>
  workflow?.current_step ||
  workflow?.state?.current_step ||
  workflow?.step ||
  "-";

const getWorkflowDate = (workflow) =>
  workflow?.updated_at ||
  workflow?.created_at ||
  workflow?.started_at ||
  workflow?.completed_at ||
  null;

const getStatusClass = (status) =>
  normalizeStatus(status)
    .replaceAll("_", "-")
    .replaceAll(" ", "-") || "unknown";

const sortByLatest = (items = []) =>
  [...items].sort((a, b) => {
    const firstDate = new Date(
      a?.updated_at ||
        a?.created_at ||
        a?.started_at ||
        a?.completed_at ||
        a?.reviewed_at ||
        0
    ).getTime();

    const secondDate = new Date(
      b?.updated_at ||
        b?.created_at ||
        b?.started_at ||
        b?.completed_at ||
        b?.reviewed_at ||
        0
    ).getTime();

    return secondDate - firstDate;
  });

// ========================================
// APP
// ========================================

function App() {
  const [token, setToken] = useState(() =>
    localStorage.getItem("access_token")
  );

  const [activePage, setActivePage] =
    useState("dashboard");

  const [authMode, setAuthMode] =
    useState("login");

  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");
  const [fullName, setFullName] =
    useState("");

  const [loginError, setLoginError] =
    useState("");

  const [registerMessage, setRegisterMessage] =
    useState("");

  const [
    registerMessageType,
    setRegisterMessageType,
  ] = useState("");

  const [loggingIn, setLoggingIn] =
    useState(false);

  const [registering, setRegistering] =
    useState(false);

  const [monitoring, setMonitoring] =
    useState(null);

  const [requests, setRequests] =
    useState([]);

  const [workflows, setWorkflows] =
    useState([]);

  const [approvals, setApprovals] =
    useState([]);

  const [auditLogs, setAuditLogs] =
    useState([]);

  const [backgroundJobs, setBackgroundJobs] =
    useState([]);

  const [analyticsSummary, setAnalyticsSummary] =
    useState(null);

  const [analyticsRecords, setAnalyticsRecords] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  const [lastUpdated, setLastUpdated] =
    useState(null);

  const [autoRefresh, setAutoRefresh] =
    useState(false);

  const [
    dashboardWorkflowFilter,
    setDashboardWorkflowFilter,
  ] = useState("all");

  const [
    dashboardSearch,
    setDashboardSearch,
  ] = useState("");

  const [
    showRequestModal,
    setShowRequestModal,
  ] = useState(false);

  const [
    creatingRequest,
    setCreatingRequest,
  ] = useState(false);

  const [
    requestMessage,
    setRequestMessage,
  ] = useState("");

  const [
    requestMessageType,
    setRequestMessageType,
  ] = useState("");

  const [
    approvalActionLoading,
    setApprovalActionLoading,
  ] = useState("");

  const [
    agentLoading,
    setAgentLoading,
  ] = useState(false);

  const [
    agentResult,
    setAgentResult,
  ] = useState(null);

  const [
    agentMessage,
    setAgentMessage,
  ] = useState("");

  const [
    agentForm,
    setAgentForm,
  ] = useState({
    task: "",
    context: "",
  });

  const [
    jobActionLoading,
    setJobActionLoading,
  ] = useState("");

  const [
    jobsMessage,
    setJobsMessage,
  ] = useState("");

  const [
    jobsMessageType,
    setJobsMessageType,
  ] = useState("");

  const [
    showJobModal,
    setShowJobModal,
  ] = useState(false);

  const [
    schedulingJob,
    setSchedulingJob,
  ] = useState(false);

  const [
    jobForm,
    setJobForm,
  ] = useState({
    job_type: "workflow",
    name: "",
    payload: "",
  });

  const requestModalTimeoutRef =
    useRef(null);

  const [requestForm, setRequestForm] =
    useState({
      title: "",
      description: "",
      request_type: "general",
      priority: "medium",
    });

  // ========================================
  // LOAD PLATFORM DATA
  // ========================================

  const loadDashboard = useCallback(
    async (showLoader = true) => {
      const accessToken =
        localStorage.getItem("access_token");

      if (!accessToken) {
        setLoading(false);
        return;
      }

      try {
        if (showLoader) {
          setLoading(true);
        }

        setError("");

        const results =
          await Promise.allSettled([
            getMonitoringSummary(),
            getRequests(),
            getWorkflowExecutions(),
            getApprovals(),
            getAuditLogs(),
            api.get("/api/v1/background-jobs/"),
            api.get("/api/v1/analytics/summary"),
            api.get("/api/v1/analytics/records"),
          ]);

        if (results[0].status === "fulfilled") {
          setMonitoring(
            results[0].value || {}
          );
        }

        if (results[1].status === "fulfilled") {
          setRequests(
            getArrayData(results[1].value)
          );
        }

        if (results[2].status === "fulfilled") {
          setWorkflows(
            getArrayData(results[2].value)
          );
        }

        if (results[3].status === "fulfilled") {
          setApprovals(
            getArrayData(results[3].value)
          );
        }

        if (results[4].status === "fulfilled") {
          setAuditLogs(
            getArrayData(results[4].value)
          );
        }

        if (results[5].status === "fulfilled") {
          setBackgroundJobs(
            getArrayData(
              results[5].value?.data ||
                results[5].value
            )
          );
        }

        if (results[6].status === "fulfilled") {
          setAnalyticsSummary(
            results[6].value?.data ||
              results[6].value ||
              {}
          );
        }

        if (results[7].status === "fulfilled") {
          setAnalyticsRecords(
            getArrayData(
              results[7].value?.data ||
                results[7].value
            )
          );
        }

        const unauthorized = results.some(
          (result) =>
            result.status === "rejected" &&
            result.reason?.response?.status ===
              401
        );

        if (unauthorized) {
          localStorage.removeItem(
            "access_token"
          );

          setToken(null);
          setLoading(false);
          return;
        }

        setLastUpdated(new Date());
      } catch (err) {
        setError(
          getErrorMessage(
            err,
            "Failed to load platform data."
          )
        );
      } finally {
        setLoading(false);
      }
    },
    []
  );

  // ========================================
  // INITIAL LOAD
  // ========================================

  useEffect(() => {
    if (token) {
      // eslint-disable-next-line react-hooks/set-state-in-effect
      loadDashboard();
    } else {
      setLoading(false);
    }
  }, [token, loadDashboard]);

  // ========================================
  // AUTO REFRESH
  // ========================================

  useEffect(() => {
    if (!token || !autoRefresh) {
      return undefined;
    }

    const interval = setInterval(() => {
      loadDashboard(false);
    }, 30000);

    return () => clearInterval(interval);
  }, [
    token,
    autoRefresh,
    loadDashboard,
  ]);

  useEffect(() => {
    return () => {
      if (requestModalTimeoutRef.current) {
        clearTimeout(
          requestModalTimeoutRef.current
        );
      }
    };
  }, []);

  // ========================================
  // AUTH
  // ========================================

  const switchAuthMode = (mode) => {
    setAuthMode(mode);
    setLoginError("");
    setRegisterMessage("");
    setRegisterMessageType("");
  };

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      setLoggingIn(true);
      setLoginError("");

      const response = await api.post(
        "/api/v1/auth/login",
        {
          email,
          password,
        }
      );

      const accessToken =
        response?.data?.access_token ||
        response?.access_token;

      if (!accessToken) {
        throw new Error(
          "Access token was not returned."
        );
      }

      localStorage.setItem(
        "access_token",
        accessToken
      );

      setToken(accessToken);
      setPassword("");
    } catch (err) {
      setLoginError(
        getErrorMessage(
          err,
          "Invalid email or password."
        )
      );
    } finally {
      setLoggingIn(false);
    }
  };

  const handleRegister = async (event) => {
    event.preventDefault();

    if (password !== confirmPassword) {
      setRegisterMessage(
        "Passwords do not match."
      );

      setRegisterMessageType("error");
      return;
    }

    try {
      setRegistering(true);
      setRegisterMessage("");

      await api.post(
        "/api/v1/auth/register",
        {
          full_name: fullName,
          email,
          password,
        }
      );

      setRegisterMessage(
        "Account created successfully. Please sign in."
      );

      setRegisterMessageType("success");

      setPassword("");
      setConfirmPassword("");
      setFullName("");

      setTimeout(() => {
        setAuthMode("login");
      }, 1200);
    } catch (err) {
      setRegisterMessage(
        getErrorMessage(
          err,
          "Failed to create account."
        )
      );

      setRegisterMessageType("error");
    } finally {
      setRegistering(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");

    setToken(null);
    setRequests([]);
    setWorkflows([]);
    setApprovals([]);
    setAuditLogs([]);
    setBackgroundJobs([]);
    setAnalyticsSummary(null);
    setAnalyticsRecords([]);
    setMonitoring(null);
    setActivePage("dashboard");
  };

  // ========================================
  // REQUESTS
  // ========================================

  const updateRequestForm = (
    field,
    value
  ) => {
    setRequestForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const closeRequestModal = () => {
    if (creatingRequest) return;

    setShowRequestModal(false);
    setRequestMessage("");
    setRequestMessageType("");
  };

  const handleCreateRequest = async (
    event
  ) => {
    event.preventDefault();

    try {
      setCreatingRequest(true);
      setRequestMessage("");

      await api.post(
        "/api/v1/requests",
        requestForm
      );

      setRequestMessage(
        "Request created successfully."
      );

      setRequestMessageType("success");

      setRequestForm({
        title: "",
        description: "",
        request_type: "general",
        priority: "medium",
      });

      const response = await getRequests();

      setRequests(
        getArrayData(response)
      );

      if (requestModalTimeoutRef.current) {
        clearTimeout(
          requestModalTimeoutRef.current
        );
      }

      requestModalTimeoutRef.current =
        setTimeout(() => {
          setShowRequestModal(false);
          setRequestMessage("");
        }, 1200);
    } catch (err) {
      setRequestMessage(
        getErrorMessage(
          err,
          "Failed to create request."
        )
      );

      setRequestMessageType("error");
    } finally {
      setCreatingRequest(false);
    }
  };

  // ========================================
  // APPROVALS
  // ========================================

  const handleApproval = async (
    approval,
    decision
  ) => {
    const approvalId = approval?.id;

    if (!approvalId) return;

    try {
      setApprovalActionLoading(
        `${approvalId}-${decision}`
      );

      if (decision === "approved") {
        await approveApproval(approvalId);
      } else {
        await rejectApproval(approvalId);
      }

      const response = await getApprovals();

      setApprovals(
        getArrayData(response)
      );

      await loadDashboard(false);
    } catch (err) {
      setError(
        getErrorMessage(
          err,
          "Failed to update approval."
        )
      );
    } finally {
      setApprovalActionLoading("");
    }
  };

  // ========================================
  // AGENTS
  // ========================================

  const handleAgentFormChange = (
    field,
    value
  ) => {
    setAgentForm((previous) => ({
      ...previous,
      [field]: value,
    }));
  };

  const handleOrchestrateAgent = async (
    event
  ) => {
    event.preventDefault();

    try {
      setAgentLoading(true);
      setAgentMessage("");
      setAgentResult(null);

      const response = await api.post(
        "/api/v1/agents/orchestrate",
        {
          task: agentForm.task,
          context: agentForm.context || undefined,
        }
      );

      setAgentResult(
        response?.data || response
      );

      setAgentMessage(
        "Agent orchestration completed successfully."
      );
    } catch (err) {
      setAgentMessage(
        getErrorMessage(
          err,
          "Agent orchestration failed."
        )
      );
    } finally {
      setAgentLoading(false);
    }
  };

  // ========================================
  // BACKGROUND JOBS
  // ========================================

  const loadBackgroundJobs = async () => {
    try {
      const response = await api.get(
        "/api/v1/background-jobs/"
      );

      setBackgroundJobs(
        getArrayData(
          response?.data || response
        )
      );
    } catch (err) {
      setJobsMessage(
        getErrorMessage(
          err,
          "Failed to load background jobs."
        )
      );

      setJobsMessageType("error");
    }
  };

  const handleScheduleJob = async (
    event
  ) => {
    event.preventDefault();

    try {
      setSchedulingJob(true);
      setJobsMessage("");

      let parsedPayload = {};

      if (jobForm.payload.trim()) {
        try {
          parsedPayload = JSON.parse(
            jobForm.payload
          );
        } catch {
          throw new Error(
            "Payload must be valid JSON."
          );
        }
      }

      await api.post(
        "/api/v1/background-jobs/schedule",
        {
          job_type: jobForm.job_type,
          name: jobForm.name,
          payload: parsedPayload,
        }
      );

      setJobsMessage(
        "Background job scheduled successfully."
      );

      setJobsMessageType("success");

      setJobForm({
        job_type: "workflow",
        name: "",
        payload: "",
      });

      setShowJobModal(false);

      await loadBackgroundJobs();
    } catch (err) {
      setJobsMessage(
        getErrorMessage(
          err,
          "Failed to schedule background job."
        )
      );

      setJobsMessageType("error");
    } finally {
      setSchedulingJob(false);
    }
  };

  const handleJobAction = async (
    endpoint,
    loadingKey
  ) => {
    try {
      setJobActionLoading(loadingKey);
      setJobsMessage("");

      await api.post(endpoint);

      setJobsMessage(
        "Background job action completed successfully."
      );

      setJobsMessageType("success");

      await loadBackgroundJobs();
    } catch (err) {
      setJobsMessage(
        getErrorMessage(
          err,
          "Background job action failed."
        )
      );

      setJobsMessageType("error");
    } finally {
      setJobActionLoading("");
    }
  };

  // ========================================
  // COMPUTED DATA
  // ========================================

  const sortedRequests = useMemo(
    () => sortByLatest(requests),
    [requests]
  );

  const sortedWorkflows = useMemo(
    () => sortByLatest(workflows),
    [workflows]
  );

  const sortedAuditLogs = useMemo(
    () => sortByLatest(auditLogs),
    [auditLogs]
  );

  const pendingRequests = useMemo(
    () =>
      requests.filter((request) => {
        const status = normalizeStatus(
          request?.status
        );

        return (
          status.includes("pending") ||
          status.includes("review")
        );
      }).length,
    [requests]
  );

  const pendingApprovals = useMemo(
    () =>
      approvals.filter(
        (approval) =>
          normalizeStatus(
            approval?.status
          ) === "pending"
      ).length,
    [approvals]
  );

  const activeWorkflows = useMemo(
    () =>
      workflows.filter((workflow) => {
        const status = normalizeStatus(
          workflow?.status
        );

        return (
          status === "running" ||
          status === "processing" ||
          status === "active"
        );
      }).length,
    [workflows]
  );

  const completedWorkflows = useMemo(
    () =>
      workflows.filter((workflow) => {
        const status = normalizeStatus(
          workflow?.status
        );

        return (
          status === "completed" ||
          status === "success" ||
          status === "successful"
        );
      }).length,
    [workflows]
  );

  const failedWorkflows = useMemo(
    () =>
      workflows.filter((workflow) =>
        normalizeStatus(
          workflow?.status
        ).includes("fail")
      ).length,
    [workflows]
  );

  const successRate = useMemo(() => {
    const total =
      completedWorkflows + failedWorkflows;

    if (!total) return 0;

    return Math.round(
      (completedWorkflows / total) * 100
    );
  }, [
    completedWorkflows,
    failedWorkflows,
  ]);

  const systemStatus = useMemo(() => {
    const status =
      monitoring?.status ||
      monitoring?.system_status ||
      monitoring?.overall_status;

    if (!status) {
      return "Operational";
    }

    return formatText(status);
  }, [monitoring]);

  const filteredWorkflows = useMemo(() => {
    const search =
      dashboardSearch.toLowerCase().trim();

    return sortedWorkflows.filter(
      (workflow) => {
        const name =
          getWorkflowName(
            workflow
          ).toLowerCase();

        const status = normalizeStatus(
          workflow?.status
        );

        const matchesSearch =
          !search ||
          name.includes(search) ||
          status.includes(search);

        const matchesFilter =
          dashboardWorkflowFilter ===
            "all" ||
          status ===
            dashboardWorkflowFilter;

        return (
          matchesSearch &&
          matchesFilter
        );
      }
    );
  }, [
    sortedWorkflows,
    dashboardSearch,
    dashboardWorkflowFilter,
  ]);

  const recentRequests =
    sortedRequests.slice(0, 5);

  const recentAuditActivity =
    sortedAuditLogs.slice(0, 6);

  const dashboardPendingApprovals =
    approvals
      .filter(
        (approval) =>
          normalizeStatus(
            approval?.status
          ) === "pending"
      )
      .slice(0, 5);

  // ========================================
  // AUTH PAGE
  // ========================================

  if (!token) {
    return (
      <div className="login-page">
        <div className="login-card">
          <div className="login-brand-icon">
            A
          </div>

          <h1>AURIXA</h1>

          <p className="auth-description">
            Enterprise AI Automation Platform
          </p>

          {authMode === "login" ? (
            <form onSubmit={handleLogin}>
              <h2 className="auth-heading">
                Welcome back
              </h2>

              {loginError && (
                <div className="form-message form-error">
                  {loginError}
                </div>
              )}

              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>

                <input
                  type="password"
                  placeholder="Enter your password"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  required
                />
              </div>

              <button
                type="submit"
                className="login-button"
                disabled={loggingIn}
              >
                {loggingIn
                  ? "Signing in..."
                  : "Sign In"}
              </button>

              <p className="auth-switch-text">
                New to AURIXA?{" "}

                <button
                  type="button"
                  onClick={() =>
                    switchAuthMode("register")
                  }
                >
                  Create an account
                </button>
              </p>
            </form>
          ) : (
            <form onSubmit={handleRegister}>
              <h2 className="auth-heading">
                Create your account
              </h2>

              {registerMessage && (
                <div
                  className={
                    registerMessageType ===
                    "success"
                      ? "form-message form-success"
                      : "form-message form-error"
                  }
                >
                  {registerMessage}
                </div>
              )}

              <div className="form-group">
                <label>Full Name</label>

                <input
                  type="text"
                  placeholder="Enter your full name"
                  value={fullName}
                  onChange={(event) =>
                    setFullName(event.target.value)
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label>Email</label>

                <input
                  type="email"
                  placeholder="Enter your email"
                  value={email}
                  onChange={(event) =>
                    setEmail(event.target.value)
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label>Password</label>

                <input
                  type="password"
                  placeholder="Minimum 6 characters"
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  minLength="6"
                  required
                />
              </div>

              <div className="form-group">
                <label>Confirm Password</label>

                <input
                  type="password"
                  placeholder="Confirm your password"
                  value={confirmPassword}
                  onChange={(event) =>
                    setConfirmPassword(
                      event.target.value
                    )
                  }
                  minLength="6"
                  required
                />
              </div>

              <button
                type="submit"
                className="login-button"
                disabled={registering}
              >
                {registering
                  ? "Creating Account..."
                  : "Create Account"}
              </button>

              <p className="auth-switch-text">
                Already have an account?{" "}

                <button
                  type="button"
                  onClick={() =>
                    switchAuthMode("login")
                  }
                >
                  Sign in
                </button>
              </p>
            </form>
          )}
        </div>
      </div>
    );
  }

  // ========================================
  // MAIN APPLICATION
  // ========================================

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">A</div>

          <div>
            <h1>AURIXA</h1>

            <span>
              Enterprise AI Platform
            </span>
          </div>
        </div>

        <nav>
          <NavButton
            icon="▣"
            label="Dashboard"
            page="dashboard"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            icon="◈"
            label="Requests"
            page="requests"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            icon="⚙"
            label="Workflows"
            page="workflows"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            icon="✦"
            label="Agents"
            page="agents"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            icon="◫"
            label="Background Jobs"
            page="background-jobs"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <button
            type="button"
            className={`nav-item ${
              activePage === "approvals"
                ? "active"
                : ""
            }`}
            onClick={() =>
              setActivePage("approvals")
            }
          >
            <span>✓</span>

            Approvals

            {pendingApprovals > 0 && (
              <b className="nav-count">
                {pendingApprovals}
              </b>
            )}
          </button>

          <NavButton
            icon="▤"
            label="Analytics"
            page="analytics"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            icon="◷"
            label="Audit Logs"
            page="audit"
            activePage={activePage}
            setActivePage={setActivePage}
          />

          <NavButton
            icon="◉"
            label="Monitoring"
            page="monitoring"
            activePage={activePage}
            setActivePage={setActivePage}
          />
        </nav>

        <div className="sidebar-footer">
          <div className="system-status">
            <span className="status-dot" />

            System Operational
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="welcome">
              Enterprise Automation Platform
            </p>

            <h2>
              {activePage === "dashboard" &&
                "AURIXA Command Center"}

              {activePage === "requests" &&
                "Enterprise Requests"}

              {activePage === "workflows" &&
                "Workflow Executions"}

              {activePage === "agents" &&
                "AI Agent Orchestration"}

              {activePage ===
                "background-jobs" &&
                "Background Job Center"}

              {activePage === "approvals" &&
                "Approval Center"}

              {activePage === "analytics" &&
                "Enterprise Analytics"}

              {activePage === "audit" &&
                "Audit Logs"}

              {activePage === "monitoring" &&
                "System Monitoring"}
            </h2>

            {lastUpdated && (
              <span className="last-updated">
                Last updated:{" "}
                {formatDate(lastUpdated)}
              </span>
            )}
          </div>

          <div className="topbar-actions">
            {activePage === "requests" && (
              <button
                type="button"
                className="create-button"
                onClick={() =>
                  setShowRequestModal(true)
                }
              >
                + New Request
              </button>
            )}

            {activePage ===
              "background-jobs" && (
              <button
                type="button"
                className="create-button"
                onClick={() =>
                  setShowJobModal(true)
                }
              >
                + Schedule Job
              </button>
            )}

            {activePage === "dashboard" && (
              <button
                type="button"
                className={`auto-refresh-button ${
                  autoRefresh ? "enabled" : ""
                }`}
                onClick={() =>
                  setAutoRefresh(
                    (previous) => !previous
                  )
                }
              >
                {autoRefresh
                  ? "● Live"
                  : "○ Auto Refresh"}
              </button>
            )}

            <button
              type="button"
              className="refresh-button"
              onClick={() =>
                loadDashboard(false)
              }
            >
              ↻ Refresh
            </button>

            <button
              type="button"
              className="logout-button"
              onClick={handleLogout}
            >
              Logout
            </button>
          </div>
        </header>

        {loading ? (
          <div className="loading-state">
            <div className="spinner" />

            Loading AURIXA platform...
          </div>
        ) : (
          <>
            {error && (
              <div className="error-banner">
                {error}
              </div>
            )}

            {activePage === "dashboard" && (
              <DashboardPage
                requests={requests}
                workflows={workflows}
                pendingRequests={pendingRequests}
                completedWorkflows={
                  completedWorkflows
                }
                pendingApprovals={
                  pendingApprovals
                }
                activeWorkflows={
                  activeWorkflows
                }
                failedWorkflows={
                  failedWorkflows
                }
                successRate={successRate}
                systemStatus={systemStatus}
                filteredWorkflows={
                  filteredWorkflows
                }
                dashboardSearch={
                  dashboardSearch
                }
                setDashboardSearch={
                  setDashboardSearch
                }
                dashboardWorkflowFilter={
                  dashboardWorkflowFilter
                }
                setDashboardWorkflowFilter={
                  setDashboardWorkflowFilter
                }
                dashboardPendingApprovals={
                  dashboardPendingApprovals
                }
                recentRequests={recentRequests}
                recentAuditActivity={
                  recentAuditActivity
                }
                approvalActionLoading={
                  approvalActionLoading
                }
                handleApproval={handleApproval}
                setActivePage={setActivePage}
                setShowRequestModal={
                  setShowRequestModal
                }
              />
            )}

            {activePage === "requests" && (
              <RequestsPage
                requests={sortedRequests}
              />
            )}

            {activePage === "workflows" && (
              <WorkflowsPage
                workflows={sortedWorkflows}
              />
            )}

            {activePage === "agents" && (
              <AgentsPage
                agentForm={agentForm}
                handleAgentFormChange={
                  handleAgentFormChange
                }
                handleOrchestrateAgent={
                  handleOrchestrateAgent
                }
                agentLoading={agentLoading}
                agentResult={agentResult}
                agentMessage={agentMessage}
              />
            )}

            {activePage ===
              "background-jobs" && (
              <BackgroundJobsPage
                backgroundJobs={backgroundJobs}
                jobActionLoading={
                  jobActionLoading
                }
                jobsMessage={jobsMessage}
                jobsMessageType={
                  jobsMessageType
                }
                handleJobAction={
                  handleJobAction
                }
                loadBackgroundJobs={
                  loadBackgroundJobs
                }
                setShowJobModal={
                  setShowJobModal
                }
              />
            )}

            {activePage === "approvals" && (
              <ApprovalsPage
                approvals={approvals}
                pendingApprovals={
                  pendingApprovals
                }
                approvalActionLoading={
                  approvalActionLoading
                }
                handleApproval={handleApproval}
              />
            )}

            {activePage === "analytics" && (
              <AnalyticsPage
                analyticsSummary={
                  analyticsSummary
                }
                analyticsRecords={
                  analyticsRecords
                }
                requests={requests}
                workflows={workflows}
              />
            )}

            {activePage === "audit" && (
              <AuditPage
                sortedAuditLogs={
                  sortedAuditLogs
                }
              />
            )}

            {activePage === "monitoring" && (
              <MonitoringPage
                monitoring={monitoring}
                systemStatus={systemStatus}
                requests={requests}
                workflows={workflows}
                approvals={approvals}
                auditLogs={auditLogs}
                activeWorkflows={
                  activeWorkflows
                }
                pendingApprovals={
                  pendingApprovals
                }
                completedWorkflows={
                  completedWorkflows
                }
              />
            )}
          </>
        )}
      </main>

      {showRequestModal && (
        <RequestModal
          requestForm={requestForm}
          updateRequestForm={
            updateRequestForm
          }
          handleCreateRequest={
            handleCreateRequest
          }
          creatingRequest={
            creatingRequest
          }
          requestMessage={requestMessage}
          requestMessageType={
            requestMessageType
          }
          closeRequestModal={
            closeRequestModal
          }
        />
      )}

      {showJobModal && (
        <JobModal
          jobForm={jobForm}
          setJobForm={setJobForm}
          handleScheduleJob={
            handleScheduleJob
          }
          schedulingJob={schedulingJob}
          closeJobModal={() =>
            setShowJobModal(false)
          }
        />
      )}
    </div>
  );
}

// ========================================
// NAV BUTTON
// ========================================

function NavButton({
  icon,
  label,
  page,
  activePage,
  setActivePage,
}) {
  return (
    <button
      type="button"
      className={`nav-item ${
        activePage === page ? "active" : ""
      }`}
      onClick={() => setActivePage(page)}
    >
      <span>{icon}</span>

      {label}
    </button>
  );
}

// ========================================
// DASHBOARD
// ========================================

function DashboardPage({
  requests,
  workflows,
  pendingRequests,
  completedWorkflows,
  pendingApprovals,
  activeWorkflows,
  failedWorkflows,
  successRate,
  systemStatus,
  filteredWorkflows,
  dashboardSearch,
  setDashboardSearch,
  dashboardWorkflowFilter,
  setDashboardWorkflowFilter,
  dashboardPendingApprovals,
  recentRequests,
  recentAuditActivity,
  approvalActionLoading,
  handleApproval,
  setActivePage,
  setShowRequestModal,
}) {
  return (
    <section className="page-content dashboard-page">
      <div className="section-title">
        <div>
          <h3>Platform Overview</h3>

          <p>
            Real-time enterprise automation
            insights and operational status
          </p>
        </div>

        <div className="dashboard-health">
          <span className="health-dot" />

          <div>
            <small>Platform Status</small>

            <strong>{systemStatus}</strong>
          </div>
        </div>
      </div>

      <div className="stats-grid">
        <DashboardStat
          icon="◈"
          title="Total Requests"
          value={requests.length}
          subtitle={`${pendingRequests} pending`}
          onClick={() =>
            setActivePage("requests")
          }
        />

        <DashboardStat
          icon="⚙"
          title="Workflow Executions"
          value={workflows.length}
          subtitle={`${completedWorkflows} completed`}
          onClick={() =>
            setActivePage("workflows")
          }
        />

        <DashboardStat
          icon="✓"
          title="Pending Approvals"
          value={pendingApprovals}
          subtitle="Awaiting human review"
          onClick={() =>
            setActivePage("approvals")
          }
        />

        <DashboardStat
          icon="●"
          title="Active Workflows"
          value={activeWorkflows}
          subtitle="Currently processing"
          onClick={() =>
            setActivePage("workflows")
          }
        />
      </div>

      <div className="dashboard-grid">
        <div className="dashboard-performance-panel">
          <div className="panel-header">
            <div>
              <h3>
                Automation Performance
              </h3>

              <p>
                Workflow execution health
              </p>
            </div>

            <span className="performance-badge">
              {successRate}%
            </span>
          </div>

          <div className="performance-grid">
            <div className="performance-item main-performance">
              <span>Success Rate</span>

              <strong>{successRate}%</strong>

              <div className="progress-track">
                <div
                  className="progress-bar"
                  style={{
                    width: `${successRate}%`,
                  }}
                />
              </div>
            </div>

            <div className="performance-item">
              <span>Completed</span>

              <strong>
                {completedWorkflows}
              </strong>
            </div>

            <div className="performance-item">
              <span>Failed</span>

              <strong>
                {failedWorkflows}
              </strong>
            </div>
          </div>
        </div>

        <div className="quick-actions-panel">
          <div className="panel-header">
            <div>
              <h3>Quick Actions</h3>

              <p>
                Manage the platform faster
              </p>
            </div>
          </div>

          <div className="quick-actions">
            <button
              type="button"
              onClick={() =>
                setShowRequestModal(true)
              }
            >
              <span>+</span>

              <div>
                <strong>New Request</strong>

                <small>
                  Create automation
                </small>
              </div>
            </button>

            <button
              type="button"
              onClick={() =>
                setActivePage("approvals")
              }
            >
              <span>✓</span>

              <div>
                <strong>
                  Review Approvals
                </strong>

                <small>
                  {pendingApprovals} pending
                </small>
              </div>
            </button>

            <button
              type="button"
              onClick={() =>
                setActivePage("workflows")
              }
            >
              <span>⚙</span>

              <div>
                <strong>
                  View Workflows
                </strong>

                <small>
                  Monitor executions
                </small>
              </div>
            </button>

            <button
              type="button"
              onClick={() =>
                setActivePage("monitoring")
              }
            >
              <span>◉</span>

              <div>
                <strong>System Health</strong>

                <small>
                  Check monitoring
                </small>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="dashboard-two-column">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>
                Workflow Executions
              </h3>

              <p>
                Recent automation activity
              </p>
            </div>
          </div>

          <div className="dashboard-controls">
            <input
              type="text"
              placeholder="Search workflows..."
              value={dashboardSearch}
              onChange={(event) =>
                setDashboardSearch(
                  event.target.value
                )
              }
            />

            <select
              value={
                dashboardWorkflowFilter
              }
              onChange={(event) =>
                setDashboardWorkflowFilter(
                  event.target.value
                )
              }
            >
              <option value="all">
                All Statuses
              </option>

              <option value="running">
                Running
              </option>

              <option value="completed">
                Completed
              </option>

              <option value="failed">
                Failed
              </option>
            </select>
          </div>

          <WorkflowTable
            workflows={filteredWorkflows.slice(
              0,
              6
            )}
          />
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>
                Pending Approvals
              </h3>

              <p>
                Human review queue
              </p>
            </div>
          </div>

          {dashboardPendingApprovals.length ===
          0 ? (
            <div className="empty-state">
              No pending approvals.
            </div>
          ) : (
            <div className="compact-list">
              {dashboardPendingApprovals.map(
                (approval, index) => (
                  <ApprovalCard
                    key={
                      approval?.id || index
                    }
                    approval={approval}
                    approvalActionLoading={
                      approvalActionLoading
                    }
                    handleApproval={
                      handleApproval
                    }
                    compact
                  />
                )
              )}
            </div>
          )}
        </div>
      </div>

      <div className="dashboard-two-column">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Recent Requests</h3>

              <p>
                Latest enterprise requests
              </p>
            </div>
          </div>

          {recentRequests.length === 0 ? (
            <div className="empty-state">
              No requests found.
            </div>
          ) : (
            <div className="activity-list">
              {recentRequests.map(
                (request, index) => (
                  <div
                    className="activity-item"
                    key={
                      request?.id || index
                    }
                  >
                    <div>
                      <strong>
                        {formatText(
                          request?.title ||
                            request?.name
                        )}
                      </strong>

                      <small>
                        {formatDate(
                          request?.created_at
                        )}
                      </small>
                    </div>

                    <StatusBadge
                      status={request?.status}
                    />
                  </div>
                )
              )}
            </div>
          )}
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Audit Activity</h3>

              <p>
                Latest platform events
              </p>
            </div>
          </div>

          {recentAuditActivity.length ===
          0 ? (
            <div className="empty-state">
              No audit activity found.
            </div>
          ) : (
            <div className="activity-list">
              {recentAuditActivity.map(
                (log, index) => (
                  <div
                    className="activity-item"
                    key={log?.id || index}
                  >
                    <div>
                      <strong>
                        {formatText(
                          log?.action
                        )}
                      </strong>

                      <small>
                        {formatText(
                          log?.entity_type
                        )}
                      </small>
                    </div>

                    <small>
                      {formatDate(
                        log?.created_at ||
                          log?.updated_at
                      )}
                    </small>
                  </div>
                )
              )}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

function DashboardStat({
  icon,
  title,
  value,
  subtitle,
  onClick,
}) {
  return (
    <button
      type="button"
      className="stat-card"
      onClick={onClick}
    >
      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <span>{title}</span>

        <strong>{value}</strong>

        <small>{subtitle}</small>
      </div>
    </button>
  );
}

// ========================================
// REQUESTS
// ========================================

function RequestsPage({ requests }) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>Enterprise Requests</h3>

          <p>
            AI-powered automation requests
          </p>
        </div>

        <span className="large-count">
          {requests.length}
        </span>
      </div>

      {requests.length === 0 ? (
        <div className="empty-page">
          <h3>No Requests Found</h3>

          <p>
            Create a new enterprise request to
            start automation.
          </p>
        </div>
      ) : (
        <div className="requests-grid">
          {requests.map(
            (request, index) => (
              <div
                className="request-card"
                key={request?.id || index}
              >
                <div className="card-top">
                  <div>
                    <h3>
                      {formatText(
                        request?.title ||
                          request?.name
                      )}
                    </h3>

                    <p>
                      {formatText(
                        request?.description
                      )}
                    </p>
                  </div>

                  <StatusBadge
                    status={request?.status}
                  />
                </div>

                <div className="card-meta">
                  <span>
                    Type:{" "}
                    {formatText(
                      request?.request_type
                    )}
                  </span>

                  <span>
                    Priority:{" "}
                    {formatText(
                      request?.priority
                    )}
                  </span>
                </div>

                <div className="recommendation-box">
                  {formatRecommendation(
                    request?.recommendation ||
                      request?.ai_result
                  )}
                </div>

                <small className="card-date">
                  {formatDate(
                    request?.created_at ||
                      request?.updated_at
                  )}
                </small>
              </div>
            )
          )}
        </div>
      )}
    </section>
  );
}

// ========================================
// WORKFLOWS
// ========================================

function WorkflowsPage({ workflows }) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>Workflow Executions</h3>

          <p>
            Monitor enterprise workflow execution
          </p>
        </div>

        <span className="large-count">
          {workflows.length}
        </span>
      </div>

      <div className="panel full-panel">
        <WorkflowTable workflows={workflows} />
      </div>
    </section>
  );
}

function WorkflowTable({ workflows }) {
  if (!workflows.length) {
    return (
      <div className="empty-state">
        No workflow executions found.
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>Workflow</th>

            <th>Status</th>

            <th>Current Step</th>

            <th>Updated</th>
          </tr>
        </thead>

        <tbody>
          {workflows.map(
            (workflow, index) => (
              <tr
                key={
                  workflow?.id ||
                  workflow?.execution_id ||
                  index
                }
              >
                <td>
                  {getWorkflowName(
                    workflow
                  )}
                </td>

                <td>
                  <StatusBadge
                    status={workflow?.status}
                  />
                </td>

                <td>
                  {getWorkflowStep(
                    workflow
                  )}
                </td>

                <td>
                  {formatDate(
                    getWorkflowDate(
                      workflow
                    )
                  )}
                </td>
              </tr>
            )
          )}
        </tbody>
      </table>
    </div>
  );
}

// ========================================
// AGENTS
// ========================================

function AgentsPage({
  agentForm,
  handleAgentFormChange,
  handleOrchestrateAgent,
  agentLoading,
  agentResult,
  agentMessage,
}) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>AI Agent Orchestration</h3>

          <p>
            Execute enterprise tasks through the
            AURIXA agent orchestration system
          </p>
        </div>

        <span className="api-route-badge">
          POST /agents/orchestrate
        </span>
      </div>

      <div className="agents-layout">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Orchestrate Agent</h3>

              <p>
                Submit a task for AI execution
              </p>
            </div>
          </div>

          <form
            className="agent-form"
            onSubmit={
              handleOrchestrateAgent
            }
          >
            <div className="form-group">
              <label>Task</label>

              <textarea
                placeholder="Describe the task you want AURIXA agents to execute..."
                value={agentForm.task}
                onChange={(event) =>
                  handleAgentFormChange(
                    "task",
                    event.target.value
                  )
                }
                required
              />
            </div>

            <div className="form-group">
              <label>
                Additional Context
              </label>

              <textarea
                placeholder="Optional context, business requirements, or additional instructions..."
                value={agentForm.context}
                onChange={(event) =>
                  handleAgentFormChange(
                    "context",
                    event.target.value
                  )
                }
              />
            </div>

            <button
              type="submit"
              className="primary-button"
              disabled={agentLoading}
            >
              {agentLoading
                ? "Orchestrating..."
                : "Run Agent Orchestration"}
            </button>
          </form>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Agent Result</h3>

              <p>
                Orchestration response
              </p>
            </div>
          </div>

          {agentMessage && (
            <div className="form-message form-success">
              {agentMessage}
            </div>
          )}

          {!agentResult ? (
            <div className="empty-state">
              Submit an agent task to view the
              orchestration result.
            </div>
          ) : (
            <div className="agent-result">
              <pre>
                {JSON.stringify(
                  agentResult,
                  null,
                  2
                )}
              </pre>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

// ========================================
// BACKGROUND JOBS
// ========================================

function BackgroundJobsPage({
  backgroundJobs,
  jobActionLoading,
  jobsMessage,
  jobsMessageType,
  handleJobAction,
  loadBackgroundJobs,
  setShowJobModal,
}) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>Background Job Center</h3>

          <p>
            Schedule, execute, pause and manage
            enterprise background jobs
          </p>
        </div>

        <span className="large-count">
          {backgroundJobs.length}
        </span>
      </div>

      {jobsMessage && (
        <div
          className={
            jobsMessageType === "error"
              ? "form-message form-error"
              : "form-message form-success"
          }
        >
          {jobsMessage}
        </div>
      )}

      <div className="jobs-toolbar">
        <button
          type="button"
          className="primary-button"
          onClick={() =>
            setShowJobModal(true)
          }
        >
          + Schedule Background Job
        </button>

        <button
          type="button"
          className="secondary-button"
          disabled={
            jobActionLoading === "run-next"
          }
          onClick={() =>
            handleJobAction(
              "/api/v1/background-jobs/run-next",
              "run-next"
            )
          }
        >
          {jobActionLoading === "run-next"
            ? "Running..."
            : "Run Next"}
        </button>

        <button
          type="button"
          className="secondary-button"
          disabled={
            jobActionLoading === "pause"
          }
          onClick={() =>
            handleJobAction(
              "/api/v1/background-jobs/pause",
              "pause"
            )
          }
        >
          Pause Jobs
        </button>

        <button
          type="button"
          className="secondary-button"
          disabled={
            jobActionLoading === "resume"
          }
          onClick={() =>
            handleJobAction(
              "/api/v1/background-jobs/resume",
              "resume"
            )
          }
        >
          Resume Jobs
        </button>

        <button
          type="button"
          className="secondary-button"
          onClick={loadBackgroundJobs}
        >
          ↻ Refresh
        </button>
      </div>

      <div className="panel full-panel">
        {backgroundJobs.length === 0 ? (
          <div className="empty-state">
            No background jobs found.
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Job</th>

                  <th>Type</th>

                  <th>Status</th>

                  <th>Created</th>

                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {backgroundJobs.map(
                  (job, index) => {
                    const jobId =
                      job?.id ||
                      job?.job_id;

                    return (
                      <tr
                        key={
                          jobId || index
                        }
                      >
                        <td>
                          {formatText(
                            job?.name ||
                              job?.job_name
                          )}
                        </td>

                        <td>
                          {formatText(
                            job?.job_type ||
                              job?.type
                          )}
                        </td>

                        <td>
                          <StatusBadge
                            status={
                              job?.status
                            }
                          />
                        </td>

                        <td>
                          {formatDate(
                            job?.created_at ||
                              job?.scheduled_at
                          )}
                        </td>

                        <td>
                          <div className="table-actions">
                            {jobId && (
                              <>
                                <button
                                  type="button"
                                  disabled={
                                    jobActionLoading ===
                                    `retry-${jobId}`
                                  }
                                  onClick={() =>
                                    handleJobAction(
                                      `/api/v1/background-jobs/${jobId}/retry`,
                                      `retry-${jobId}`
                                    )
                                  }
                                >
                                  Retry
                                </button>

                                <button
                                  type="button"
                                  disabled={
                                    jobActionLoading ===
                                    `complete-${jobId}`
                                  }
                                  onClick={() =>
                                    handleJobAction(
                                      `/api/v1/background-jobs/${jobId}/complete`,
                                      `complete-${jobId}`
                                    )
                                  }
                                >
                                  Complete
                                </button>
                              </>
                            )}
                          </div>
                        </td>
                      </tr>
                    );
                  }
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

// ========================================
// APPROVALS
// ========================================

function ApprovalsPage({
  approvals,
  pendingApprovals,
  approvalActionLoading,
  handleApproval,
}) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>Approval Center</h3>

          <p>
            Review AI decisions and approve or
            reject workflow execution
          </p>
        </div>

        <span className="large-count">
          {pendingApprovals}
        </span>
      </div>

      {approvals.length === 0 ? (
        <div className="empty-page">
          <h3>No Approvals Found</h3>

          <p>
            Workflows requiring human decisions
            will appear here.
          </p>
        </div>
      ) : (
        <div className="approvals-grid">
          {approvals.map(
            (approval, index) => (
              <ApprovalCard
                key={
                  approval?.id || index
                }
                approval={approval}
                approvalActionLoading={
                  approvalActionLoading
                }
                handleApproval={
                  handleApproval
                }
              />
            )
          )}
        </div>
      )}
    </section>
  );
}

function ApprovalCard({
  approval,
  approvalActionLoading,
  handleApproval,
  compact = false,
}) {
  const approvalId = approval?.id;

  const approving =
    approvalActionLoading ===
    `${approvalId}-approved`;

  const rejecting =
    approvalActionLoading ===
    `${approvalId}-rejected`;

  return (
    <div
      className={`approval-card ${
        compact ? "compact" : ""
      }`}
    >
      <div className="card-top">
        <div>
          <h3>
            {formatText(
              approval?.title ||
                approval?.request_title ||
                approval?.workflow_name,
              "Approval Request"
            )}
          </h3>

          <p>
            {formatText(
              approval?.description ||
                approval?.reason
            )}
          </p>
        </div>

        <StatusBadge
          status={approval?.status}
        />
      </div>

      <div className="card-meta">
        <span>
          {formatDate(
            approval?.created_at
          )}
        </span>
      </div>

      {normalizeStatus(
        approval?.status
      ) === "pending" && (
        <div className="approval-actions">
          <button
            type="button"
            className="approve-button"
            disabled={approving || rejecting}
            onClick={() =>
              handleApproval(
                approval,
                "approved"
              )
            }
          >
            {approving
              ? "Approving..."
              : "Approve"}
          </button>

          <button
            type="button"
            className="reject-button"
            disabled={approving || rejecting}
            onClick={() =>
              handleApproval(
                approval,
                "rejected"
              )
            }
          >
            {rejecting
              ? "Rejecting..."
              : "Reject"}
          </button>
        </div>
      )}
    </div>
  );
}

// ========================================
// ANALYTICS
// ========================================

function AnalyticsPage({
  analyticsSummary,
  analyticsRecords,
  requests,
  workflows,
}) {
  const summary =
    analyticsSummary || {};

  const totalExecutions =
    summary?.total_executions ||
    summary?.executions ||
    workflows.length;

  const totalRequests =
    summary?.total_requests ||
    requests.length;

  const successful =
    summary?.successful_executions ||
    summary?.completed ||
    0;

  const failed =
    summary?.failed_executions ||
    summary?.failed ||
    0;

  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>Enterprise Analytics</h3>

          <p>
            Operational performance and execution
            intelligence
          </p>
        </div>

        <span className="api-route-badge">
          GET /analytics/summary
        </span>
      </div>

      <div className="stats-grid analytics-stats">
        <DashboardStat
          icon="▤"
          title="Total Requests"
          value={totalRequests}
          subtitle="Platform requests"
        />

        <DashboardStat
          icon="⚙"
          title="Executions"
          value={totalExecutions}
          subtitle="Workflow activity"
        />

        <DashboardStat
          icon="✓"
          title="Successful"
          value={successful}
          subtitle="Completed successfully"
        />

        <DashboardStat
          icon="!"
          title="Failed"
          value={failed}
          subtitle="Requires attention"
        />
      </div>

      <div className="analytics-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Analytics Summary</h3>

              <p>
                Current aggregated platform metrics
              </p>
            </div>
          </div>

          <div className="analytics-summary-list">
            {Object.keys(summary).length ===
            0 ? (
              <div className="empty-state">
                No analytics summary available.
              </div>
            ) : (
              Object.entries(summary).map(
                ([key, value]) => (
                  <div
                    className="analytics-row"
                    key={key}
                  >
                    <span>
                      {key
                        .replaceAll("_", " ")
                        .replace(
                          /\b\w/g,
                          (char) =>
                            char.toUpperCase()
                        )}
                    </span>

                    <strong>
                      {typeof value ===
                      "object"
                        ? JSON.stringify(value)
                        : String(value)}
                    </strong>
                  </div>
                )
              )
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Execution Insights</h3>

              <p>
                Latest analytics records
              </p>
            </div>
          </div>

          {analyticsRecords.length === 0 ? (
            <div className="empty-state">
              No analytics records available.
            </div>
          ) : (
            <div className="analytics-records">
              {analyticsRecords
                .slice(0, 10)
                .map((record, index) => (
                  <div
                    className="analytics-record"
                    key={
                      record?.id || index
                    }
                  >
                    <div>
                      <strong>
                        {formatText(
                          record?.workflow_name ||
                            record?.name ||
                            record?.execution_id,
                          "Execution Record"
                        )}
                      </strong>

                      <small>
                        {formatDate(
                          record?.created_at ||
                            record?.timestamp
                        )}
                      </small>
                    </div>

                    <StatusBadge
                      status={
                        record?.status ||
                        record?.result
                      }
                    />
                  </div>
                ))}
            </div>
          )}
        </div>
      </div>
    </section>
  );
}

// ========================================
// AUDIT
// ========================================

function AuditPage({
  sortedAuditLogs,
}) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>Live Audit Activity</h3>

          <p>
            Complete traceable enterprise activity
          </p>
        </div>
      </div>

      <div className="panel full-panel">
        {sortedAuditLogs.length === 0 ? (
          <div className="empty-state">
            No audit logs found.
          </div>
        ) : (
          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>Action</th>

                  <th>Event Type</th>

                  <th>Entity</th>

                  <th>Time</th>
                </tr>
              </thead>

              <tbody>
                {sortedAuditLogs.map(
                  (log, index) => (
                    <tr
                      key={log?.id || index}
                    >
                      <td>
                        {formatText(
                          log?.action
                        )}
                      </td>

                      <td>
                        {formatText(
                          log?.event_type
                        )}
                      </td>

                      <td>
                        {formatText(
                          log?.entity_type
                        )}
                      </td>

                      <td>
                        {formatDate(
                          log?.created_at ||
                            log?.updated_at
                        )}
                      </td>
                    </tr>
                  )
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </section>
  );
}

// ========================================
// MONITORING
// ========================================

function MonitoringPage({
  monitoring,
  systemStatus,
  requests,
  workflows,
  approvals,
  auditLogs,
  activeWorkflows,
  pendingApprovals,
  completedWorkflows,
}) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>System Monitoring</h3>

          <p>
            Real-time platform operational health
          </p>
        </div>

        <StatusBadge
          status={systemStatus}
        />
      </div>

      <div className="monitoring-grid">
        <MonitoringCard
          title="System Status"
          value={systemStatus}
          icon="◉"
        />

        <MonitoringCard
          title="Total Requests"
          value={requests.length}
          icon="◈"
        />

        <MonitoringCard
          title="Active Workflows"
          value={activeWorkflows}
          icon="⚙"
        />

        <MonitoringCard
          title="Completed"
          value={completedWorkflows}
          icon="✓"
        />

        <MonitoringCard
          title="Pending Approvals"
          value={pendingApprovals}
          icon="!"
        />

        <MonitoringCard
          title="Audit Events"
          value={auditLogs.length}
          icon="◷"
        />
      </div>

      <div className="panel full-panel">
        <div className="panel-header">
          <div>
            <h3>Monitoring Details</h3>

            <p>
              Backend monitoring summary
            </p>
          </div>
        </div>

        {!monitoring ||
        Object.keys(monitoring).length === 0 ? (
          <div className="empty-state">
            Monitoring data is unavailable.
          </div>
        ) : (
          <div className="monitoring-details">
            {Object.entries(monitoring).map(
              ([key, value]) => (
                <div
                  className="monitoring-detail"
                  key={key}
                >
                  <span>
                    {key
                      .replaceAll("_", " ")
                      .replace(
                        /\b\w/g,
                        (char) =>
                          char.toUpperCase()
                      )}
                  </span>

                  <strong>
                    {typeof value ===
                    "object"
                      ? JSON.stringify(value)
                      : String(value)}
                  </strong>
                </div>
              )
            )}
          </div>
        )}
      </div>

      <div className="panel full-panel">
        <div className="panel-header">
          <div>
            <h3>Workflow Inventory</h3>

            <p>
              Current workflow execution records
            </p>
          </div>
        </div>

        <WorkflowTable
          workflows={workflows.slice(0, 10)}
        />
      </div>

      <div className="panel full-panel">
        <div className="panel-header">
          <div>
            <h3>Approval Inventory</h3>

            <p>
              Current approval records
            </p>
          </div>
        </div>

        <div className="monitoring-details">
          <div className="monitoring-detail">
            <span>Total Approvals</span>

            <strong>
              {approvals.length}
            </strong>
          </div>

          <div className="monitoring-detail">
            <span>Pending Approvals</span>

            <strong>
              {pendingApprovals}
            </strong>
          </div>
        </div>
      </div>
    </section>
  );
}

function MonitoringCard({
  title,
  value,
  icon,
}) {
  return (
    <div className="monitoring-card">
      <span>{icon}</span>

      <div>
        <small>{title}</small>

        <strong>{value}</strong>
      </div>
    </div>
  );
}

// ========================================
// STATUS BADGE
// ========================================

function StatusBadge({ status }) {
  const normalized =
    normalizeStatus(status);

  return (
    <span
      className={`status-badge ${getStatusClass(
        normalized
      )}`}
    >
      {formatText(status, "Unknown")}
    </span>
  );
}

// ========================================
// REQUEST MODAL
// ========================================

function RequestModal({
  requestForm,
  updateRequestForm,
  handleCreateRequest,
  creatingRequest,
  requestMessage,
  requestMessageType,
  closeRequestModal,
}) {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <div>
            <h3>Create New Request</h3>

            <p>
              Submit an enterprise automation
              request
            </p>
          </div>

          <button
            type="button"
            className="modal-close"
            onClick={closeRequestModal}
          >
            ×
          </button>
        </div>

        <form
          className="request-form"
          onSubmit={handleCreateRequest}
        >
          {requestMessage && (
            <div
              className={
                requestMessageType === "error"
                  ? "form-message form-error"
                  : "form-message form-success"
              }
            >
              {requestMessage}
            </div>
          )}

          <div className="form-group">
            <label>Request Title</label>

            <input
              type="text"
              placeholder="Enter request title"
              value={requestForm.title}
              onChange={(event) =>
                updateRequestForm(
                  "title",
                  event.target.value
                )
              }
              required
            />
          </div>

          <div className="form-group">
            <label>Description</label>

            <textarea
              placeholder="Describe the request..."
              value={
                requestForm.description
              }
              onChange={(event) =>
                updateRequestForm(
                  "description",
                  event.target.value
                )
              }
              required
            />
          </div>

          <div className="request-options">
            <div className="form-group">
              <label>Request Type</label>

              <select
                value={
                  requestForm.request_type
                }
                onChange={(event) =>
                  updateRequestForm(
                    "request_type",
                    event.target.value
                  )
                }
              >
                <option value="general">
                  General
                </option>

                <option value="automation">
                  Automation
                </option>

                <option value="research">
                  Research
                </option>

                <option value="document">
                  Document
                </option>
              </select>
            </div>

            <div className="form-group">
              <label>Priority</label>

              <select
                value={
                  requestForm.priority
                }
                onChange={(event) =>
                  updateRequestForm(
                    "priority",
                    event.target.value
                  )
                }
              >
                <option value="low">
                  Low
                </option>

                <option value="medium">
                  Medium
                </option>

                <option value="high">
                  High
                </option>

                <option value="urgent">
                  Urgent
                </option>
              </select>
            </div>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={closeRequestModal}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={creatingRequest}
            >
              {creatingRequest
                ? "Creating..."
                : "Create Request"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ========================================
// JOB MODAL
// ========================================

function JobModal({
  jobForm,
  setJobForm,
  handleScheduleJob,
  schedulingJob,
  closeJobModal,
}) {
  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <div>
            <h3>
              Schedule Background Job
            </h3>

            <p>
              Create a new background execution
            </p>
          </div>

          <button
            type="button"
            className="modal-close"
            onClick={closeJobModal}
          >
            ×
          </button>
        </div>

        <form
          className="request-form"
          onSubmit={handleScheduleJob}
        >
          <div className="form-group">
            <label>Job Name</label>

            <input
              type="text"
              placeholder="Enter job name"
              value={jobForm.name}
              onChange={(event) =>
                setJobForm((previous) => ({
                  ...previous,
                  name: event.target.value,
                }))
              }
              required
            />
          </div>

          <div className="form-group">
            <label>Job Type</label>

            <select
              value={jobForm.job_type}
              onChange={(event) =>
                setJobForm((previous) => ({
                  ...previous,
                  job_type:
                    event.target.value,
                }))
              }
            >
              <option value="workflow">
                Workflow
              </option>

              <option value="automation">
                Automation
              </option>

              <option value="processing">
                Processing
              </option>
            </select>
          </div>

          <div className="form-group">
            <label>
              Payload JSON (Optional)
            </label>

            <textarea
              placeholder='{"key":"value"}'
              value={jobForm.payload}
              onChange={(event) =>
                setJobForm((previous) => ({
                  ...previous,
                  payload: event.target.value,
                }))
              }
            />
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="secondary-button"
              onClick={closeJobModal}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={schedulingJob}
            >
              {schedulingJob
                ? "Scheduling..."
                : "Schedule Job"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default App;