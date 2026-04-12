# Generation Modes - Modular

## Structure

- `base_strategy3.md` - Shared Strategy 3 validation rules
- Mode files - Mode-specific instructions for standard modes
- `generative.md` - Standalone generative prompt with the adapted base rules embedded

The pipeline automatically combines the base file with the selected mode file at runtime, except for `generative`, which uses its standalone prompt file directly.

## Mode Selection

| Mode | Length | Reading Level | Chunks/Page | Use Case |
|------|--------|---------------|-------------|----------|
| `faithful` | 100% | Original | 2-4 | Precision, source-preserving conversion |
| `simplified` | 100% | Grade 9-10 | 3-6 | Accessibility, ESL, high school |
| `condensed` | 60% | Original | 4-8 | Review and exam prep |
| `generative` | Teachable coverage | Inferred | 3-6 | Course-outline PDF/PPTX-to-content authoring |
| `interaction-heavy` | 100% | Original | 6-12 | Active learning and frequent checkpoints |

## Usage

```bash
./generate_mode.sh generative path/to/course-outline.pptx
```

Or run the pipeline directly:

```bash
python -m src.pipeline.main \
  --input path/to/course-outline.pptx \
  --mode generative \
  --mode-folder modular \
  --reference-json prompts/reference.json \
  --output results/output.json
```
