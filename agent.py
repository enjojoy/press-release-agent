#!/usr/bin/env python3
import os
import httpx
from dotenv import load_dotenv
from masumi import run

load_dotenv()

# ── Input Schema (MIP-003 Attachment 01 format) ──────────────────────────────
INPUT_SCHEMA = {
    "input_data": [
        {
            "id": "company_name",
            "type": "string",
            "name": "Company Name",
            "description": "Name of the company issuing the press release"
        },
        {
            "id": "headline",
            "type": "string",
            "name": "Headline",
            "description": "Main headline / announcement topic"
        },
        {
            "id": "body_points",
            "type": "string",
            "name": "Key Facts & Details",
            "description": "Key facts, quotes, and details to include (bullet points or plain text)"
        },
        {
            "id": "city",
            "type": "string",
            "name": "City",
            "description": "City for the dateline (e.g. Prague, New York)"
        },
        {
            "id": "tone",
            "type": "string",
            "name": "Tone",
            "description": "Tone of the release: formal, startup, technical, consumer (default: formal)"
        },
        {
            "id": "contact_name",
            "type": "string",
            "name": "Contact Name",
            "description": "Media contact person name (optional)"
        },
        {
            "id": "contact_email",
            "type": "string",
            "name": "Contact Email",
            "description": "Media contact email (optional)"
        }
    ]
}

# ── Prompt Template ───────────────────────────────────────────────────────────
PRESS_RELEASE_PROMPT = """You are an expert PR writer with 20 years of experience writing press releases for tech companies, startups, and enterprises. You follow AP Style and standard press release format precisely.

Write a professional press release based on the following inputs:

Company: {company_name}
Headline: {headline}
City: {city}
Tone: {tone}
Key Facts / Details:
{body_points}

Contact Name: {contact_name}
Contact Email: {contact_email}

PRESS RELEASE FORMAT RULES (follow strictly):
1. Start with "FOR IMMEDIATE RELEASE" on its own line
2. Blank line, then the HEADLINE in title case
3. Blank line, then DATELINE: "CITY, Country — " followed by the lead paragraph
4. Lead paragraph answers: Who, What, When, Where, Why in 1-2 sentences
5. 2-3 body paragraphs expanding on key facts, with at least one direct quote attributed to a named person
6. If no quote is provided, create a plausible one attributed to "a company spokesperson"
7. Boilerplate paragraph: one sentence "About {company_name}" ending with website placeholder
8. End with "###" on its own line
9. Media contact block: name, email

TONE GUIDELINES:
- formal: traditional corporate language, measured and authoritative
- startup: energetic, vision-forward, uses words like "announces", "launches", "breakthrough"
- technical: precise, uses correct technical terminology, appeals to developer/engineering audience
- consumer: simple language, benefit-focused, avoids jargon

Output ONLY the press release text. No commentary, no markdown, no code fences."""


# ── Core Logic ───────────────────────────────────────────────────────────────
async def process_job(identifier_from_purchaser: str, input_data: dict) -> str:
    company_name = input_data.get("company_name", "")
    headline = input_data.get("headline", "")
    body_points = input_data.get("body_points", "")
    contact_name = input_data.get("contact_name", "Media Relations")
    contact_email = input_data.get("contact_email", "press@company.com")
    city = input_data.get("city", "")
    tone = input_data.get("tone", "formal")

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set in environment")

    prompt = PRESS_RELEASE_PROMPT.format(
        company_name=company_name,
        headline=headline,
        body_points=body_points,
        contact_name=contact_name,
        contact_email=contact_email,
        city=city,
        tone=tone
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json={
                "model": "gpt-4o",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert PR copywriter. Output only the press release, no extra text."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
        )
        resp.raise_for_status()
        result = resp.json()

    return result["choices"][0]["message"]["content"].strip()


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    run(
        start_job_handler=process_job,
        input_schema_handler=INPUT_SCHEMA
    )
