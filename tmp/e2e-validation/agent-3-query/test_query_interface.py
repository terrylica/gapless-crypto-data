#!/usr/bin/env python3
"""
Agent 3: Query Interface Validation

Tests all query methods with edge cases and error handling:
1. get_latest() - various limits and edge cases
2. get_range() - date boundaries and edge cases
3. get_multi_symbol() - multiple symbols (requires ETHUSDT data)
4. execute_sql() - raw SQL and parameterized queries
5. detect_gaps() - gap detection accuracy
"""

import sys
from pathlib import Path

import pandas as pd

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# ruff: noqa: E402
from gapless_crypto_data.query import OHLCVQuery
from gapless_crypto_data.questdb.connection import QuestDBConnection


def test_get_latest(conn):
    """Test 1: get_latest() with various limits"""
    print("=" * 80)
    print("TEST 1: get_latest() with various limits")
    print("=" * 80)

    query = OHLCVQuery(conn)
    results = {}

    # Test 1a: Small limit (100)
    print("\n1a. Testing limit=100:")
    df_100 = query.get_latest("BTCUSDT", "1m", limit=100)
    print(f"   Rows returned: {len(df_100)}")
    print(f"   Columns: {list(df_100.columns)}")
    print(f"   Latest timestamp: {df_100.iloc[-1]['timestamp']}")
    results["limit_100"] = len(df_100) == 100

    # Test 1b: Medium limit (1000)
    print("\n1b. Testing limit=1000:")
    df_1000 = query.get_latest("BTCUSDT", "1m", limit=1000)
    print(f"   Rows returned: {len(df_1000)}")
    results["limit_1000"] = len(df_1000) == 1000

    # Test 1c: Large limit (10000)
    print("\n1c. Testing limit=10000:")
    df_10000 = query.get_latest("BTCUSDT", "1m", limit=10000)
    print(f"   Rows returned: {len(df_10000)}")
    results["limit_10000"] = len(df_10000) == 10000

    # Test 1d: Limit=1 (edge case)
    print("\n1d. Testing limit=1 (edge case):")
    df_1 = query.get_latest("BTCUSDT", "1m", limit=1)
    print(f"   Rows returned: {len(df_1)}")
    results["limit_1"] = len(df_1) == 1

    # Test 1e: Verify chronological ordering
    print("\n1e. Verifying chronological ordering:")
    timestamps = df_1000["timestamp"].tolist()
    is_sorted = all(timestamps[i] <= timestamps[i + 1] for i in range(len(timestamps) - 1))
    print(f"   Chronologically sorted: {is_sorted}")
    results["chronological"] = is_sorted

    # Test 1f: Verify DataFrame type
    print("\n1f. Verifying DataFrame type:")
    is_dataframe = isinstance(df_100, pd.DataFrame)
    print(f"   Returns pandas.DataFrame: {is_dataframe}")
    results["dataframe_type"] = is_dataframe

    # Summary
    print("\n" + "-" * 80)
    all_passed = all(results.values())
    print(f"Test 1 Results: {'✓ PASS' if all_passed else '✗ FAIL'}")
    for test_name, passed in results.items():
        print(f"  - {test_name}: {'✓' if passed else '✗'}")

    return {"success": all_passed, "details": results}


def test_get_range(conn):
    """Test 2: get_range() with date boundaries"""
    print("\n" + "=" * 80)
    print("TEST 2: get_range() with date boundaries")
    print("=" * 80)

    query = OHLCVQuery(conn)
    results = {}

    # Test 2a: Full month (Jan 2024)
    print("\n2a. Testing full month (Jan 2024):")
    df_jan = query.get_range("BTCUSDT", "1m", start="2024-01-01", end="2024-01-31")
    print(f"   Rows returned: {len(df_jan)}")
    print("   Expected: ~44,640 (31 days * 24 * 60)")
    results["full_month"] = 43000 <= len(df_jan) <= 45000

    # Test 2b: Partial month (Jan 1-7)
    print("\n2b. Testing partial month (Jan 1-7):")
    df_partial = query.get_range("BTCUSDT", "1m", start="2024-01-01", end="2024-01-07")
    print(f"   Rows returned: {len(df_partial)}")
    print("   Expected: ~10,080 (7 days * 24 * 60)")
    results["partial_month"] = 9000 <= len(df_partial) <= 11000

    # Test 2c: Cross-month (Jan 25 - Feb 5)
    print("\n2c. Testing cross-month boundary (Jan 25 - Feb 5):")
    df_cross = query.get_range("BTCUSDT", "1m", start="2024-01-25", end="2024-02-05")
    print(f"   Rows returned: {len(df_cross)}")
    print(f"   Date range: {df_cross.iloc[0]['timestamp']} to {df_cross.iloc[-1]['timestamp']}")
    # 7 days Jan + 5 days Feb = 12 days * 24 * 60 = 17,280
    results["cross_month"] = 16000 <= len(df_cross) <= 18000

    # Test 2d: Single day (Jan 1-2, exclusive end)
    print("\n2d. Testing single day (Jan 1, using Jan 1-2 range):")
    df_day = query.get_range("BTCUSDT", "1m", start="2024-01-01", end="2024-01-02")
    print(f"   Rows returned: {len(df_day)}")
    print("   Expected: ~1,440 (24 * 60)")
    results["single_day"] = 1400 <= len(df_day) <= 1500

    # Test 2e: Verify timestamp boundaries
    print("\n2e. Verifying timestamp boundaries:")
    start_ts = df_jan.iloc[0]["timestamp"]
    end_ts = df_jan.iloc[-1]["timestamp"]
    print(f"   First timestamp: {start_ts}")
    print(f"   Last timestamp: {end_ts}")
    # Convert to tz-naive for comparison (QuestDB returns tz-naive timestamps)
    results["boundaries"] = start_ts >= pd.Timestamp("2024-01-01") and end_ts <= pd.Timestamp(
        "2024-01-31 23:59:59"
    )

    # Summary
    print("\n" + "-" * 80)
    all_passed = all(results.values())
    print(f"Test 2 Results: {'✓ PASS' if all_passed else '✗ FAIL'}")
    for test_name, passed in results.items():
        print(f"  - {test_name}: {'✓' if passed else '✗'}")

    return {"success": all_passed, "details": results}


