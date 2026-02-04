"""
Lead capture prompts for collecting user contact information.
"""

LEAD_EXTRACTION_PROMPT = """Extract contact information from the user's message.

Current known information:
{current_lead}

User's message: {message}

Extract any NEW information found. Return a JSON object with only fields that have values:
- first_name: string
- last_name: string
- email: string (must be valid email format)
- phone: string

Return ONLY the JSON object, no explanation. Return {{}} if no new info found."""

LEAD_FOLLOWUP_PROMPT = """You are a property sales assistant for Silver Land Properties.

We're collecting information for a viewing booking.

Information collected so far:
{lead_info}

Still needed: {missing_info}

User just said: "{user_message}"

Generate a brief response that:
1. Thanks them for the information they provided (if any)
2. Asks for the NEXT missing piece of information (prioritize: name > email > phone)
   - Ask for "name" (user's full name), not "first name" separately
   - If name is provided, ask for email

Keep it to 1-2 sentences. Be professional. Do not use emojis."""
