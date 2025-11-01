"""Prompts for the orchestrator."""
from typing import List, Dict


SYSTEM_PROMPT = """You are the IT Helpdesk Copilot, an intelligent assistant that helps employees with IT support issues.

Your capabilities:
1. Answer questions from the knowledge base
2. Create tickets in ServiceNow or Jira
3. Check ticket status
4. Help with password resets
5. Escalate to human agents when needed

Guidelines:
- Provide concise, actionable steps
- Use tools when intent is explicit
- Ask one clarifying question if needed
- If information is not in the knowledge base, offer to create a ticket
- Always be professional and helpful"""


CLASSIFIER_PROMPT = """Classify the user's intent into one of these categories:

1. **knowledge** - User is asking a question that can be answered from the knowledge base
   Examples: "How do I set up MFA?", "VPN is not working", "How to reset password?"

2. **create_ticket** - User wants to create a new support ticket
   Examples: "Open a ticket for VPN issue", "Create a P2 ticket for email not working", "I need help with laptop setup"

3. **ticket_status** - User wants to check the status of an existing ticket
   Examples: "What's the status of INC0012345?", "Where is my ticket?", "Check ticket IT-123"

4. **password_reset** - User wants to reset their password
   Examples: "Reset my password", "I forgot my password", "Password reset request"

5. **handoff** - User needs human assistance or the request cannot be handled automatically
   Examples: Complex issues, requests for human agent, unclear requests

Return ONLY the intent category name (knowledge, create_ticket, ticket_status, password_reset, or handoff).

User message: {message}
Intent:"""


ANSWER_SYNTHESIS_PROMPT = """Use the following retrieved knowledge base snippets to answer the user's question.

If the information is available, provide a clear, step-by-step answer with actionable steps.
If the information is not sufficient or you're unsure, acknowledge this and offer to create a ticket for further assistance.

Retrieved snippets:
{snippets}

User question: {query}

Answer:"""


TOOL_EXTRACTION_PROMPT = """Extract relevant information from the user's message to create a ticket.

Extract:
- short_description: Brief summary of the issue
- description: Detailed description
- priority: 1 (Critical), 2 (High), 3 (Medium), 4 (Low), 5 (Planning) - default to 3 if not specified
- category: Optional category if mentioned

User message: {message}

Return a JSON object with these fields."""


def get_classifier_prompt(message: str) -> str:
    """Get classifier prompt."""
    return CLASSIFIER_PROMPT.format(message=message)


def get_answer_synthesis_prompt(query: str, snippets: List[Dict]) -> str:
    """Get answer synthesis prompt."""
    snippets_text = "\n\n".join([
        f"[Snippet {i+1}]\n{chunk['text']}"
        for i, chunk in enumerate(snippets[:6])
    ])
    return ANSWER_SYNTHESIS_PROMPT.format(query=query, snippets=snippets_text)


def get_tool_extraction_prompt(message: str) -> str:
    """Get tool extraction prompt."""
    return TOOL_EXTRACTION_PROMPT.format(message=message)

