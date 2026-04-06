from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional, Sequence

from dotenv import load_dotenv

try:
    from .gemini_client import OpenAIClient
    from .extract_images import ExtractImages
    from .utils import (
        build_conversion_prompt,
        build_mode_guide_text,
        encode_pdf_to_base64,
        format_image_metadata,
        load_guide_instructions,
        load_reference_json,
        resolve_mode_directory,
        select_reference_example,
    )
except ImportError:  # pragma: no cover
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from pipeline.gemini_client import OpenAIClient  # type: ignore
    from pipeline.extract_images import ExtractImages  # type: ignore
    from pipeline.utils import (  # type: ignore
        build_conversion_prompt,
        build_mode_guide_text,
        encode_pdf_to_base64,
        format_image_metadata,
        load_guide_instructions,
        load_reference_json,
        resolve_mode_directory,
        select_reference_example,
    )


DEFAULT_GUIDE_PATH = Path("prompts/guide_strategy3_validation.md")
DEFAULT_REFERENCE_PATH = Path("prompts/reference.json")
DEFAULT_PDF_PATH = Path("data/input.pdf")
DEFAULT_IMAGE_DIR = Path("results/extracted-images")
OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert a PDF into iTELL JSON via OpenAI-compatible APIs."
    )
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF_PATH, help="Path to the PDF that should be converted.")
    parser.add_argument(
        "--guide",
        type=Path,
        default=DEFAULT_GUIDE_PATH,
        help="Instruction guide file (.docx/.md/.txt) when not using a named mode.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        default=None,
        help="Named generation mode file to load from the mode folder, e.g. generative or faithful.",
    )
    parser.add_argument(
        "--mode-folder",
        type=str,
        default="modular",
        help="Mode directory alias or path. 'modular' resolves to generation_modes_modular.",
    )
    parser.add_argument(
        "--reference-json",
        type=Path,
        default=DEFAULT_REFERENCE_PATH,
        help="Reference iTELL JSON file that will be embedded in the prompt.",
    )
    parser.add_argument(
        "--example-title",
        type=str,
        default=None,
        help="Optional page title from the reference JSON to use as the example section.",
    )
    parser.add_argument("--output", type=Path, default=None, help="Optional file path to write the LLM response JSON.")
    parser.add_argument("--model", type=str, default=None, help="Override the model name (defaults to OPENAI_MODEL env).")
    parser.add_argument("--api-key", type=str, default=None, help="Explicit API key (defaults to env OPENAI_API_KEY).")
    parser.add_argument("--base-url", type=str, default=None, help="Override the OpenAI-compatible base URL.")
    parser.add_argument(
        "--image-dir",
        type=Path,
        default=DEFAULT_IMAGE_DIR,
        help="Directory to store extracted images + metadata before LLM conversion.",
    )
    parser.add_argument(
        "--skip-image-extraction",
        action="store_true",
        help="By default images are extracted to generate coordinate tags. Set this flag to skip extraction.",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=4_000,
        help="Maximum completion tokens for the chat.completions call.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> str:
    load_dotenv()
    args = parse_args(argv)

    reference_json = load_reference_json(args.reference_json)
    example_json = select_reference_example(reference_json, args.example_title)

    if args.mode:
        mode_root = resolve_mode_directory(args.mode_folder)
        guide_text = build_mode_guide_text(args.mode, mode_root)
    else:
        guide_text = load_guide_instructions(args.guide)

    image_metadata_text = None
    if not args.skip_image_extraction:
        extractor = ExtractImages(str(args.pdf), str(args.image_dir))
        image_metadata = extractor.extract_img()
        extractor.save_metadata(str(args.image_dir / "metadata.json"))
        image_metadata_text = format_image_metadata(image_metadata) or None

    prompt = build_conversion_prompt(
        guide_text, example_json, image_metadata_text=image_metadata_text
    )
    pdf_b64 = encode_pdf_to_base64(args.pdf)

    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    api_key = args.api_key or openai_key or openrouter_key
    if not api_key:
        raise RuntimeError(
            "Set OPENAI_API_KEY (or OPENROUTER_API_KEY) before running the pipeline."
        )

    using_openrouter = False
    if openrouter_key and not args.api_key and not openai_key:
        using_openrouter = True
    elif args.base_url and "openrouter" in args.base_url:
        using_openrouter = True

    openrouter_base_url_env = os.getenv("OPENROUTER_BASE_URL")
    openai_base_url_env = os.getenv("OPENAI_BASE_URL")
    if using_openrouter:
        base_url = args.base_url or openrouter_base_url_env or OPENROUTER_DEFAULT_BASE_URL
    else:
        base_url = args.base_url or openai_base_url_env or openrouter_base_url_env

    if args.model:
        model = args.model
    elif using_openrouter:
        model = os.getenv("OPENROUTER_MODEL") or os.getenv("OPENAI_MODEL") or "google/gemini-2.5-flash"
    else:
        model = os.getenv("OPENAI_MODEL") or "gpt-5-mini"

    default_headers = None
    if using_openrouter:
        headers = {}
        referer = os.getenv("OPENROUTER_SITE_URL")
        app_name = os.getenv("OPENROUTER_APP_NAME")
        if referer:
            headers["HTTP-Referer"] = referer
        if app_name:
            headers["X-Title"] = app_name
        default_headers = headers or None

    client = OpenAIClient(
        model=model,
        api_key=api_key,
        base_url=base_url,
        max_completion_tokens=args.max_tokens,
        default_headers=default_headers,
    )

    result_json = client.generate_itell_json(
        pdf_filename=args.pdf.name,
        pdf_base64=pdf_b64,
        prompt=prompt,
    )

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result_json, encoding="utf-8")
        print(f"Wrote LLM response to {args.output}")
    else:
        print(result_json)

    return result_json


if __name__ == "__main__":
    main()
