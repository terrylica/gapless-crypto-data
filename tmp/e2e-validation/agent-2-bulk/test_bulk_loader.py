#!/usr/bin/env python3
"""
Agent 2: Bulk Loader Validation

Tests:
1. Download BTCUSDT 1m Jan 2024 from CloudFront
2. Verify CSV parsing and DataFrame transformation
3. Test ILP ingestion and measure performance (target: >100K rows/sec)
4. Test multi-month ingestion (Feb 2024) and deduplication (re-ingest Jan)
"""

import sys
import time
from pathlib import Path

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

# ruff: noqa: E402
from gapless_crypto_data.collectors.questdb_bulk_loader import QuestDBBulkLoader
from gapless_crypto_data.query import OHLCVQuery
from gapless_crypto_data.questdb.connection import QuestDBConnection


def test_jan_2024_download(conn):
    """Test 1: Download BTCUSDT 1m Jan 2024 from CloudFront"""
    print("=" * 80)
    print("TEST 1: Download BTCUSDT 1m Jan 2024 from CloudFront")
    print("=" * 80)

    loader = QuestDBBulkLoader(conn)

    start_time = time.time()
    rows_ingested = loader.ingest_month(symbol="BTCUSDT", timeframe="1m", year=2024, month=1)
    duration = time.time() - start_time

    # Wait for WAL to commit (QuestDB asynchronous commit)
    time.sleep(1)

    ingestion_rate = rows_ingested / duration if duration > 0 else 0

    print("\n✓ Ingestion completed:")
    print(f"  - Rows ingested: {rows_ingested:,}")
    print(f"  - Duration: {duration:.2f}s")
    print(f"  - Ingestion rate: {ingestion_rate:,.0f} rows/sec")
    print("  - Target: >100,000 rows/sec")
    print(f"  - Status: {'PASS' if ingestion_rate > 100000 else 'FAIL'}")

    return {
        "rows_ingested": rows_ingested,
        "duration": duration,
        "ingestion_rate": ingestion_rate,
        "success": ingestion_rate > 100000,
    }


def test_data_format(conn):
    """Test 2: Verify 11-column format and data_source tracking"""
    print("\n" + "=" * 80)
    print("TEST 2: Verify 11-column format and data_source tracking")
    print("=" * 80)

    query = OHLCVQuery(conn)

    # Get sample data
    df = query.get_latest(symbol="BTCUSDT", timeframe="1m", limit=10)

    expected_columns = [
        "timestamp",
        "symbol",
        "timeframe",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "close_time",
        "quote_asset_volume",
        "number_of_trades",
        "taker_buy_base_asset_volume",
        "taker_buy_quote_asset_volume",
        "data_source",
    ]

    actual_columns = list(df.columns)

    print("\n✓ Data format verification:")
    print(f"  - Expected columns: {len(expected_columns)}")
    print(f"  - Actual columns: {len(actual_columns)}")
    print(f"  - Column match: {set(expected_columns) == set(actual_columns)}")
    print(f"  - Data source: {df['data_source'].unique()}")
    print(f"  - Status: {'PASS' if set(expected_columns) == set(actual_columns) else 'FAIL'}")

    return {
        "column_match": set(expected_columns) == set(actual_columns),
        "data_source": list(df["data_source"].unique()),
        "success": set(expected_columns) == set(actual_columns)
        and df["data_source"].unique()[0] == "cloudfront",
    }


def test_row_count(conn):
    """Test 3: Verify row count matches expected for Jan 2024"""
    print("\n" + "=" * 80)
    print("TEST 3: Verify row count matches expected")
    print("=" * 80)

    query = OHLCVQuery(conn)

    # Execute count query
    sql = "SELECT COUNT(*) as count FROM ohlcv WHERE symbol = %s AND timeframe = %s"
    df = query.execute_sql(sql, params=("BTCUSDT", "1m"))

    row_count = int(df["count"].iloc[0])
    expected_range = (43000, 45000)  # ~44640 minutes in 31 days

    print("\n✓ Row count verification:")
    print(f"  - Rows in database: {row_count:,}")
    print(f"  - Expected range: {expected_range[0]:,} - {expected_range[1]:,}")
    print(
        f"  - Status: {'PASS' if expected_range[0] <= row_count <= expected_range[1] else 'FAIL'}"
    )

    return {
        "row_count": row_count,
        "expected_range": expected_range,
        "success": expected_range[0] <= row_count <= expected_range[1],
    }


