from __future__ import annotations

import base64
import json
import textwrap
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

__all__ = [
    "build_conversion_prompt",
    "build_mode_guide_text",
    "encode_pdf_to_base64",
    "format_image_metadata",
    "load_guide_instructions",
    "load_reference_json",
    "resolve_mode_directory",
    "select_reference_example",
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
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "python-docx is required to parse .docx instruction files"
            ) from exc

        document = Document(str(guide_path))
        paragraphs = [
            paragraph.text.strip()
            for paragraph in document.paragraphs
            if paragraph.text.strip()
        ]
        return "\n".join(paragraphs)

    raise ValueError(
        f"Unsupported guide format '{suffix}'. Expected .md, .txt, or .docx"
    )


def resolve_mode_directory(mode_folder: Optional[str]) -> Path:
    if not mode_folder or mode_folder == "modular":
        cwd_modular = Path("generation_modes_modular")
        if cwd_modular.is_dir():
            return cwd_modular.resolve()
        # Notebooks often run with cwd under src/; anchor to repo root.
        repo_root = Path(__file__).resolve().parents[2]
        return repo_root / "generation_modes_modular"
    return Path(mode_folder)


def build_mode_guide_text(mode: str, mode_root: Path) -> str:
    """Load prompt instructions for a generation mode.

    Non-adaptive modes compose the shared base with mode-specific instructions.
    Adaptive uses only ``adaptive.md`` so it is not layered on top of the
    extraction-oriented base.
    """
    mode_root = Path(mode_root)
    mode_text = load_guide_instructions(mode_root / f"{mode}.md")
    if mode == "adaptive":
        return mode_text.strip()

    base_text = load_guide_instructions(mode_root / "base_strategy3.md")
    return f"{base_text}\n\n{mode_text}".strip()

def encode_pdf_to_base64(pdf_path: Path) -> str:
    """Return a base64 string of the PDF contents."""
    pdf_path = Path(pdf_path)
    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found at {pdf_path}")

    with pdf_path.open("rb") as handle:
        return base64.b64encode(handle.read()).decode("utf-8")


def select_reference_example(
    reference_json: Dict[str, Any], example_title: Optional[str] = None
) -> Any:
    """Pick a specific page from a reference volume if a title is provided."""
    if not example_title:
        return reference_json

    normalized = example_title.strip().casefold()

    pages = reference_json.get("Pages") if isinstance(reference_json, dict) else None
    if isinstance(pages, list):
        for page in pages:
            if not isinstance(page, dict):
                continue
            title = page.get("Title") or page.get("title")
            if isinstance(title, str) and title.strip().casefold() == normalized:
                return page

    data = reference_json.get("data") if isinstance(reference_json, dict) else None
    if isinstance(data, list):
        for page in data:
            if not isinstance(page, dict):
                continue
            title = page.get("Title") or page.get("title")
            if isinstance(title, str) and title.strip().casefold() == normalized:
                return page

    raise ValueError(f"Could not find a reference section titled '{example_title}'.")


def format_image_metadata(image_metadata: Sequence[Dict[str, Any]]) -> str:
    if not image_metadata:
        return ""

    lines = ["Image Reference Guide:"]

    for entry in image_metadata:
        desc = (
            f"\n- {entry.get('filename')} (id: {entry.get('image_id')}): "
            f"{entry.get('position')} of page {entry.get('page_num')}"
        )

        width_pct = float(entry.get("size", {}).get("width_pct", "0%").rstrip("%"))
        if width_pct > 80:
            desc += ", spanning nearly full width"
        elif width_pct < 30:
            desc += ", small inline image"

        if caption := entry.get("caption"):
            desc += f'\n  Caption: "{caption}"'

        nearby = entry.get("nearby_text", {})
        context_parts = [
            f'{pos}: "{nearby[pos][0][:60]}..."'
            for pos in ["above", "below"]
            if nearby.get(pos)
        ]
        if context_parts:
            desc += f"\n  Context ({', '.join(context_parts)})"

        lines.append(desc)

    lines.append("\n**Instructions for Image Placement:**")
    lines.append(
        "- Use the Context field to match each image to the correct location in the content"
    )
    lines.append("- Use standard Markdown image syntax: ![brief description](image_id)")
    lines.append("- Example: ![Diagram of cell membrane](image_page_1_1)")
    lines.append("- Never use placeholder syntax like {{image_id}} or HTML image tags")
    return "\n".join(lines)


def build_conversion_prompt(
    guide_text: str, example_json: Any, image_metadata_text: Optional[str] = None
) -> str:
    """Create the LLM prompt by combining guide instructions with a JSON example."""
    if not guide_text.strip():
        raise ValueError("Guide instructions are empty; cannot craft a prompt.")

    example_json_str = json.dumps(example_json, indent=2, ensure_ascii=False)

    template = f"""
    Your Role: iTELL Content Authoring Expert
    You are a specialized AI assistant expert in the iTELL framework. Your primary function is to convert source documents into perfectly structured iTELL JSON files.

    GUIDE TO iTELL JSON:
    {guide_text.strip()}

    REFERENCE iTELL JSON:
    ```json
    {example_json_str}
    ```

    Carefully analyze the provided source document and convert it into iTELL JSON.
    Only return JSON that adheres to the example schema and instructions above."""

    if image_metadata_text:
        template += f"""

    EXTRACTED IMAGES WITH CONTEXT:
    {image_metadata_text}"""

    return textwrap.dedent(template).strip()
