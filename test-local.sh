#!/bin/bash
# Local Development Test Script for ShieldPR

set -e

echo "=========================================="
echo "ShieldPR - Local Test"
echo "=========================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test 1: Version Check
echo -e "${BLUE}[1/8] Version Check${NC}"
poetry run shield-pr version
echo ""

# Test 2: Platform List
echo -e "${BLUE}[2/8] Platform List${NC}"
poetry run shield-pr platforms
echo ""

# Test 3: Sample file exists check
echo -e "${BLUE}[3/8] Test Sample Files${NC}"
if [ -f "test-samples/sample_backend.py" ]; then
    echo -e "${GREEN}✓${NC} Backend sample exists"
fi
if [ -f "test-samples/sample_frontend.tsx" ]; then
    echo -e "${GREEN}✓${NC} Frontend sample exists"
fi
if [ -f "test-samples/SampleAndroid.kt" ]; then
    echo -e "${GREEN}✓${NC} Android sample exists"
fi
echo ""

# Test 4: Review command (dry run, no API key needed)
echo -e "${BLUE}[4/8] Review Command (Mock)${NC}"
echo -e "${YELLOW}Note: This uses mock data (no API key required)${NC}"
CRA_API_KEY="test-key" poetry run shield-pr review test-samples/sample_backend.py 2>&1 || true
echo ""

# Test 5: Review with format
echo -e "${BLUE}[5/8] Review Output Formats${NC}"
CRA_API_KEY="test-key" poetry run shield-pr review --format json test-samples/sample_backend.py 2>&1 | head -5 || true
echo ""

# Test 6: Git operations (if in git repo)
echo -e "${BLUE}[6/8] Git Integration${NC}"
if [ -d ".git" ]; then
    echo "Git repository detected"
    echo -e "${YELLOW}Note: review-diff requires git repo with commits${NC}"
else
    echo -e "${YELLOW}Not a git repository - skipping git tests${NC}"
fi
echo ""

# Test 7: Configuration check
echo -e "${BLUE}[7/8] Configuration${NC}"
CONFIG_DIR="$HOME/.config/shield-pr"
if [ -d "$CONFIG_DIR" ]; then
    echo -e "${GREEN}✓${NC} Config directory exists: $CONFIG_DIR"
else
    echo -e "${YELLOW}Config directory will be created at: $CONFIG_DIR${NC}"
fi
echo ""

# Test 8: Type check
echo -e "${BLUE}[8/8] Type Check${NC}"
poetry run mypy cra/ --no-error-summary 2>&1 | grep -E "Success|Found" || echo "Type check: see above"
echo ""

echo "=========================================="
echo -e "${GREEN}Test Summary${NC}"
echo "=========================================="
echo ""
echo "To use with real API key:"
echo ""
echo "1. Set your API key:"
echo "   export CRA_API_KEY='your-gemini-api-key'"
echo ""
echo "2. Review a file:"
echo "   poetry run shield-pr review test-samples/sample_backend.py"
echo ""
echo "3. Review with options:"
echo "   poetry run shield-pr review --platform backend --depth deep test-samples/sample_backend.py"
echo ""
echo "4. Review git changes:"
echo "   poetry run shield-pr review-diff --branch main"
echo ""
echo "5. Review a PR:"
echo "   poetry run shield-pr pr --url https://github.com/org/repo/pull/123"
echo ""
