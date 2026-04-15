# iTELL Content Authoring Guide - Strategy 3 Base

**This file contains the core Strategy 3 validation rules used by all generation modes.**

## JSON Schema Requirements

### Required Structure

```
Volume
├── Title (string, required)
├── Description (string, required, 1-2 sentences)
├── VolumeSummary (string, required, 4-8 sentences)
└── Pages (array, required)
    └── Page
        ├── Title (string, required, Title Case)
        └── Content (array, required)
            └── Chunk
                ├── __component (string, required, exactly "page.chunk" or "page.plain-chunk")
                ├── Header (string, required, Title Case)
                ├── Text (string, required, valid Markdown)
                ├── Question (string, required for page.chunk only)
                ├── Answer (string, required for page.chunk only)
                └── KeyPhrase (string, required for page.chunk only)
```

## Validation Rules (Check Each One)

### Volume-Level Validation

- [ ] **Rule V1**: Title field exists and is non-empty string
- [ ] **Rule V2**: Description field exists and is 1-2 complete sentences
- [ ] **Rule V3**: VolumeSummary field exists and is 4-8 complete sentences
- [ ] **Rule V4**: VolumeSummary covers topics from all pages
- [ ] **Rule V5**: VolumeSummary contains no bullet points or lists
- [ ] **Rule V6**: Pages field is an array with at least 1 page

### Page-Level Validation

**Note: "Page" in iTELL = logical organizational unit (chapter section), NOT physical PDF page**

- [ ] **Rule P1**: Every iTELL page has Title field (string, Title Case)
- [ ] **Rule P2**: Every iTELL page has Content field (array with at least 2 chunks, typically 3-6)
- [ ] **Rule P3**: iTELL page titles use Title Case (e.g., "The Science of Psychology")
- [ ] **Rule P5**: **iTELL pages are divided into multiple chunks by heading/topic - NOT one large chunk**
- [ ] **Rule P6**: **Create FEWER pages, not more - group related content into single pages with multiple chunks**
- [ ] **Rule P7**: **Create as FEW iTELL pages as possible - one iTELL page should comprise MANY PDF pages** - Group extensive content together; only split for major topic boundaries
- [ ] **Rule P8**: **For textbooks, only create a new page for major chapter boundaries or completely distinct topics**
- [ ] **Rule P9**: **When in doubt, add more chunks to an existing page rather than creating a new page**

#### When to Create a New Page

Create a new iTELL page ONLY when:
1. **Major chapter boundary**: Starting a completely new chapter with a distinct topic
2. **Completely unrelated topic**: The content has no relationship to previous pages
3. **Very large volume**: For textbooks with 20+ chapters, you may need multiple pages, but still group related chapters

#### When to Add Chunks to Existing Page

Add chunks to an existing page when:
1. **Related sections**: All content is part of the same topic/chapter
2. **Subsections**: Content is organized under the same main heading
3. **Single-page document**: For a single PDF page or small section, use exactly 1 page with multiple chunks
4. **Related concepts**: Content builds on or relates to previous chunks

### Chunk-Level Validation

#### Universal Chunk Rules (both types)

- [ ] **Rule C1**: Every chunk has __component field
- [ ] **Rule C2**: __component value is exactly "page.chunk" or "page.plain-chunk" (no typos)
- [ ] **Rule C3**: Every chunk has Header field (string, Title Case)
- [ ] **Rule C4**: Every chunk has Text field (string, valid Markdown)
- [ ] **Rule C5**: Text field contains properly formatted Markdown:
  - Blank lines only between distinct paragraphs
  - No line breaks within paragraphs
  - Appropriate **bold** and *italic* formatting
  - Preserved list indentation
- [ ] **Rule C6**: Chunk word count is 150-500 words
- [ ] **Rule C7**: **Each page has MULTIPLE chunks (3-6 typical) - do NOT put all content in one chunk**
- [ ] **Rule C8**: **Each chunk represents ONE heading/topic - do NOT combine multiple topics**

#### page.chunk Specific Rules

- [ ] **Rule C9**: Every page.chunk has Question field (non-empty string)
- [ ] **Rule C10**: Every page.chunk has Answer field (non-empty string)
- [ ] **Rule C11**: Every page.chunk has KeyPhrase field (non-empty string)
- [ ] **Rule C12**: Question is not a yes/no question
- [ ] **Rule C13**: Answer is 1-3 sentences
- [ ] **Rule C14**: KeyPhrase contains 3-5 terms separated by commas
- [ ] **Rule C15**: KeyPhrase terms are noun phrases from the text

