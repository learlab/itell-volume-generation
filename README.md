# itell-volume-generation

Standalone test harness for converting PDFs into iTELL JSON, including the modular mode system used by `itell-api`.

## What this repo is for

Use this repo to test prompt and pipeline behavior before wiring changes into the API or CMS. The current modular flow supports:

- `faithful`
- `simplified`
- `condensed`
- `generative`
- `interaction-heavy`

`generative` is intended for **course-outline PDFs or PPTX slide decks** where the model authors iTELL content from the outline rather than extracting textbook prose verbatim.

## Setup

### Prerequisites
- Python 3.8 or higher

### Installation

1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and configure one provider:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   OPENROUTER_API_KEY=your_openrouter_api_key_here

   OPENAI_MODEL=gpt-4o-mini
   OPENROUTER_MODEL=google/gemini-2.5-flash
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
   OPENROUTER_SITE_URL=https://yoursite.com
   OPENROUTER_APP_NAME=YourAppName
   ```

## Quick start

Run a named mode:

```bash
./generate_mode.sh generative path/to/course-outline.pptx
```

Or call the pipeline directly:

```bash
python -m src.pipeline.main \
  --input path/to/course-outline.pptx \
  --mode generative \
  --mode-folder modular \
  --reference-json prompts/reference.json \
  --output results/outline_generative.json
```

PDF inputs are uploaded to the model as PDFs. PPTX inputs are parsed locally into slide and speaker-note text, then sent to the same prompt as the outline source.

If you want to bypass the modular mode system and provide a custom guide directly, you can still use:

```bash
python -m src.pipeline.main \
  --input path/to/input.pdf \
  --guide prompts/guide_strategy3_validation.md \
  --reference-json prompts/reference.json \
  --output results/itell.json
```

## OpenRouter setup

- Provide only `OPENROUTER_API_KEY` (omit `OPENAI_API_KEY`) to automatically target `https://openrouter.ai/api/v1`.
- Override with `OPENROUTER_BASE_URL` or `--base-url` if needed.
- Most OpenRouter models use provider-scoped names such as `google/gemini-2.5-flash`.
- If you keep both OpenAI and OpenRouter keys, pass `--api-key` and `--base-url` explicitly.
