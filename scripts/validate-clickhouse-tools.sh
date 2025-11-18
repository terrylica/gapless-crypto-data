#!/usr/bin/env bash
#
# ClickHouse Visualization Tools Validation Suite
#
# Validates all 5 tools in the local visualization toolchain:
# - CH-UI web interface
# - ClickHouse Play built-in UI
# - clickhouse-client CLI
# - chdig TUI monitoring
# - clickhouse-local file analysis
#
# Exit codes:
#   0 - All validations passed
#   1 - One or more validations failed
#
# Usage:
#   bash scripts/validate-clickhouse-tools.sh
#
# Refs: ADR-0008 ClickHouse Local Visualization Toolchain

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Test result tracking
pass() {
    echo -e "${GREEN}✅ PASS${NC}: $1"
    ((TESTS_PASSED++))
}

fail() {
    echo -e "${RED}❌ FAIL${NC}: $1"
    ((TESTS_FAILED++))
}

warn() {
    echo -e "${YELLOW}⚠️  WARN${NC}: $1"
}

echo "=========================================="
echo "ClickHouse Visualization Tools Validation"
echo "=========================================="
echo ""

# Test 1: Docker ClickHouse container running
echo "[1/7] Checking ClickHouse container..."
if docker ps | grep -q "gapless.*clickhouse"; then
    pass "ClickHouse container running"
else
    fail "ClickHouse container not running (run: docker-compose up -d clickhouse)"
fi

# Test 2: ClickHouse HTTP interface
echo "[2/7] Checking ClickHouse HTTP interface (port 8123)..."
if curl -sf http://localhost:8123/ping > /dev/null 2>&1; then
    pass "ClickHouse HTTP interface responding"
else
    fail "ClickHouse HTTP interface not responding (check: curl http://localhost:8123/ping)"
fi

# Test 3: ClickHouse Play UI accessible
echo "[3/7] Checking ClickHouse Play UI..."
if curl -sf http://localhost:8123/play 2>&1 | grep -q "ClickHouse"; then
    pass "ClickHouse Play UI accessible at http://localhost:8123/play"
else
    fail "ClickHouse Play UI not accessible"
fi

# Test 4: CH-UI container running and accessible
echo "[4/7] Checking CH-UI web interface..."
if docker ps | grep -q "gapless-ch-ui"; then
    if curl -sf http://localhost:5521 > /dev/null 2>&1; then
        pass "CH-UI web interface accessible at http://localhost:5521"
    else
        fail "CH-UI container running but port 5521 not responding"
    fi
else
    warn "CH-UI container not running (optional, run: docker-compose up -d ch-ui)"
fi

# Test 5: clickhouse-client functionality
echo "[5/7] Checking clickhouse-client CLI..."
if docker exec gapless-clickhouse clickhouse-client --query "SELECT 1" 2>&1 | grep -q "1"; then
    pass "clickhouse-client functional (Docker exec)"
else
    fail "clickhouse-client not working"
fi

# Test 6: chdig installation
echo "[6/7] Checking chdig TUI monitoring..."
if command -v chdig > /dev/null 2>&1; then
    if chdig --version > /dev/null 2>&1; then
        pass "chdig installed and operational"
    else
        warn "chdig found but --version failed"
    fi
else
    warn "chdig not installed (optional, install: brew install chdig)"
fi

# Test 7: clickhouse-local functionality
echo "[7/7] Checking clickhouse-local file analysis..."
# Create temporary test CSV
TEST_CSV="/tmp/clickhouse_test_$$.csv"
echo "a,b" > "$TEST_CSV"
echo "1,2" >> "$TEST_CSV"

if docker exec gapless-clickhouse clickhouse-local --query "SELECT * FROM file('$TEST_CSV', CSV)" 2>&1 | grep -q "1"; then
    pass "clickhouse-local functional"
    rm -f "$TEST_CSV"
else
    fail "clickhouse-local not working"
    rm -f "$TEST_CSV"
fi

# Summary
echo ""
echo "=========================================="
echo "Validation Summary"
echo "=========================================="
echo -e "Tests passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests failed: ${RED}${TESTS_FAILED}${NC}"
echo ""

if [ "$TESTS_FAILED" -eq 0 ]; then
    echo -e "${GREEN}✅ All critical validations passed!${NC}"
    echo ""
    echo "Available tools:"
    echo "  - CH-UI:             http://localhost:5521"
    echo "  - ClickHouse Play:   http://localhost:8123/play"
    echo "  - clickhouse-client: docker exec -it gapless-clickhouse clickhouse-client"
    echo "  - chdig:             chdig --host localhost --port 9000"
    echo "  - clickhouse-local:  docker exec gapless-clickhouse clickhouse-local"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some validations failed${NC}"
    echo ""
    echo "Common fixes:"
    echo "  - Start ClickHouse:  docker-compose up -d clickhouse"
    echo "  - Start CH-UI:       docker-compose up -d ch-ui"
    echo "  - Install chdig:     brew install chdig"
    echo ""
    exit 1
fi
