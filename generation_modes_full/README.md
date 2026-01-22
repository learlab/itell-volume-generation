# Generation Modes - Full Inclusion (Option 1)

## Overview

This folder contains **self-contained** generation mode files. Each file includes:
- Mode-specific instructions (~100-150 lines)
- **Complete Strategy 3 content** (~850 lines)  
- All error examples and validation rules

**File sizes**: ~900-1000 lines each

## Advantages

✅ **Self-contained** - Each file has everything needed  
✅ **No dependencies** - Works with existing pipeline as-is  
✅ **Simple to use** - Just point to one file  
✅ **Complete examples** - All 17 error examples included  
✅ **Proven effective** - Full Strategy 3 guidance in every mode  

## Disadvantages

⚠️ **Duplication** - Strategy 3 content repeated 5 times  
⚠️ **Larger files** - ~900-1000 lines per file  
⚠️ **Updates** - Changes to base Strategy 3 require updating all files  

## Files

- `faithful.md` (889 lines) - Exact preservation
- `simplified.md` (922 lines) - Grade 9-10 language  
- `condensed.md` (924 lines) - 60% length
- `hybrid.md` (942 lines) - 80% length, balanced ⭐
- `interaction-heavy.md` (977 lines) - Maximum engagement

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

## When to Use This Approach

Choose **Full Inclusion** when:
- ✅ You want simplest setup (no pipeline changes needed)
- ✅ You value self-contained files
- ✅ File size isn't a concern  
- ✅ You won't frequently update base Strategy 3
- ✅ You want proven, battle-tested prompts immediately

## Comparison with Modular Approach

| Aspect | Full Inclusion | Modular |
|--------|---------------|---------|
| File size | ~900-1000 lines | ~50-140 lines |
| Dependencies | None | Requires base file |
| Pipeline changes | None needed | Requires update |
| Duplication | Yes (5x) | No |
| Updates | Update all 5 files | Update 1 base file |
| Complexity | Simple | More complex |

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
