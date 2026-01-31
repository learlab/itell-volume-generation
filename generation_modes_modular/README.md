# Generation Modes - Modular

## Structure

- `_base_strategy3.md` - Shared Strategy 3 validation rules
- Mode files - Mode-specific instructions only

The pipeline automatically combines mode + base files at runtime.

# Generation Mode Characteristics

## Mode Selection

| Mode | Length | Reading Level | Chunks/Page | Use Case |
|------|--------|---------------|-------------|----------|
| `faithful` | 100% | Original | 2-4 | Medical/legal precision |
| `simplified` | 100% | Grade 9-10 | 3-6 | High school, ESL |
| `condensed` | 60% | Original | 4-8 | Review, exam prep |
| `adaptive` | LLM decides | LLM decides | LLM decides | General use - LLM optimizes |
| `interaction-heavy` | 100% | Original | 6-12 | Online courses |

## Mode Details

### faithful
Exact preservation of source material. No modifications, all examples, technical terms unchanged.

### simplified  
Accessible for younger audiences. Plain language, shorter sentences (15-20 words), definitions included.

### condensed
Core concepts only. Removes redundancy, keeps 1-2 key examples per concept.

### adaptive
LLM decides optimal structure. Full autonomy to optimize length, chunking, and complexity for learning.

### interaction-heavy
Maximum engagement. Small chunks (100-250w), 80-90% with questions, varied types, frequent checkpoints.

## Usage

```bash
# Using pipeline directly
python -m src.pipeline.main \
    --pdf input.pdf \
    --mode adaptive \
    --mode-folder modular \
    --output output.json
```
