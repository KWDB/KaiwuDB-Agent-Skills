# TS Settings Checklist

Query `SHOW CLUSTER SETTINGS` via MCP and check each parameter below.

## Query Optimization

| Parameter | Type | Default | Abnormal Condition | Recommendation |
|-----------|------|---------|-------------------|----------------|
| `ts.partition_agg.enabled` | b | true | false | `SET CLUSTER SETTING ts.partition_agg.enabled = true;` |
| `ts.count.use_statistics.enabled` | b | true | false | `SET CLUSTER SETTING ts.count.use_statistics.enabled = true;` |

- `ts.partition_agg.enabled` must be true. Without partition aggregation, count/sum/max/min scans all rows instead of using pre-aggregated partitions.
- `ts.count.use_statistics.enabled` must be true. Without it, count queries read full data instead of using table statistics.

## Compression and Encoding

| Parameter | Type | Default | Abnormal Condition | Recommendation |
|-----------|------|---------|-------------------|----------------|
| `ts.compress.algorithm` | s | lz4 | disabled | `SET CLUSTER SETTING ts.compress.algorithm = 'lz4';` |
| `ts.compress.level` | s | medium | — | Adjust based on workload: low for write-heavy, high for read-heavy |
| `ts.compress.stage` | i | 3 | 0 or 1 | `SET CLUSTER SETTING ts.compress.stage = 3;` |
| `ts.compress.last_segment.enabled` | b | false | — | Enable if last-row queries are slow: `SET CLUSTER SETTING ts.compress.last_segment.enabled = true;` |
| `ts.dedup.rule` | s | override | — | `override` for most workloads; `reject` if duplicate timestamps must fail; `filter` to silently skip duplicates |

- `ts.compress.stage` = 0 means no encoding or compression, which wastes storage and slows range scans.
- `ts.compress.stage` = 1 (encoding only) saves less space than full compression.
- `ts.compress.algorithm` = `disabled` disables compression entirely and should almost never be used in production.
- `ts.compress.last_segment.enabled` trades write throughput for last-row query speed.

## Memory and Cache

| Parameter | Type | Default | Abnormal Condition | Recommendation |
|-----------|------|---------|-------------------|----------------|
| `ts.block.lru_cache.max_limit` | z | 1.0 GiB | too low for data volume | Increase when cache hit rate is low |
| `ts.last_cache_size.max_limit` | z | 1.0 GiB | too low for last-row workload | Increase for frequent last-row queries |
| `ts.mem_segment_size.max_limit` | z | 512 MiB | too low for write bursts | Increase if write stalls occur during bursts |
| `ts.metric_schema_cache.max_limit` | i | 100 | cache evictions frequent | Increase when many metric tables exist |
| `ts.table_cache.capacity` | i | 1000 | cache evictions frequent | Increase for clusters with many time-series tables |

- All cache sizes should be evaluated relative to available system memory and data volume.
- If the cluster hosts many time-series tables, increase `ts.table_cache.capacity` and `ts.metric_schema_cache.max_limit` to avoid repeated metadata lookups.
- `ts.last_cache_size.max_limit` is critical for workloads that rely on last-row queries.

## Storage and Background Tasks

| Parameter | Type | Default | Abnormal Condition | Recommendation |
|-----------|------|---------|-------------------|----------------|
| `ts.rows_per_block.max_limit` | i | 4096 | — | Larger blocks improve compression ratio but increase read amplification |
| `ts.rows_per_block.min_limit` | i | 512 | — | Smaller min limit reduces waste for sparse data |
| `ts.reserved_last_segment.max_limit` | i | 3 | too low | Increase if last-row queries scan many segments |
| `ts.compact.max_limit` | i | 10 | too low for large clusters | Increase if compaction lag is visible |
| `ts.auto_vacuum.enabled` | b | true | false | `SET CLUSTER SETTING ts.auto_vacuum.enabled = true;` |
| `ts.agg_recalc.cycle` | i | 1800 | 0 (disabled) | `SET CLUSTER SETTING ts.agg_recalc.cycle = 1800;` |
| `ts.block_filter.sampling_ratio` | f | 0.2 | — | Increase toward 1.0 for more accurate filtering at higher CPU cost |

