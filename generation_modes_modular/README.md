# Generation Modes - Modular (Option 2)

## Overview

This folder contains **modular** generation mode files. The structure is:
- **`_base_strategy3.md`** - Shared Strategy 3 validation rules
- **Mode files** - Mode-specific instructions only

**Total content same as Full Inclusion, just organized differently.**

## Files

**Shared Base:**
- `_base_strategy3.md` (846 lines) - Complete Strategy 3 validation rules

**Mode-Specific:**
- `faithful.md` - Exact preservation instructions
- `simplified.md` - Language simplification instructions  
- `condensed.md` - Content reduction instructions
- `hybrid.md`  - Balanced optimization instructions
- `interaction-heavy.md` - Micro-chunking instructions

## Usage (Requires Pipeline Update)

### Option A: Update main.py to load both files

```python
# In src/pipeline/utils.py, add:
def load_modular_guide(mode_file: Path, base_file: Path) -> str:
    """Load mode-specific + base Strategy 3 content"""
    mode_content = mode_file.read_text()
    base_content = base_file.read_text()
    return f"{mode_content}\n\n---\n\n{base_content}"

# In src/pipeline/main.py:
if args.mode and args.use_modular:
    mode_file = workspace_root / "generation_modes_modular" / f"{args.mode}.md"
    base_file = workspace_root / "generation_modes_modular" / "_base_strategy3.md"
    guide_text = load_modular_guide(mode_file, base_file)
```

### Option B: Use helper script (combines files)

```bash
# combine_mode.sh
MODE=$1
cat generation_modes_modular/${MODE}.md \
    generation_modes_modular/_base_strategy3.md \
    > /tmp/combined_${MODE}.md

python -m src.pipeline.main \
    --pdf input.pdf \
    --guide /tmp/combined_${MODE}.md \
    --output output.json
```

### Option C: Manual combination

```bash
# Combine mode + base manually
cat generation_modes_modular/hybrid.md \
    generation_modes_modular/_base_strategy3.md \
    > prompts/hybrid_combined.md

# Use combined file
python -m src.pipeline.main \
    --pdf input.pdf \
    --guide prompts/hybrid_combined.md \
    --output output.json
```

## Comparison with Full Inclusion

| Aspect | Modular | Full Inclusion |
|--------|---------|---------------|
| File size | ~50-140 lines | ~900-1000 lines |
| Dependencies | Requires base | None |
| Pipeline changes | Required | None needed |
| Duplication | No | Yes (5x) |
| Updates | Update 1 file | Update 5 files |
| Complexity | More complex | Simple |

## Testing

```bash
# Test by combining files manually
cat generation_modes_modular/hybrid.md \
    generation_modes_modular/_base_strategy3.md \
    > /tmp/test_hybrid.md

# Verify combined file has ~1000 lines
wc -l /tmp/test_hybrid.md

# Test with pipeline
python -m src.pipeline.main \
    --pdf test_sample.pdf \
    --guide /tmp/test_hybrid.md \
    --output test_output.json
```

## Maintenance

To update Strategy 3 rules:
1. Edit `generation_modes_modular/_base_strategy3.md`
2. All modes automatically use updated rules (no regeneration needed)

To update a specific mode:
1. Edit `generation_modes_modular/{mode}.md`
2. Only that mode is affected

To regenerate from source:
```bash
python build_mode_folders.py
```

## Pipeline Integration Example

Here's how to update `src/pipeline/main.py` to support modular modes:

```python
# Add to parse_args():
parser.add_argument(
    "--modular",
    action="store_true",
    help="Use modular mode files (requires combining with base)"
)

# Update main():
if args.mode:
    if args.modular:
        # Option 2: Modular approach
        workspace_root = Path(__file__).resolve().parents[2]
        mode_file = workspace_root / "generation_modes_modular" / f"{args.mode}.md"
        base_file = workspace_root / "generation_modes_modular" / "_base_strategy3.md"
        
        # Combine files
        mode_content = mode_file.read_text()
        base_content = base_file.read_text()
        guide_text = f"{mode_content}\n\n---\n\n{base_content}"
        
        print(f"Using modular mode: {args.mode}")
        print(f"  Mode file: {mode_file}")
        print(f"  Base file: {base_file}")
    else:
        # Option 1: Full inclusion (default)
        workspace_root = Path(__file__).resolve().parents[2]
        args.guide = workspace_root / "generation_modes_full" / f"{args.mode}.md"
        guide_text = load_guide_instructions(args.guide)
        print(f"Using full mode: {args.mode}")
```

## Recommended Default

**Use this folder if:**
- You want cleaner organization
- You'll make frequent updates to Strategy 3
- You're comfortable with minor pipeline changes
- You value DRY principles

**Use full folder if:**
- You want simplest setup (no changes needed)
- You don't plan frequent Strategy 3 updates
- You prefer self-contained files