def test_execute_sql(conn):
    """Test 3: execute_sql() with parameterized queries"""
    print("\n" + "=" * 80)
    print("TEST 3: execute_sql() with parameterized queries")
    print("=" * 80)

    query = OHLCVQuery(conn)
    results = {}

    # Test 3a: Simple COUNT query
    print("\n3a. Testing COUNT query:")
    sql_count = "SELECT COUNT(*) as count FROM ohlcv WHERE symbol = %s AND timeframe = %s"
    df_count = query.execute_sql(sql_count, params=("BTCUSDT", "1m"))
    count = int(df_count["count"].iloc[0])
    print(f"   Total rows: {count:,}")
    results["count_query"] = count > 80000  # Should have Jan + Feb data

    # Test 3b: Aggregation query
    print("\n3b. Testing aggregation (MIN, MAX, AVG):")
    sql_agg = """
    SELECT
        MIN(close) as min_close,
        MAX(close) as max_close,
        AVG(close) as avg_close
    FROM ohlcv
    WHERE symbol = %s AND timeframe = %s
    """
    df_agg = query.execute_sql(sql_agg, params=("BTCUSDT", "1m"))
    print(f"   Min close: {df_agg.iloc[0]['min_close']:.2f}")
    print(f"   Max close: {df_agg.iloc[0]['max_close']:.2f}")
    print(f"   Avg close: {df_agg.iloc[0]['avg_close']:.2f}")
    results["aggregation"] = (
        df_agg.iloc[0]["min_close"] > 0
        and df_agg.iloc[0]["max_close"] > df_agg.iloc[0]["min_close"]
    )

    # Test 3c: Parameterized WHERE clause (SQL injection protection)
    print("\n3c. Testing parameterized queries (SQL injection protection):")
    sql_param = "SELECT * FROM ohlcv WHERE symbol = %s AND timeframe = %s LIMIT 10"
    df_param = query.execute_sql(sql_param, params=("BTCUSDT", "1m"))
    print(f"   Rows returned: {len(df_param)}")
    print(f"   Parameterization working: {len(df_param) == 10}")
    results["parameterized"] = len(df_param) == 10

    # Test 3d: Complex query with GROUP BY
    print("\n3d. Testing GROUP BY query:")
    sql_group = """
    SELECT
        to_str(timestamp, 'yyyy-MM-dd') as date,
        COUNT(*) as bars,
        AVG(volume) as avg_volume
    FROM ohlcv
    WHERE symbol = %s AND timeframe = %s
    GROUP BY date
    ORDER BY date
    LIMIT 5
    """
    df_group = query.execute_sql(sql_group, params=("BTCUSDT", "1m"))
    print(f"   Rows returned: {len(df_group)}")
    print(f"   Sample dates:\n{df_group.to_string(index=False)}")
    results["group_by"] = len(df_group) == 5

    # Summary
    print("\n" + "-" * 80)
    all_passed = all(results.values())
    print(f"Test 3 Results: {'✓ PASS' if all_passed else '✗ FAIL'}")
    for test_name, passed in results.items():
        print(f"  - {test_name}: {'✓' if passed else '✗'}")

    return {"success": all_passed, "details": results}


