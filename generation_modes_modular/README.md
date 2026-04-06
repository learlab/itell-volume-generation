# Generation Modes - Modular

## Structure

- `base_strategy3.md` - Shared Strategy 3 validation rules
- Mode files - Mode-specific instructions only

The pipeline automatically combines the base file with the selected mode file at runtime.

## Mode Selection

| Mode | Length | Reading Level | Chunks/Page | Use Case |
|------|--------|---------------|-------------|----------|
| `faithful` | 100% | Original | 2-4 | Precision, source-preserving conversion |
| `simplified` | 100% | Grade 9-10 | 3-6 | Accessibility, ESL, high school |
| `condensed` | 60% | Original | 4-8 | Review and exam prep |
| `adaptive` | LLM decides | LLM decides | LLM decides | Course-outline-to-content authoring |
| `interaction-heavy` | 100% | Original | 6-12 | Active learning and frequent checkpoints |

## Usage

```bash
./generate_mode.sh adaptive path/to/course-outline.pdf
```

Or run the pipeline directly:

```bash
python -m src.pipeline.main \
  --pdf path/to/course-outline.pdf \
  --mode adaptive \
  --mode-folder modular \
  --reference-json prompts/reference.json \
  --output results/output.json
```
