from __future__ import annotations

import base64
import json
import logging
from typing import Any, Dict, Optional, Sequence, Type, TypeVar

import google.generativeai as genai
from openai import OpenAI
from pydantic import BaseModel


logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


# def inline_schema_refs(schema: dict) -> dict:
#     """
#     Inline $defs references and remove unsupported fields for Gemini compatibility.

#     Gemini supports a subset of JSON Schema:
#     - Supported: type, properties, required, items, description, enum, format
#     - Arrays: items, minItems, maxItems
#     - NOT supported: $defs, $ref, anyOf, allOf, oneOf, not, title, default, examples, etc.
#     """
#     # Remove $defs and extract definitions
#     defs = schema.pop("$defs", {})

#     # Fields that Gemini doesn't support
#     unsupported_fields = {
#         "title", "$schema", "examples", "additionalProperties",
#         "default", "const", "pattern", "minLength", "maxLength",
#         "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
#         "multipleOf", "uniqueItems", "minProperties", "maxProperties"
#     }

#     def replace_refs(obj: Any) -> Any:
#         """Recursively replace $ref, inline anyOf/allOf/oneOf, and remove unsupported fields."""
#         if isinstance(obj, dict):
#             # Handle $ref
#             if "$ref" in obj:
#                 ref_path = obj["$ref"].split("/")[-1]
#                 if ref_path in defs:
#                     return replace_refs(defs[ref_path].copy())
#                 return obj

#             # Handle anyOf (used for Optional fields and discriminated unions)
#             if "anyOf" in obj:
#                 any_of = obj["anyOf"]
#                 # Filter out null types
#                 non_null_types = [t for t in any_of if t.get("type") != "null"]

#                 if not non_null_types:
#                     # All types are null, use first
#                     return replace_refs(any_of[0]) if any_of else {"type": "string"}

#                 if len(non_null_types) == 1:
#                     # Single non-null type (Optional field)
#                     return replace_refs(non_null_types[0])

#                 # Multiple non-null types (discriminated union like NewChunk | NewPlainChunk)
#                 # Merge all object schemas and make fields optional
#                 merged = {"type": "object", "properties": {}, "required": []}
#                 all_required = set()

#                 for schema in non_null_types:
#                     resolved = replace_refs(schema)
#                     if isinstance(resolved, dict) and resolved.get("type") == "object":
#                         # Merge properties
#                         if "properties" in resolved:
#                             merged["properties"].update(resolved["properties"])
#                         # Track which fields are required in ALL schemas
#                         if "required" in resolved:
#                             if not all_required:
#                                 all_required = set(resolved["required"])
#                             else:
#                                 all_required &= set(resolved["required"])

#                 # Only mark fields as required if they're required in ALL variants
#                 if all_required:
#                     merged["required"] = list(all_required)
#                 else:
#                     merged.pop("required", None)

#                 return merged

#             # Handle allOf (merge all schemas)
#             if "allOf" in obj:
#                 merged = {}
#                 for schema in obj["allOf"]:
#                     resolved = replace_refs(schema)
#                     if isinstance(resolved, dict):
#                         merged.update(resolved)
#                 return merged

#             # Handle oneOf (use the first option)
#             if "oneOf" in obj:
#                 one_of = obj["oneOf"]
#                 if one_of:
#                     return replace_refs(one_of[0])
#                 return {"type": "string"}

#             # Remove unsupported fields and recursively process remaining values
#             cleaned = {}
#             for k, v in obj.items():
#                 if k not in unsupported_fields:
#                     cleaned[k] = replace_refs(v)

#             return cleaned

#         elif isinstance(obj, list):
#             return [replace_refs(item) for item in obj]
#         else:
#             return obj

#     return replace_refs(schema)


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
        self.request_timeout = request_timeout
        self.max_output_tokens = max_output_tokens

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name=model)

    def generate_itell_json(self, pdf_filename: str, pdf_base64: str, prompt: str) -> str:
        pdf_bytes = base64.b64decode(pdf_base64)

        pdf_part = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }
        response = self.model.generate_content(
            [pdf_part, prompt],
            generation_config=genai.GenerationConfig(
                max_output_tokens=self.max_output_tokens,
            ),
            request_options={"timeout": self.request_timeout} if self.request_timeout else None,
        )

        return response.text.strip()

    def generate_itell_structured(
        self, pdf_filename: str, pdf_base64: str, prompt: str, response_format: Type[T]
    ) -> T:
        """Send PDF + prompt to Gemini and return structured output as Pydantic model."""
        pdf_bytes = base64.b64decode(pdf_base64)
        pdf_part = {
            "mime_type": "application/pdf",
            "data": pdf_bytes
        }
        response = self.model.generate_content(
            [pdf_part, prompt],
            generation_config={
                "response_mime_type": "application/json",
                "response_schema": response_format.model_json_schema(),
            },
        )
        try:
            response_dict = json.loads(response.text)
            return response_format.model_validate(response_dict)
        except (json.JSONDecodeError, ValueError) as e:
            raise RuntimeError(f"Failed to parse structured output from Gemini: {e}") from e
