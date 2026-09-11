# AURIXA Architecture Documentation

## 1. High-Level Architecture Diagram

```mermaid
flowchart TB
    User[User]
    Frontend[React Frontend]
    API[FastAPI Backend]
    
    Auth[Authentication]
    Agents[AI Agents]
    Workflows[Workflow Engine]
    Approvals[Human Approval]
    Tools[Tool Runtime]
    RAG[RAG / Knowledge Base]
    Documents[Document Processing]
    Monitoring[Monitoring & Analytics]
    
    DB[(SQLite Database)]
    VectorDB[(ChromaDB)]
    Email[Brevo Email Service]

    User --> Frontend
    Frontend --> API

    API --> Auth
    API --> Agents
    API --> Workflows
    API --> Approvals
    API --> Documents
    API --> Monitoring

    Agents --> RAG
    Agents --> Tools
    Agents --> Workflows

    Workflows --> Approvals
    Workflows --> Tools

    Documents --> RAG
    RAG --> VectorDB

    API --> DB
    Workflows --> DB
    Approvals --> DB
    Monitoring --> DB

    Tools --> Email
```

---

# 2. Component Architecture

```mermaid
flowchart LR
    API[API Layer]

    API --> AuthAPI[Authentication API]
    API --> AgentAPI[Agents API]
    API --> WorkflowAPI[Workflow API]
    API --> ApprovalAPI[Approval API]
    API --> DocumentAPI[Document API]
    API --> ToolAPI[Tools API]
    API --> MonitoringAPI[Monitoring API]

    AgentAPI --> Orchestrator[AI Orchestrator]

    Orchestrator --> Classifier[Classifier Agent]
    Orchestrator --> Automation[Automation Agent]
    Orchestrator --> DocumentAgent[Document Agent]
    Orchestrator --> ResearchAgent[Research Agent]
    Orchestrator --> ValidationAgent[Validation Agent]

    Orchestrator --> Policies[Policy Engine]
    Orchestrator --> Tools[Tool Runtime]
    Orchestrator --> RAG[RAG System]

    WorkflowAPI --> Engine[Workflow Engine]
    Engine --> Tasks[Workflow Tasks]
    Engine --> ApprovalService[Approval Service]

    API --> Database[(Database)]
```

---

# 3. Agent Communication Diagram

```mermaid
sequenceDiagram
    participant U as User
    participant API as FastAPI API
    participant O as AI Orchestrator
    participant C as Classifier Agent
    participant A as Automation Agent
    participant D as Document Agent
    participant R as Research Agent
    participant V as Validation Agent

    U->>API: Submit Request
    API->>O: orchestrate_request()

    O->>C: classify_request()
    C-->>O: Request Type + Confidence

    O->>A: decide_automation()
    A-->>O: Automation Decision

    alt Invoice Processing
        O->>D: analyze_document()
        D-->>O: Extracted Fields
    end

    alt Knowledge Query
        O->>R: research_knowledge()
        R-->>O: Knowledge Context
    end

    O->>V: validate_result()
    V-->>O: Validation Result

    O-->>API: Final Decision
    API-->>U: Response
```

---

# 4. RAG Data Flow Diagram

```mermaid
flowchart LR
    Document[Uploaded Document]
    Extract[PDF/Text Extraction]
    Chunk[Text Chunking]
    Embed[Embedding Generation]
    VectorDB[(ChromaDB)]

    Query[User Query]
    Search[Similarity Search]
    Context[Relevant Context]
    Research[Research Agent]
    Answer[Final Response]

    Document --> Extract
    Extract --> Chunk
    Chunk --> Embed
    Embed --> VectorDB

    Query --> Search
    Search --> VectorDB
    VectorDB --> Context
    Context --> Research
    Research --> Answer
```

---

# 5. Workflow Execution Diagram

```mermaid
flowchart TD
    Start[Create Request]
    Create[Create Workflow Execution]
    Pending[Pending]
    Running[Running]
    Task[Create Workflow Task]
    Execute[Execute AI Workflow]
    Validate[Validate Result]
    Approval{Approval Required?}
    Complete[Completed]
    Failed[Failed]

    Start --> Create
    Create --> Pending
    Pending --> Running
    Running --> Task
    Task --> Execute
    Execute --> Validate
    Validate --> Approval

    Approval -->|No| Complete
    Approval -->|Yes| HumanApproval[Waiting for Human Approval]

    HumanApproval --> Approved{Approved?}
    Approved -->|Yes| Complete
    Approved -->|No| Failed
```

---

# 6. Human Approval Diagram

```mermaid
sequenceDiagram
    participant AI as AI Workflow
    participant P as Policy Engine
    participant A as Approval Service
    participant H as Human Reviewer
    participant W as Workflow Engine

    AI->>P: Evaluate Result
    P-->>AI: Approval Required

    AI->>A: Create Approval Request
    A->>H: Notify Reviewer

    H->>A: Approve / Reject

    alt Approved
        A->>W: Continue Workflow
        W->>W: Complete Execution
    else Rejected
        A->>W: Stop Workflow
        W->>W: Mark Failed / Rejected
    end
```

---

# 7. Data Lifecycle Diagram

```mermaid
flowchart LR
    Input[User Request / Document]
    Validate[Prompt & Input Validation]
    Store[Database Storage]
    Process[AI Processing]
    Workflow[Workflow Execution]
    Approval[Human Approval]
    Result[Final Result]
    Audit[Audit Log]
    Monitor[Monitoring & Analytics]

    Input --> Validate
    Validate --> Store
    Store --> Process
    Process --> Workflow
    Workflow --> Approval
    Approval --> Result

    Workflow --> Audit
    Result --> Audit
    Audit --> Monitor
```

---

# Architecture Summary

AURIXA is an Autonomous Enterprise AI Platform built with:

- **Frontend:** React + Vite
- **Backend:** FastAPI
- **Database:** SQLite with SQLAlchemy Async
- **AI Architecture:** Multi-Agent Orchestration
- **RAG:** ChromaDB Knowledge Retrieval
- **Workflow Engine:** Custom asynchronous workflow execution
- **Human-in-the-Loop:** Approval system
- **Email Notifications:** Brevo
- **Security:** Prompt validation and authentication
- **Monitoring:** Request, workflow, and approval monitoring
- **Auditability:** Audit logs and workflow execution tracking