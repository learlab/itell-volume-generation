from __future__ import annotations

import base64
import json
import logging
from typing import Any, Dict, Optional, Sequence, Type, TypeVar

from google import genai
from openai import OpenAI
from pydantic import BaseModel, ValidationError


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OpenAIClient:
    """Simple wrapper for sending PDF + prompt payloads to the OpenAI chat completions API."""

    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        base_url: Optional[str] = None,
        request_timeout: Optional[float] = None,
        default_headers: Optional[Dict[str, str]] = None,
        max_completion_tokens: int = 4_000,
    ) -> None:
        if not api_key:
            raise ValueError("An compatible API key is required.")

        self.model = model
        self.request_timeout = request_timeout
        self.max_completion_tokens = max_completion_tokens
        self.client = OpenAI(api_key=api_key, base_url=base_url, default_headers=default_headers)

    def generate_itell_json(self, pdf_filename: str, pdf_base64: str, prompt: str) -> str:
        """Send the encoded PDF + prompt to the model and return the JSON response text."""
        data_uri = f"data:application/pdf;base64,{pdf_base64}"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "file",
                        "file": {
                            "filename": pdf_filename,
                            "file_data": data_uri,
                        },
                    },
                    {
                        "type": "text",
                        "text": prompt,
                    },
                ],
            }
        ]

        logger.info("Sending PDF '%s' to %s", pdf_filename, self.model)
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_completion_tokens=self.max_completion_tokens,
            timeout=self.request_timeout,
        )
        return self._extract_message_text(completion)

    @staticmethod
    def _extract_message_text(completion: Any) -> str:
        """Normalize the response payload into a string for downstream use."""
        choices = getattr(completion, "choices", None) or []
        if not choices:
            raise RuntimeError("No completion choices were returned by the API.")

        message = choices[0].message
        content = getattr(message, "content", "")

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, Sequence):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    text = block.get("text")
                else:
                    text = getattr(block, "text", None)
                if text:
                    text_parts.append(text)
            return "\n".join(text_parts).strip()

        return str(content).strip()


class GeminiClient:
    def __init__(
        self,
        model: str,
        api_key: str,
        *,
        request_timeout: Optional[float] = None,
        max_output_tokens: int = 99999,

    ) -> None:
        if not api_key:
            raise ValueError("A Gemini API key is required.")

        self.model_name = model
        self.max_output_tokens = max_output_tokens
        http_options = genai.types.HttpOptions(timeout=request_timeout) if request_timeout else None
        self.model = model
        self.client = genai.Client(
            api_key=api_key,
            http_options=http_options
        )

    def generate_itell_json(self, pdf_filename: str, pdf_base64: str, prompt: str) -> str:
        pdf_bytes = base64.b64decode(pdf_base64)

        pdf_part = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }
        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                  genai.types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type='application/pdf',
                  ),
                  prompt
              ],
            config=genai.types.GenerateContentConfig(
                max_output_tokens=self.max_output_tokens,
            ),
        )

        return response.text.strip()

    def generate_itell_structured(
        self, pdf_filename: str, pdf_base64: str, prompt: str, response_format: Type[T]
    ) -> T:
        """Send PDF + prompt to Gemini and return structured output as Pydantic model."""
        pdf_bytes = base64.b64decode(pdf_base64)
        
        completion = self.client.models.generate_content(
            model=self.model,
            contents=[
                  genai.types.Part.from_bytes(
                    data=pdf_bytes,
                    mime_type='application/pdf',
                  ),
                  prompt
              ],
            config=genai.types.GenerateContentConfig(
                max_output_tokens=self.max_output_tokens,
                response_mime_type="application/json",
                response_schema=response_format,
            ),
        )
        parsed = getattr(completion, "parsed", None)
        if parsed is not None:
            if isinstance(parsed, BaseModel):
                return parsed
            try:
                return response_format.model_validate(parsed)
            except ValidationError as e:
                raise RuntimeError(f"Gemini returned data that failed validation: {e}") from e

        try:
            cleaned_text = self._extract_json_payload(completion.text or "")
            response_dict = json.loads(cleaned_text)
            return response_format.model_validate(response_dict)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            snippet = (completion.text or "")[:500]
            raise RuntimeError(
                f"Failed to parse structured output from Gemini: {e}. Raw response (truncated): {snippet}"
            ) from e

    @staticmethod
    def _extract_json_payload(raw_text: str) -> str:
        """Strip code fences and leading/trailing chatter to isolate JSON."""
        cleaned = raw_text.strip()
        lower_cleaned = cleaned.lower()
        if lower_cleaned.startswith("```json"):
            cleaned = cleaned[len("```json"):].strip()
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:].strip()

        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

        # Walk the response so we only capture the balanced JSON payload even if
        # stray braces appear inside quoted text.
        start_index = None
        brace_depth = 0
        in_string = False
        escape = False
        for idx, char in enumerate(cleaned):
            if start_index is None:
                if char == "{":
                    start_index = idx
                    brace_depth = 1
                continue

            if in_string:
                if escape:
                    escape = False
                    continue
                if char == "\\":
                    escape = True
                    continue
                if char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
                continue

            if char == "{":
                brace_depth += 1
            elif char == "}":
                brace_depth -= 1
                if brace_depth == 0 and start_index is not None:
                    cleaned = cleaned[start_index:idx + 1]
                    break

        return cleaned
