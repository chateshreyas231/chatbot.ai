# IT Helpdesk Copilot - Architecture & Setup Guide

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [System Components](#system-components)
3. [Data Flow](#data-flow)
4. [Technology Stack](#technology-stack)
5. [Project Structure](#project-structure)
6. [File Reference](#file-reference)
7. [Environment Setup](#environment-setup)
8. [Quick Start Guide](#quick-start-guide)
9. [Configuration](#configuration)
10. [Security Guidelines](#security-guidelines)
11. [Deployment](#deployment)
12. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The IT Helpdesk Copilot is an AI-powered support assistant that combines:
- **RAG (Retrieval Augmented Generation)** for knowledge base queries
- **LLM-powered orchestration** for intent classification and response generation
- **Integrations** with ServiceNow, Jira, and M365 for ticket management
- **Agentic workflows** using LangGraph for intelligent routing

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Browser                          │
│                    (Port 3000/3003)                          │
└────────────────────────┬──────────────────────────────────────┘
                         │ HTTP/HTTPS
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    Next.js Frontend                          │
│  • React Components                                           │
│  • Tailwind CSS (White Theme with Animations)               │
│  • ChatWidget, LoginForm                                     │
└────────────────────────┬──────────────────────────────────────┘
                         │ REST API
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Backend                           │
│                    (Port 8000)                               │
│  • /chat - Main chat endpoint                               │
│  • /health - Health check                                   │
│  • /sessions - Session management                           │
│  • Authentication middleware                                │
└────────────────────────┬──────────────────────────────────────┘
                         │
                         ├──► LangGraph Orchestrator
                         │    ├── Intent Classification
                         │    ├── Knowledge Handler
                         │    ├── Ticket Handler
                         │    └── Password Reset Handler
                         │
                         ├──► MongoDB Atlas
                         │    ├── it_helpdesk DB
                         │    │   ├── users
                         │    │   ├── sessions
                         │    │   ├── messages
                         │    │   ├── tickets
                         │    │   ├── kb_docs
                         │    │   ├── kb_chunks (Vector Search)
                         │    │   └── audit_logs
                         │    └── sample_mflix DB (Movies)
                         │
                         ├──► OpenAI API
                         │    ├── GPT-4o-mini (LLM)
                         │    └── text-embedding-3-large (Embeddings)
                         │
                         ├──► External Integrations
                         │    ├── ServiceNow (Tickets)
                         │    ├── Jira (Tickets)
                         │    └── M365 Graph (Password Reset)
                         │
                         └──► n8n (Automation)
                              ├── Webhook: ticket-created
                              └── Webhook: escalate
```

### Component Interaction Flow

```
User Query
    │
    ▼
Frontend (ChatWidget)
    │
    ▼ HTTP POST /chat
Backend (FastAPI)
    │
    ▼
Orchestrator (LangGraph)
    │
    ├─► Classify Intent (knowledge/ticket/password_reset)
    │
    ├─► Knowledge Query:
    │   ├─ Check if movie query → MflixRetriever → sample_mflix DB
    │   ├─ Try KB Vector Search → MongoDB Atlas Vector Search
    │   └─ If empty → Fallback to OpenAI (generic IT helpdesk answer)
    │
    ├─► Ticket Creation:
    │   ├─ Extract ticket fields (LLM)
    │   ├─ Create ticket (ServiceNow/Jira/Mock)
    │   └─ Notify n8n webhook
    │
    └─► Response Generation:
        ├─ Synthesize answer from KB chunks + LLM
        └─ Return to user
```

---

## System Components

### 1. Frontend (Next.js 14)

**Location**: `apps/web/`

**Components**:
- `app/page.tsx` - Main page with white theme and animated background
- `components/ChatWidget.tsx` - Chat interface with message history
- `components/LoginForm.tsx` - Authentication form (currently disabled for demo)

**Features**:
- Clean white UI with subtle animations
- Real-time chat interface
- Session management
- Error handling with detailed messages

**Tech Stack**:
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Lucide React (icons)

### 2. Backend (FastAPI)

**Location**: `apps/api/`

**Key Files**:
- `main.py` - FastAPI application, routes, middleware
- `config.py` - Configuration management, environment variables
- `auth.py` - Authentication utilities (currently simplified for demo)
- `db/connection.py` - MongoDB connection management
- `db/models.py` - Pydantic models for MongoDB documents

**API Endpoints**:
- `POST /chat` - Main chat endpoint (no auth required for demo)
- `GET /health` - Health check with MongoDB ping
- `GET /me` - Get current user (auth required)
- `GET /sessions/{id}/messages` - Get conversation history

**Configuration**:
- Environment variables loaded from `infra/.env`
- Priority: `infra/.env` > `apps/api/.env` > root `.env`

### 3. Orchestrator (LangGraph)

**Location**: `packages/orchestrator/`

**Files**:
- `graph.py` - ITHelpdeskOrchestrator class with workflow handlers
- `prompts.py` - System prompts, intent classification, answer synthesis

**Workflow**:
1. **Intent Classification**: Classify user message into:
   - `knowledge` - Questions that can be answered from KB
   - `create_ticket` - User wants to create a ticket
   - `ticket_status` - Check ticket status
   - `password_reset` - Password reset request
   - `handoff` - Escalate to human agent

2. **Knowledge Handling**:
   - Check if query is about movies → Query `sample_mflix` database
   - Try KB vector search → MongoDB Atlas Vector Search
   - If KB empty → Fallback to OpenAI with generic IT helpdesk knowledge

3. **Ticket Creation**:
   - Extract ticket fields using LLM
   - Create ticket via ServiceNow/Jira/Mock client
   - Notify n8n webhook

4. **Error Handling**:
   - Comprehensive try/catch blocks at all levels
   - Fallback to OpenAI for generic answers
   - Never crashes - always returns a response

### 4. RAG System

**Location**: `packages/rag/`

**Components**:
- `retriever.py` - VectorRetriever for MongoDB Atlas Vector Search
- `embeddings.py` - OpenAI embedding generation
- `ingestion.py` - KB document ingestion and chunking
- `chunkers.py` - Text chunking strategies
- `loaders.py` - Document loaders (Markdown)
- `mflix_retriever.py` - Retriever for `sample_mflix` database

**Features**:
- Vector search with MongoDB Atlas
- Fallback to client-side cosine similarity if Vector Search unavailable
- Chunking with metadata preservation
- Embedding generation with OpenAI

### 5. Client Integrations

**Location**: `packages/clients/`

**Clients**:
- `servicenow.py` - ServiceNow REST API client
- `jira.py` - Jira REST API client (optional)
- `m365.py` - Microsoft 365 Graph API client (optional)
- `mock.py` - Mock clients for demo/testing
- `ticket_system.py` - Adapter pattern for ticket systems

**Features**:
- Adapter pattern for switching between ticket systems
- Mock mode for demo (default)
- Real integrations when `USE_MOCK_INTEGRATIONS=false`

### 6. Database (MongoDB Atlas)

**Collections**:
- `users` - User accounts
- `sessions` - Chat sessions
- `messages` - Conversation messages
- `tickets` - Created tickets
- `kb_docs` - Knowledge base documents
- `kb_chunks` - Knowledge base chunks with embeddings (Vector Search)
- `audit_logs` - Audit trail

**Vector Search Index**:
- Index name: `kb_chunks_vec`
- Path: `embedding`
- Dimensions: 1536 (text-embedding-3-large)
- Similarity: cosine

**Additional Database**:
- `sample_mflix` - Sample MongoDB database for movie queries

---

## Data Flow

### Knowledge Query Flow

```
1. User: "How do I set up MFA?"
   │
2. Frontend → POST /chat
   │
3. Backend → Orchestrator.invoke()
   │
4. Orchestrator → classify_intent() → "knowledge"
   │
5. Orchestrator → handle_knowledge()
   │
6. Check if movie query? NO
   │
7. Try KB retrieval:
   ├─ VectorRetriever.retrieve()
   ├─ MongoDB Vector Search (kb_chunks collection)
   └─ If empty → return []
   │
8. If chunks empty:
   ├─ Use OpenAI with generic IT helpdesk prompt
   └─ Return LLM-generated answer
   │
9. If chunks found:
   ├─ Synthesize answer from chunks + LLM
   └─ Return answer with sources
   │
10. Backend → Save assistant message to MongoDB
    │
11. Frontend → Display answer
```

### Ticket Creation Flow

```
1. User: "Open a ticket for VPN issue"
   │
2. Orchestrator → classify_intent() → "create_ticket"
   │
3. Orchestrator → handle_create_ticket()
   │
4. Extract ticket fields using LLM:
   ├─ short_description
   ├─ description
   ├─ priority (default: 3)
   └─ category (optional)
   │
5. Create ticket:
   ├─ ticket_client.create_ticket()
   ├─ ServiceNow/Jira/Mock client
   └─ Return external_id
   │
6. Notify n8n:
   ├─ POST to webhook/ticket-created
   └─ Send ticket details
   │
7. Return answer: "I've created ticket {id}..."
```

### Movie Query Flow

```
1. User: "What movies are about action?"
   │
2. Orchestrator → handle_knowledge()
   │
3. Detect movie keywords: ["movie", "film", "actor", etc.]
   │
4. Use MflixRetriever:
   ├─ Connect to sample_mflix database
   ├─ Search movies collection
   └─ Return matching movies
   │
5. Format movies:
   ├─ Title, year, genres, plot
   └─ Pass to LLM for answer synthesis
   │
6. Return answer with movie sources
```

---

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: React hooks, custom components
- **Icons**: Lucide React
- **State Management**: React useState/useEffect

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **ASGI Server**: Uvicorn
- **Validation**: Pydantic v2
- **Database**: MongoDB Atlas (via motor/pymongo)
- **LLM**: OpenAI API (langchain-openai)
- **Orchestration**: LangGraph + LangChain

### AI/ML
- **LLM**: OpenAI GPT-4o-mini
- **Embeddings**: OpenAI text-embedding-3-large (1536 dimensions)
- **Vector Search**: MongoDB Atlas Vector Search
- **Fallback**: Client-side cosine similarity

### Infrastructure
- **Database**: MongoDB Atlas (M0 free tier)
- **Automation**: n8n (Docker)
- **Containerization**: Docker (optional)
- **Environment**: dotenv for configuration

### Integrations
- **ServiceNow**: REST API
- **Jira**: REST API (optional)
- **Microsoft 365**: Graph API (optional)
- **n8n**: Webhooks for automation

---

## Project Structure

```
Chatbot.ai/
├── apps/
│   ├── api/                    # FastAPI Backend
│   │   ├── __init__.py
│   │   ├── main.py            # FastAPI app, routes
│   │   ├── config.py          # Configuration
│   │   ├── auth.py            # Authentication
│   │   ├── requirements.txt   # Python dependencies
│   │   ├── Dockerfile         # Docker config
│   │   ├── db/                # Database layer
│   │   │   ├── __init__.py
│   │   │   ├── connection.py # MongoDB connection
│   │   │   └── models.py      # Pydantic models
│   │   └── venv/              # Virtual environment (gitignored)
│   │
│   └── web/                    # Next.js Frontend
│       ├── app/
│       │   ├── page.tsx        # Main page
│       │   ├── layout.tsx      # App layout
│       │   └── globals.css     # Global styles
│       ├── components/
│       │   ├── ChatWidget.tsx  # Chat interface
│       │   └── LoginForm.tsx   # Login form
│       ├── package.json        # Node dependencies
│       ├── next.config.js      # Next.js config
│       ├── tailwind.config.js  # Tailwind config
│       └── tsconfig.json       # TypeScript config
│
├── packages/                   # Shared Packages
│   ├── clients/               # External API clients
│   │   ├── __init__.py
│   │   ├── ticket_system.py   # Adapter pattern
│   │   ├── servicenow.py      # ServiceNow client
│   │   ├── jira.py            # Jira client (optional)
│   │   ├── m365.py            # M365 client (optional)
│   │   └── mock.py            # Mock clients
│   │
│   ├── orchestrator/          # LangGraph Orchestrator
│   │   ├── __init__.py
│   │   ├── graph.py          # Orchestrator logic
│   │   └── prompts.py        # LLM prompts
│   │
│   └── rag/                   # RAG System
│       ├── __init__.py
│       ├── retriever.py      # Vector retriever
│       ├── embeddings.py     # Embedding generation
│       ├── ingestion.py      # KB ingestion
│       ├── chunkers.py        # Text chunking
│       ├── loaders.py         # Document loaders
│       └── mflix_retriever.py # Movie retriever
│
├── seeds/                     # Seed Data
│   └── kb/                    # Knowledge Base Articles
│       ├── mfa-setup.md
│       ├── password-reset.md
│       ├── vpn-troubleshooting.md
│       ├── email-setup.md
│       ├── teams-setup.md
│       └── laptop-setup.md
│
├── infra/                     # Infrastructure
│   ├── env.example            # Environment template
│   └── docker-compose.yml    # Docker Compose config
│
├── README.md                  # Main documentation
├── ARCHITECTURE.md            # This file
├── QUICKSTART.md              # Quick setup guide
├── SECURITY.md                # Security guidelines
├── package.json              # Root package.json (scripts)
└── .gitignore                # Git ignore rules
```

---

## File Reference

This section provides a detailed explanation of each file in the project, its purpose, and key functionality.

### Backend Files (`apps/api/`)

#### `main.py`
**Purpose**: FastAPI application entry point and route definitions.

**Key Functionality**:
- Initializes FastAPI app with CORS middleware
- Defines API endpoints:
  - `POST /chat` - Main chat endpoint (no auth required for demo)
  - `GET /health` - Health check with MongoDB ping
  - `GET /me` - Get current user info
  - `GET /sessions/{id}/messages` - Get conversation history
- Handles guest user creation for demo mode
- Manages session creation and message storage
- Integrates with orchestrator for chat processing
- Error handling and response formatting

**Dependencies**: `config`, `db`, `auth`, `packages.orchestrator`

#### `config.py`
**Purpose**: Configuration management and environment variable loading.

**Key Functionality**:
- Loads environment variables from multiple locations (priority order):
  1. `infra/.env` (primary)
  2. `apps/api/.env` (fallback)
  3. Root `.env` (fallback)
- Defines `Settings` class with Pydantic validation:
  - MongoDB connection settings
  - OpenAI API configuration
  - Integration credentials (ServiceNow, Jira, M365)
  - Feature flags (`USE_MOCK_INTEGRATIONS`, `ENABLE_AUDIT_LOGS`)
  - Server configuration
- Provides centralized settings access via `settings` singleton

**Key Settings**:
- `mongodb_uri`, `mongodb_db_name`
- `openai_api_key`, `openai_model`, `embedding_model`
- `use_mock_integrations` (default: `true`)
- Integration credentials (optional)

#### `auth.py`
**Purpose**: Authentication utilities and JWT token management.

**Key Functionality**:
- Password hashing/verification using bcrypt
- JWT token creation and validation
- Magic link token generation (for demo)
- User authentication helpers:
  - `get_current_user()` - Extract user from JWT token
  - `create_access_token()` - Generate JWT
  - `create_magic_link_token()` - Generate magic link token
  - `get_user_by_email()` - Find user in database

**Note**: Currently simplified for demo mode (guest user access enabled).

#### `db/connection.py`
**Purpose**: MongoDB connection management and database initialization.

**Key Functionality**:
- `init_database()` - Initialize MongoDB connection
- `get_database()` - Get database instance (singleton pattern)
- `close_database()` - Close connection on shutdown
- Connection pooling and error handling
- Automatic retry logic for connection failures

**Collections Accessed**:
- `users`, `sessions`, `messages`, `tickets`, `kb_docs`, `kb_chunks`, `audit_logs`

#### `db/models.py`
**Purpose**: Pydantic models for MongoDB documents with ObjectId handling.

**Key Models**:
- `PyObjectId` - Custom ObjectId validator (Pydantic v2 compatible)
- `User` - User document model (email, name, role)
- `Session` - Chat session model (userId, createdAt, updatedAt)
- `Message` - Message model (sessionId, role, text, toolCalls, sources)
- `Ticket` - Ticket model (externalId, userId, status, priority)
- `KBDoc` - Knowledge base document model
- `KBChunk` - Knowledge base chunk model with embeddings
- `AuditLog` - Audit log model

**Key Features**:
- Automatic ObjectId conversion
- Pydantic v2 compatibility
- Alias handling for MongoDB field names
- Validation and type checking

#### `requirements.txt`
**Purpose**: Python dependency definitions.

**Key Dependencies**:
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `motor` / `pymongo` - MongoDB driver
- `langchain`, `langchain-openai` - LLM orchestration
- `openai` - OpenAI API client
- `pydantic` - Data validation
- `python-dotenv` - Environment variable loading
- `python-jose` - JWT handling
- `passlib` - Password hashing

#### `Dockerfile`
**Purpose**: Docker container configuration for API deployment.

**Key Configuration**:
- Base image: Python 3.11-slim
- Installs system dependencies (gcc, g++)
- Copies requirements and installs Python packages
- Copies application code and packages
- Exposes port 8000
- Runs uvicorn server

### Frontend Files (`apps/web/`)

#### `app/page.tsx`
**Purpose**: Main page component with white theme and animations.

**Key Functionality**:
- Renders main application layout
- White background with subtle animated gradient blobs
- Floating particle animations
- Header with glass morphism effect
- Guest user setup (no authentication required)
- Integrates ChatWidget component

**Styling**: Tailwind CSS with custom animations defined in `globals.css`

#### `app/layout.tsx`
**Purpose**: Root layout component for Next.js App Router.

**Key Functionality**:
- Defines HTML structure and metadata
- Imports global CSS
- Wraps all pages with layout structure

#### `app/globals.css`
**Purpose**: Global CSS styles and animations.

**Key Features**:
- Tailwind CSS imports
- Custom blob animation keyframes
- Floating particle animations
- Animation delay utilities
- Base styling for white theme

#### `components/ChatWidget.tsx`
**Purpose**: Main chat interface component.

**Key Functionality**:
- Chat message display (user/assistant messages)
- Message input with send button
- Session management (creates/retrieves sessions)
- API integration with backend `/chat` endpoint
- Loading states and error handling
- Auto-scroll to latest message
- Displays tool calls and sources

**State Management**:
- `messages` - Chat message history
- `input` - Current input text
- `loading` - Loading state
- `sessionId` - Current session ID

**API Integration**:
- Default API URL: `http://localhost:8000`
- Configurable via `NEXT_PUBLIC_API_URL` env var

#### `components/LoginForm.tsx`
**Purpose**: Authentication form component (currently disabled for demo).

**Key Functionality**:
- Email input for magic link authentication
- Calls `/auth/magic-link` endpoint
- Token verification and login flow
- Error display and loading states

**Note**: Currently not rendered due to guest user access enabled.

#### `next.config.js`
**Purpose**: Next.js configuration.

**Key Configuration**:
- Environment variable forwarding
- API URL configuration
- Build optimizations

#### `tailwind.config.js`
**Purpose**: Tailwind CSS configuration.

**Key Configuration**:
- Content paths for Tailwind scanning
- Custom color theme (primary blue palette)
- Custom animations (blob, float)
- Animation keyframes

#### `package.json`
**Purpose**: Node.js dependencies and scripts.

**Key Dependencies**:
- `next` - Next.js framework
- `react`, `react-dom` - React library
- `typescript` - TypeScript support
- `tailwindcss` - CSS framework
- `lucide-react` - Icon library

**Scripts**:
- `dev` - Start development server
- `build` - Build for production
- `start` - Start production server

#### `tsconfig.json`
**Purpose**: TypeScript compiler configuration.

**Key Settings**:
- React/Next.js JSX support
- Strict type checking
- Path aliases (`@/` for components)

### Orchestrator Files (`packages/orchestrator/`)

#### `graph.py`
**Purpose**: Main orchestrator class implementing LangGraph workflows.

**Key Class**: `ITHelpdeskOrchestrator`

**Key Methods**:
- `__init__()` - Initialize LLM and clients (mock or real)
- `invoke()` - Main entry point, routes to handlers based on intent
- `classify_intent()` - Classify user message (knowledge/ticket/password_reset/handoff)
- `handle_knowledge()` - Process knowledge queries:
  - Detects movie queries → uses `MflixRetriever`
  - Tries KB vector search → MongoDB Atlas
  - Falls back to OpenAI if KB empty
- `handle_create_ticket()` - Create tickets in ServiceNow/Jira
- `handle_ticket_status()` - Check ticket status
- `handle_password_reset()` - Trigger password reset
- `handle_handoff()` - Escalate to human agent

**Error Handling**:
- Comprehensive try/catch blocks
- Fallback to OpenAI for generic answers
- Never crashes - always returns response

#### `prompts.py`
**Purpose**: LLM prompt templates for the orchestrator.

**Key Prompts**:
- `SYSTEM_PROMPT` - System role definition for IT Helpdesk Assistant
- `CLASSIFIER_PROMPT` - Intent classification prompt
- `ANSWER_SYNTHESIS_PROMPT` - Answer synthesis from KB chunks
- `TOOL_EXTRACTION_PROMPT` - Extract ticket fields from user message

**Helper Functions**:
- `get_classifier_prompt(message)` - Format classification prompt
- `get_answer_synthesis_prompt(query, snippets)` - Format synthesis prompt
- `get_tool_extraction_prompt(message)` - Format extraction prompt

### RAG Files (`packages/rag/`)

#### `retriever.py`
**Purpose**: Vector retrieval for MongoDB Atlas Vector Search.

**Key Class**: `VectorRetriever`

**Key Methods**:
- `retrieve(query, k, filter_dict)` - Retrieve top-k chunks:
  - Generates query embedding
  - Uses MongoDB Vector Search aggregation pipeline
  - Falls back to client-side cosine similarity if Vector Search unavailable
- `_fallback_retrieve()` - Client-side similarity calculation

**Features**:
- Automatic fallback if Vector Search not available
- Configurable collection and index names
- Filter support for metadata

#### `embeddings.py`
**Purpose**: Embedding generation using OpenAI.

**Key Functions**:
- `embed_query(query)` - Generate embedding for query string
- `get_embeddings(texts)` - Batch embedding generation

**Configuration**:
- Uses `text-embedding-3-large` model (1536 dimensions)
- Configurable via `EMBEDDING_MODEL` env var

#### `ingestion.py`
**Purpose**: Knowledge base document ingestion pipeline.

**Key Functions**:
- `ingest_document(file_path, tags, chunk_size, chunk_overlap)` - Ingest single document:
  - Loads file using loader
  - Chunks text using chunker
  - Generates embeddings
  - Stores KBDoc and KBChunks in MongoDB
- `ingest_directory(directory)` - Batch ingestion from directory

**Workflow**:
1. Load document → 2. Chunk text → 3. Generate embeddings → 4. Store in MongoDB

#### `chunkers.py`
**Purpose**: Text chunking strategies.

**Key Functions**:
- `chunk_text(text, chunk_size, chunk_overlap)` - Simple text chunking
- `chunk_by_headers(text)` - Chunk by markdown headers

**Features**:
- Preserves metadata (title, source, chunk index)
- Configurable chunk size and overlap
- Header-aware chunking for markdown

#### `loaders.py`
**Purpose**: Document loaders for different file types.

**Key Functions**:
- `load_file(file_path)` - Load file and extract metadata:
  - Supports Markdown files
  - Extracts title from frontmatter or first heading
  - Returns source, title, rawText

**Supported Formats**:
- Markdown (`.md`)

#### `mflix_retriever.py`
**Purpose**: Retriever for `sample_mflix` database (movie queries).

**Key Class**: `MflixRetriever`

**Key Methods**:
- `search_movies(query, limit)` - Search movies collection:
  - Uses regex search on title, plot, genres, cast, directors
  - Returns top N matching movies
- `get_movie_details(title)` - Get specific movie by title

**Database**: `sample_mflix.movies` collection

### Client Integration Files (`packages/clients/`)

#### `ticket_system.py`
**Purpose**: Adapter pattern for ticket systems.

**Key Classes**:
- `TicketSystem` - Abstract base class
- `TicketSystemAdapter` - Adapter for different ticket systems

**Key Methods**:
- `create_ticket()` - Create ticket
- `get_ticket_status()` - Get ticket status
- `update_ticket()` - Update ticket

#### `servicenow.py`
**Purpose**: ServiceNow REST API client.

**Key Class**: `ServiceNowClient`

**Key Functionality**:
- Authenticates using Basic Auth
- Creates incidents via REST API
- Retrieves incident status
- Maps priority levels

#### `jira.py`
**Purpose**: Jira REST API client (optional dependency).

**Key Class**: `JiraClient`

**Key Functionality**:
- Authenticates using API token
- Creates issues via REST API
- Retrieves issue status

**Note**: Requires `jira` package (`pip install jira`)

#### `m365.py`
**Purpose**: Microsoft 365 Graph API client (optional dependency).

**Key Class**: `M365Client`

**Key Functionality**:
- Authenticates using MSAL (Microsoft Authentication Library)
- Triggers password reset flows
- Sends password reset emails

**Note**: Requires `msal` package (`pip install msal`)

#### `mock.py`
**Purpose**: Mock clients for demo/testing.

**Key Classes**:
- `MockTicketClient` - Mock ticket system
- `MockM365Client` - Mock M365 client

**Key Functionality**:
- Simulates ticket creation (returns fake IDs)
- Simulates password reset (no actual action)
- No external API calls

**Usage**: Default when `USE_MOCK_INTEGRATIONS=true`

#### `__init__.py`
**Purpose**: Package initialization and exports.

**Key Functionality**:
- Imports all clients
- Handles optional dependencies (Jira, M365) gracefully
- Exports available clients via `__all__`

### Infrastructure Files (`infra/`)

#### `env.example`
**Purpose**: Environment variable template.

**Key Variables**:
- MongoDB connection string template
- OpenAI API key placeholder
- Integration credentials templates
- Feature flags

**Usage**: Copy to `.env` and fill in real values.

#### `docker-compose.yml`
**Purpose**: Docker Compose configuration for full-stack deployment.

**Services**:
- `api` - FastAPI backend service
- `n8n` - Automation workflow service

**Key Features**:
- Environment variable injection
- Volume mounts for code hot-reload
- Service dependencies
- Port mapping

### Seed Files (`seeds/kb/`)

#### `*.md` files (mfa-setup.md, password-reset.md, etc.)
**Purpose**: Sample knowledge base articles.

**Content**: Markdown files with:
- Title
- Step-by-step instructions
- Troubleshooting sections
- Support information

**Usage**: Ingested into MongoDB via `ingestion.py` script.

### Root Files

#### `package.json`
**Purpose**: Root package.json with convenience scripts.

**Scripts**:
- `dev:api` - Start API server
- `dev:web` - Start web server
- `ingest` - Ingest KB documents

**Dependencies**:
- `dotenv` - Environment variable loading
- `mongodb` - MongoDB driver (for scripts)

#### `README.md`
**Purpose**: Main project documentation.

**Content**: Overview, features, quick start, usage examples.

#### `QUICKSTART.md`
**Purpose**: Quick setup guide.

**Content**: Step-by-step setup instructions.

#### `SECURITY.md`
**Purpose**: Security best practices.

**Content**: Credential management, `.gitignore` rules, production security.

#### `.gitignore`
**Purpose**: Git ignore rules.

**Excluded**:
- `.env` files
- `venv/`, `node_modules/`
- `*.pyc`, `__pycache__`
- Credential files
- Log files

---

## Environment Setup

### Required Environment Variables

Create `infra/.env` file (copy from `infra/env.example`):

```bash
# MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/?appName=AIChatbot
MONGODB_DB_NAME=it_helpdesk

# OpenAI
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-large

# Feature Flags
USE_MOCK_INTEGRATIONS=true
ENABLE_AUDIT_LOGS=true

# n8n (optional)
N8N_USER=admin
N8N_PASSWORD=admin

# Optional: Real Integrations (set USE_MOCK_INTEGRATIONS=false)
# SERVICENOW_INSTANCE_URL=https://yourinstance.service-now.com
# SERVICENOW_USERNAME=your_username
# SERVICENOW_PASSWORD=your_password

# JIRA_SERVER_URL=https://yourcompany.atlassian.net
# JIRA_EMAIL=your_email
# JIRA_API_TOKEN=your_api_token

# M365_TENANT_ID=your_tenant_id
# M365_CLIENT_ID=your_client_id
# M365_CLIENT_SECRET=your_client_secret
```

### Environment Variable Priority

The backend checks environment variables in this order:
1. `infra/.env` (highest priority)
2. `apps/api/.env`
3. Root `.env`
4. System environment variables

### Getting Credentials

#### MongoDB Atlas
1. Create account: https://www.mongodb.com/cloud/atlas
2. Create cluster (M0 free tier)
3. Create database user (username/password)
4. Whitelist IP (0.0.0.0/0 for demo)
5. Get connection string: "Connect" → "Connect your application"

#### OpenAI
1. Create account: https://platform.openai.com
2. Go to API keys: https://platform.openai.com/api-keys
3. Create new secret key
4. Copy key to `OPENAI_API_KEY`

---

## Quick Start Guide

### Prerequisites

- Python 3.9+
- Node.js 18+
- MongoDB Atlas account (free tier)
- OpenAI API key
- Docker (optional, for n8n)

### Step 1: Setup Environment (2 min)

```bash
# Navigate to project
cd /path/to/Chatbot.ai

# Copy environment file
cp infra/env.example infra/.env

# Edit infra/.env and add:
# - MONGODB_URI (from MongoDB Atlas)
# - OPENAI_API_KEY (from OpenAI dashboard)
```

### Step 2: Install Dependencies (3 min)

```bash
# Python dependencies
cd apps/api
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cd ../..

# Node dependencies
cd apps/web
npm install
cd ../..
```

### Step 3: Initialize MongoDB (1 min)

Database auto-initializes on first run, or manually:

```bash
cd apps/api
source venv/bin/activate
python -c "from db import init_database; import asyncio; asyncio.run(init_database())"
```

### Step 4: Ingest Knowledge Base (2 min)

```bash
cd apps/api
source venv/bin/activate
python -m packages.rag.ingestion ../seeds/kb
```

This loads 6 sample KB articles from `seeds/kb/`.

### Step 5: Create Vector Search Index (2 min)

1. Go to MongoDB Atlas: https://cloud.mongodb.com
2. Navigate to: Cluster → Collections → `kb_chunks`
3. Click "Create Search Index" → "JSON Editor"
4. Paste:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

5. Name: `kb_chunks_vec`
6. Click "Create Search Index"
7. Wait ~1 minute for index to build

**Note**: If Vector Search isn't available, the system falls back to client-side similarity.

### Step 6: Start Services (1 min)

```bash
# Terminal 1: API
cd apps/api
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Web
cd apps/web
npm run dev

# Terminal 3: n8n (optional)
docker-compose -f infra/docker-compose.yml up n8n
```

### Step 7: Test It!

1. Open browser: http://localhost:3000 (or 3003 if Next.js uses that port)
2. Enter any email (demo mode - no auth required)
3. Try queries:
   - "How do I set up MFA?"
   - "What movies are about action?"
   - "Open a ticket for VPN issue"
   - "Reset my password"

---

## Configuration

### Feature Flags

- `USE_MOCK_INTEGRATIONS=true` - Use mock clients (default)
- `USE_MOCK_INTEGRATIONS=false` - Use real ServiceNow/Jira/M365
- `ENABLE_AUDIT_LOGS=true` - Enable audit logging

### Switching to Real Integrations

1. Set `USE_MOCK_INTEGRATIONS=false` in `infra/.env`
2. Add credentials:
   - ServiceNow: `SERVICENOW_INSTANCE_URL`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD`
   - Jira: `JIRA_SERVER_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN`
   - M365: `M365_TENANT_ID`, `M365_CLIENT_ID`, `M365_CLIENT_SECRET`

### n8n Webhooks

Configure n8n workflows:
- `/webhook/ticket-created` - Called when ticket is created
- `/webhook/escalate` - Called when escalation is needed

---

## Security Guidelines

### Environment Variables

**All sensitive credentials must be stored in `.env` files and NEVER committed to git.**

### Files Excluded from Git

The following are automatically excluded via `.gitignore`:
- `.env` files (all variants)
- `*.key`, `*.pem` - Private keys
- `secrets/` - Secret files directory
- `*credentials*`, `*password*` - Files with credentials/passwords

### Best Practices

1. **Never commit `.env` files** - Use `.env.example` as template
2. **Rotate credentials regularly** - Change passwords and API keys periodically
3. **Use environment variables** - Never hardcode credentials in source code
4. **Review commits before pushing** - Verify no sensitive data is included
5. **Use secret management** - For production, consider AWS Secrets Manager or Azure Key Vault

### If You Accidentally Commit Credentials

1. **Rotate credentials immediately** - Change all exposed passwords/keys
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (coordinate with team first):
   ```bash
   git push origin --force --all
   ```

### Production Security Checklist

- [ ] Use managed secret services (AWS Secrets Manager, Azure Key Vault)
- [ ] Enable encryption at rest
- [ ] Use HTTPS/TLS for all connections
- [ ] Implement rate limiting
- [ ] Enable audit logging
- [ ] Use least-privilege access controls
- [ ] Regularly review access logs
- [ ] Set up Azure AD OAuth (replace magic link)
- [ ] Configure CORS for production domains

---

## Deployment

### Production Checklist

- [ ] Set `USE_MOCK_INTEGRATIONS=false`
- [ ] Configure real integrations (ServiceNow, Jira, M365)
- [ ] Set up Azure AD OAuth (replace magic link)
- [ ] Enable rate limiting
- [ ] Set up monitoring (e.g., Sentry)
- [ ] Configure HTTPS
- [ ] Set secure secrets management
- [ ] Enable audit logs
- [ ] Test all workflows end-to-end
- [ ] Configure CORS for production domains

### Deployment Options

#### Option 1: Render/Fly.io

Deploy API and web separately:
- **API**: FastAPI app on Render/Fly.io
- **Web**: Next.js app on Vercel/Render
- **Database**: MongoDB Atlas (already cloud)
- **n8n**: Docker container or SaaS

#### Option 2: AWS/GCP

- **API**: AWS ECS / GCP Cloud Run
- **Web**: AWS S3+CloudFront / GCP App Engine
- **Database**: MongoDB Atlas
- **Secrets**: AWS Secrets Manager / GCP Secret Manager

#### Option 3: Docker Compose (On-Premise)

```bash
docker-compose -f infra/docker-compose.yml up -d
```

---

## Troubleshooting

### MongoDB Connection Issues

- **Problem**: "MongoDB connection failed"
- **Solution**:
  - Verify connection string in `infra/.env`
  - Check MongoDB Atlas IP whitelist (allow 0.0.0.0/0 for demo)
  - Ensure network access is enabled
  - Verify database user exists and password is correct

### Vector Search Not Working

- **Problem**: "Vector search failed"
- **Solution**:
  - Verify index `kb_chunks_vec` exists and is built
  - Check embedding dimensions (1536 for text-embedding-3-large)
  - System will fall back to client-side similarity automatically

### OpenAI API Errors

- **Problem**: "OpenAI API error"
- **Solution**:
  - Verify API key is correct in `infra/.env`
  - Check API quota/limits in OpenAI dashboard
  - Ensure billing is set up
  - Verify model name is correct (`gpt-4o-mini`)

### n8n Not Receiving Webhooks

- **Problem**: "n8n not receiving webhooks"
- **Solution**:
  - Verify n8n is running (http://localhost:5678)
  - Check webhook URLs in `.env`
  - Test webhook manually in n8n UI
  - Verify firewall/network allows connections

### Import Errors

- **Problem**: "ModuleNotFoundError"
- **Solution**:
  - Ensure you're in the correct directory
  - Activate virtual environment (`source venv/bin/activate`)
  - Install dependencies (`pip install -r requirements.txt`)
  - Check Python path includes `apps/api`

### Backend Not Responding

- **Problem**: Backend times out or doesn't respond
- **Solution**:
  - Check if backend process is running: `ps aux | grep uvicorn`
  - Verify port 8000 is not in use: `lsof -i :8000`
  - Check backend logs for errors
  - Restart backend: `pkill -f uvicorn && uvicorn main:app --reload --port 8000`

### Frontend Connection Errors

- **Problem**: "Failed to fetch" or connection refused
- **Solution**:
  - Verify backend is running on port 8000
  - Check `NEXT_PUBLIC_API_URL` in frontend (default: `http://localhost:8000`)
  - Check CORS settings in backend
  - Verify no firewall blocking connections

### Knowledge Base Empty

- **Problem**: Chatbot doesn't answer questions from KB
- **Solution**:
  - Verify KB was ingested: Check `kb_chunks` collection in MongoDB
  - Run ingestion: `python -m packages.rag.ingestion ../seeds/kb`
  - Verify Vector Search index exists
  - System will fall back to OpenAI if KB is empty (expected behavior)

---

## Current Features

### ✅ Implemented

- [x] RAG with MongoDB Atlas Vector Search
- [x] Fallback to OpenAI for generic answers
- [x] Movie queries from `sample_mflix` database
- [x] Intent classification
- [x] Ticket creation (mock/real)
- [x] Ticket status checking
- [x] Password reset (mock/real)
- [x] n8n integration
- [x] White UI theme with animations
- [x] Comprehensive error handling
- [x] Guest user access (no auth required)

### 🔄 In Progress / Future

- [ ] KB ingestion from multiple sources
- [ ] Multi-turn conversation context
- [ ] Advanced n8n workflows
- [ ] Azure AD OAuth integration
- [ ] Rate limiting
- [ ] Monitoring and observability
- [ ] Production deployment guides

---

## Demo Script

### Flow A: Knowledge Query (RAG)

**User**: "How do I set up MFA on a new laptop?"
**Bot**: Returns step-by-step instructions from KB (if available) or generic OpenAI answer

### Flow B: Movie Query

**User**: "What movies are about action?"
**Bot**: Searches `sample_mflix` database and returns relevant movies with details

### Flow C: Create Ticket

**User**: "Open a P2 ticket for VPN failing on Mac"
**Bot**: Creates ticket (mock or real) and returns ID, notifies n8n

### Flow D: Ticket Status

**User**: "What's the status of INC0012345?"
**Bot**: Returns current ticket status

### Flow E: Password Reset

**User**: "Reset my password"
**Bot**: Sends password reset link (mock or real)

---

## Support & Resources

- **API Documentation**: http://localhost:8000/docs (when backend is running)
- **MongoDB Atlas**: https://cloud.mongodb.com
- **OpenAI Dashboard**: https://platform.openai.com
- **n8n Documentation**: https://docs.n8n.io
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Next.js Docs**: https://nextjs.org/docs

---

## License

MIT

---

**Last Updated**: Current version includes:
- White UI theme with subtle animations
- Comprehensive error handling with LLM fallback
- Movie database integration
- Guest user access (no authentication required)
- MongoDB and OpenAI integration

