#!/usr/bin/env python
"""
Quick test script to verify OpenAI Chat Completions API integration.
Run with: python test_openai_integration.py
"""

import asyncio
import json
import os
from typing import List
from openai import AsyncOpenAI

# Test configuration
TEST_COMMENTS = [
    "El servicio fue excelente, muy satisfecho con la atención recibida.",
    "Pésima experiencia, nunca más volveré. Muy decepcionado.",
    "Regular, nada especial pero tampoco malo."
]

async def test_chat_completions():
    """Test the Chat Completions API with structured output."""

    # Initialize client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not set in environment")
        return False

    client = AsyncOpenAI(api_key=api_key)

    # Prepare prompts
    system_prompt = """You are an expert customer feedback analyst.
Analyze each comment and provide JSON output with:
- emotions: object with scores (0-1) for: satisfaccion, frustracion, enojo, confianza, decepcion, confusion, anticipacion
- churn_risk: float 0-1
- nps: string "promoter", "passive", or "detractor"
"""

    user_prompt = f"""Analyze these {len(TEST_COMMENTS)} comments:

{chr(10).join(f'[{i+1}] {comment}' for i, comment in enumerate(TEST_COMMENTS))}

Return a JSON object with an "analyses" array containing the analysis for each comment."""

    # Define the expected schema
    response_schema = {
        "type": "object",
        "properties": {
            "analyses": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "emotions": {
                            "type": "object",
                            "properties": {
                                "satisfaccion": {"type": "number", "minimum": 0, "maximum": 1},
                                "frustracion": {"type": "number", "minimum": 0, "maximum": 1},
                                "enojo": {"type": "number", "minimum": 0, "maximum": 1},
                                "confianza": {"type": "number", "minimum": 0, "maximum": 1},
                                "decepcion": {"type": "number", "minimum": 0, "maximum": 1},
                                "confusion": {"type": "number", "minimum": 0, "maximum": 1},
                                "anticipacion": {"type": "number", "minimum": 0, "maximum": 1}
                            },
                            "required": ["satisfaccion", "frustracion", "enojo", "confianza", "decepcion", "confusion", "anticipacion"]
                        },
                        "churn_risk": {"type": "number", "minimum": 0, "maximum": 1},
                        "nps": {"type": "string", "enum": ["promoter", "passive", "detractor"]}
                    },
                    "required": ["emotions", "churn_risk", "nps"]
                }
            }
        },
        "required": ["analyses"]
    }

    try:
        print("🔄 Testing Chat Completions API with structured output...")
        print(f"   Model: gpt-4o-mini")
        print(f"   Comments: {len(TEST_COMMENTS)}")

        # Make the API call
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "batch_analysis",
                    "schema": response_schema,
                    "strict": True
                }
            },
            temperature=0.3,
            max_tokens=1000,
            seed=42
        )

        # Extract and parse response
        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        print("✅ API call successful!")
        print(f"   Usage: {response.usage.total_tokens} tokens")
        print(f"   Analyses returned: {len(result.get('analyses', []))}")

        # Validate response structure
        if len(result.get('analyses', [])) != len(TEST_COMMENTS):
            print(f"⚠️  Warning: Expected {len(TEST_COMMENTS)} analyses, got {len(result.get('analyses', []))}")

        # Display results
        print("\n📊 Analysis Results:")
        for i, analysis in enumerate(result.get('analyses', []), 1):
            print(f"\n   Comment {i}:")
            print(f"   - NPS: {analysis.get('nps', 'N/A')}")
            print(f"   - Churn Risk: {analysis.get('churn_risk', 0):.2f}")
            emotions = analysis.get('emotions', {})
            top_emotion = max(emotions.items(), key=lambda x: x[1]) if emotions else ('N/A', 0)
            print(f"   - Top Emotion: {top_emotion[0]} ({top_emotion[1]:.2f})")

        return True

    except Exception as e:
        print(f"❌ Error: {type(e).__name__}: {str(e)}")
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("OpenAI Chat Completions API Integration Test")
    print("=" * 60)

    success = await test_chat_completions()

    print("\n" + "=" * 60)
    if success:
        print("✅ Test PASSED - Chat Completions API is working correctly")
    else:
        print("❌ Test FAILED - Check error messages above")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())