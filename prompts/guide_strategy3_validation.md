# iTELL Content Authoring Guide - Strategy 3: Rule-Based Validation

**Your Role**: iTELL JSON Validator and Generator

Generate JSON that passes all validation rules, then self-check your output before submitting.

## JSON Schema Requirements

### Required Structure

Volume
├── Title (string, required)
├── Description (string, required, 1-2 sentences)
├── VolumeSummary (string, required, 4-8 sentences)
└── Pages (array, required)
    └── Page
        ├── Title (string, required, Title Case)
        ├── ReferenceSummary (string or null, required)
        └── Content (array, required)
            └── Chunk
                ├── __component (string, required, exactly "page.chunk" or "page.plain-chunk")
                ├── Header (string, required, Title Case)
                ├── Text (string, required, valid Markdown)
                ├── Question (string, required for page.chunk only)
                ├── ConstructedResponse (string, required for page.chunk only)
                └── KeyPhrase (string, required for page.chunk only)

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
- [ ] **Rule P2**: Every iTELL page has ReferenceSummary field (string or null)
- [ ] **Rule P3**: Every iTELL page has Content field (array with at least 2 chunks, typically 3-6)
- [ ] **Rule P4**: iTELL page titles use Title Case (e.g., "The Science of Psychology")
- [ ] **Rule P5**: **iTELL pages are divided into multiple chunks by heading/topic - NOT one large chunk**
- [ ] **Rule P6**: **Physical PDF page breaks do NOT determine chunk boundaries**

### Chunk-Level Validation

#### Universal Chunk Rules (both types)

- [ ] **Rule C1**: Every chunk has \_\_component field
- [ ] **Rule C2**: \_\_component value is exactly "page.chunk" or "page.plain-chunk" (no typos)
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
- [ ] **Rule C10**: Every page.chunk has ConstructedResponse field (non-empty string)
- [ ] **Rule C11**: Every page.chunk has KeyPhrase field (non-empty string)
- [ ] **Rule C12**: Question is not a yes/no question
- [ ] **Rule C13**: ConstructedResponse is 1-3 sentences
- [ ] **Rule C14**: KeyPhrase contains 3-5 terms separated by commas
- [ ] **Rule C15**: KeyPhrase terms are noun phrases from the text

#### page.plain-chunk Specific Rules

- [ ] **Rule C16**: page.plain-chunk does NOT have Question field
- [ ] **Rule C17**: page.plain-chunk does NOT have ConstructedResponse field
- [ ] **Rule C18**: page.plain-chunk does NOT have KeyPhrase field

### Chunking Strategy Validation

- [ ] **Rule CS1**: Each iTELL page contains MULTIPLE chunks (minimum 2, typically 3-6)
- [ ] **Rule CS2**: Each chunk has a DISTINCT header representing one topic/heading
- [ ] **Rule CS3**: Content is divided by natural headings/subsections from source
- [ ] **Rule CS4**: Long sections (>500 words) are split into multiple chunks
- [ ] **Rule CS5**: Related but distinct topics are in separate chunks
- [ ] **Rule CS6**: **Chunks are NOT split by PDF page breaks - only by topic/heading changes**
- [ ] **Rule CS7**: **Content on same topic stays together even if it spans multiple PDF pages**

### Markdown Validation Rules

- [ ] **Rule M1**: Blank lines (`\n\n`) only between distinct paragraphs, NOT within paragraphs
- [ ] **Rule M2**: Paragraphs flow continuously without internal line breaks
- [ ] **Rule M3**: Ampersands use `&` as-is (no encoding needed)
- [ ] **Rule M4**: Bold (`**text**`) applied appropriately for key terms, emphasis, important concepts
- [ ] **Rule M5**: Italics (`*text*`) used for book/journal titles, foreign words, definitions
- [ ] **Rule M6**: List indentation preserved (2 spaces per nested level)
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
- [ ] **Rule M12**: Image alt text (in brackets) contains full caption or meaningful description