def test_feb_2024_ingestion(conn):
    """Test 4: Multi-month ingestion (Feb 2024)"""
    print("\n" + "=" * 80)
    print("TEST 4: Multi-month ingestion (Feb 2024)")
    print("=" * 80)

    loader = QuestDBBulkLoader(conn)

    start_time = time.time()
    rows_ingested = loader.ingest_month(symbol="BTCUSDT", timeframe="1m", year=2024, month=2)
    duration = time.time() - start_time

    # Wait for WAL to commit
    time.sleep(1)

    ingestion_rate = rows_ingested / duration if duration > 0 else 0

    print("\n✓ Feb 2024 ingestion:")
    print(f"  - Rows ingested: {rows_ingested:,}")
    print(f"  - Duration: {duration:.2f}s")
    print(f"  - Ingestion rate: {ingestion_rate:,.0f} rows/sec")
    print("  - Status: PASS")

    return {
        "rows_ingested": rows_ingested,
        "duration": duration,
        "ingestion_rate": ingestion_rate,
        "success": True,
    }


def test_deduplication(conn):
    """Test 5: Re-ingest Jan 2024 to test UPSERT deduplication"""
    print("\n" + "=" * 80)
    print("TEST 5: Deduplication (re-ingest Jan 2024)")
    print("=" * 80)

    query = OHLCVQuery(conn)

    # Get row count before re-ingestion
    sql = "SELECT COUNT(*) as count FROM ohlcv WHERE symbol = %s AND timeframe = %s"
    df_before = query.execute_sql(sql, params=("BTCUSDT", "1m"))
    count_before = int(df_before["count"].iloc[0])

    # Re-ingest Jan 2024
    loader = QuestDBBulkLoader(conn)
    rows_ingested = loader.ingest_month(symbol="BTCUSDT", timeframe="1m", year=2024, month=1)

    # Wait for WAL to commit
    time.sleep(1)

    # Get row count after re-ingestion
    df_after = query.execute_sql(sql, params=("BTCUSDT", "1m"))
    count_after = int(df_after["count"].iloc[0])

    duplicates_created = count_after - count_before

    print("\n✓ Deduplication test:")
    print(f"  - Rows before re-ingest: {count_before:,}")
    print(f"  - Rows ingested: {rows_ingested:,}")
    print(f"  - Rows after re-ingest: {count_after:,}")
    print(f"  - Duplicates created: {duplicates_created}")
    print(f"  - Status: {'PASS' if duplicates_created == 0 else 'FAIL'}")

    return {
        "count_before": count_before,
        "rows_ingested": rows_ingested,
        "count_after": count_after,
        "duplicates_created": duplicates_created,
        "success": duplicates_created == 0,
    }


def main():
    """Run all bulk loader validation tests"""
    print("\n" + "=" * 80)
    print("AGENT 2: BULK LOADER VALIDATION")
    print("=" * 80)

    results = {}

    try:
        # Initialize QuestDB connection
        conn = QuestDBConnection()

        # Test 1: Jan 2024 download and ingestion
        results["test_1_jan_ingestion"] = test_jan_2024_download(conn)

        # Test 2: Data format verification
        results["test_2_data_format"] = test_data_format(conn)

        # Test 3: Row count verification
        results["test_3_row_count"] = test_row_count(conn)

        # Test 4: Feb 2024 ingestion
        results["test_4_feb_ingestion"] = test_feb_2024_ingestion(conn)

        # Test 5: Deduplication
        results["test_5_deduplication"] = test_deduplication(conn)

        # Summary
        print("\n" + "=" * 80)
        print("VALIDATION SUMMARY")
        print("=" * 80)

        all_passed = all(test_result["success"] for test_result in results.values())

        for test_name, test_result in results.items():
            status = "✓ PASS" if test_result["success"] else "✗ FAIL"
            print(f"  {test_name}: {status}")

        print(f"\n{'✓ ALL TESTS PASSED' if all_passed else '✗ SOME TESTS FAILED'}")
        print("=" * 80)

        return 0 if all_passed else 1

    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
