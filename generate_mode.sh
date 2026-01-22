#!/bin/bash
# Updated generation script supporting both full and modular approaches
#
# Usage:
#   ./generate_mode.sh <mode> <input.pdf> [approach] [output.json]
#
# Approaches: full (default), modular, original
# Modes: faithful, simplified, condensed, hybrid, interaction-heavy

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Check arguments
if [ "$#" -lt 2 ]; then
    echo -e "${RED}Error: Missing required arguments${NC}"
    echo ""
    echo "Usage: $0 <mode> <input.pdf> [approach] [output.json]"
    echo ""
    echo "Modes:"
    echo "  faithful          - Exact preservation (900 lines)"
    echo "  simplified        - Grade 9-10 reading level (920 lines)"
    echo "  condensed         - Core concepts only (920 lines)"
    echo "  hybrid            - Balanced optimization (940 lines) ⭐"
    echo "  interaction-heavy - Maximum engagement (980 lines)"
    echo ""
    echo "Approaches:"
    echo "  full     - Self-contained files (default, recommended)"
    echo "  modular  - Combines mode + base files"
    echo "  original - Old short versions (for comparison)"
    echo ""
    echo "Examples:"
    echo "  $0 hybrid textbook.pdf"
    echo "  $0 hybrid textbook.pdf full"
    echo "  $0 condensed chapter1.pdf modular results/output.json"
    exit 1
fi

MODE=$1
INPUT_PDF=$2
APPROACH=${3:-"full"}
OUTPUT_JSON=${4:-""}

# Validate mode
case "$MODE" in
    faithful|simplified|condensed|hybrid|interaction-heavy)
        ;;
    *)
        echo -e "${RED}Error: Invalid mode '$MODE'${NC}"
        echo "Available modes: faithful, simplified, condensed, hybrid, interaction-heavy"
        exit 1
        ;;
esac

# Validate approach
case "$APPROACH" in
    full|modular|original)
        ;;
    *)
        echo -e "${RED}Error: Invalid approach '$APPROACH'${NC}"
        echo "Available approaches: full, modular, original"
        exit 1
        ;;
esac

# Check if PDF exists
if [ ! -f "$INPUT_PDF" ]; then
    echo -e "${RED}Error: PDF file not found: $INPUT_PDF${NC}"
    exit 1
fi

# Generate default output name if not provided
if [ -z "$OUTPUT_JSON" ]; then
    BASENAME=$(basename "$INPUT_PDF" .pdf)
    OUTPUT_JSON="results/${BASENAME}_${MODE}_${APPROACH}.json"
fi

# Create output directory
OUTPUT_DIR=$(dirname "$OUTPUT_JSON")
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}iTELL Generation - $MODE mode${NC}"
echo -e "${GREEN}Approach: $APPROACH${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Input:    $INPUT_PDF"
echo "Output:   $OUTPUT_JSON"
echo "Mode:     $MODE"
echo "Approach: $APPROACH"
echo ""

# Show approach details
case "$APPROACH" in
    full)
        echo -e "${BLUE}Using full inclusion (self-contained file)${NC}"
        echo "  File: generation_modes_full/${MODE}.md (~900-1000 lines)"
        ;;
    modular)
        echo -e "${BLUE}Using modular approach (mode + base)${NC}"
        echo "  Mode: generation_modes_modular/${MODE}.md"
        echo "  Base: generation_modes_modular/_base_strategy3.md"
        echo "  Combined: ~900-1000 lines"
        ;;
    original)
        echo -e "${YELLOW}Using original short mode files (WARNING: Missing Strategy 3 examples!)${NC}"
        echo "  File: generation_modes/${MODE}.md (~200-300 lines)"
        ;;
esac

echo ""
echo -e "${YELLOW}Starting generation...${NC}"
echo ""

# Run the pipeline
python -m src.pipeline.main \
    --pdf "$INPUT_PDF" \
    --mode "$MODE" \
    --mode-folder "$APPROACH" \
    --output "$OUTPUT_JSON"

# Check success
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Generation Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Output saved to: $OUTPUT_JSON"
    
    # Show statistics if jq available
    if command -v jq &> /dev/null; then
        echo ""
        echo "Statistics:"
        echo "  Pages:  $(jq '.Pages | length' "$OUTPUT_JSON")"
        echo "  Chunks: $(jq '[.Pages[].Content | length] | add' "$OUTPUT_JSON")"
        
        CHUNKS_WITH_QUESTIONS=$(jq '[.Pages[].Content[] | select(.__component == "page.chunk")] | length' "$OUTPUT_JSON")
        TOTAL_CHUNKS=$(jq '[.Pages[].Content[]] | length' "$OUTPUT_JSON")
        echo "  Interactive chunks: $CHUNKS_WITH_QUESTIONS / $TOTAL_CHUNKS"
    fi
    echo ""
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Generation Failed${NC}"
    echo -e "${RED}========================================${NC}"
    echo ""
    exit 1
fi