#### page.plain-chunk Specific Rules

- [ ] **Rule C16**: page.plain-chunk does NOT have Question field
- [ ] **Rule C17**: page.plain-chunk does NOT have Answer field
- [ ] **Rule C18**: page.plain-chunk does NOT have KeyPhrase field

### Chunking Strategy Validation

- [ ] **Rule CS1**: Each iTELL page contains MULTIPLE chunks (minimum 2, typically 3-6)
- [ ] **Rule CS2**: Each chunk has a DISTINCT header representing one topic/heading
- [ ] **Rule CS3**: Content is divided by natural headings/subsections from source
- [ ] **Rule CS4**: Long sections (>500 words) are split into multiple chunks
- [ ] **Rule CS5**: Related but distinct topics are in separate chunks

### Markdown Validation Rules

- [ ] **Rule M1**: Blank lines (`\n\n`) only between distinct paragraphs, NOT within paragraphs
- [ ] **Rule M2**: Paragraphs flow continuously without internal line breaks
- [ ] **Rule M3**: Ampersands use `&` as-is (no encoding needed)
- [ ] **Rule M4**: Bold (`**text**`) applied appropriately for key terms, emphasis, important concepts
- [ ] **Rule M5**: Italics (`*text*`) used for book/journal titles, foreign words, definitions
- [ ] **Rule M6**: **Nested lists are FORBIDDEN.** The downstream CMS (Payload) cannot render nested lists — they will be lost or concatenated into a single garbled line. When the source has a hierarchical/outline structure (e.g. `4.1.`, `4.2.`, `4.1.1.`), flatten it into a SINGLE-LEVEL list and put the original numbering inside a bold prefix on each item. Each item MUST be on its own line, starting with `- `. Example:

  Source text with nested outline:

  ```
  4. Definitions
  4.1. MMT: Module Methods Task
  4.2. TEAMS: The Microsoft TEAMS application
  4.3. Clustermarket: The online scheduling software
  ```

  Correct flattened output:

  **4. Definitions**

  - **4.1.** MMT: Module Methods Task
  - **4.2.** TEAMS: The Microsoft TEAMS application
  - **4.3.** Clustermarket: The online scheduling software

  Never emit indented sub-bullets, never concatenate items on one line, never use `  -` or `\t-` for a sub-level.
- [ ] **Rule M7**: Math uses `$...$` for inline
- [ ] **Rule M8**: Math uses `$$...$$` for block equations
- [ ] **Rule M9**: Info callouts use blockquote structure:

  ```markdown
  > **Title**
  >
  > Content
  ```

- [ ] **Rule M10**: Images use markdown syntax: `![description](image_page_X_Y)` (standard Markdown)
- [ ] **Rule M11**: Image paths match image_id from metadata exactly (format: `image_page_X_Y`, e.g., image_page_2_1)
- [ ] **Rule M12**: Image alt text (in brackets) contains brief descriptive caption

### Image Validation Rules (If Metadata Provided)

- [ ] **Rule I1**: Images with captions (i.e., Figures) should be included in the JSON
- [ ] **Rule I2**: Each image uses correct `image_id` in Markdown format: `![description](image_page_X_Y)`
- [ ] **Rule I3**: Images are placed in logical positions within text with blank lines before/after
- [ ] **Rule I4**: Images have brief, descriptive captions generated by you as alt text (in brackets)
- [ ] **Rule I5**: No placeholder text like "[IMAGE]", `{{image}}` remains in output
- [ ] **Rule I6**: Images use standard Markdown syntax `![alt text](image_page_X_Y)`, NOT `{{image_page_X_Y}}` or HTML tags

### Content Quality Rules

- [ ] **Rule Q1**: No citation markers like `[cite_start]` or `[cite: X]` in text
- [ ] **Rule Q2**: No image references or descriptions in text
- [ ] **Rule Q3**: Headers accurately describe chunk content
- [ ] **Rule Q4**: Answer answers can be found in chunk text
- [ ] **Rule Q5**: KeyPhrases are actual phrases from the chunk text
- [ ] **Rule Q6**: No duplicate KeyPhrases within a chunk

## Markdown Transformation Rules

Apply these rules in order when converting source text to Markdown:

