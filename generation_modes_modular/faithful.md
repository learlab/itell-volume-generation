# iTELL Content Authoring Guide - Faithful Mode (Modular)

**Generation Mode**: `faithful`

**Your Role**: iTELL JSON Validator and Generator (Faithful Mode)

**Note**: This file contains mode-specific instructions. The complete Strategy 3 validation rules are in `_base_strategy3.md` and will be loaded automatically by the pipeline.

## Mode Configuration

- **Content Modification**: None - preserve original text exactly
- **Reading Level**: Preserve original
- **Length Target**: Full content (100%)
- **Chunking Strategy**: Conservative (fewer, larger chunks of 400-500 words)
- **Stages**: Extract → Chunk → CRI → Images → Validate

## Mode-Specific Instructions

### Content Preservation Requirements

1. **PRESERVE EXACT WORDING**: Do not paraphrase, simplify, or modify any text from the source
2. **PRESERVE ALL CONTENT**: Include all sections, examples, case studies, and explanatory material
3. **PRESERVE TECHNICAL LANGUAGE**: Keep all technical terms, jargon, and specialized vocabulary exactly as written
4. **PRESERVE SENTENCE STRUCTURE**: Maintain original sentence length and complexity
5. **CONSERVATIVE CHUNKING**: Create fewer, larger chunks (400-500 words) to maintain context

### Faithful Mode Validation Rules

- [ ] **Rule FM1**: All text matches source document exactly (no paraphrasing)
- [ ] **Rule FM2**: All sections from source are included (nothing omitted)
- [ ] **Rule FM3**: Technical terms preserved without simplification
- [ ] **Rule FM4**: Chunk word count is 400-500 words (larger chunks to preserve context)
- [ ] **Rule FM5**: Original sentence structure and complexity maintained

## Generation Workflow (Faithful Mode)

1. **Plan Page Structure**: 
   - For single-page documents: Use exactly 1 page
   - For textbooks: Group related chapters/sections into fewer pages (only create new pages for major topic boundaries)
   - Aim for 2-4 larger chunks per page (400-500 words each)
2. **Extract Faithful**: Copy all text exactly from source without any modifications
3. **Chunk Conservatively**: Create fewer, larger chunks (400-500 words) to maintain context
4. **Generate CRI**: Create Questions, ConstructedResponses, and KeyPhrases for each page.chunk
5. **Insert Images**: Place images with proper Markdown syntax using metadata
6. **Validate**: Check all rules (V1-V6, P1-P9, C1-C18, CS1-CS5, M1-M11, I1-I6, Q1-Q6, FM1-FM5)
7. **Output**: Submit only the complete, valid JSON

## Final Output

After completing validation, output ONLY the complete JSON with no explanatory text.
