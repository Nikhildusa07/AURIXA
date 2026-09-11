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

  if (Array.isArray(data?.items)) {
    return data.items;
  }

  if (Array.isArray(data?.data)) {
    return data.data;
  }

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

  if (typeof recommendation === "string") {
    return recommendation;
  }

  if (typeof recommendation === "number") {
    return String(recommendation);
  }

  if (Array.isArray(recommendation)) {
    if (!recommendation.length) {
      return "No AI recommendation available.";
    }

    return recommendation
      .map((item) => {
        if (typeof item === "object") {
          return Object.values(item).join(" • ");
        }

        return String(item);
      })
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

  const [email, setEmail] = useState("");
  const [password, setPassword] =
    useState("");

  const [loginError, setLoginError] =
    useState("");

  const [loggingIn, setLoggingIn] =
    useState(false);

  const [monitoring, setMonitoring] =
    useState(null);

  const [requests, setRequests] = useState([]);

  const [workflows, setWorkflows] =
    useState([]);

  const [approvals, setApprovals] =
    useState([]);

  const [auditLogs, setAuditLogs] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] = useState("");

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

        const failedResults = results.filter(
          (result) =>
            result.status === "rejected"
        );

        if (failedResults.length > 0) {
          setError(
            "Some platform data could not be loaded. Please check the backend API."
          );
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

    return () => {
      clearInterval(interval);
    };
  }, [
    token,
    autoRefresh,
    loadDashboard,
  ]);

  // ========================================
  // CLEANUP TIMEOUT
  // ========================================

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
  // LOGIN
  // ========================================

  const handleLogin = async (event) => {
    event.preventDefault();

    try {
      setLoggingIn(true);
      setLoginError("");

      const response = await api.post(
        "/auth/login",
        {
          email: String(
            email || ""
          ).trim(),
          password: String(password || ""),
        }
      );

      const accessToken =
        response?.data?.access_token;

      if (!accessToken) {
        throw new Error(
          "No access token received from server."
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
          "Login failed. Check your credentials."
        )
      );
    } finally {
      setLoggingIn(false);
    }
  };

  // ========================================
  // LOGOUT
  // ========================================

  const handleLogout = () => {
    localStorage.removeItem(
      "access_token"
    );

    setToken(null);
    setMonitoring(null);
    setRequests([]);
    setWorkflows([]);
    setApprovals([]);
    setAuditLogs([]);

    setActivePage("dashboard");

    setError("");
    setLastUpdated(null);
    setAutoRefresh(false);

    setDashboardSearch("");
    setDashboardWorkflowFilter("all");

    setShowRequestModal(false);
  };

  // ========================================
  // CLOSE REQUEST MODAL
  // ========================================

  const closeRequestModal = () => {
    setShowRequestModal(false);

    setRequestMessage("");
    setRequestMessageType("");

    setRequestForm({
      title: "",
      description: "",
      request_type: "general",
      priority: "medium",
    });
  };

  // ========================================
  // CREATE REQUEST
  // ========================================

  const handleCreateRequest = async (
    event
  ) => {
    event.preventDefault();

    try {
      setCreatingRequest(true);
      setRequestMessage("");
      setRequestMessageType("");

      const payload = {
        title: String(
          requestForm.title || ""
        ).trim(),

        content: String(
          requestForm.description || ""
        ).trim(),

        request_type:
          requestForm.request_type,

        priority:
          requestForm.priority,
      };

      if (!payload.title || !payload.content) {
        throw new Error(
          "Title and description are required."
        );
      }

      await api.post(
        "/requests",
        payload
      );

      setRequestMessage(
        "Request created successfully."
      );

      setRequestMessageType("success");

      await loadDashboard(false);

      requestModalTimeoutRef.current =
        setTimeout(() => {
          closeRequestModal();
        }, 1000);
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
  // APPROVAL ACTIONS
  // ========================================

  const handleApproval = async (
    approvalId,
    action
  ) => {
    const message =
      action === "approved"
        ? "Approve this workflow?"
        : "Reject this workflow?";

    const confirmed =
      window.confirm(message);

    if (!confirmed) {
      return;
    }

    const comment =
      window.prompt(
        action === "approved"
          ? "Optional approval comment:"
          : "Optional rejection reason:"
      ) || "";

    try {
      setApprovalActionLoading(
        String(approvalId)
      );

      if (action === "approved") {
        await approveApproval(
          approvalId,
          comment
        );
      } else {
        await rejectApproval(
          approvalId,
          comment
        );
      }

      await loadDashboard(false);
    } catch (err) {
      alert(
        getErrorMessage(
          err,
          `Failed to ${action} approval.`
        )
      );
    } finally {
      setApprovalActionLoading("");
    }
  };

  // ========================================
  // FORM UPDATE
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

  // ========================================
  // STATISTICS
  // IMPORTANT:
  // ALL HOOKS MUST BE BEFORE CONDITIONAL RETURN
  // ========================================

  const completedWorkflows =
    workflows.filter(
      (workflow) =>
        normalizeStatus(
          workflow?.status
        ) === "completed"
    ).length;

  const failedWorkflows =
    workflows.filter((workflow) => {
      const status = normalizeStatus(
        workflow?.status
      );

      return [
        "failed",
        "error",
        "cancelled",
        "canceled",
      ].includes(status);
    }).length;

  const pendingApprovals =
    approvals.filter(
      (approval) =>
        normalizeStatus(
          approval?.status
        ) === "pending"
    ).length;

  const pendingRequests =
    requests.filter(
      (request) =>
        normalizeStatus(
          request?.status
        ) === "pending"
    ).length;

  const activeWorkflows =
    workflows.filter((workflow) => {
      const status = normalizeStatus(
        workflow?.status
      );

      return [
        "running",
        "processing",
        "in-progress",
        "in_progress",
        "active",
      ].includes(status);
    }).length;

  const successRate =
    workflows.length > 0
      ? Math.round(
          (completedWorkflows /
            workflows.length) *
            100
        )
      : 0;

  const systemStatus =
    monitoring?.status ||
    monitoring?.system_status ||
    "Operational";

  const sortedWorkflows = useMemo(
    () => sortByLatest(workflows),
    [workflows]
  );

  const sortedRequests = useMemo(
    () => sortByLatest(requests),
    [requests]
  );

  const sortedAuditLogs = useMemo(
    () => sortByLatest(auditLogs),
    [auditLogs]
  );

  const filteredDashboardWorkflows =
    useMemo(() => {
      const search = dashboardSearch
        .toLowerCase()
        .trim();

      return sortedWorkflows.filter(
        (workflow) => {
          const status = normalizeStatus(
            workflow?.status
          );

          const workflowName =
            getWorkflowName(
              workflow
            ).toLowerCase();

          const workflowStep =
            String(
              getWorkflowStep(workflow)
            ).toLowerCase();

          const matchesSearch =
            !search ||
            workflowName.includes(search) ||
            status.includes(search) ||
            workflowStep.includes(search);

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
  // LOGIN PAGE
  // ========================================

  if (!token) {
    return (
      <div className="login-page">
        <form
          className="login-card"
          onSubmit={handleLogin}
        >
          <div className="login-brand-icon">
            A
          </div>

          <h1>AURIXA</h1>

          <p>
            Sign in to the Enterprise AI Platform
          </p>

          {loginError && (
            <div className="error-box">
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
        </form>
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

              {activePage === "approvals" &&
                "Approval Center"}

              {activePage === "audit" &&
                "Audit Logs"}

              {activePage === "monitoring" &&
                "System Monitoring"}
            </h2>

            {activePage === "dashboard" &&
              lastUpdated && (
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
                loadDashboard()
              }
              disabled={loading}
            >
              {loading
                ? "Loading..."
                : "↻ Refresh"}
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

        {error && (
          <div className="error-box">
            <span>{error}</span>

            <button
              type="button"
              onClick={() =>
                loadDashboard()
              }
            >
              Retry
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading">
            Loading AURIXA...
          </div>
        ) : (
          <>
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
                  filteredDashboardWorkflows
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
              <section className="page-content">
                <div className="page-heading">
                  <div>
                    <h3>
                      Enterprise Requests
                    </h3>

                    <p>
                      Create and manage automation
                      requests
                    </p>
                  </div>

                  <button
                    type="button"
                    className="create-button"
                    onClick={() =>
                      setShowRequestModal(true)
                    }
                  >
                    + Create Request
                  </button>
                </div>

                {sortedRequests.length === 0 ? (
                  <div className="empty-page">
                    <h3>No Requests Yet</h3>

                    <p>
                      Create your first enterprise
                      automation request.
                    </p>

                    <button
                      type="button"
                      className="create-button"
                      onClick={() =>
                        setShowRequestModal(true)
                      }
                    >
                      + Create Request
                    </button>
                  </div>
                ) : (
                  <div className="requests-grid">
                    {sortedRequests.map(
                      (request, index) => (
                        <RequestCard
                          key={
                            request?.id ||
                            request?.request_id ||
                            index
                          }
                          request={request}
                          index={index}
                        />
                      )
                    )}
                  </div>
                )}
              </section>
            )}

            {activePage === "workflows" && (
              <section className="page-content">
                <div className="page-heading">
                  <div>
                    <h3>
                      Workflow Executions
                    </h3>

                    <p>
                      Monitor all AI workflow
                      processing
                    </p>
                  </div>

                  <span className="large-count">
                    {workflows.length}
                  </span>
                </div>

                <div className="panel full-panel">
                  <WorkflowTable
                    workflows={sortedWorkflows}
                  />
                </div>
              </section>
            )}

            {activePage === "approvals" && (
              <section className="page-content">
                <div className="page-heading">
                  <div>
                    <h3>
                      Human Approval Center
                    </h3>

                    <p>
                      Review AI decisions and approve
                      or reject workflow execution
                    </p>
                  </div>

                  <span className="large-count">
                    {pendingApprovals}
                  </span>
                </div>

                {approvals.length === 0 ? (
                  <div className="empty-page">
                    <h3>
                      No Approvals Found
                    </h3>

                    <p>
                      Workflows requiring human
                      decisions will appear here.
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
            )}

            {activePage === "audit" && (
              <section className="page-content">
                <div className="page-heading">
                  <div>
                    <h3>
                      Live Audit Activity
                    </h3>

                    <p>
                      Complete traceable enterprise
                      activity
                    </p>
                  </div>
                </div>

                <div className="panel full-panel">
                  {sortedAuditLogs.length ===
                  0 ? (
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
                                key={
                                  log?.id ||
                                  index
                                }
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
          requestMessage={
            requestMessage
          }
          requestMessageType={
            requestMessageType
          }
          closeRequestModal={
            closeRequestModal
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
// DASHBOARD PAGE
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
        <div className="panel dashboard-performance-panel">
          <div className="panel-header">
            <div>
              <h3>
                Automation Performance
              </h3>

              <p>
                Workflow execution health
              </p>
            </div>

            <span className="panel-count">
              {successRate}%
            </span>
          </div>

          <div className="performance-grid">
            <div className="performance-item">
              <span>Success Rate</span>

              <strong>
                {successRate}%
              </strong>

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

            <div className="performance-item">
              <span>Running</span>
              <strong>
                {activeWorkflows}
              </strong>
            </div>
          </div>
        </div>

        <div className="panel quick-actions-panel">
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
              onClick={() => {
                setActivePage("requests");
                setShowRequestModal(true);
              }}
            >
              <span>＋</span>

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
                <strong>
                  System Health
                </strong>

                <small>
                  Check monitoring
                </small>
              </div>
            </button>
          </div>
        </div>
      </div>

      <div className="panel full-panel">
        <div className="panel-header">
          <div>
            <h3>
              Recent Workflow Activity
            </h3>

            <p>
              Search and monitor the latest
              automation executions
            </p>
          </div>

          <button
            type="button"
            className="view-all-button"
            onClick={() =>
              setActivePage("workflows")
            }
          >
            View All
          </button>
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
            value={dashboardWorkflowFilter}
            onChange={(event) =>
              setDashboardWorkflowFilter(
                event.target.value
              )
            }
          >
            <option value="all">
              All Status
            </option>

            <option value="running">
              Running
            </option>

            <option value="processing">
              Processing
            </option>

            <option value="completed">
              Completed
            </option>

            <option value="failed">
              Failed
            </option>

            <option value="cancelled">
              Cancelled
            </option>
          </select>
        </div>

        <WorkflowTable
          workflows={
            filteredWorkflows.slice(0, 6)
          }
        />
      </div>

      <div className="dashboard-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Pending Approvals</h3>

              <p>
                Human decisions required
              </p>
            </div>

            <button
              type="button"
              className="panel-count panel-count-button"
              onClick={() =>
                setActivePage("approvals")
              }
            >
              {pendingApprovals}
            </button>
          </div>

          <div className="mini-list">
            {dashboardPendingApprovals.map(
              (approval, index) => {
                const isLoading =
                  approvalActionLoading ===
                  String(approval?.id);

                return (
                  <div
                    className="dashboard-approval-item"
                    key={
                      approval?.id || index
                    }
                  >
                    <div className="mini-item">
                      <div>
                        <strong>
                          {approval.reason ||
                            "Workflow requires review"}
                        </strong>

                        <span>
                          {formatRecommendation(
                            approval.recommendation
                          )}
                        </span>
                      </div>

                      <StatusBadge
                        status={
                          approval.status
                        }
                      />
                    </div>

                    <div className="dashboard-approval-actions">
                      <button
                        type="button"
                        className="small-reject-button"
                        disabled={isLoading}
                        onClick={() =>
                          handleApproval(
                            approval.id,
                            "rejected"
                          )
                        }
                      >
                        Reject
                      </button>

                      <button
                        type="button"
                        className="small-approve-button"
                        disabled={isLoading}
                        onClick={() =>
                          handleApproval(
                            approval.id,
                            "approved"
                          )
                        }
                      >
                        {isLoading
                          ? "Processing..."
                          : "Approve"}
                      </button>
                    </div>
                  </div>
                );
              }
            )}

            {pendingApprovals === 0 && (
              <div className="empty-state">
                No pending approvals.
              </div>
            )}
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div>
              <h3>Recent Requests</h3>

              <p>
                Latest enterprise requests
              </p>
            </div>

            <button
              type="button"
              className="view-all-button"
              onClick={() =>
                setActivePage("requests")
              }
            >
              View All
            </button>
          </div>

          <div className="mini-list">
            {recentRequests.map(
              (request, index) => (
                <button
                  type="button"
                  className="mini-item mini-item-button"
                  key={
                    request?.id ||
                    request?.request_id ||
                    index
                  }
                  onClick={() =>
                    setActivePage("requests")
                  }
                >
                  <div>
                    <strong>
                      {request?.title ||
                        "Untitled Request"}
                    </strong>

                    <span>
                      {formatText(
                        request?.request_type,
                        "General"
                      )}{" "}
                      •{" "}
                      {formatText(
                        request?.priority,
                        "Medium"
                      )}
                    </span>
                  </div>

                  <StatusBadge
                    status={request?.status}
                  />
                </button>
              )
            )}

            {recentRequests.length === 0 && (
              <div className="empty-state">
                No requests found.
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="panel full-panel">
        <div className="panel-header">
          <div>
            <h3>Live Activity Feed</h3>

            <p>
              Latest traceable platform events
            </p>
          </div>

          <button
            type="button"
            className="view-all-button"
            onClick={() =>
              setActivePage("audit")
            }
          >
            Audit Logs
          </button>
        </div>

        {recentAuditActivity.length === 0 ? (
          <div className="empty-state">
            No recent activity found.
          </div>
        ) : (
          <div className="activity-feed">
            {recentAuditActivity.map(
              (log, index) => (
                <div
                  className="activity-item"
                  key={log?.id || index}
                >
                  <div className="activity-icon">
                    ◷
                  </div>

                  <div className="activity-content">
                    <strong>
                      {formatText(
                        log?.action,
                        "Platform activity"
                      )}
                    </strong>

                    <span>
                      {formatText(
                        log?.event_type,
                        "System Event"
                      )}{" "}
                      •{" "}
                      {formatText(
                        log?.entity_type,
                        "Platform"
                      )}
                    </span>
                  </div>

                  <time>
                    {formatDate(
                      log?.created_at ||
                        log?.updated_at
                    )}
                  </time>
                </div>
              )
            )}
          </div>
        )}
      </div>
    </section>
  );
}

// ========================================
// DASHBOARD STAT
// ========================================

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
      className="stat-card stat-card-button"
      onClick={onClick}
    >
      <div className="stat-icon">
        {icon}
      </div>

      <div>
        <p>{title}</p>

        <h3>{value}</h3>

        <span>{subtitle}</span>
      </div>
    </button>
  );
}

// ========================================
// REQUEST CARD
// ========================================

function RequestCard({
  request,
  index,
}) {
  return (
    <div className="request-card">
      <div className="request-card-top">
        <div className="request-number">
          REQUEST{" "}
          {String(index + 1).padStart(
            2,
            "0"
          )}
        </div>

        <StatusBadge
          status={request?.status}
        />
      </div>

      <h3>
        {request?.title ||
          "Untitled Request"}
      </h3>

      <p className="request-description">
        {request?.content ||
          request?.description ||
          "No description available."}
      </p>

      <div className="request-meta">
        <div>
          <span>Type</span>

          <strong>
            {formatText(
              request?.request_type,
              "General"
            )}
          </strong>
        </div>

        <div>
          <span>Priority</span>

          <strong className="priority-text">
            {formatText(
              request?.priority,
              "Medium"
            )}
          </strong>
        </div>
      </div>

      <div className="request-footer">
        <span>
          Created:{" "}
          {formatDate(
            request?.created_at
          )}
        </span>
      </div>
    </div>
  );
}

// ========================================
// APPROVAL CARD
// ========================================

function ApprovalCard({
  approval,
  approvalActionLoading,
  handleApproval,
}) {
  const isPending =
    normalizeStatus(
      approval?.status
    ) === "pending";

  const isLoading =
    approvalActionLoading ===
    String(approval?.id);

  return (
    <div className="approval-card">
      <div className="approval-card-header">
        <div>
          <span className="approval-label">
            HUMAN REVIEW
          </span>

          <h3>
            Workflow Approval
          </h3>
        </div>

        <StatusBadge
          status={approval?.status}
        />
      </div>

      <div className="approval-section">
        <span>
          Why approval is required
        </span>

        <p>
          {approval?.reason ||
            "This AI workflow requires human review before continuing."}
        </p>
      </div>

      <div className="approval-section">
        <span>
          AI Recommendation
        </span>

        <p className="recommendation-text">
          {formatRecommendation(
            approval?.recommendation
          )}
        </p>
      </div>

      <div className="approval-section approval-workflow-id">
        <span>
          Workflow Execution
        </span>

        <p>
          {approval?.workflow_execution_id ||
            "-"}
        </p>
      </div>

      {approval?.reviewer_comment && (
        <div className="approval-section">
          <span>
            Reviewer Comment
          </span>

          <p>
            {approval.reviewer_comment}
          </p>
        </div>
      )}

      {isPending ? (
        <div className="approval-actions">
          <button
            type="button"
            className="reject-button"
            disabled={isLoading}
            onClick={() =>
              handleApproval(
                approval.id,
                "rejected"
              )
            }
          >
            {isLoading
              ? "Processing..."
              : "Reject"}
          </button>

          <button
            type="button"
            className="approve-button"
            disabled={isLoading}
            onClick={() =>
              handleApproval(
                approval.id,
                "approved"
              )
            }
          >
            {isLoading
              ? "Processing..."
              : "Approve"}
          </button>
        </div>
      ) : (
        <div className="approval-decision">
          <strong>
            Decision completed
          </strong>

          {approval?.reviewed_at && (
            <span>
              {formatDate(
                approval.reviewed_at
              )}
            </span>
          )}
        </div>
      )}
    </div>
  );
}

// ========================================
// MONITORING PAGE
// ========================================

function MonitoringPage({
  monitoring,
  systemStatus,
  requests,
  activeWorkflows,
  pendingApprovals,
  completedWorkflows,
  auditLogs,
}) {
  return (
    <section className="page-content">
      <div className="page-heading">
        <div>
          <h3>System Monitoring</h3>

          <p>
            Platform health and operational
            metrics
          </p>
        </div>
      </div>

      <div className="monitoring-grid">
        <MonitorCard
          title="System Status"
          value={systemStatus}
          description="Current platform health"
          healthy
        />

        <MonitorCard
          title="Total Requests"
          value={
            monitoring?.total_requests ??
            requests.length
          }
          description="Requests in the platform"
        />

        <MonitorCard
          title="Active Workflows"
          value={
            monitoring?.active_workflows ??
            activeWorkflows
          }
          description="Currently running workflows"
        />

        <MonitorCard
          title="Pending Reviews"
          value={
            monitoring?.pending_approvals ??
            pendingApprovals
          }
          description="Awaiting human decisions"
        />

        <MonitorCard
          title="Completed Workflows"
          value={
            monitoring?.completed_workflows ??
            completedWorkflows
          }
          description="Successfully completed"
        />

        <MonitorCard
          title="Total Audit Events"
          value={
            monitoring?.total_audit_logs ??
            auditLogs.length
          }
          description="Recorded platform activity"
        />
      </div>

      <div className="panel full-panel">
        <div className="panel-header">
          <div>
            <h3>
              Monitoring Summary
            </h3>

            <p>
              Live information returned by the
              AURIXA monitoring service
            </p>
          </div>
        </div>

        <MonitoringDetails
          monitoring={monitoring}
        />
      </div>
    </section>
  );
}

// ========================================
// MONITOR CARD
// ========================================

function MonitorCard({
  title,
  value,
  description,
  healthy = false,
}) {
  return (
    <div className="monitor-card">
      <p className="monitor-card-title">
        {title}
      </p>

      <h3
        className={
          healthy
            ? "healthy-status"
            : ""
        }
      >
        {value}
      </h3>

      <span>{description}</span>
    </div>
  );
}

// ========================================
// MONITORING DETAILS
// ========================================

function MonitoringDetails({
  monitoring,
}) {
  const data =
    monitoring &&
    typeof monitoring === "object"
      ? monitoring
      : {};

  const entries =
    Object.entries(data);

  if (!entries.length) {
    return (
      <div className="empty-state">
        Monitoring information is not available.
      </div>
    );
  }

  return (
    <div className="monitoring-details">
      {entries.map(
        ([key, value]) => {
          const label = key
            .replaceAll("_", " ")
            .replace(
              /\b\w/g,
              (char) =>
                char.toUpperCase()
            );

          let displayValue;

          if (
            value === null ||
            value === undefined
          ) {
            displayValue = "-";
          } else if (
            typeof value === "object"
          ) {
            displayValue =
              formatRecommendation(value);
          } else {
            displayValue = String(value);
          }

          return (
            <div
              className="monitoring-detail-item"
              key={key}
            >
              <span>{label}</span>

              <strong>
                {displayValue}
              </strong>
            </div>
          );
        }
      )}
    </div>
  );
}

// ========================================
// WORKFLOW TABLE
// ========================================

function WorkflowTable({
  workflows,
}) {
  if (!workflows?.length) {
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
            <th>Created</th>
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
                    status={
                      workflow?.status
                    }
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
      <div className="modal request-modal">
        <div className="modal-header">
          <div>
            <span className="modal-label">
              NEW AUTOMATION
            </span>

            <h2>
              Create Enterprise Request
            </h2>

            <p>
              Tell AURIXA what you want to
              automate.
            </p>
          </div>

          <button
            type="button"
            className="close-button"
            onClick={closeRequestModal}
          >
            ×
          </button>
        </div>

        <form
          onSubmit={handleCreateRequest}
          className="request-form"
        >
          {requestMessage && (
            <div
              className={`form-message ${
                requestMessageType === "error"
                  ? "form-error"
                  : "form-success"
              }`}
            >
              {requestMessage}
            </div>
          )}

          <div className="form-group">
            <label>
              Request Title
            </label>

            <input
              type="text"
              placeholder="Example: Generate monthly sales report"
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
            <label>
              What should AURIXA do?
            </label>

            <textarea
              placeholder="Describe the task, expected result, and important requirements..."
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
              <label>
                Request Type
              </label>

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

                <option value="analysis">
                  Analysis
                </option>

                <option value="document">
                  Document Processing
                </option>
              </select>
            </div>

            <div className="form-group">
              <label>Priority</label>

              <select
                value={requestForm.priority}
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

                <option value="critical">
                  Critical
                </option>
              </select>
            </div>
          </div>

          <div className="modal-actions">
            <button
              type="button"
              className="cancel-button"
              onClick={closeRequestModal}
              disabled={creatingRequest}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="create-button"
              disabled={creatingRequest}
            >
              {creatingRequest
                ? "Creating Request..."
                : "Create Request"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// ========================================
// STATUS BADGE
// ========================================

function StatusBadge({ status }) {
  const normalizedStatus =
    getStatusClass(status);

  return (
    <span
      className={`status-badge ${normalizedStatus}`}
    >
      {formatText(status, "unknown")}
    </span>
  );
}

export default App;