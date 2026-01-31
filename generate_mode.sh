#!/bin/bash
# iTELL content generation with modular modes
#
# Usage: ./generate_mode.sh <mode> <input.pdf> [output.json]
#
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
    echo "Usage: $0 <mode> <input.pdf> [output.json]"
    echo ""
    echo "Modes:"
    echo "  faithful          - Exact preservation (400-500w chunks)"
    echo "  simplified        - Grade 9-10 reading level (200-400w chunks)"
    echo "  condensed         - Core concepts only, 60% length (150-300w chunks)"
    echo "  hybrid            - Balanced optimization, 80% length (250-400w chunks) ⭐"
    echo "  interaction-heavy - Maximum engagement (100-250w chunks)"
    echo ""
    echo "Examples:"
    echo "  $0 hybrid textbook.pdf"
    echo "  $0 condensed chapter1.pdf results/output.json"
    exit 1
fi

MODE=$1
INPUT_PDF=$2
OUTPUT_JSON=${3:-""}

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

# Check if PDF exists
if [ ! -f "$INPUT_PDF" ]; then
    echo -e "${RED}Error: PDF file not found: $INPUT_PDF${NC}"
    exit 1
fi

# Generate default output name if not provided
if [ -z "$OUTPUT_JSON" ]; then
    BASENAME=$(basename "$INPUT_PDF" .pdf)
    OUTPUT_JSON="results/${BASENAME}_${MODE}.json"
fi

# Create output directory
OUTPUT_DIR=$(dirname "$OUTPUT_JSON")
mkdir -p "$OUTPUT_DIR"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}iTELL Generation - $MODE mode${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Input:  $INPUT_PDF"
echo "Output: $OUTPUT_JSON"
echo "Mode:   $MODE"
echo ""
echo -e "${BLUE}Mode file: generation_modes_modular/${MODE}.md${NC}"
echo -e "${BLUE}Base:      generation_modes_modular/_base_strategy3.md${NC}"
echo ""
echo -e "${YELLOW}Starting generation...${NC}"
echo ""

# Run the pipeline
python -m src.pipeline.main \
    --pdf "$INPUT_PDF" \
    --mode "$MODE" \
    --mode-folder "modular" \
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
