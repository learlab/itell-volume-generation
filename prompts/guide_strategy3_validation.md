# iTELL Content Authoring Guide - Strategy 3: Rule-Based Validation

**Your Role**: iTELL JSON Validator and Generator

Generate JSON that passes all validation rules, then self-check your output before submitting.

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
        ├── ReferenceSummary (string or null, required)
        └── Content (array, required)
            └── Chunk
                ├── __component (string, required, exactly "page.chunk" or "page.plain-chunk")
                ├── Header (string, required, Title Case)
                ├── Text (string, required, valid HTML)
                ├── Question (string, required for page.chunk only)
                ├── ConstructedResponse (string, required for page.chunk only)
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

- [ ] **Rule P1**: Every page has Title field (string, Title Case)
- [ ] **Rule P2**: Every page has ReferenceSummary field (string or null)
- [ ] **Rule P3**: Every page has Content field (array with at least 1 chunk)
- [ ] **Rule P4**: Page titles use Title Case (e.g., "The Science of Psychology")

### Chunk-Level Validation

#### Universal Chunk Rules (both types)
- [ ] **Rule C1**: Every chunk has __component field
- [ ] **Rule C2**: __component value is exactly "page.chunk" or "page.plain-chunk" (no typos)
- [ ] **Rule C3**: Every chunk has Header field (string, Title Case)
- [ ] **Rule C4**: Every chunk has Text field (string, valid HTML)
- [ ] **Rule C5**: Text field contains only valid HTML (no markdown)
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

### HTML Validation Rules

- [ ] **Rule H1**: All HTML tags are properly closed
- [ ] **Rule H2**: Ampersands are encoded as `&amp;`
- [ ] **Rule H3**: Less-than signs are encoded as `&lt;` (if present)
- [ ] **Rule H4**: Greater-than signs are encoded as `&gt;` (if present)
- [ ] **Rule H5**: Paragraphs use `<p>` tags (not markdown)
- [ ] **Rule H6**: Bold uses `<b>` tags (not `**` or `<strong>`)
- [ ] **Rule H7**: Italics use `<i>` tags (not `*` or `<em>`)
- [ ] **Rule H8**: Math uses `<span class="math-tex">\( ... \)</span>` for inline
- [ ] **Rule H9**: Math uses `<span class="math-tex">\[ ... \]</span>` for blocks
- [ ] **Rule H10**: Info callouts use exact structure:
```html
<section class="Info">
<h3 class="InfoTitle">Title</h3>
<p class="InfoContent">Content</p>
</section>
```
- [ ] **Rule H11**: Images use self-closing tag: `<img src="image_id" alt="description" />`
- [ ] **Rule H12**: Image src attributes match image_id from metadata (format: `image_page_X_Y`)
- [ ] **Rule H13**: Image alt attributes contain caption or meaningful description

### Image Validation Rules (If Metadata Provided)

- [ ] **Rule I1**: All images from metadata are included in the JSON
- [ ] **Rule I2**: Each image has correct `image_id` as src attribute
- [ ] **Rule I3**: Images are placed in logical positions within text
- [ ] **Rule I4**: Images with captions use caption as alt text
- [ ] **Rule I5**: Images without captions have descriptive alt text
- [ ] **Rule I6**: No placeholder text like "[IMAGE]" remains in output
- [ ] **Rule I7**: Image tags are self-closing with space before `/>`

### Content Quality Rules

- [ ] **Rule Q1**: No citation markers like `[cite_start]` or `[cite: X]` in text
- [ ] **Rule Q2**: No image references or descriptions in text
- [ ] **Rule Q3**: Headers accurately describe chunk content
- [ ] **Rule Q4**: ConstructedResponse answers can be found in chunk text
- [ ] **Rule Q5**: KeyPhrases are actual phrases from the chunk text
- [ ] **Rule Q6**: No duplicate KeyPhrases within a chunk

## HTML Transformation Rules

Apply these rules in order when converting source text to HTML:

1. **Rule T1**: Wrap each paragraph in `<p>` and `</p>` tags
2. **Rule T2**: Replace all `&` with `&amp;`
3. **Rule T3**: Replace `**text**` or __text__ with `<b>text</b>`
4. **Rule T4**: Replace `*text*` or _text_ with `<i>text</i>`
5. **Rule T5**: Convert image references to `<img src="image_id" alt="caption or description" />`
6. **Rule T6**: Remove all `[cite_start]` and `[cite: N]` markers
7. **Rule T7**: Convert book/journal titles to `<i>Title</i>`
8. **Rule T8**: Convert inline math to `<span class="math-tex">\( formula \)</span>`
9. **Rule T9**: Convert block math to `<span class="math-tex">\[ formula \]</span>`
10. **Rule T10**: Convert Learning Objectives sections to Info callout structure
11. **Rule T11**: Match each image to its metadata using page_num and position information
12. **Rule T12**: Place images between paragraphs, not mid-sentence

## Common Errors with Corrections

