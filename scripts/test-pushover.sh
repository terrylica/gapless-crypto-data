#!/usr/bin/env bash
# =============================================================================
# Pushover Test Script with Doppler
# ADR-0005: Test Pushover notifications locally
# =============================================================================
#
# Usage: ./scripts/test-pushover.sh [version] [release_url]
#
# Prerequisites:
#   - Doppler CLI: brew install dopplerhq/cli/doppler
#   - Doppler auth: doppler login
#   - PUSHOVER_USER_KEY in Doppler (notifications/prd)
#   - PUSHOVER_APP_TOKEN in Doppler (notifications/prd)
# =============================================================================

set -euo pipefail

VERSION="${1:-test}"
RELEASE_URL="${2:-https://github.com/terrylica/gapless-crypto-data/releases}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Testing Pushover notification...${NC}"

# Get credentials from Doppler (notifications project)
PUSHOVER_USER_KEY=$(doppler secrets get PUSHOVER_USER_KEY --project notifications --config prd --plain 2>/dev/null) || {
    echo -e "${RED}ERROR: PUSHOVER_USER_KEY not found in Doppler${NC}"
    echo "Add with: doppler secrets set PUSHOVER_USER_KEY='your-user-key' --project notifications --config prd"
    exit 1
}

PUSHOVER_APP_TOKEN=$(doppler secrets get PUSHOVER_APP_TOKEN --project notifications --config prd --plain 2>/dev/null) || {
    echo -e "${RED}ERROR: PUSHOVER_APP_TOKEN not found in Doppler${NC}"
    echo "Add with: doppler secrets set PUSHOVER_APP_TOKEN='your-app-token' --project notifications --config prd"
    exit 1
}

# Send test notification
RESPONSE=$(curl -s \
    --form-string "token=$PUSHOVER_APP_TOKEN" \
    --form-string "user=$PUSHOVER_USER_KEY" \
    --form-string "title=gapless-crypto-data Test" \
    --form-string "message=Test notification for version $VERSION" \
    --form-string "url=$RELEASE_URL" \
    --form-string "url_title=View Release" \
    --form-string "priority=0" \
    https://api.pushover.net/1/messages.json)

if echo "$RESPONSE" | grep -q '"status":1'; then
    echo -e "${GREEN}Pushover notification sent successfully!${NC}"
else
    echo -e "${RED}ERROR: Pushover notification failed${NC}"
    echo "Response: $RESPONSE"
    exit 1
fi
