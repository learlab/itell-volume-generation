from __future__ import annotations

import logging
from typing import Any, Dict, Optional, Sequence

from openai import OpenAI


logger = logging.getLogger(__name__)


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
