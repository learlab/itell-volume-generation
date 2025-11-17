from __future__ import annotations

import base64
import json
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional, Sequence


__all__ = [
    "load_reference_json",
    "load_guide_instructions",
    "encode_pdf_to_base64",
    "select_reference_example",
    "build_conversion_prompt",
    "format_image_metadata",
]


def load_reference_json(reference_path: Path) -> Dict[str, Any]:
    """Load and parse the baseline iTELL JSON reference file."""
    reference_path = Path(reference_path)
    if not reference_path.exists():
        raise FileNotFoundError(f"Reference JSON not found at {reference_path}")

    with reference_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_guide_instructions(guide_path: Path) -> str:
    """Read instructions from a Markdown/text/docx guide file."""
    guide_path = Path(guide_path)
    if not guide_path.exists():
        raise FileNotFoundError(f"Guide file not found at {guide_path}")

    suffix = guide_path.suffix.lower()
    if suffix in {".md", ".txt"}:
        return guide_path.read_text(encoding="utf-8").strip()

    if suffix == ".docx":
        try:
            from docx import Document  # type: ignore import
        except ImportError as exc:  # pragma: no cover - informative error path
            raise ImportError(
                "python-docx is required to parse .docx instruction files; add it to requirements.txt"
            ) from exc

        document = Document(str(guide_path))
        paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
        return "\n".join(paragraphs)

    raise ValueError(f"Unsupported guide format '{suffix}'. Expected .md, .txt, or .docx")


def encode_pdf_to_base64(pdf_path: Path) -> str:
    """Return a base64 string of the PDF contents."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    with pdf_path.open("rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")


def select_reference_example(reference_json: Dict[str, Any], example_title: Optional[str] = None) -> Any:
    """Pick a specific section from the reference data if a title is provided."""
    if not example_title:
        return reference_json

    if not isinstance(reference_json, dict):
        raise ValueError("Reference JSON must be a dictionary when filtering by title.")

    data = reference_json.get("data")
    if isinstance(data, list):
        normalized = example_title.strip().casefold()
        for page in data:
            if not isinstance(page, dict):
                continue
            title = page.get("Title") or page.get("title")
            if isinstance(title, str) and title.strip().casefold() == normalized:
                return page

    raise ValueError(f"Could not find a reference section titled '{example_title}'.")


def format_image_metadata(image_metadata: Sequence[Dict[str, Any]]) -> str:
    """Convert extracted image metadata into inline <image> tags for the LLM prompt."""
    if not image_metadata:
        return ""

    tag_lines = []
    for entry in image_metadata:
        image_id = entry.get("image_id") or Path(entry.get("filepath", "")).stem or "image"
        page_num = entry.get("page_num", "?")
        bbox = entry.get("bbox") or {}
        coords = {
            "x0": bbox.get("x0", 0),
            "y0": bbox.get("y0", 0),
            "x1": bbox.get("x1", 0),
            "y1": bbox.get("y1", 0),
        }
        x0 = coords["x0"]
        y0 = coords["y0"]
        x1 = coords["x1"]
        y1 = coords["y1"]
        filepath = entry.get("filepath", "")
        tag_lines.append(
            "<image "
            f'id="{image_id}" '
            f'page="{page_num}" '
            f'x0="{x0:.2f}" '
            f'y0="{y0:.2f}" '
            f'x1="{x1:.2f}" '
            f'y1="{y1:.2f}" '
            f'filepath="{filepath}"'
            " />"
        )
    tag_lines.append(
        "Use the image id attribute when referencing a figure within the iTELL JSON so downstream consumers can map coordinates to assets."
    )
    return "\n".join(tag_lines)


def build_conversion_prompt(guide_text: str, example_json: Any, image_metadata_text: Optional[str] = None) -> str:
    """Create the LLM prompt by combining guide instructions with a JSON example."""
    if not guide_text.strip():
        raise ValueError("Guide instructions are empty; cannot craft a prompt.")

    example_json_str = json.dumps(example_json, indent=2, ensure_ascii=False)
    template = f"""
    Your Role: iTELL Content Authoring Expert
        You are a specialized AI assistant expert in the iTELL framework. Your primary function is to convert source documents into perfectly structured iTELL JSON files.
    Source Files for This Task:

    INSTRUCTIONS:
    {guide_text.strip()}

    REFERENCE OUTPUT EXAMPLE:
    ```json
    {example_json_str}
    ```

    Carefully read the provided PDF and convert it into iTELL JSON.
    Only return JSON that adheres to the example schema and instructions above.
    """
    if image_metadata_text:
        template += f"""

    IMAGE TAGS WITH COORDINATES:
    {image_metadata_text}

    Each <image> tag identifies a figure extracted from the PDF along with its coordinates. When embedding or describing a figure in the JSON, include the referenced image id so downstream systems can match it to the extracted asset.
        """
    return textwrap.dedent(template).strip()
