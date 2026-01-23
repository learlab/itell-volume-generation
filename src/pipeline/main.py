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
        encode_pdf_to_base64,
        format_image_metadata,
        load_guide_instructions,
        load_reference_json,
        select_reference_example,
    )
except ImportError:  # pragma: no cover - allows running as a script without module context
    import sys

    sys.path.append(str(Path(__file__).resolve().parents[1]))
    from pipeline.gemini_client import OpenAIClient  # type: ignore
    from pipeline.extract_images import ExtractImages  # type: ignore
    from pipeline.utils import (  # type: ignore
        build_conversion_prompt,
        encode_pdf_to_base64,
        format_image_metadata,
        load_guide_instructions,
        load_reference_json,
        select_reference_example,
    )


DEFAULT_GUIDE_PATH = Path("src/resources/guide.md")
DEFAULT_REFERENCE_PATH = Path("src/resources/reference.json")
DEFAULT_PDF_PATH = Path("src/resources/input.pdf")
DEFAULT_IMAGE_DIR = Path("results/extracted-images")
OPENROUTER_DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert a PDF into iTELL JSON via OpenAI-compatible APIs.")
    parser.add_argument("--pdf", type=Path, default=DEFAULT_PDF_PATH, help="Path to the PDF that should be converted.")
    parser.add_argument(
        "--guide",
        type=Path,
        default=None,
        help="Instruction guide file (.docx/.md/.txt) that the LLM should follow.",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["faithful", "simplified", "condensed", "hybrid", "interaction-heavy"],
        default=None,
        help="Generation mode (uses guide from generation_modes folder). Overrides --guide if specified.",
    )
    parser.add_argument(
        "--mode-folder",
        type=str,
        choices=["full", "modular", "original"],
        default="full",
        help="Which mode folder to use: 'full' (self-contained, default), 'modular' (requires combining), 'original' (old short versions)",
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
        help="Optional title from the reference JSON to use as the example section.",
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

    # Handle --mode flag
    workspace_root = Path(__file__).resolve().parents[2]
    guide_text = None
    
    if args.mode:
        if args.mode_folder == "modular":
            # Modular approach - combine mode + base files
            mode_file = workspace_root / "generation_modes_modular" / f"{args.mode}.md"
            base_file = workspace_root / "generation_modes_modular" / "_base_strategy3.md"
            
            if not mode_file.exists() or not base_file.exists():
                raise FileNotFoundError(
                    f"Modular mode files not found. Ensure both {mode_file} and {base_file} exist."
                )
            
            mode_content = mode_file.read_text()
            base_content = base_file.read_text()
            guide_text = f"{mode_content}\n\n---\n\n{base_content}"
            
            print(f"Using modular mode: {args.mode}")
            print(f"  Mode file: {mode_file}")
            print(f"  Base file: {base_file}")
            
        elif args.mode_folder == "full":
            # Full inclusion - self-contained files
            args.guide = workspace_root / "generation_modes_full" / f"{args.mode}.md"
            
            if not args.guide.exists():
                raise FileNotFoundError(f"Full mode file not found: {args.guide}")
            
            print(f"Using full mode: {args.mode}")
            print(f"Guide: {args.guide}")
            
    elif args.guide is None:
        # Use default guide if neither --mode nor --guide specified
        args.guide = DEFAULT_GUIDE_PATH

    reference_json = load_reference_json(args.reference_json)
    
    # Load guide text if not already loaded (modular mode loads it directly)
    if guide_text is None:
        guide_text = load_guide_instructions(args.guide)
    
    example_json = select_reference_example(reference_json, args.example_title)

    image_metadata_text = None
    if not args.skip_image_extraction:
        extractor = ExtractImages(str(args.pdf), str(args.image_dir))
        image_metadata = extractor.extract_img(str(args.pdf))
        extractor.save_metadata(str(args.image_dir / "metadata.json"))
        image_metadata_text = format_image_metadata(image_metadata) or None

    prompt = build_conversion_prompt(guide_text, example_json, image_metadata_text=image_metadata_text)
    pdf_b64 = encode_pdf_to_base64(args.pdf)

    openai_key = os.getenv("OPENAI_API_KEY")
    openrouter_key = os.getenv("OPENROUTER_API_KEY")

    api_key = args.api_key or openai_key or openrouter_key
    if not api_key:
        raise RuntimeError("Set OPENAI_API_KEY (or OPENROUTER_API_KEY) before running the pipeline.")

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

    result_json = client.generate_itell_json(pdf_filename=args.pdf.name, pdf_base64=pdf_b64, prompt=prompt)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result_json, encoding="utf-8")
        print(f"Wrote LLM response to {args.output}")
    else:
        print(result_json)

    return result_json


if __name__ == "__main__":
    main()
