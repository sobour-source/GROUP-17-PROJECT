import os
import json
import requests


class ReadingGuideGenerator:
    """Uses the Gemini API to generate a plain-language summary, reading level,
    and discussion questions for a Book."""

    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No Gemini API key found. Set the GEMINI_API_KEY environment variable before running the app."
            )

    def generate(self, book):
        """Return a dict with 'summary', 'reading_level', and 'questions' for the given book."""
        prompt = self._build_prompt(book)
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        params = {"key": self.api_key}

        try:
            response = requests.post(self.API_URL, params=params, json=payload, timeout=20)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Gemini request failed: {e}")

        data = response.json()

        try:
            text = data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise RuntimeError("Gemini returned an unexpected response format.")

        # Gemini sometimes wraps JSON in ```json ... ``` fences — strip those if present.
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`")
            cleaned = cleaned.replace("json", "", 1).strip()

        try:
            guide = json.loads(cleaned)
        except json.JSONDecodeError:
            raise RuntimeError("Could not parse Gemini's response as JSON.")

        return guide

    def _build_prompt(self, book):
        return f"""You are a helpful reading assistant. Respond ONLY with a JSON object
(no markdown, no extra text) with exactly these keys: "summary", "reading_level", "questions".

- "summary": a plain-language summary in 3-4 sentences, for someone who has not read the book.
- "reading_level": a short label such as "Middle Grade", "Young Adult", "Adult - Easy", "Adult - Advanced".
- "questions": a list of exactly 3 discussion or comprehension questions about the book.

Book title: {book.title}
Author(s): {', '.join(book.authors)}
First published: {book.first_publish_year or 'Unknown'}
Subjects: {', '.join(book.subjects) if book.subjects else 'Unknown'}
"""
