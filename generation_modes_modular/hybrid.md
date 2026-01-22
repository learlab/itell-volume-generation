# iTELL Content Authoring Guide - Hybrid Mode (Modular)

**Generation Mode**: `hybrid`

**Your Role**: iTELL JSON Validator and Generator (Hybrid Mode)

**Note**: This file contains mode-specific instructions. The complete Strategy 3 validation rules are in `_base_strategy3.md` and will be loaded automatically by the pipeline.

## Mode Configuration

- **Content Modification**: Minimal - smart optimization
- **Reading Level**: Grade 11-12 (balanced readability)
- **Length Target**: 80% of original content
- **Chunking Strategy**: Standard (3-6 chunks of 250-400 words)
- **Stages**: Extract → Chunk → Optimize CRI → Images → Validate
- **Smart Omissions**: LLM-guided decisions on what to condense

## Mode-Specific Instructions

### Hybrid Mode Philosophy

**Balance three goals**:
1. Maintain fidelity to original content (like faithful mode)
2. Improve accessibility (like simplified mode)
3. Optimize for learning efficiency (like condensed mode)

### Content Optimization Requirements

1. **SMART OMISSIONS** (LLM decides based on these criteria):
   - Remove redundant explanations (if a concept is explained well once, don't repeat)
   - Condense overly detailed examples (keep the example but make it more concise)
   - Reduce tangential content (keep only if it significantly aids understanding)
   - Preserve all unique concepts and key information

2. **MINIMAL SIMPLIFICATION**:
   - Keep technical vocabulary but ensure context makes meaning clear
   - Break extremely long sentences (>40 words) into two sentences
   - Target Grade 11-12 reading level (college-prep appropriate)
   - Add brief clarifications only where absolutely needed

3. **OPTIMIZED CRI GENERATION**:
   - Questions should target the most important concepts in each chunk
   - ConstructedResponses should synthesize key ideas
   - KeyPhrases should focus on terms students must know

4. **TARGET 80% LENGTH**: Aim for 75-85% of original word count through smart omissions

### Hybrid Mode Validation Rules

- [ ] **Rule HM1**: Total word count is 75-85% of original (target 80%)
- [ ] **Rule HM2**: All core concepts preserved (100% concept coverage)
- [ ] **Rule HM3**: Reading level is Grade 11-12 (Flesch-Kincaid 50-60)
- [ ] **Rule HM4**: Technical vocabulary preserved with sufficient context
- [ ] **Rule HM5**: Only truly redundant/tangential content removed
- [ ] **Rule HM6**: Chunk word count is 250-400 words
- [ ] **Rule HM7**: CRI elements focus on most important concepts

### Optimization Decision Framework

When deciding what to omit or condense, ask:
1. **Is this concept unique?** → If yes, KEEP
2. **Does this example significantly clarify a difficult concept?** → If yes, KEEP (but may condense)
3. **Is this the clearest explanation available?** → If yes, KEEP; if redundant, OMIT
4. **Does this tangent connect to core learning objectives?** → If no, OMIT
5. **Would a student miss this if it were gone?** → If yes, KEEP

### Optimization Examples

**Original (200 words):**
"Psychology is usually defined as the scientific study of human behavior and mental processes, and this example illustrates the features that make it scientific. In this chapter, we look closely at these features, review the goals of psychology, and address several basic questions that students often have about it. Who conducts scientific research in psychology? Why? Does scientific psychology tell us anything that common sense does not? Why should I bother to learn the scientific approach—especially if I want to be a clinical psychologist and not a researcher? These are extremely good questions, and answering them now will provide a solid foundation for learning the rest of the material in your course."

**Hybrid Optimized (160 words - 80%):**
"**Psychology** is the scientific study of human behavior and mental processes. This example illustrates what makes psychology scientific. In this chapter, we examine psychology's scientific features and goals, and address key questions students often have. Who conducts psychological research and why? Does scientific psychology reveal insights beyond common sense? Why learn the scientific approach if you want to be a clinical psychologist rather than a researcher? These questions are important because their answers provide a foundation for understanding psychology as a scientific discipline."

**What Changed:**
- Removed meta-commentary ("extremely good questions")
- Condensed repetitive phrasing
- Maintained all core questions and concepts
- Preserved technical vocabulary with context
- 80% of original length, 100% of concepts


## Generation Workflow (Hybrid Mode)

1. **Plan Page Structure**: 
   - For single-page documents: Use exactly 1 page
   - For textbooks: Group related chapters/sections into fewer pages
   - Aim for 3-6 chunks per page (250-400 words each)
2. **Extract**: Get all content from source
3. **Smart Optimize**: 
   - Apply decision framework to each section
   - Remove only truly redundant/tangential content
   - Condense verbose explanations while preserving clarity
   - Target 80% of original length
4. **Chunk**: Divide optimized content into 250-400 word chunks
5. **Optimize CRI**: Create Questions, ConstructedResponses, and KeyPhrases focused on most important concepts
6. **Insert Images**: Place key images with proper Markdown syntax
7. **Validate**: Check all rules (V1-V6, P1-P9, C1-C18, CS1-CS5, M1-M11, I1-I6, Q1-Q6, HM1-HM7)
8. **Output**: Submit only the complete, valid JSON

## Final Output

After completing validation, output ONLY the complete JSON with no explanatory text.
