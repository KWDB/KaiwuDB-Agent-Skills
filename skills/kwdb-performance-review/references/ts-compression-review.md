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

## Compression Diagnostic Queries

Use MCP to assess current compression state:

```sql
-- Check compression algorithm and stage
SHOW CLUSTER SETTING ts.compress.algorithm;
SHOW CLUSTER SETTING ts.compress.stage;
SHOW CLUSTER SETTING ts.compress.level;
SHOW CLUSTER SETTING ts.compress.last_segment.enabled;
SHOW CLUSTER SETTING ts.dedup.rule;
```

Signs of compression issues:
- Storage growth rate exceeds data ingestion rate (compression may be disabled or ineffective).
- `ts.compress.stage = 0` or `ts.compress.algorithm = 'disabled'` (no compression applied).
- High CPU usage during reads after switching to a high-cost algorithm (decompression overhead).

## Algorithm Migration Guidance

| Migration | When | How | Impact |
|-----------|------|-----|--------|
| `lz4` → `zstd` | Storage cost dominates, CPU headroom exists | `SET CLUSTER SETTING ts.compress.algorithm = 'zstd';` | New writes use zstd; existing data retains lz4 compression |
| `zstd` → `lz4` | Read latency matters more than storage | `SET CLUSTER SETTING ts.compress.algorithm = 'lz4';` | New writes use lz4; existing data retains zstd compression |
| Any → `disabled` | Debugging only | `SET CLUSTER SETTING ts.compress.algorithm = 'disabled';` | Never use in production; causes unbounded storage growth |
| `zlib` → `zstd` | Need similar ratio with less CPU | `SET CLUSTER SETTING ts.compress.algorithm = 'zstd';` | zstd provides comparable ratio with lower CPU cost than zlib |

- Algorithm change affects **new writes only**; existing data retains its original compression.
- After changing algorithm, monitor CPU and read latency to verify the trade-off is acceptable.
- Consider `ts.compress.level` adjustment alongside algorithm change: `low` for write-heavy, `high` for read-heavy.

## Compression Troubleshooting

| Symptom | Likely Cause | Diagnostic | Fix |
|---------|-------------|------------|-----|
| Compression not taking effect | `stage=0` or `algorithm='disabled'` | `SHOW CLUSTER SETTING ts.compress.stage;` and `ts.compress.algorithm;` | Set `stage=3` and `algorithm='lz4'` (or `zstd`) |
| High CPU after switching to zstd | Decompression overhead on read-heavy workload | Monitor CPU metrics; compare with pre-change baseline | Revert to `lz4` if CPU headroom is insufficient |
| Storage still growing after enabling compression | Only new writes are compressed; old data unchanged | Check data age distribution; most data may predate the change | Normal behavior; storage will stabilize as old data is vacuumed |
| Last-row queries slow after enabling last segment compression | Compressed last segment requires decompression | `SHOW CLUSTER SETTING ts.compress.last_segment.enabled;` | Disable: `SET CLUSTER SETTING ts.compress.last_segment.enabled = false;` |
| Write stalls during burst | High compression level on write path | `SHOW CLUSTER SETTING ts.compress.level;` | Lower compression level: `SET CLUSTER SETTING ts.compress.level = 'low';` |