### Image Validation Rules (If Metadata Provided)

- [ ] **Rule I1**: **ALL images with captions from metadata are included in the JSON (CRITICAL)**
- [ ] **Rule I2**: Each image uses correct `image_id` in Markdown format: `![caption](image_page_X_Y)`
- [ ] **Rule I3**: Images are placed in logical positions within text with blank lines before/after
- [ ] **Rule I4**: Images with captions use **full caption** as alt text (in brackets)
- [ ] **Rule I5**: Images without captions have descriptive alt text (in brackets)
- [ ] **Rule I6**: No placeholder text like "[IMAGE]", `{{image}}`, or "see Figure X" remains in output
- [ ] **Rule I7**: Images use standard Markdown syntax `![alt text](image_page_X_Y)`, NOT `{{image_page_X_Y}}` or HTML tags
- [ ] **Rule I8**: Never skip images that have captions - they are essential content

### Content Quality Rules

- [ ] **Rule Q1**: No citation markers like `[cite_start]` or `[cite: X]` in text
- [ ] **Rule Q2**: No image references or descriptions in text
- [ ] **Rule Q3**: Headers accurately describe chunk content
- [ ] **Rule Q4**: ConstructedResponse answers can be found in chunk text
- [ ] **Rule Q5**: KeyPhrases are actual phrases from the chunk text
- [ ] **Rule Q6**: No duplicate KeyPhrases within a chunk

## Markdown Transformation Rules

Apply these rules in order when converting source text to Markdown:

1. **Rule T1**: Separate distinct paragraphs with blank lines (`\n\n`)
2. **Rule T2**: Do NOT add line breaks within paragraphs - let text flow continuously
3. **Rule T3**: Keep ampersands as `&` (no encoding needed)
4. **Rule T4**: Apply bold `**text**` to key terms, important concepts, names, emphasis
5. **Rule T5**: Apply italic `*text*` to book/journal titles, foreign words, definitions
6. **Rule T6**: Preserve list indentation using 2 spaces per nested level
7. **Rule T7**: Convert image references to `![caption or description](image_page_X_Y)`
8. **Rule T8**: Remove all `[cite_start]` and `[cite: N]` markers
9. **Rule T9**: Convert inline math to `$formula$`
10. **Rule T10**: Convert block math to `$$formula$$` (on separate lines with blank lines)
11. **Rule T11**: Convert Learning Objectives to blockquote structure with `> **Title**\n>\n> Content`
12. **Rule T12**: Match each image to its metadata using page_num and position information
13. **Rule T13**: Place images between paragraphs with blank lines, not mid-sentence
14. **Rule T14**: Convert all image references to standard Markdown: `![caption](image_page_X_Y)`
15. **Rule T15**: Never use `{{image_page_X_Y}}`, HTML `<img>`, or text references like "see Figure 1"

## Common Errors with Corrections

### Error 1: Missing Required Fields for page.chunk

**INVALID:**

```json
{
  "__component": "page.chunk",
  "Header": "Introduction",
  "Text": "Content here"
}
```

**Violated Rules:** C7, C8, C9
**VALID:**

```json
{
  "__component": "page.chunk",
  "Header": "Introduction",
  "Text": "Content here",
  "Question": "What is introduced in this section?",
  "ConstructedResponse": "This section introduces...",
  "KeyPhrase": "key term, main concept, important idea"
}
```

### Error 2: Citation Markers in Text

**INVALID:**

```json
{
  "Text": "[cite_start]The Constitution was written in 1787[cite: 19]."
}
```

**Violated Rules:** Q1
**VALID:**

```json
{
  "Text": "The Constitution was written in 1787."
}
```

### Error 3: Ampersand Handling

**INVALID:**

```json
{
  "Text": "Research &amp; Development"
}
```

**Violated Rules:** M2
**VALID:**

