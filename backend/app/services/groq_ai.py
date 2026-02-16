"""Lead qualification using Groq's Llama model (OpenAI-compatible API)."""

import json
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

# Groq's fast open-source Llama model
MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def qualify_lead(message: str) -> dict:
    """Qualify lead using Groq's Llama model."""

    prompt = f"""You are a lead qualification assistant for a financial advisory service in India.

Analyze this lead's message and extract information. Respond with ONLY a JSON object:

{{
  "goal": "investment | retirement | insurance | tax | wealth_management | unclear",
  "timeline": "immediate | 1-3_months | 6-12_months | 5+_years | unclear",
  "budget_range": "<5L | 5-20L | 20-50L | 50L+ | not_disclosed",
  "quality_score": <number 0-100>
}}

Scoring guide:
- Budget: <5L=20pts, 5-20L=30pts, 20-50L=35pts, 50L+=40pts, not_disclosed=10pts
- Timeline: immediate=30pts, 1-3mo=25pts, 6-12mo=20pts, 5+yrs=15pts, unclear=5pts
- Message clarity: Clear=20pts, Vague=10pts, Very vague=5pts
- Completeness: All info=10pts, Partial=5pts, Minimal=0pts

Lead's message: "{message}"

Return ONLY the JSON object."""

    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        text = response.choices[0].message.content.strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return result

    except Exception as e:
        print(f"Groq API error: {e}")
        return {
            "goal": "unclear",
            "timeline": "unclear",
            "budget_range": "not_disclosed",
            "quality_score": 30,
        }
