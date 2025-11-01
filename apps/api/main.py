"""FastAPI main application."""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId

from config import settings
from db import init_database, get_database, close_database
from db.models import Session, Message, Ticket
from auth import (
    get_current_user,
    create_user,
    create_access_token,
    create_magic_link_token,
    get_user_by_email,
    User
)
# Add packages to path
import sys
from pathlib import Path
packages_path = Path(__file__).parent.parent.parent / "packages"
sys.path.insert(0, str(packages_path))

from packages.orchestrator.graph import get_orchestrator, invoke_orchestrator
from packages.clients import TicketSystemAdapter, MockTicketClient, ServiceNowClient, JiraClient

app = FastAPI(
    title="IT Helpdesk Copilot API",
    description="API for IT Helpdesk Copilot with RAG, ticket creation, and agentic workflows",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models
class ChatRequest(BaseModel):
    sessionId: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    answer: str
    sessionId: str
    sources: Optional[List[Dict[str, Any]]] = None
    toolCalls: Optional[List[Dict[str, Any]]] = None
    intent: Optional[str] = None


class MagicLinkRequest(BaseModel):
    email: EmailStr


class MagicLinkResponse(BaseModel):
    message: str
    token: Optional[str] = None


class TicketResponse(BaseModel):
    externalId: str
    shortDesc: str
    status: str
    priority: Optional[str] = None
    openedBy: str
    assignedTo: Optional[str] = None
    createdAt: str
    updatedAt: str


# Startup/Shutdown
@app.on_event("startup")
async def startup():
    """Initialize database on startup."""
    await init_database()


@app.on_event("shutdown")
async def shutdown():
    """Close database on shutdown."""
    await close_database()


# Health check
@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


# Authentication endpoints
@app.post("/auth/magic-link", response_model=MagicLinkResponse)
async def create_magic_link(request: MagicLinkRequest):
    """Create magic link for demo authentication."""
    email = request.email
    
    # Get or create user
    user = await get_user_by_email(email)
    if not user:
        user = await create_user(email=email, name=email.split("@")[0])
    
    # Create magic link token
    token = await create_magic_link_token(email)
    
    # In production, send email with magic link
    # For demo, return token directly
    magic_link = f"/auth/verify?token={token}"
    
    return MagicLinkResponse(
        message=f"Magic link created for {email}. Use token for authentication.",
        token=token  # For demo only - in production, don't return token
    )


@app.post("/auth/verify")
async def verify_magic_link(token: str):
    """Verify magic link token."""
    from auth import verify_magic_link_token
    
    email = await verify_magic_link_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    # Create JWT access token
    access_token = create_access_token(data={"sub": email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "name": current_user.name,
        "role": current_user.role
    }


# Chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_user: User = Depends(get_current_user)):
    """Main chat endpoint."""
    database = await get_database()
    
    # Get or create session
    if request.sessionId:
        try:
            session_id = ObjectId(request.sessionId)
            session_doc = await database.sessions.find_one({"_id": session_id})
            if not session_doc or str(session_doc["userId"]) != str(current_user.id):
                raise HTTPException(status_code=404, detail="Session not found")
        except:
            raise HTTPException(status_code=400, detail="Invalid session ID")
    else:
        # Create new session
        session = Session(userId=current_user.id)
        session_dict = session.model_dump(by_alias=True, exclude={"id"})
        result = await database.sessions.insert_one(session_dict)
        session_id = result.inserted_id
    
    # Save user message
    user_message = Message(
        sessionId=session_id,
        role="user",
        text=request.message
    )
    user_msg_dict = user_message.model_dump(by_alias=True, exclude={"id"})
    await database.messages.insert_one(user_msg_dict)
    
    # Invoke orchestrator
    try:
        result = await invoke_orchestrator(
            message=request.message,
            user_email=current_user.email,
            session_id=str(session_id)
        )
    except Exception as e:
        print(f"Error in orchestrator: {e}")
        result = {
            "answer": "I encountered an error processing your request. Please try again or contact support.",
            "intent": "handoff"
        }
    
    # Save assistant message
    assistant_message = Message(
        sessionId=session_id,
        role="assistant",
        text=result.get("answer", ""),
        toolCalls=result.get("tool_calls", []),
        metadata={
            "intent": result.get("intent"),
            "sources": result.get("sources", [])
        }
    )
    assistant_msg_dict = assistant_message.model_dump(by_alias=True, exclude={"id"})
    await database.messages.insert_one(assistant_msg_dict)
    
    # Update session
    await database.sessions.update_one(
        {"_id": session_id},
        {"$set": {"updatedAt": datetime.utcnow()}}
    )
    
    return ChatResponse(
        answer=result.get("answer", ""),
        sessionId=str(session_id),
        sources=result.get("sources"),
        toolCalls=result.get("tool_calls", []),
        intent=result.get("intent")
    )


@app.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: str, current_user: User = Depends(get_current_user)):
    """Get messages for a session."""
    database = await get_database()
    
    try:
        session_oid = ObjectId(session_id)
    except:
        raise HTTPException(status_code=400, detail="Invalid session ID")
    
    # Verify session belongs to user
    session_doc = await database.sessions.find_one({"_id": session_oid})
    if not session_doc or str(session_doc["userId"]) != str(current_user.id):
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get messages
    messages = []
    async for msg_doc in database.messages.find(
        {"sessionId": session_oid}
    ).sort("createdAt", 1):
        messages.append({
            "id": str(msg_doc["_id"]),
            "role": msg_doc["role"],
            "text": msg_doc["text"],
            "toolCalls": msg_doc.get("toolCalls", []),
            "createdAt": msg_doc["createdAt"].isoformat()
        })
    
    return {"messages": messages}


@app.get("/tickets/{external_id}", response_model=TicketResponse)
async def get_ticket(external_id: str, current_user: User = Depends(get_current_user)):
    """Get ticket by external ID."""
    # Get orchestrator to use its ticket client
    orchestrator = await get_orchestrator()
    
    try:
        ticket = await orchestrator.ticket_client.get_ticket(external_id)
        
        return TicketResponse(
            externalId=ticket.get("externalId", external_id),
            shortDesc=ticket.get("shortDesc", "N/A"),
            status=ticket.get("status", "Unknown"),
            priority=ticket.get("priority"),
            openedBy=ticket.get("openedBy", "Unknown"),
            assignedTo=ticket.get("assignedTo"),
            createdAt=ticket.get("createdAt", datetime.utcnow().isoformat()),
            updatedAt=ticket.get("updatedAt", datetime.utcnow().isoformat())
        )
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Ticket not found: {str(e)}")


# Admin endpoints
@app.post("/admin/ingest")
async def ingest_kb(
    directory: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Ingest knowledge base documents."""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if not directory:
        # Default to seeds/kb
        directory = str(Path(__file__).parent.parent.parent / "seeds" / "kb")
    
    from packages.rag.ingestion import ingest_directory
    
    try:
        doc_ids = await ingest_directory(directory)
        return {"message": f"Ingested {len(doc_ids)} documents", "doc_ids": doc_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error ingesting: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.api_host, port=settings.api_port)

