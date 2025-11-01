"""LangGraph orchestrator for IT Helpdesk Copilot."""
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, AIMessage, SystemMessage
import json

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "apps" / "api"))

from config import settings
from db import get_database
from db.models import AuditLog
from packages.rag.retriever import retrieve_kb
from packages.clients import TicketSystemAdapter, MockTicketClient, ServiceNowClient, MockM365Client
try:
    from packages.clients import M365Client
except ImportError:
    M365Client = None  # Optional (requires msal)
try:
    from packages.clients import JiraClient
except ImportError:
    JiraClient = None  # Optional
from packages.orchestrator.prompts import (
    SYSTEM_PROMPT,
    get_classifier_prompt,
    get_answer_synthesis_prompt,
    get_tool_extraction_prompt
)


class ITHelpdeskOrchestrator:
    """Orchestrator for IT Helpdesk Copilot workflows."""
    
    def __init__(
        self,
        ticket_client: Optional[TicketSystemAdapter] = None,
        m365_client: Optional[M365Client] = None
    ):
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.2,
            api_key=settings.openai_api_key
        )
        
        # Initialize clients (mock or real)
        if settings.use_mock_integrations:
            self.ticket_client = TicketSystemAdapter(MockTicketClient(system="servicenow"))
            self.m365_client = MockM365Client()
        else:
            # Use real clients if configured
            if ticket_client:
                self.ticket_client = ticket_client
            elif settings.servicenow_instance_url:
                self.ticket_client = TicketSystemAdapter(ServiceNowClient())
            elif settings.jira_server_url:
                self.ticket_client = TicketSystemAdapter(JiraClient())
            else:
                self.ticket_client = TicketSystemAdapter(MockTicketClient())
            
            if m365_client:
                self.m365_client = m365_client
            elif settings.m365_client_id:
                self.m365_client = M365Client()
            else:
                self.m365_client = MockM365Client()
    
    async def classify_intent(self, message: str, user_email: str) -> str:
        """Classify user intent."""
        prompt = get_classifier_prompt(message)
        
        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
        
        intent = response.content.strip().lower()
        
        # Validate intent
        valid_intents = ["knowledge", "create_ticket", "ticket_status", "password_reset", "handoff"]
        if intent not in valid_intents:
            # Default to knowledge if unclear
            intent = "knowledge"
        
        # Log classification
        if settings.enable_audit_logs:
            await self._log_audit("intent_classified", {
                "message": message[:200],  # Truncate for privacy
                "intent": intent,
                "user_email": user_email
            })
        
        return intent
    
    async def handle_knowledge(self, query: str, user_email: str) -> Dict[str, Any]:
        """Handle knowledge base queries."""
        try:
            # Check if query is about movies (sample_mflix database)
            movie_keywords = ["movie", "film", "actor", "director", "genre", "rating", "imdb", "plot", "cast"]
            is_movie_query = any(keyword in query.lower() for keyword in movie_keywords)
            
            if is_movie_query:
                # Use sample_mflix database
                try:
                    # Import MflixRetriever - need to add path
                    from pathlib import Path as PathLib
                    api_path = PathLib(__file__).parent.parent.parent / "apps" / "api"
                    if str(api_path) not in sys.path:
                        sys.path.insert(0, str(api_path))
                    
                    from packages.rag.mflix_retriever import MflixRetriever
                    
                    retriever = MflixRetriever()
                    movies = await retriever.search_movies(query, limit=6)
                    
                    if movies:
                        # Format movies for response
                        movies_text = "\n\n".join([
                            f"**{m['title']}** ({m.get('year', 'N/A')})\n"
                            f"Genres: {', '.join(m.get('genres', []))}\n"
                            f"Plot: {m.get('plot', 'N/A')[:200]}..."
                            for m in movies
                        ])
                        
                        prompt = f"""Based on the following movies from our database, answer the user's question about movies:

{movies_text}

User question: {query}

Provide a helpful answer about these movies."""
                        
                        response = await self.llm.ainvoke([HumanMessage(content=prompt)])
                        answer = response.content.strip()
                        
                        return {
                            "answer": answer,
                            "sources": [{"title": m["title"], "year": m.get("year")} for m in movies],
                            "intent": "knowledge",
                            "data_source": "sample_mflix"
                        }
                except Exception as e:
                    print(f"Error retrieving from sample_mflix: {e}")
                    import traceback
                    traceback.print_exc()
                    # Fall through to KB retrieval or generic LLM
        except Exception as e:
            print(f"Error in handle_knowledge: {e}")
            import traceback
            traceback.print_exc()
            # Fall through to generic LLM
        
        # Fallback to KB retrieval - wrap in try-catch to handle errors
        chunks = []
        try:
            chunks = await retrieve_kb(query, k=6)
        except Exception as e:
            print(f"Error retrieving from KB: {e}")
            chunks = []  # Empty chunks will trigger LLM fallback
        
        # Log retrieval
        if settings.enable_audit_logs:
            try:
                await self._log_audit("rag_retrieved", {
                    "query": query[:200],
                    "num_chunks": len(chunks),
                    "chunk_ids": [c["id"] for c in chunks] if chunks else []
                })
            except:
                pass  # Don't fail if audit logging fails
        
        # If KB is empty, use LLM with general IT helpdesk knowledge
        if not chunks:
            print(f"No KB chunks found for query: {query}. Using LLM general knowledge.")
            prompt = f"""As an IT Helpdesk Assistant, answer the user's question about IT support. 
Provide clear, step-by-step instructions based on IT best practices.

User question: {query}

If this is a common IT issue (like MFA setup, password reset, VPN issues), provide helpful instructions.
If you're unsure or this requires specific company policies, acknowledge this and offer to create a support ticket.

Provide a helpful answer:"""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            
            answer = response.content.strip()
            
            return {
                "answer": answer,
                "sources": [],
                "intent": "knowledge",
                "data_source": "llm_general_knowledge"
            }
        
        # Synthesize answer from KB chunks
        try:
            prompt = get_answer_synthesis_prompt(query, chunks)
            
            response = await self.llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            
            answer = response.content.strip()
            
            return {
                "answer": answer,
                "sources": [{"id": c["id"], "docId": c.get("docId"), "text": c["text"][:200]} for c in chunks],
                "intent": "knowledge"
            }
        except Exception as e:
            print(f"Error synthesizing answer from KB: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to generic LLM answer
            prompt = f"""As an IT Helpdesk Assistant, answer the user's question about IT support. 
Provide clear, step-by-step instructions based on IT best practices.

User question: {query}

If this is a common IT issue (like MFA setup, password reset, VPN issues), provide helpful instructions.
If you're unsure or this requires specific company policies, acknowledge this and offer to create a support ticket.

Provide a helpful answer:"""
            
            response = await self.llm.ainvoke([
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=prompt)
            ])
            
            return {
                "answer": response.content.strip(),
                "sources": [],
                "intent": "knowledge",
                "data_source": "llm_fallback"
            }
    
    async def handle_create_ticket(self, message: str, user_email: str) -> Dict[str, Any]:
        """Handle ticket creation."""
        # Extract ticket fields using LLM
        extraction_prompt = get_tool_extraction_prompt(message)
        
        response = await self.llm.ainvoke([HumanMessage(content=extraction_prompt)])
        
        try:
            # Try to parse JSON response
            fields = json.loads(response.content.strip())
        except json.JSONDecodeError:
            # Fallback: extract from message
            fields = {
                "short_description": message[:100],
                "description": message,
                "priority": "3"
            }
        
        short_desc = fields.get("short_description") or fields.get("shortDesc") or message[:100]
        description = fields.get("description") or message
        priority = fields.get("priority") or "3"
        
        # Create ticket
        try:
            external_id = await self.ticket_client.create_ticket(
                short_desc=short_desc,
                description=description,
                priority=str(priority),
                user=user_email
            )
            
            # Notify n8n (if configured)
            await self._notify_n8n("ticket_created", {
                "external_id": external_id,
                "user_email": user_email,
                "short_desc": short_desc
            })
            
            # Log action
            if settings.enable_audit_logs:
                await self._log_audit("tool_called", {
                    "tool": "create_ticket",
                    "external_id": external_id,
                    "user_email": user_email
                })
            
            answer = f"I've created ticket {external_id} for: {short_desc}. You'll receive updates via email. I'll keep you posted on the progress."
            
            return {
                "answer": answer,
                "tool_calls": [{"tool": "create_ticket", "id": external_id}],
                "intent": "create_ticket"
            }
        except Exception as e:
            print(f"Error creating ticket: {e}")
            return {
                "answer": "I encountered an error creating the ticket. Would you like me to escalate this to a human agent?",
                "intent": "handoff",
                "error": str(e)
            }
    
    async def handle_ticket_status(self, message: str, user_email: str) -> Dict[str, Any]:
        """Handle ticket status queries."""
        # Extract ticket ID from message
        # Simple regex or LLM extraction
        import re
        
        # Try to find ticket ID patterns
        patterns = [
            r'(INC\d+)',  # ServiceNow
            r'([A-Z]+-\d+)',  # Jira (IT-123)
            r'(TICKET-\w+)',  # Generic
        ]
        
        ticket_id = None
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                ticket_id = match.group(1)
                break
        
        if not ticket_id:
            # Try LLM extraction
            extraction_prompt = f"""Extract the ticket ID from this message. Return only the ticket ID (e.g., INC0012345, IT-123).

Message: {message}
Ticket ID:"""
            
            response = await self.llm.ainvoke([HumanMessage(content=extraction_prompt)])
            ticket_id = response.content.strip()
        
        # Get ticket
        try:
            ticket = await self.ticket_client.get_ticket(ticket_id)
            
            status = ticket.get("status", "Unknown")
            short_desc = ticket.get("shortDesc", "N/A")
            priority = ticket.get("priority", "N/A")
            assigned_to = ticket.get("assignedTo", "Unassigned")
            
            answer = f"Ticket {ticket_id}: **{status}**\n\nSummary: {short_desc}\nPriority: {priority}\nAssigned to: {assigned_to}"
            
            return {
                "answer": answer,
                "ticket_data": ticket,
                "intent": "ticket_status"
            }
        except Exception as e:
            print(f"Error getting ticket: {e}")
            return {
                "answer": f"I couldn't find ticket {ticket_id}. Please verify the ticket ID or I can create a new ticket for you.",
                "intent": "ticket_status",
                "error": str(e)
            }
    
    async def handle_password_reset(self, message: str, user_email: str) -> Dict[str, Any]:
        """Handle password reset requests."""
        # Get password reset link
        try:
            ssr_link = await self.m365_client.get_ssr_link(user_email)
            
            # Optionally send email
            await self.m365_client.send_password_reset_email(user_email)
            
            # Log action
            if settings.enable_audit_logs:
                await self._log_audit("tool_called", {
                    "tool": "password_reset",
                    "user_email": user_email
                })
            
            answer = f"I've sent a secure password reset link to {user_email}. Click the link to reset your password. If you can't access email, please contact IT support for alternative options."
            
            return {
                "answer": answer,
                "ssr_link": ssr_link,
                "intent": "password_reset"
            }
        except Exception as e:
            print(f"Error with password reset: {e}")
            return {
                "answer": "I encountered an error with the password reset. Would you like me to create a ticket for IT support to help you?",
                "intent": "handoff",
                "error": str(e)
            }
    
    async def handle_handoff(self, message: str, user_email: str, session_id: str) -> Dict[str, Any]:
        """Handle handoff to human agent."""
        # Get recent messages for context
        database = await get_database()
        recent_messages = await database.messages.find(
            {"sessionId": session_id}
        ).sort("createdAt", -1).limit(10).to_list(10)
        
        # Create handoff message
        transcript = "\n".join([
            f"{msg['role']}: {msg['text']}"
            for msg in reversed(recent_messages)
        ])
        
        # Notify n8n for escalation
        await self._notify_n8n("escalate", {
            "session_id": str(session_id),
            "user_email": user_email,
            "transcript": transcript[:1000]  # Truncate
        })
        
        answer = "I've escalated your request to a human agent. They'll review our conversation and contact you shortly. In the meantime, is there anything else I can help with?"
        
        return {
            "answer": answer,
            "intent": "handoff",
            "handoff": True
        }
    
    async def invoke(self, message: str, user_email: str, session_id: str) -> Dict[str, Any]:
        """Main orchestrator entry point."""
        try:
            # Classify intent
            intent = await self.classify_intent(message, user_email)
            
            # Route to handler
            if intent == "knowledge":
                return await self.handle_knowledge(message, user_email)
            elif intent == "create_ticket":
                return await self.handle_create_ticket(message, user_email)
            elif intent == "ticket_status":
                return await self.handle_ticket_status(message, user_email)
            elif intent == "password_reset":
                return await self.handle_password_reset(message, user_email)
            else:
                return await self.handle_handoff(message, user_email, session_id)
        except Exception as e:
            print(f"Error in orchestrator.invoke: {e}")
            import traceback
            traceback.print_exc()
            # Fallback to generic LLM answer
            try:
                prompt = f"""As an IT Helpdesk Assistant, answer the user's question. Be helpful and professional.
                
User question: {message}

Provide a helpful answer based on IT best practices. If you don't know the answer, acknowledge it and offer to create a support ticket."""
                
                response = await self.llm.ainvoke([
                    SystemMessage(content=SYSTEM_PROMPT),
                    HumanMessage(content=prompt)
                ])
                
                return {
                    "answer": response.content.strip(),
                    "sources": [],
                    "intent": "knowledge",
                    "data_source": "llm_fallback"
                }
            except Exception as fallback_error:
                print(f"Error in fallback LLM: {fallback_error}")
                return {
                    "answer": "I encountered an error processing your request. Please try again or contact support.",
                    "intent": "handoff",
                    "error": str(e)
                }
    
    async def _log_audit(self, event: str, payload: Dict):
        """Log audit event."""
        database = await get_database()
        
        audit_log = AuditLog(
            event=event,
            payload=payload
        )
        
        audit_dict = audit_log.model_dump(by_alias=True, exclude={"id", "sessionId", "userId"})
        await database.audit_logs.insert_one(audit_dict)
    
    async def _notify_n8n(self, event: str, payload: Dict):
        """Notify n8n webhook."""
        if not settings.n8n_webhook_ticket_created and not settings.n8n_webhook_escalate:
            return
        
        webhook_url = None
        if event == "ticket_created" and settings.n8n_webhook_ticket_created:
            webhook_url = settings.n8n_webhook_ticket_created
        elif event == "escalate" and settings.n8n_webhook_escalate:
            webhook_url = settings.n8n_webhook_escalate
        
        if not webhook_url:
            return
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json={"event": event, "payload": payload}, timeout=3)
        except Exception as e:
            print(f"Error notifying n8n: {e}")


# Global orchestrator instance
_orchestrator: Optional[ITHelpdeskOrchestrator] = None


async def get_orchestrator() -> ITHelpdeskOrchestrator:
    """Get orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ITHelpdeskOrchestrator()
    return _orchestrator


async def classify_intent(message: str, user_email: str) -> str:
    """Classify intent (convenience function)."""
    orchestrator = await get_orchestrator()
    return await orchestrator.classify_intent(message, user_email)


async def invoke_orchestrator(message: str, user_email: str, session_id: str) -> Dict[str, Any]:
    """Invoke orchestrator (convenience function)."""
    orchestrator = await get_orchestrator()
    return await orchestrator.invoke(message, user_email, session_id)