```json
{
  "Text": "Research & Development"
}
```

### Error 4: Wrong \_\_component Value

**INVALID:**

```json
{
  "__component": "chunk",
  "Header": "Title",
  "Text": "Content"
}
```

**Violated Rules:** C2
**VALID:**

```json
{
  "__component": "page.chunk",
  "Header": "Title",
  "Text": "Content",
  "Question": "...",
  "ConstructedResponse": "...",
  "KeyPhrase": "..."
}
```

### Error 5: Yes/No Question

**INVALID:**

```json
{
  "Question": "Is psychology a science?"
}
```

**Violated Rules:** C10
**VALID:**

```json
{
  "Question": "Why is psychology considered a science?"
}
```

### Error 6: Vague KeyPhrases Not From Text

**INVALID:**

```json
{
  "KeyPhrase": "important concepts, key ideas, main points"
}
```

**Violated Rules:** Q5
**VALID:**

```json
{
  "KeyPhrase": "systematic observation, empirical research, scientific method"
}
```

### Error 7: Lowercase Header

**INVALID:**

```json
{
  "Header": "introduction to psychology"
}
```

**Violated Rules:** C3, P4
**VALID:**

```json
{
  "Header": "Introduction to Psychology"
}
```

### Error 8: Extra Fields on page.plain-chunk

**INVALID:**

```json
{
  "__component": "page.plain-chunk",
  "Header": "References",
  "Text": "Citations here",
  "Question": "What sources were cited?",
  "ConstructedResponse": "Multiple sources...",
  "KeyPhrase": "references, citations"
}
```

**Violated Rules:** C14, C15, C16
**VALID:**

```json
{
  "__component": "page.plain-chunk",
  "Header": "References",
  "Text": "Citations here"
}
```

### Error 9: Missing Volume Summary

**INVALID:**

```json
{
  "Title": "Psychology Textbook",
  "Description": "A textbook about psychology.",
  "Pages": [...]
}
```

**Violated Rules:** V3
**VALID:**

```json
{
  "Title": "Psychology Textbook",
  "Description": "A textbook about psychology.",
  "VolumeSummary": "This volume covers the foundations of psychology as a scientific discipline. Topics include research methods, cognitive processes, developmental psychology, and social behavior. Students learn to apply the scientific method to understand human behavior and mental processes.",
  "Pages": [...]
}
```

### Error 10: Extra Line Breaks Within Paragraphs

**INVALID:**

```json
{
  "Text": "Psychology is the scientific study of behavior.\nIt emerged in the 19th century.\nResearchers use various methods."
}
```

**Violated Rules:** M1, M2, T2
**VALID:**

```json
{
  "Text": "Psychology is the scientific study of behavior. It emerged in the 19th century. Researchers use various methods.\n\nThe field has evolved significantly over time."
}
```

### Error 10b: Missing Text Formatting

**INVALID:**

```json
{
  "Text": "The term psychology comes from psyche and logos. B.F. Skinner introduced operant conditioning."
}
```

**Violated Rules:** M4, M5, T4
**VALID:**

```json
{
  "Text": "The term **psychology** comes from *psyche* and *logos*. **B.F. Skinner** introduced **operant conditioning**."
}
```

### Error 10c: Lost List Indentation

**INVALID:**

```json
{
  "Text": "Research methods include:\n- Observation\n- Experiment\n- Control group\n- Experimental group\n- Analysis"
}
```

**Violated Rules:** M6, T6
**VALID:**

```json
{
  "Text": "Research methods include:\n\n- Observation\n- Experiment\n  - Control group\n  - Experimental group\n- Analysis"
}
```

### Error 11: Missing Image from Metadata

**INVALID:**

```json
{
  "Text": "The cell membrane controls what enters and exits the cell.\n\nThis selective permeability is essential for cell function."
}
```

**Context:** Metadata provided image_page_3_1 with caption "Figure 2: Cell membrane structure"
**Violated Rules:** I1, T5
**VALID:**

