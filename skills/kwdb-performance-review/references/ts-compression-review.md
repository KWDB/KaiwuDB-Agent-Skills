# TS Compression Review

Rules for reviewing compression strategy on KWDB time-series tables.

## Compression Algorithm Comparison

| Algorithm | Compression Ratio | CPU Cost | Best For |
|-----------|------------------|----------|----------|
| `lz4` | Low | Very low | Write-heavy workloads, real-time ingestion |
| `zstd` | High | Medium | Read-heavy or storage-constrained workloads |
| `zlib` | Medium-High | High | Archival or rarely-queried data |
| `snappy` | Low | Very low | Low-latency reads with moderate compression |
| `disabled` | None | None | Debugging only; never use in production |

- Default `lz4` is the safest choice for mixed workloads.
- Switch to `zstd` when storage cost is the primary concern and the cluster has CPU headroom.
- `zlib` adds significant CPU overhead; only use for cold data.

## Compression Stage

`ts.compress.stage` controls which encoding and compression steps are applied:

| Value | Meaning | Storage Saved | Query Impact |
|-------|---------|---------------|-------------|
| 0 | None | None | Fastest reads, worst storage |
| 1 | Encoding only | Low | Moderate reads |
| 2 | Compression only | Medium | Moderate reads |
| 3 | Encoding + compression | High | Slightly slower reads due to decompression |

- Stage 3 is the default and recommended for production.
- Stage 0 or 1 should be flagged as abnormal unless the user has an explicit reason (e.g., benchmarking).
- Stage 2 without encoding misses delta-of-delta and gorilla encoding, which are effective for time-series numeric patterns.

## Last Segment Compression

`ts.compress.last_segment.enabled` controls whether the most recent segment is compressed:

- Default: false. The last segment stays uncompressed for fast appends and last-row queries.
- Enable when: last-row queries are not the primary access pattern and storage savings matter.
- Trade-off: enabling it slows down appends and last-row reads on the active partition.

## Deduplication Rule

`ts.dedup.rule` controls how duplicate timestamps are handled:

| Rule | Behavior | Use Case |
|------|----------|----------|
| `override` | Newer value replaces older | Default; most ETL and metric pipelines |
| `reject` | Duplicate timestamp causes error | Strict data integrity requirements |
| `filter` | Duplicate is silently dropped | Idempotent re-ingestion pipelines |

- `override` is the default and works for most workloads.
- `reject` adds write-path overhead for duplicate checking.
- `filter` can silently hide data issues; only use when the ingestion pipeline is known to produce duplicates.

## Compression and Query Performance Trade-off

- Higher compression (zstd + stage 3) reduces I/O for full-partition scans but adds CPU for decompression.
- For queries that read a small fraction of a partition, lower compression (lz4 + stage 3) may be faster because decompression cost dominates.
- For queries that scan entire partitions (aggregation, range scans), higher compression is usually faster because I/O savings outweigh decompression cost.
