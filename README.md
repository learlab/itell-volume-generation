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

## Setup

### Prerequisites
- Python 3.8 or higher

### Installation

1. **Clone the repository** (if not already done):
   ```bash
   git clone <repository-url>
   cd itell-volume-generation
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a `.env` file** in the project root:
   ```bash
   touch .env
   ```

6. **Configure environment variables** in `.env`:
   ```env
   # Required: Choose one API provider
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   OPENROUTER_API_KEY=your_openrouter_api_key_here

   # Optional: Model configuration
   OPENAI_MODEL=gpt-4o-mini
   OPENROUTER_MODEL=google/gemini-2.5-flash

   # Optional: Base URL overrides
   OPENAI_BASE_URL=https://api.openai.com/v1
   OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

   # Optional: OpenRouter-specific headers
   OPENROUTER_SITE_URL=https://yoursite.com
   OPENROUTER_APP_NAME=YourAppName
   ```

## CLI usage
Run the pipeline:
   ```bash
   python src/pipeline/main.py \
     --pdf src/resources/input.pdf \
     --guide src/resources/guide.md \
     --reference-json src/resources/reference.json \
     --image-dir results/extracted-images \
     --output results/itell.json
   ```

### OpenRouter setup
- Provide only `OPENROUTER_API_KEY` (omit `OPENAI_API_KEY`) to automatically target `https://openrouter.ai/api/v1`. Override with `OPENROUTER_BASE_URL` or `--base-url` if needed.
- Most OpenRouter models use provider-scoped names such as `google/gemini-2.5-flash` (the default when no model is specified) or `openrouter/openai/gpt-4o-mini`. Pass a custom name via `--model` or set `OPENROUTER_MODEL`.
- Optional headers recommended by OpenRouter can be set via `OPENROUTER_SITE_URL` (becomes `HTTP-Referer`) and `OPENROUTER_APP_NAME` (becomes `X-Title`).
- If you keep both OpenAI and OpenRouter keys, pass `--api-key`/`--base-url` explicitly so the correct provider is used.
