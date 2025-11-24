#!/usr/bin/env bash
#
# PyPI Publishing Script (Local-Only)
#
# CRITICAL: This script must ONLY be run on your LOCAL machine.
# NEVER run in CI/CD (GitHub Actions, GitLab CI, Jenkins, CircleCI, etc.)
#
# Workspace Policy: ADR-0027 - Local-Only PyPI Publishing
# See: docs/development/PUBLISHING.md

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Publishing to PyPI (Local Workflow)${NC}"
echo "======================================"
echo ""

# ============================================================================
# Step 0: CI Detection Guards
# ============================================================================
echo -e "${BLUE}🔐 Step 0: CI Detection Guards...${NC}"

if [[ "${CI:-}" == "true" ]] || \
   [[ -n "${GITHUB_ACTIONS:-}" ]] || \
   [[ -n "${GITLAB_CI:-}" ]] || \
   [[ -n "${JENKINS_URL:-}" ]] || \
   [[ -n "${CIRCLECI:-}" ]]; then
    echo -e "${RED}❌ ERROR: This script must ONLY be run on your LOCAL machine${NC}"
    echo ""
    echo "   Detected CI environment variables:"
    echo "   - CI: ${CI:-<not set>}"
    echo "   - GITHUB_ACTIONS: ${GITHUB_ACTIONS:-<not set>}"
    echo "   - GITLAB_CI: ${GITLAB_CI:-<not set>}"
    echo "   - JENKINS_URL: ${JENKINS_URL:-<not set>}"
    echo "   - CIRCLECI: ${CIRCLECI:-<not set>}"
    echo ""
    echo "   This project enforces LOCAL-ONLY PyPI publishing for:"
    echo "   - Security: No long-lived PyPI tokens in GitHub secrets"
    echo "   - Speed: 30 seconds locally vs 3-5 minutes in CI"
    echo "   - Control: Manual approval step before production release"
    echo ""
    echo "   See: docs/development/PUBLISHING.md (ADR-0027)"
    exit 1
fi

echo -e "${GREEN}   ✅ Running on local machine${NC}"
echo ""

# ============================================================================
# Step 1: Verify Doppler Credentials
# ============================================================================
echo -e "${BLUE}🔐 Step 1: Verifying Doppler credentials...${NC}"

if ! command -v doppler &> /dev/null; then
    echo -e "${RED}   ❌ Doppler CLI not found${NC}"
    echo "   Install: brew install dopplerhq/cli/doppler"
    exit 1
fi

# Test Doppler access
if ! doppler secrets get PYPI_TOKEN --project claude-config --config prd --plain &> /dev/null; then
    echo -e "${RED}   ❌ Cannot access PYPI_TOKEN in Doppler${NC}"
    echo "   Verify:"
    echo "   1. doppler login"
    echo "   2. doppler projects (should show claude-config)"
    echo "   3. doppler secrets --project claude-config --config prd"
    exit 1
fi

echo -e "${GREEN}   ✅ Doppler token verified${NC}"
echo ""

# ============================================================================
# Step 2: Pull Latest Release Commit
# ============================================================================
echo -e "${BLUE}📥 Step 2: Pulling latest release commit...${NC}"

git pull origin main --no-verify

CURRENT_VERSION=$(grep '^version = ' pyproject.toml | head -1 | sed 's/version = "\(.*\)"/\1/')
echo -e "${GREEN}   Current version: v${CURRENT_VERSION}${NC}"
echo ""

# ============================================================================
# Step 3: Clean Old Builds
# ============================================================================
echo -e "${BLUE}🧹 Step 3: Cleaning old builds...${NC}"

rm -rf dist/ build/ *.egg-info
echo -e "${GREEN}   ✅ Cleaned${NC}"
echo ""

# ============================================================================
# Step 4: Build Package
# ============================================================================
echo -e "${BLUE}📦 Step 4: Building package...${NC}"

uv build

# Verify build artifacts
WHEEL_COUNT=$(ls dist/*.whl 2>/dev/null | wc -l)
if [[ ${WHEEL_COUNT} -eq 0 ]]; then
    echo -e "${RED}   ❌ Build failed - no wheel found${NC}"
    exit 1
fi

echo -e "${GREEN}   ✅ Built: $(ls dist/*.whl)${NC}"
echo ""

# ============================================================================
# Step 5: Publish to PyPI
# ============================================================================
echo -e "${BLUE}📤 Step 5: Publishing to PyPI...${NC}"

# Retrieve token from Doppler
PYPI_TOKEN=$(doppler secrets get PYPI_TOKEN --project claude-config --config prd --plain)

echo "   Using PYPI_TOKEN from Doppler"

# Publish
UV_PUBLISH_TOKEN="${PYPI_TOKEN}" uv publish

echo -e "${GREEN}   ✅ Published to PyPI${NC}"
echo ""

# ============================================================================
# Step 6: Verify on PyPI
# ============================================================================
echo -e "${BLUE}🔍 Step 6: Verifying on PyPI...${NC}"

PACKAGE_NAME=$(grep '^name = ' pyproject.toml | head -1 | sed 's/name = "\(.*\)"/\1/')
PYPI_URL="https://pypi.org/project/${PACKAGE_NAME}/${CURRENT_VERSION}/"

# Wait a few seconds for PyPI to process
sleep 5

# Check if package is available
if curl -sf "${PYPI_URL}" > /dev/null; then
    echo -e "${GREEN}   ✅ Verified: ${PYPI_URL}${NC}"
else
    echo -e "${YELLOW}   ⚠️  Package may still be processing on PyPI${NC}"
    echo "   Check manually: ${PYPI_URL}"
fi

echo ""
echo -e "${GREEN}✅ Complete! Published v${CURRENT_VERSION} to PyPI${NC}"
