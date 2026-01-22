# iTELL Content Authoring Guide - Interaction-Heavy Mode (Modular)

**Generation Mode**: `interaction-heavy`

**Your Role**: iTELL JSON Validator and Generator (Interaction-Heavy Mode)

**Note**: This file contains mode-specific instructions. The complete Strategy 3 validation rules are in `_base_strategy3.md` and will be loaded automatically by the pipeline.

## Mode Configuration

- **Content Modification**: Minimal
- **Reading Level**: Preserve original
- **Length Target**: Same overall length (100%)
- **Chunking Strategy**: Very Aggressive (many small chunks of 100-250 words)
- **Stages**: Extract → Micro-Chunk → Enhanced CRI → Images → Validate
- **Focus**: Maximize learning interactions per page

## Mode-Specific Instructions

### Interaction-Heavy Philosophy

**Maximize student engagement through frequent, high-quality learning checkpoints.**

The goal is to create MORE opportunities for students to:
- Answer questions about what they just read
- Generate constructed responses
- Identify and work with key concepts
- Self-assess comprehension frequently

### Micro-Chunking Requirements

1. **VERY SMALL CHUNKS**: Target 100-250 words per chunk (vs. standard 200-400)
   - Each chunk = one focused concept or idea
   - Students read less before being asked to engage

2. **MORE CHUNKS PER PAGE**: Aim for 6-12 chunks per page (vs. standard 3-6)
   - More frequent interaction points
   - Better pacing for active learning

3. **MAXIMIZE page.chunk USAGE**: 
   - Use page.chunk for almost everything (80-90% of chunks)
   - Use page.plain-chunk ONLY for: Learning Objectives, References, very short transitions
   - Every substantial concept gets a question

4. **STRATEGIC CHUNKING**:
   - Split long paragraphs if they contain multiple distinct ideas
   - Each example or explanation becomes its own chunk
   - Break at natural comprehension checkpoints

### Enhanced CRI (Questions, Responses, KeyPhrases) Requirements

1. **VARIED QUESTION TYPES** (rotate through these):
   - **Conceptual**: "What is the main idea of [concept]?"
   - **Application**: "How would you apply [concept] to [scenario]?"
   - **Analysis**: "What is the relationship between [concept A] and [concept B]?"
   - **Synthesis**: "How does [concept] relate to what you learned earlier?"
   - **Evaluation**: "Why is [concept] important for understanding [topic]?"

2. **PROGRESSIVE DIFFICULTY**:
   - Early chunks: simpler recall questions
   - Middle chunks: application and analysis
   - Later chunks: synthesis and evaluation

3. **HIGHLY FOCUSED KEYPHRASES**:
   - Only 3-4 terms per chunk (vs. 3-5 in standard)
   - Most important terms for that micro-concept
   - Each chunk builds student's mental vocabulary incrementally

4. **CONCISE CONSTRUCTED RESPONSES**:
   - Keep to 1-2 sentences
   - Model clear, focused answers
   - Guide students on expected response length

### Interaction-Heavy Mode Validation Rules

- [ ] **Rule IH1**: Chunk word count is 100-250 words (smaller than standard)
- [ ] **Rule IH2**: Each page has 6-12 chunks (more than standard 3-6)
- [ ] **Rule IH3**: 80-90% of chunks are page.chunk (not plain-chunk)
- [ ] **Rule IH4**: Every page.chunk has high-quality, varied Question
- [ ] **Rule IH5**: Questions vary in cognitive level (not all recall)
- [ ] **Rule IH6**: KeyPhrases focus on 3-4 most essential terms
- [ ] **Rule IH7**: Each chunk focuses on exactly ONE concept or idea

### Interaction-Heavy Examples

**Standard Mode (1 chunk - 350 words):**
```
Chunk 1: "The Scientific Method in Psychology"
[Contains: definition of scientific method, steps in the method, example research, and importance]
Question: "What is the scientific method and why is it important in psychology?"
```

**Interaction-Heavy Mode (3 chunks from same content):**
```
Chunk 1: "Defining the Scientific Method" (120 words)
[Contains: definition and basic principles]
Question: "What makes the scientific method different from other ways of gaining knowledge?"

Chunk 2: "Steps in Psychological Research" (110 words)
[Contains: observation, hypothesis, testing, analysis]
Question: "How do psychologists move from observation to testing their ideas?"

Chunk 3: "Why Psychology Needs Science" (120 words)
[Contains: importance, examples of misconceptions corrected by research]
Question: "Why can't psychologists rely only on intuition and common sense?"
```

**Notice:**
- Same content, divided into 3 smaller, focused chunks
- More questions = more engagement points
- Each question targets one specific aspect
- Students check understanding more frequently


## Generation Workflow (Interaction-Heavy Mode)

1. **Plan Page Structure**: 
   - For single-page documents: Use exactly 1 page with 6-12 chunks
   - For textbooks: Group related chapters/sections into fewer pages
   - Aim for 6-12 very small chunks per page (100-250 words each)
2. **Extract**: Get all content from source
3. **Micro-Chunk**: 
   - Divide content at every natural comprehension checkpoint
   - Each concept = one chunk
   - Target 100-250 words per chunk
   - Create 2-3x more chunks than standard mode
4. **Enhanced CRI**: 
   - Create varied, high-quality Questions for ~85% of chunks
   - Vary cognitive levels (recall, application, analysis, synthesis, evaluation)
   - Write concise 1-2 sentence ConstructedResponses
   - Select 3-4 most essential KeyPhrases per chunk
5. **Insert Images**: Place images with proper Markdown syntax
6. **Validate**: Check all rules (V1-V6, P1-P9, C1-C19, CS1-CS5, M1-M11, I1-I6, Q1-Q7, IH1-IH7)
7. **Output**: Submit only the complete, valid JSON

## Final Output

After completing validation, output ONLY the complete JSON with no explanatory text.
