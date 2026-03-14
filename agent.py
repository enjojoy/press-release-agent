import os
import httpx
from dotenv import load_dotenv
from masumi.agent import MasumiAgent

load_dotenv()

# ── Input Schema ────────────────────────────────────────────────────────────
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "company_name": {
            "type": "string",
            "description": "Name of the company issuing the press release"
        },
        "headline": {
            "type": "string",
            "description": "Main headline / announcement topic"
        },
        "body_points": {
            "type": "string",
            "description": "Key facts, quotes, and details to include (bullet points or plain text)"
        },
        "contact_name": {
            "type": "string",
            "description": "Media contact person name"
        },
        "contact_email": {
            "type": "string",
            "description": "Media contact email"
        },
        "city": {
            "type": "string",
            "description": "City for the dateline (e.g. Prague, New York)"
        },
        "tone": {
            "type": "string",
            "description": "Tone of the release: formal, startup, technical, consumer",
            "enum": ["formal", "startup", "technical", "consumer"],
            "default": "formal"
        }
    },
    "required": ["company_name", "headline", "body_points", "city"]
}

# ── Demo ─────────────────────────────────────────────────────────────────────
DEMO = {
    "input": [
        {"key": "company_name", "value": "Masumi Network"},
        {"key": "headline", "value": "Masumi Network Launches Decentralized AI Agent Marketplace on Cardano"},
        {"key": "body_points", "value": "- Protocol enables agent-to-agent payments\n- Built on Cardano blockchain\n- Sokosumi marketplace launches with 50+ agents\n- Quote from CEO Patrick Tobler: 'This is the future of autonomous AI commerce'"},
        {"key": "city", "value": "Zug"},
        {"key": "tone", "value": "startup"},
        {"key": "contact_name", "value": "Albina Nikiforova"},
        {"key": "contact_email", "value": "press@masumi.network"}
    ],
    "output": """FOR IMMEDIATE RELEASE

Masumi Network Launches Decentralized AI Agent Marketplace on Cardano

ZUG, Switzerland — Masumi Network today announced the launch of Sokosumi, a decentralized marketplace enabling autonomous AI agents to discover, hire, and pay each other using blockchain technology.

Built on the Cardano blockchain, the Masumi protocol introduces a new standard for agent-to-agent (A2A) payments, allowing AI services to transact without human intervention. The Sokosumi marketplace launches with more than 50 registered agents spanning summarization, data analysis, content generation, and financial research.

"This is the future of autonomous AI commerce," said Patrick Tobler, CEO of Masumi Network. "We're giving AI agents the financial infrastructure they need to collaborate at scale."

The Masumi protocol uses USDM, a MiCA-compliant USD stablecoin on Cardano, ensuring price stability for automated systems. Agents register via the Masumi Registry and are discoverable by other agents through standardized APIs.

Developers can register their AI agents at docs.masumi.network and list them on Sokosumi starting today.

###

Media Contact:
Albina Nikiforova
press@masumi.network"""
}


# ── Core Logic ───────────────────────────────────────────────────────────────
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


async def process_job(job_id: str, input_data: dict) -> str:
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

    press_release = result["choices"][0]["message"]["content"].strip()
    return press_release


# ── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    agent = MasumiAgent(
        process_job=process_job,
        input_schema=INPUT_SCHEMA,
        demo=DEMO
    )
    agent.run(host="0.0.0.0", port=port)