### Error 1: Missing Required Fields for page.chunk
**INVALID:**
```json
{
  "__component": "page.chunk",
  "Header": "Introduction",
  "Text": "<p>Content here</p>"
}
```
**Violated Rules:** C7, C8, C9
**VALID:**
```json
{
  "__component": "page.chunk",
  "Header": "Introduction",
  "Text": "<p>Content here</p>",
  "Question": "What is introduced in this section?",
  "ConstructedResponse": "This section introduces...",
  "KeyPhrase": "key term, main concept, important idea"
}
```

### Error 2: Citation Markers in Text
**INVALID:**
```json
{
  "Text": "[cite_start]<p>The Constitution was written in 1787[cite: 19].</p>"
}
```
**Violated Rules:** Q1
**VALID:**
```json
{
  "Text": "<p>The Constitution was written in 1787.</p>"
}
```

### Error 3: Unencoded Ampersand
**INVALID:**
```json
{
  "Text": "<p>Research & Development</p>"
}
```
**Violated Rules:** H2
**VALID:**
```json
{
  "Text": "<p>Research &amp; Development</p>"
}
```

### Error 4: Wrong __component Value
**INVALID:**
```json
{
  "__component": "chunk",
  "Header": "Title",
  "Text": "<p>Content</p>"
}
```
**Violated Rules:** C2
**VALID:**
```json
{
  "__component": "page.chunk",
  "Header": "Title",
  "Text": "<p>Content</p>",
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
  "Text": "<p>Citations here</p>",
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
  "Text": "<p>Citations here</p>"
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

### Error 10: Markdown Instead of HTML
**INVALID:**
```json
{
  "Text": "Psychology is the **scientific study** of *behavior*.\n\n- Observation\n- Experimentation\n- Analysis"
}
```
**Violated Rules:** C5, H5, H6, H7
**VALID:**
```json
{
  "Text": "<p>Psychology is the <b>scientific study</b> of <i>behavior</i>.</p><p>Observation, experimentation, and analysis are key methods.</p>"
}
```

### Error 11: Missing Image from Metadata
**INVALID:**
```json
{
  "Text": "<p>The cell membrane controls what enters and exits the cell.</p><p>This selective permeability is essential for cell function.</p>"
}
```
**Context:** Metadata provided image_page_3_1 with caption "Figure 2: Cell membrane structure"
**Violated Rules:** I1, T5
**VALID:**
```json
{
  "Text": "<p>The cell membrane controls what enters and exits the cell.</p><img src=\"image_page_3_1\" alt=\"Figure 2: Cell membrane structure\" /><p>This selective permeability is essential for cell function.</p>"
}
```

### Error 12: Wrong Image Tag Format
**INVALID:**
```json
{
  "Text": "<p>See the diagram below.</p><img src='image_page_2_1'><p>This shows the process.</p>"
}
```
**Violated Rules:** H11, I7
**VALID:**
```json
{
  "Text": "<p>See the diagram below.</p><img src=\"image_page_2_1\" alt=\"Process diagram\" /><p>This shows the process.</p>"
}
```

### Error 13: Image Placeholder Not Replaced
**INVALID:**
```json
{
  "Text": "<p>Photosynthesis occurs in chloroplasts.</p><p>[IMAGE: Chloroplast diagram]</p><p>The process involves light and dark reactions.</p>"
}
```
**Violated Rules:** I6, T5
**VALID:**
```json
{
  "Text": "<p>Photosynthesis occurs in chloroplasts.</p><img src=\"image_page_5_1\" alt=\"Chloroplast diagram\" /><p>The process involves light and dark reactions.</p>"
}
```

### Error 14: Wrong Image ID Format
**INVALID:**
```json
{
  "Text": "<p>Cell structure is complex.</p><img src=\"page_3_img_1.png\" alt=\"Cell diagram\" />"
}
```
**Violated Rules:** H12, I2
**VALID:**
```json
{
  "Text": "<p>Cell structure is complex.</p><img src=\"image_page_3_1\" alt=\"Cell diagram\" />"
}
```

### Error 15: Missing Alt Text
**INVALID:**
```json
{
  "Text": "<p>The diagram shows the cycle.</p><img src=\"image_page_7_2\" />"
}
```
**Violated Rules:** H13, I4 or I5
**VALID:**
```json
{
  "Text": "<p>The diagram shows the cycle.</p><img src=\"image_page_7_2\" alt=\"Diagram of the water cycle\" />"
}
```

## Self-Validation Checklist

Before outputting JSON, verify each category:

### Structure Validation
- [ ] All required volume fields present (V1-V6)
- [ ] All required page fields present (P1-P4)
- [ ] All required chunk fields present (C1-C16)
- [ ] Correct __component values used (C2)

### HTML Validation
- [ ] All HTML properly formed (H1-H13)
- [ ] Special characters encoded (H2-H4)
- [ ] No markdown syntax (H5-H7)
- [ ] Images use correct format (H11-H13)

### Content Validation
- [ ] No citation markers (Q1)
- [ ] No image placeholders like "[IMAGE]" (Q2, I6)
- [ ] Questions are open-ended (C10)
- [ ] KeyPhrases from actual text (Q5)

### Image Validation (If Metadata Provided)
- [ ] All images from metadata included (I1)
- [ ] Correct image_id format used (I2, H12)
- [ ] All images have alt text (H13, I4, I5)
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