# Generation Modes - Modular

## Structure

- `_base_strategy3.md` - Shared Strategy 3 validation rules
- Mode files - Mode-specific instructions only

The pipeline automatically combines mode + base files at runtime.

# Generation Mode Characteristics

## Mode Selection

| Mode | Length | Reading Level | Chunks/Page | Chunk Size | Use Case |
|------|--------|---------------|-------------|------------|----------|
| `faithful` | 100% | Original | 2-4 | 400-500w | Medical/legal precision |
| `simplified` | 100% | Grade 9-10 | 3-6 | 200-400w | High school, ESL |
| `condensed` | 60% | Original | 4-8 | 150-300w | Review, exam prep |
| `hybrid` | 80% | Grade 11-12 | 3-6 | 250-400w | General college |
| `interaction-heavy` | 100% | Original | 6-12 | 100-250w | Online courses |

## Mode Details

### faithful
Preserves source material exactly as written.
- No content modification
- All examples included
- Technical terms unchanged
- Conservative chunking for context

### simplified  
Makes content accessible for younger audiences.
- Replaces jargon with plain language
- Shorter sentences (15-20 words)
- Adds definitions for technical terms
- Grade 9-10 Flesch-Kincaid target

### condensed
Reduces content to core concepts.
- Removes redundancy and elaboration
- Keeps 1-2 key examples per concept
- Omits extended case studies
- Preserves all core concepts

### hybrid
Balances completeness and accessibility.
- Smart omissions of redundant content
- Minimal simplification where needed
- Maintains technical vocabulary with context
- Grade 11-12 reading level

### interaction-heavy
Maximizes student engagement.
- Many small chunks (100-250w)
- 80-90% of chunks have questions
- Varied question types (recall, application, analysis)
- Frequent comprehension checkpoints

## Usage

```bash
# Using helper script
./generate_mode.sh hybrid input.pdf modular

# Using pipeline directly
python -m src.pipeline.main \
    --pdf input.pdf \
    --mode hybrid \
    --mode-folder modular \
    --output output.json
```

## Maintenance

**Update Strategy 3 base:**
```bash
vim generation_modes_modular/_base_strategy3.md
```
Changes apply to all modes automatically.

**Update specific mode:**
```bash
vim generation_modes_modular/hybrid.md
```
Only affects that mode.

**Regenerate from source:**
```bash
python build_mode_folders.py
```