```json
{
  "Text": "The cell membrane controls what enters and exits the cell.\n\n![Figure 2: Cell membrane structure](image_page_3_1)\n\nThis selective permeability is essential for cell function."
}
```

### Error 12: Wrong Image Format

**INVALID (HTML tag):**

```json
{
  "Text": "See the diagram below.\n\n<img src='image_page_2_1'>\n\nThis shows the process."
}
```

**INVALID (Double brace placeholder):**

```json
{
  "Text": "The interface is shown below.\n\n{{image_page_4_1}}\n\nThis interface is user-friendly."
}
```

**INVALID (Text reference):**

```json
{
  "Text": "The graphical user interface (see Figure 1) requires no programming knowledge."
}
```

**Violated Rules:** M10, I7, T14, T15
**VALID:**

```json
{
  "Text": "See the diagram below.\n\n![Figure 1: Process diagram showing the workflow](image_page_2_1)\n\nThis shows the process."
}
```

### Error 13: Image Placeholder Not Replaced

**INVALID:**

```json
{
  "Text": "Photosynthesis occurs in chloroplasts.\n\n[IMAGE: Chloroplast diagram]\n\nThe process involves light and dark reactions."
}
```

**Violated Rules:** I6, T5
**VALID:**

```json
{
  "Text": "Photosynthesis occurs in chloroplasts.\n\n![Chloroplast diagram](image_page_5_1)\n\nThe process involves light and dark reactions."
}
```

### Error 14: Wrong Image ID Format

**INVALID:**

```json
{
  "Text": "Cell structure is complex.\n\n![Cell diagram](page_3_img_1.png)"
}
```

**Violated Rules:** M9, I2
**VALID:**

```json
{
  "Text": "Cell structure is complex.\n\n![Cell diagram](image_page_3_1)"
}
```

### Error 15: Missing Alt Text

**INVALID:**

```json
{
  "Text": "The diagram shows the cycle.\n\n[](image_page_7_2)"
}
```

**Violated Rules:** M12, I4 or I5
**VALID:**

```json
{
  "Text": "The diagram shows the cycle.\n\n![Diagram of the water cycle](image_page_7_2)"
}
```

### Error 16: All Content in One Chunk (CRITICAL)

**INVALID:**

```json
{
  "Title": "Cell Biology",
  "ReferenceSummary": null,
  "Content": [
    {
      "__component": "page.chunk",
      "Header": "Cell Biology",
      "Text": "Learning Objectives: Define cell structure. Explain organelles.\n\nCells are the basic units of life. They have various structures including the cell membrane, nucleus, and mitochondria.\n\nThe cell membrane controls what enters and exits. The nucleus contains DNA. Mitochondria produce energy.\n\nOrganelles work together to maintain cell function. Each has a specific role in cellular processes.",
      "Question": "What are the main parts of a cell?",
      "ConstructedResponse": "The main parts include cell membrane, nucleus, and mitochondria.",
      "KeyPhrase": "cell structure, organelles, cell membrane, nucleus"
    }
  ]
}
```

**Violated Rules:** CS1, CS2, CS3, P3, P5
**VALID:**

