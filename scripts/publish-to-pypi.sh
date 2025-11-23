#!/usr/bin/env bash
set -euo pipefail

# ==============================================================================
# PyPI Publishing Script (LOCAL-ONLY)
# ==============================================================================
#
# WORKSPACE-WIDE POLICY: This script must ONLY run on LOCAL machine, NEVER in CI/CD
#
# Rationale:
# - Security: No long-lived PyPI tokens in GitHub secrets
# - Speed: 30 seconds locally vs 3-5 minutes in CI
# - Control: Manual approval step before production release
#
# See: ADR-0027, docs/development/PUBLISHING.md
# ==============================================================================

echo "🚀 Publishing to PyPI (Local Workflow)"
echo "======================================"
echo ""

# Step 0: CI Detection Guards
# ==============================================================================
echo "🔐 Step 0: Enforcing local-only policy..."

# Check for CI environment variables
if [[ "${CI:-}" == "true" ]] || \
   [[ -n "${GITHUB_ACTIONS:-}" ]] || \
   [[ -n "${GITLAB_CI:-}" ]] || \
   [[ -n "${JENKINS_URL:-}" ]] || \
   [[ -n "${CIRCLECI:-}" ]]; then
    echo "❌ ERROR: This script must ONLY be run on your LOCAL machine"
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

echo "   ✅ Not running in CI environment"

# Step 0.1: Verify Doppler credentials
# ==============================================================================
echo ""
echo "🔐 Step 0.1: Verifying Doppler credentials..."

if ! command -v doppler &> /dev/null; then
    echo "❌ ERROR: Doppler CLI not installed"
    echo ""
    echo "   Install with: brew install dopplerhq/cli/doppler"
    exit 1
fi

# Test Doppler access
if ! doppler secrets get PYPI_TOKEN --project claude-config --config prd --plain &> /dev/null; then
    echo "❌ ERROR: Cannot retrieve PYPI_TOKEN from Doppler"
    echo ""
    echo "   Verify Doppler setup:"
    echo "   1. doppler login"
    echo "   2. doppler secrets set PYPI_TOKEN='your-token' --project claude-config --config prd"
    echo ""
    echo "   Get PyPI token from: https://pypi.org/manage/account/token/"
    exit 1
fi

echo "   ✅ Doppler credentials verified"

# Step 1: Pull latest changes
# ==============================================================================
echo ""
echo "📥 Step 1: Pulling latest release commit..."

git pull origin main-clickhouse

# Get current version
CURRENT_VERSION=$(grep '^version = ' pyproject.toml | sed 's/version = "\(.*\)"/\1/')
echo "   Current version: v${CURRENT_VERSION}"

# Step 2: Clean old builds
# ==============================================================================
echo ""
echo "🧹 Step 2: Cleaning old builds..."

rm -rf dist/ build/ *.egg-info
echo "   ✅ Cleaned"

# Step 3: Build package
# ==============================================================================
echo ""
echo "📦 Step 3: Building package..."

uv build

# Verify build artifacts
if [[ ! -d dist/ ]] || [[ -z "$(ls -A dist/)" ]]; then
    echo "❌ ERROR: Build failed - no artifacts in dist/"
    exit 1
fi

WHEEL_FILE=$(ls dist/*.whl 2>/dev/null | head -1)
if [[ -z "${WHEEL_FILE}" ]]; then
    echo "❌ ERROR: No wheel file found in dist/"
    exit 1
fi

echo "   ✅ Built: ${WHEEL_FILE}"

# Step 4: Publish to PyPI
# ==============================================================================
echo ""
echo "📤 Step 4: Publishing to PyPI..."

# Retrieve token from Doppler
PYPI_TOKEN=$(doppler secrets get PYPI_TOKEN --project claude-config --config prd --plain)

if [[ -z "${PYPI_TOKEN}" ]]; then
    echo "❌ ERROR: PYPI_TOKEN is empty"
    exit 1
fi

echo "   Using PYPI_TOKEN from Doppler (claude-config/prd)"

# Publish using uv with token
UV_PUBLISH_TOKEN="${PYPI_TOKEN}" uv publish

echo "   ✅ Published to PyPI"

# Step 5: Verify on PyPI
# ==============================================================================
echo ""
echo "🔍 Step 5: Verifying on PyPI..."

# Wait for PyPI to update (usually <10 seconds)
sleep 5

PACKAGE_NAME="gapless-crypto-data"
PYPI_URL="https://pypi.org/project/${PACKAGE_NAME}/${CURRENT_VERSION}/"

# Check if version is available on PyPI
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${PYPI_URL}")

if [[ "${HTTP_STATUS}" == "200" ]]; then
    echo "   ✅ Verified: ${PYPI_URL}"
else
    echo "   ⚠️  PyPI may still be updating (HTTP ${HTTP_STATUS})"
    echo "   Check manually: ${PYPI_URL}"
fi

# Complete
# ==============================================================================
echo ""
echo "✅ Complete! Published v${CURRENT_VERSION} to PyPI"
echo ""
echo "Next steps:"
echo "  1. Verify on PyPI: https://pypi.org/project/${PACKAGE_NAME}/"
echo "  2. Test installation: pip install ${PACKAGE_NAME}==${CURRENT_VERSION}"
echo ""