- `ts.auto_vacuum.enabled` must be true. Disabling it causes stale data accumulation.
- `ts.agg_recalc.cycle` = 0 disables aggregate recalculation, which can cause stale partition aggregates.
- `ts.compact.max_limit` should match the I/O capacity of the storage subsystem.

## Diagnostic Queries

Use MCP to fetch current settings:

```sql
-- Fetch all cluster settings (filter for ts.* prefix)
SHOW CLUSTER SETTINGS;

-- Fetch individual settings for targeted checks
SHOW CLUSTER SETTING ts.partition_agg.enabled;
SHOW CLUSTER SETTING ts.count.use_statistics.enabled;
SHOW CLUSTER SETTING ts.compress.algorithm;
SHOW CLUSTER SETTING ts.compress.stage;
SHOW CLUSTER SETTING ts.compress.level;
SHOW CLUSTER SETTING ts.compress.last_segment.enabled;
SHOW CLUSTER SETTING ts.dedup.rule;
SHOW CLUSTER SETTING ts.block.lru_cache.max_limit;
SHOW CLUSTER SETTING ts.last_cache_size.max_limit;
SHOW CLUSTER SETTING ts.mem_segment_size.max_limit;
SHOW CLUSTER SETTING ts.metric_schema_cache.max_limit;
SHOW CLUSTER SETTING ts.table_cache.capacity;
SHOW CLUSTER SETTING ts.rows_per_block.max_limit;
SHOW CLUSTER SETTING ts.rows_per_block.min_limit;
SHOW CLUSTER SETTING ts.reserved_last_segment.max_limit;
SHOW CLUSTER SETTING ts.compact.max_limit;
SHOW CLUSTER SETTING ts.auto_vacuum.enabled;
SHOW CLUSTER SETTING ts.agg_recalc.cycle;
SHOW CLUSTER SETTING ts.block_filter.sampling_ratio;
```

## Inter-Setting Dependencies

Some settings interact and must be reviewed together:

| Setting A | Setting B | Interaction |
|-----------|-----------|-------------|
| `ts.compress.algorithm` | `ts.compress.stage` | `stage=0` makes algorithm irrelevant (no compression applied). `stage=2` without encoding (stage=1 feature) misses delta-of-delta and gorilla encoding. |
| `ts.last_cache_size.max_limit` | `ts.compress.last_segment.enabled` | Both affect last-row query performance. Increasing cache size helps more than enabling last segment compression. Enabling last segment compression trades write throughput for last-row speed. |
| `ts.partition_agg.enabled` | `ts.count.use_statistics.enabled` | Both must be true for count optimization. `partition_agg=true` alone is insufficient if `count_statistics=false`. |
| `ts.compact.max_limit` | `ts.auto_vacuum.enabled` | Compaction and vacuum work together. Disabling either causes data accumulation. `compact.max_limit` controls compaction concurrency; `auto_vacuum` controls stale data cleanup. |

## Memory Sizing Tiers

| Cluster Size | Available RAM | block.lru_cache | last_cache_size | mem_segment_size | table_cache.capacity | metric_schema_cache |
|-------------|--------------|-----------------|-----------------|------------------|---------------------|-------------------|
| Small (< 16 GiB) | < 16 GiB | 1.0 GiB (default) | 1.0 GiB (default) | 512 MiB (default) | 1000 (default) | 100 (default) |
| Medium (16-64 GiB) | 16-64 GiB | 2.0-4.0 GiB | 2.0-4.0 GiB | 1.0 GiB | 2000 | 200 |
| Large (> 64 GiB) | > 64 GiB | 4.0-8.0 GiB | 4.0-8.0 GiB | 2.0 GiB | 5000 | 500 |

- All cache sizes should be evaluated relative to available system memory and data volume.
- If the cluster hosts many time-series tables, increase `ts.table_cache.capacity` and `ts.metric_schema_cache.max_limit` to avoid repeated metadata lookups.
- `ts.last_cache_size.max_limit` is critical for workloads that rely on last-row queries.
- **Warning**: total cache allocation must not exceed ~50% of available RAM to leave room for query execution and OS.