```json
{
  "Title": "Cell Biology",
  "ReferenceSummary": null,
  "Content": [
    {
      "__component": "page.plain-chunk",
      "Header": "Learning Objectives",
      "Text": "> **Learning Objectives**\n>\n> Define cell structure\n> Explain organelles"
    },
    {
      "__component": "page.chunk",
      "Header": "Introduction to Cells",
      "Text": "**Cells** are the basic units of life. They have various structures including the **cell membrane**, **nucleus**, and **mitochondria**.",
      "Question": "What are cells?",
      "ConstructedResponse": "Cells are the basic units of life with various structures.",
      "KeyPhrase": "cells, basic units of life, cell structure"
    },
    {
      "__component": "page.chunk",
      "Header": "Cell Membrane",
      "Text": "The **cell membrane** controls what enters and exits the cell. This selective permeability is essential for maintaining cellular homeostasis.",
      "Question": "What is the function of the cell membrane?",
      "ConstructedResponse": "The cell membrane controls what enters and exits the cell.",
      "KeyPhrase": "cell membrane, selective permeability, cellular homeostasis"
    },
    {
      "__component": "page.chunk",
      "Header": "Nucleus and Mitochondria",
      "Text": "The **nucleus** contains DNA and controls cell activities. **Mitochondria** produce energy through cellular respiration, earning them the nickname 'powerhouses of the cell.'",
      "Question": "What are the roles of the nucleus and mitochondria?",
      "ConstructedResponse": "The nucleus contains DNA and controls cell activities, while mitochondria produce energy.",
      "KeyPhrase": "nucleus, mitochondria, DNA, cellular respiration, energy production"
    },
    {
      "__component": "page.chunk",
      "Header": "Organelle Interactions",
      "Text": "**Organelles** work together to maintain cell function. Each has a specific role in cellular processes, and their coordination is essential for cell survival.",
      "Question": "How do organelles work together?",
      "ConstructedResponse": "Organelles coordinate their specific roles to maintain cell function and survival.",
      "KeyPhrase": "organelles, cellular processes, cell function, coordination"
    }
  ]
}
```

**Notice:**
- Invalid has only 1 chunk containing all content
- Valid has 5 chunks, each with a distinct topic/heading
- Learning objectives separated into plain-chunk
- Each major concept gets its own chunk

## Self-Validation Checklist

Before outputting JSON, verify each category:

### Structure Validation

- [ ] All required volume fields present (V1-V6)
- [ ] All required page fields present (P1-P6)
- [ ] All required chunk fields present (C1-C18)
- [ ] **Multiple chunks per page (CS1-CS7) - NOT one large chunk**
- [ ] Each chunk represents one topic/heading (CS2)
- [ ] Correct \_\_component values used (C2)

### Markdown Validation

- [ ] All Markdown properly formed (M1-M12)
- [ ] Blank lines only between distinct paragraphs, not within (M1, M2)
- [ ] Appropriate text formatting applied: **bold** and *italic* (M4, M5)
- [ ] List indentation preserved (M6)
- [ ] Correct bold and italic syntax (M4-M5)
- [ ] Images use correct format (M10-M12)

### Content Validation

- [ ] No citation markers (Q1)
- [ ] No image placeholders like "[IMAGE]" (Q2, I6)
- [ ] Questions are open-ended (C10)
- [ ] KeyPhrases from actual text (Q5)

### Image Validation (If Metadata Provided)

- [ ] **ALL images with captions from metadata included (I1, I8) - CRITICAL**
- [ ] Correct image_id format used: `image_page_X_Y` (I2, M9)
- [ ] All images have full captions or descriptions in alt text (M10, I4, I5)
- [ ] Images placed logically in text with blank lines (I3)
- [ ] No placeholder text remains: no `{{image}}`, `[IMAGE]`, or "see Figure X" (I6, T14)
- [ ] Standard Markdown syntax used: `![...](image_page_X_Y)` (I7, M8, T13)

### JSON Syntax Validation

- [ ] All objects properly nested
- [ ] Commas between array elements
- [ ] Commas between object properties
- [ ] No trailing commas
- [ ] All strings properly quoted
- [ ] All brackets matched

## Generation Workflow

1. **Generate**: Create JSON following all rules above
2. **Validate**: Check against all validation rules (V1-V6, P1-P4, C1-C16, H1-H10, Q1-Q6)
3. **Fix**: Correct any violated rules
4. **Re-validate**: Verify all rules pass
5. **Output**: Submit only the complete, valid JSON

## Final Output

After completing validation, output ONLY the complete JSON with no explanatory text.
