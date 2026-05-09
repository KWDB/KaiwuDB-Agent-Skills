# Demo Prompts

## Configuration Review

- Review my KWDB ts.* cluster settings for any misconfiguration.
- Check if my KWDB time-series compression and cache settings are optimal.
- 审查我的KWDB时序表配置参数
- 我的ts.*参数需要调优吗

## Compression Review

- Should I change the compression algorithm from lz4 to zstd for my time-series data?
- My time-series storage is growing faster than expected. Can compression help?
- 压缩策略需要调整吗

## Cache and Memory Sizing

- My KWDB cluster has many time-series tables and performance is degrading. Could cache be the issue?
- My last-row queries on time-series tables are slow. What should I check?
- 缓存大小是否足够

## Implicit Performance Issues

- My KWDB time-series aggregation query is slow. Can you review the performance?
- The COUNT query on my time-series table takes too long. Help me diagnose it.
- 时序数据查询性能差，检查一下配置
- My time-series table is growing without bounds. Is there a lifecycle setting I'm missing?

## Edge Cases

- Help me review both compression settings and cache sizing for my sensor cluster.
- I changed ts.compress.algorithm but storage is still growing. What else should I check?
