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

- [ ] **Rule P1**: Every page has Title field (string, Title Case)
- [ ] **Rule P2**: Every page has ReferenceSummary field (string or null)
- [ ] **Rule P3**: Every page has Content field (array with at least 1 chunk)
- [ ] **Rule P4**: Page titles use Title Case (e.g., "The Science of Psychology")

### Chunk-Level Validation

#### Universal Chunk Rules (both types)

- [ ] **Rule C1**: Every chunk has \_\_component field
- [ ] **Rule C2**: \_\_component value is exactly "page.chunk" or "page.plain-chunk" (no typos)
- [ ] **Rule C3**: Every chunk has Header field (string, Title Case)
- [ ] **Rule C4**: Every chunk has Text field (string, valid Markdown)
- [ ] **Rule C5**: Text field contains only valid Markdown (paragraphs separated by blank lines, **bold**, _italic_)
- [ ] **Rule C6**: Chunk word count is 150-500 words

#### page.chunk Specific Rules

- [ ] **Rule C7**: Every page.chunk has Question field (non-empty string)
- [ ] **Rule C8**: Every page.chunk has ConstructedResponse field (non-empty string)
- [ ] **Rule C9**: Every page.chunk has KeyPhrase field (non-empty string)
- [ ] **Rule C10**: Question is not a yes/no question
- [ ] **Rule C11**: ConstructedResponse is 1-3 sentences
- [ ] **Rule C12**: KeyPhrase contains 3-5 terms separated by commas
- [ ] **Rule C13**: KeyPhrase terms are noun phrases from the text

#### page.plain-chunk Specific Rules

- [ ] **Rule C14**: page.plain-chunk does NOT have Question field
- [ ] **Rule C15**: page.plain-chunk does NOT have ConstructedResponse field
- [ ] **Rule C16**: page.plain-chunk does NOT have KeyPhrase field

### Markdown Validation Rules

- [ ] **Rule M1**: Paragraphs are separated by blank lines
- [ ] **Rule M2**: Ampersands use `&` as-is (no encoding needed)
- [ ] **Rule M3**: Bold uses `**text**` syntax
- [ ] **Rule M4**: Italics use `*text*` syntax
- [ ] **Rule M5**: Math uses `$...$` for inline
- [ ] **Rule M6**: Math uses `$$...$$` for block equations
- [ ] **Rule M7**: Info callouts use blockquote structure:

```markdown
> **Title**
>
> Content
```

- [ ] **Rule M8**: Images use markdown syntax: `![description](image_id)`
- [ ] **Rule M9**: Image paths match image_id from metadata (format: `image_page_X_Y`)
- [ ] **Rule M10**: Image alt text (in brackets) contains caption or meaningful description

### Image Validation Rules (If Metadata Provided)

- [ ] **Rule I1**: All images from metadata are included in the JSON
- [ ] **Rule I2**: Each image uses correct `image_id` in Markdown format: `![description](image_id)`
- [ ] **Rule I3**: Images are placed in logical positions within text
- [ ] **Rule I4**: Images with captions use caption as alt text (in brackets)
- [ ] **Rule I5**: Images without captions have descriptive alt text (in brackets)
- [ ] **Rule I6**: No placeholder text like "[IMAGE]" remains in output
- [ ] **Rule I7**: Images use Markdown syntax `![alt text](image_id)`, not HTML tags

### Content Quality Rules

- [ ] **Rule Q1**: No citation markers like `[cite_start]` or `[cite: X]` in text
- [ ] **Rule Q2**: No image references or descriptions in text
- [ ] **Rule Q3**: Headers accurately describe chunk content
- [ ] **Rule Q4**: ConstructedResponse answers can be found in chunk text
- [ ] **Rule Q5**: KeyPhrases are actual phrases from the chunk text
- [ ] **Rule Q6**: No duplicate KeyPhrases within a chunk

## Markdown Transformation Rules

Apply these rules in order when converting source text to Markdown:

1. **Rule T1**: Separate paragraphs with blank lines
2. **Rule T2**: Keep ampersands as `&` (no encoding needed)
3. **Rule T3**: Convert bold text to `**text**`
4. **Rule T4**: Convert italic text to `*text*`
5. **Rule T5**: Convert image references to `![caption or description](image_id)`
6. **Rule T6**: Remove all `[cite_start]` and `[cite: N]` markers
7. **Rule T7**: Convert book/journal titles to `*Title*`
8. **Rule T8**: Convert inline math to `$formula$`
9. **Rule T9**: Convert block math to `$$formula$$`
10. **Rule T10**: Convert Learning Objectives sections to blockquote structure with bold header
11. **Rule T11**: Match each image to its metadata using page_num and position information
12. **Rule T12**: Place images between paragraphs with blank lines, not mid-sentence

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

### Error 10: Improper Markdown Formatting

**INVALID:**

```json
{
  "Text": "Psychology is the **scientific study** of *behavior*.- Observation\n- Experimentation\n- Analysis"
}
```

**Violated Rules:** C5, M1
**VALID:**

```json
{
  "Text": "Psychology is the **scientific study** of *behavior*.\n\nObservation, experimentation, and analysis are key methods."
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

**INVALID:**

```json
{
  "Text": "See the diagram below.\n\n<img src='image_page_2_1'>\n\nThis shows the process."
}
```

**Violated Rules:** M8, I7
**VALID:**

```json
{
  "Text": "See the diagram below.\n\n![Process diagram](image_page_2_1)\n\nThis shows the process."
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

**Violated Rules:** M10, I4 or I5
**VALID:**

```json
{
  "Text": "The diagram shows the cycle.\n\n![Diagram of the water cycle](image_page_7_2)"
}
```

## Self-Validation Checklist

Before outputting JSON, verify each category:

### Structure Validation

- [ ] All required volume fields present (V1-V6)
- [ ] All required page fields present (P1-P4)
- [ ] All required chunk fields present (C1-C16)
- [ ] Correct \_\_component values used (C2)

### Markdown Validation

- [ ] All Markdown properly formed (M1-M10)
- [ ] Paragraphs separated by blank lines (M1)
- [ ] Correct bold and italic syntax (M3-M4)
- [ ] Images use correct format (M8-M10)

### Content Validation

- [ ] No citation markers (Q1)
- [ ] No image placeholders like "[IMAGE]" (Q2, I6)
- [ ] Questions are open-ended (C10)
- [ ] KeyPhrases from actual text (Q5)

### Image Validation (If Metadata Provided)

- [ ] All images from metadata included (I1)
- [ ] Correct image_id format used (I2, M9)
- [ ] All images have alt text (M10, I4, I5)
- [ ] Images placed logically in text (I3)
- [ ] No placeholder text remains (I6)

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
