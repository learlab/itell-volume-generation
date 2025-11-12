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


