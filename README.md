# itell-volume-generation

Tests related to converting arbitrary PDFs into iTELL JSON format.

## Proof of concept
**Pipeline for Extracting Images & Embedding in ITELL JSON using Gemini API**

1. **Extract Images from PDF**
   - Use `PyMuPDF` to parse the PDF and extract **all images**.
   - Store images **locally** for now, with possible migration to a hosted DB later.
   - Extract and record **metadata** for each image:
     - Original *position* (coordinates) within the PDF page
     - Page number, image size, etc.

2. **Gemini API Integration**
   - **Send the PDF file** directly to the Gemini API.
   - In the prompt, include:
     - Reference to the **ITELL guide**
     - Example ITELL JSON
     - The **image metadata** (positions, page numbers, etc.)
   - **Goal:** Ensure Gemini embeds images within the ITELL JSON at their correct locations according to the extracted PDF positions.

## CLI usage
1. Install dependencies: `pip install -r requirements.txt`
2. Set `OPENAI_API_KEY` (or `OPENROUTER_API_KEY`) in `.env`.
3. Run the pipeline:
   ```bash
   python src/pipeline/main.py \
     --pdf src/resources/input.pdf \
     --guide src/resources/guide.docx \
     --reference-json src/resources/reference.json \
     --image-dir results/extracted-images \
     --output results/itell.json
   ```
4. Use `--example-title "Chapter 1: The U.S. Constitution"` to embed a specific reference section, and `--model/--max-tokens` to tune model usage. The script extracts every inline image into `--image-dir` and forwards their coordinates to the LLM as `<image id="..." page="..." x0="..." … />` tags; pass `--skip-image-extraction` to disable that step.

### OpenRouter setup
- Provide only `OPENROUTER_API_KEY` (omit `OPENAI_API_KEY`) to automatically target `https://openrouter.ai/api/v1`. Override with `OPENROUTER_BASE_URL` or `--base-url` if needed.
- Most OpenRouter models use provider-scoped names such as `openrouter/openai/gpt-4o-mini`. Pass this via `--model` or set `OPENROUTER_MODEL`.
- Optional headers recommended by OpenRouter can be set via `OPENROUTER_SITE_URL` (becomes `HTTP-Referer`) and `OPENROUTER_APP_NAME` (becomes `X-Title`).
- If you keep both OpenAI and OpenRouter keys, pass `--api-key`/`--base-url` explicitly so the correct provider is used.
