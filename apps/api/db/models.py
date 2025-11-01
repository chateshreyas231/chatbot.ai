"""MongoDB document models/schemas."""
from typing import List, Optional, Dict, Any
from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, Field, EmailStr


class PyObjectId(ObjectId):
    """Custom ObjectId for Pydantic."""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


class User(BaseModel):
    """User model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    email: EmailStr
    name: str
    aad_sub: Optional[str] = None  # Azure AD subject
    role: str = "user"  # user, admin, helpdesk
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Session(BaseModel):
    """Chat session model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    userId: PyObjectId
    state: str = "active"  # active, completed, archived
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Message(BaseModel):
    """Chat message model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    sessionId: PyObjectId
    role: str  # user, assistant, tool
    text: str
    toolCalls: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class KBDoc(BaseModel):
    """Knowledge base document model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    source: str  # file path or URL
    title: str
    url: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    rawText: str
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class KBChunk(BaseModel):
    """Knowledge base chunk model with embedding."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    docId: PyObjectId
    chunkIndex: int
    text: str
    embedding: List[float] = Field(default_factory=list)
    tokens: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Ticket(BaseModel):
    """Ticket model (cached from external systems)."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    system: str  # servicenow, jira
    externalId: str
    shortDesc: str
    description: Optional[str] = None
    status: str
    priority: Optional[str] = None
    openedBy: str  # email
    assignedTo: Optional[str] = None
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AuditLog(BaseModel):
    """Audit log model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    sessionId: Optional[PyObjectId] = None
    userId: Optional[PyObjectId] = None
    event: str  # intent_classified, tool_called, rag_retrieved, etc.
    payload: Dict[str, Any] = Field(default_factory=dict)
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class Connector(BaseModel):
    """Connector configuration model."""
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    type: str  # servicenow, jira, m365
    config: Dict[str, Any] = Field(default_factory=dict)
    encryptedSecretsRef: Optional[str] = None
    isActive: bool = True
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}