1. **Rule T1**: Separate distinct paragraphs with blank lines (`\n\n`)
2. **Rule T2**: Do NOT add line breaks within paragraphs - let text flow continuously
3. **Rule T3**: Keep ampersands as `&` (no encoding needed)
4. **Rule T4**: Apply bold `**text**` to key terms, important concepts, names, emphasis
5. **Rule T5**: Apply italic `*text*` to book/journal titles, foreign words, definitions
6. **Rule T6**: **Flatten any nested list into a single-level list.** Payload does not support nested lists. For every hierarchical item in the source (e.g. `4.1.`, `4.1.2.`), emit a single-level bullet whose content begins with a bold prefix holding the original numbering: `- **4.1.** item text`. Each bullet is its own line. If a parent heading precedes the list (e.g. `4. Definitions`), render the heading on its own line as bold text, followed by a blank line, followed by the flat list. Never produce indented sub-bullets.
7. **Rule T7**: Convert image references to `![caption or description](image_page_X_Y)`
8. **Rule T8**: Remove all `[cite_start]` and `[cite: N]` markers
9. **Rule T9**: Convert inline math to `$formula$`
10. **Rule T10**: Convert block math to `$$formula$$` (on separate lines with blank lines)
11. **Rule T11**: Convert Learning Objectives to blockquote structure with `> **Title**\n>\n> Content`
12. **Rule T12**: Match each image to its metadata using page_num and position information
13. **Rule T13**: Place images between paragraphs with blank lines, not mid-sentence
14. **Rule T14**: Convert all image references to standard Markdown: `![caption](image_page_X_Y)`
15. **Rule T15**: Never use `{{image_page_X_Y}}`, HTML `<img>`, or text references like "see Figure 1"

## Self-Validation Checklist

Before outputting JSON, verify each category:

### Structure Validation

- [ ] All required volume fields present (V1-V6)
- [ ] All required page fields present (P1-P9)
- [ ] All required chunk fields present (C1-C18)
- [ ] **Multiple chunks per page (CS1-CS7) - NOT one large chunk**
- [ ] **FEWER pages with MORE chunks - not many pages with few chunks (P6-P9)**
- [ ] Each chunk represents one topic/heading (CS2)
- [ ] Correct __component values used (C2)
- [ ] Page boundaries follow guidelines (only major chapter/topic breaks create new pages)

### Markdown Validation

- [ ] All Markdown properly formed (M1-M12)
- [ ] Blank lines only between distinct paragraphs, not within (M1, M2)
- [ ] Appropriate text formatting applied: **bold** and *italic* (M4, M5)
- [ ] No nested lists — hierarchical outlines flattened to single-level list with bold number prefix (M6)
- [ ] Correct bold and italic syntax (M4-M5)
- [ ] Images use correct format (M10-M12)

### Content Validation

- [ ] No citation markers (Q1)
- [ ] No image placeholders like "[IMAGE]" (Q2, I5)
- [ ] Questions are open-ended (C12)
- [ ] KeyPhrases from actual text (Q5)

### Image Validation (If Metadata Provided)

- [ ] Images with captions (Figures) should be included (I1)
- [ ] Correct image_id format used: `image_page_X_Y` (I2, M11)
- [ ] All images have brief descriptive captions in alt text (M12, I4)
- [ ] Images placed logically in text with blank lines (I3)
- [ ] No placeholder text remains: no `{{image}}`, `[IMAGE]`
- [ ] Standard Markdown syntax used: `![...](image_page_X_Y)` (I5, M10)

### JSON Syntax Validation

- [ ] All objects properly nested
- [ ] Commas between array elements
- [ ] Commas between object properties
- [ ] No trailing commas
- [ ] All strings properly quoted
- [ ] All brackets matched

## Generation Workflow

1. **Plan Page Structure**:
   - For single-page documents: Use exactly 1 page
   - For textbooks: Group related chapters/sections into fewer pages (only create new pages for major topic boundaries)
   - Aim for 3-6 chunks per page
2. **Generate**: Create JSON following all rules above, prioritizing fewer pages with more chunks
3. **Validate**: Check against all validation rules (V1-V6, P1-P8, C1-C18, CS1-CS5, M1-M12, I1-I6, Q1-Q6)
4. **Fix**: Correct any violated rules, especially:
   - Consolidate pages if you created too many (combine related content into single pages)
   - Ensure each page has 3-6 chunks
5. **Re-validate**: Verify all rules pass, especially page count (should be minimal)
6. **Output**: Submit only the complete, valid JSON

## Final Output

After completing validation, output ONLY the complete JSON with no explanatory text.
