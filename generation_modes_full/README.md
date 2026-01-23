# Generation Modes - Full Inclusion (Option 1)

## Overview

This folder contains **self-contained** generation mode files. Each file includes:
- Mode-specific instructions
- **Complete Strategy 3 content** 
- All error examples and validation rules

## Files

- `faithful.md` - Exact preservation
- `simplified.md` - Grade 9-10 language  
- `condensed.md` - 60% length
- `hybrid.md` - 80% length, balanced
- `interaction-heavy.md` - Maximum engagement

## Usage

### With Pipeline
```bash
python -m src.pipeline.main \
    --pdf input.pdf \
    --guide generation_modes_full/hybrid.md \
    --output output.json
```

### With --mode Flag (if updated pipeline)
```bash
python -m src.pipeline.main \
    --pdf input.pdf \
    --mode hybrid \
    --mode-folder generation_modes_full \
    --output output.json
```

### Direct
```bash
# Copy to main prompts folder
cp generation_modes_full/hybrid.md prompts/guide_hybrid.md

# Use normally
python -m src.pipeline.main --pdf input.pdf --guide prompts/guide_hybrid.md
```

## Testing

```bash
# Test a mode
python -m src.pipeline.main \
    --pdf test_sample.pdf \
    --guide generation_modes_full/hybrid.md \
    --output test_output.json

# Verify it includes all Strategy 3 content
wc -l generation_modes_full/hybrid.md
# Should show ~900-1000 lines
```

## Maintenance

To update base Strategy 3 rules across all modes:
1. Edit `prompts/guide_strategy3_validation.md`
2. Run: `python build_mode_folders.py`
3. This regenerates all mode files with updated Strategy 3 content

## Recommended Default

**Use this folder if:**
- You're getting started and want simplest setup
- You don't plan to frequently update Strategy 3
- You want each mode file to work independently

**Use modular folder if:**
- You want cleaner file organization
- You'll frequently update Strategy 3 base
- You don't mind pipeline modifications