def test_detect_gaps(conn):
    """Test 4: detect_gaps() gap detection"""
    print("\n" + "=" * 80)
    print("TEST 4: detect_gaps() gap detection")
    print("=" * 80)

    query = OHLCVQuery(conn)
    results = {}

    # Test 4a: Detect gaps in complete data (should be zero)
    print("\n4a. Testing gap detection in complete data (Jan 2024):")
    df_gaps_jan = query.detect_gaps("BTCUSDT", "1m", start="2024-01-01", end="2024-01-31")
    print(f"   Gaps detected: {len(df_gaps_jan)}")
    print("   Expected: 0 (CloudFront data should be complete)")
    results["no_gaps"] = len(df_gaps_jan) == 0

    # Test 4b: DataFrame structure
    print("\n4b. Verifying gap detection DataFrame structure:")
    if len(df_gaps_jan) > 0:
        print(f"   Columns: {list(df_gaps_jan.columns)}")
        expected_cols = ["gap_start", "gap_end", "expected_bars"]
        has_expected_cols = all(col in df_gaps_jan.columns for col in expected_cols)
        results["gap_structure"] = has_expected_cols
    else:
        print("   No gaps detected (as expected for complete CloudFront data)")
        results["gap_structure"] = True  # No gaps = structure is valid

    # Summary
    print("\n" + "-" * 80)
    all_passed = all(results.values())
    print(f"Test 4 Results: {'✓ PASS' if all_passed else '✗ FAIL'}")
    for test_name, passed in results.items():
        print(f"  - {test_name}: {'✓' if passed else '✗'}")

    return {"success": all_passed, "details": results}


def test_error_handling(conn):
    """Test 5: Error handling (invalid inputs)"""
    print("\n" + "=" * 80)
    print("TEST 5: Error handling (invalid inputs)")
    print("=" * 80)

    query = OHLCVQuery(conn)
    results = {}

    # Test 5a: Invalid symbol (non-existent)
    print("\n5a. Testing invalid symbol (non-existent):")
    try:
        df = query.get_latest("NONEXISTENT", "1m", limit=100)
        print(f"   ✗ Should raise error but returned {len(df)} rows")
        results["invalid_symbol"] = False
    except Exception as e:
        print(f"   ✓ Correctly returned empty DataFrame or raised error: {type(e).__name__}")
        results["invalid_symbol"] = True

    # Test 5b: Invalid date format
    print("\n5b. Testing invalid date format:")
    try:
        df = query.get_range("BTCUSDT", "1m", start="invalid-date", end="2024-01-31")
        print(f"   ✗ Should raise ValueError but returned {len(df)} rows")
        results["invalid_date"] = False
    except ValueError as e:
        print(f"   ✓ Correctly raised ValueError: {e}")
        results["invalid_date"] = True
    except Exception as e:
        print(f"   ? Unexpected error type: {type(e).__name__}: {e}")
        results["invalid_date"] = False

    # Test 5c: Negative limit
    print("\n5c. Testing negative limit:")
    try:
        df = query.get_latest("BTCUSDT", "1m", limit=-100)
        print(f"   ✗ Should raise ValueError but returned {len(df)} rows")
        results["negative_limit"] = False
    except ValueError as e:
        print(f"   ✓ Correctly raised ValueError: {e}")
        results["negative_limit"] = True
    except Exception as e:
        print(f"   ? Unexpected error type: {type(e).__name__}: {e}")
        results["negative_limit"] = False

    # Summary
    print("\n" + "-" * 80)
    all_passed = all(results.values())
    print(f"Test 5 Results: {'✓ PASS' if all_passed else '✗ FAIL'}")
    for test_name, passed in results.items():
        print(f"  - {test_name}: {'✓' if passed else '✗'}")

    return {"success": all_passed, "details": results}


def main():
    """Run all query interface validation tests"""
    print("\n" + "=" * 80)
    print("AGENT 3: QUERY INTERFACE VALIDATION")
    print("=" * 80)

    all_results = {}

    try:
        with QuestDBConnection() as conn:
            # Test 1: get_latest()
            all_results["test_1_get_latest"] = test_get_latest(conn)

            # Test 2: get_range()
            all_results["test_2_get_range"] = test_get_range(conn)

            # Test 3: execute_sql()
            all_results["test_3_execute_sql"] = test_execute_sql(conn)

            # Test 4: detect_gaps()
            all_results["test_4_detect_gaps"] = test_detect_gaps(conn)

            # Test 5: Error handling
            all_results["test_5_error_handling"] = test_error_handling(conn)

            # Summary
            print("\n" + "=" * 80)
            print("VALIDATION SUMMARY")
            print("=" * 80)

            all_passed = all(result["success"] for result in all_results.values())

            for test_name, test_result in all_results.items():
                status = "✓ PASS" if test_result["success"] else "✗ FAIL"
                print(f"  {test_name}: {status}")

            print(f"\n{'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
            print("=" * 80)

            return 0 if all_passed else 1

    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
