## Inspectable Metrics

The following table lists all metrics available for inspection via the `/ts/query` API. These metrics are queried from the `kwdb_internal.metrics_metadata` internal view.

**SQL Query:**

```sql
SELECT * FROM kwdb_internal.metrics_metadata;
```

**Note:** The `kwdb_internal.metrics_metadata` view is only available in KaiwuDB Enterprise Edition. It is not available in KaiwuDB Community Edition.

| Name | Help | Measurement | Unit |
|------|------|-------------|------|
| security.certificate.expiration.ca | Expiration for the CA certificate. 0 means no certificate or error. | Certificate Expiration | TIMESTAMP_SEC |
| security.certificate.expiration.client-ca | Expiration for the client CA certificate. 0 means no certificate or error. | Certificate Expiration | TIMESTAMP_SEC |
| security.certificate.expiration.ui-ca | Expiration for the UI CA certificate. 0 means no certificate or error. | Certificate Expiration | TIMESTAMP_SEC |
| security.certificate.expiration.node | Expiration for the node certificate. 0 means no certificate or error. | Certificate Expiration | TIMESTAMP_SEC |
| security.certificate.expiration.node-client | Expiration for the node's client certificate. 0 means no certificate or error. | Certificate Expiration | TIMESTAMP_SEC |
| security.certificate.expiration.ui | Expiration for the UI certificate. 0 means no certificate or error. | Certificate Expiration | TIMESTAMP_SEC |
| rpc.heartbeats.loops.started | Counter of the number of connection heartbeat loops which have been started | Connections | COUNT |
| rpc.heartbeats.loops.exited | Counter of the number of connection heartbeat loops which have exited with an error | Connections | COUNT |
| rpc.heartbeats.initializing | Gauge of current connections in the initializing state | Connections | COUNT |
| rpc.heartbeats.nominal | Gauge of current connections in the nominal state | Connections | COUNT |
| rpc.heartbeats.failed | Gauge of current connections in the failed state | Connections | COUNT |
| gossip.connections.incoming | Number of active incoming gossip connections | Connections | COUNT |
| gossip.connections.refused | Number of refused incoming gossip connections | Connections | COUNT |
| gossip.connections.outgoing | Number of active outgoing gossip connections | Connections | COUNT |
| gossip.bytes.received | Number of received gossip bytes | Gossip Bytes | BYTES |
| gossip.bytes.sent | Number of sent gossip bytes | Gossip Bytes | BYTES |
| gossip.infos.received | Number of received gossip Info objects | Infos | COUNT |
| gossip.infos.sent | Number of sent gossip Info objects | Infos | COUNT |
| distsender.batches | Number of batches processed | Batches | COUNT |
| distsender.batches.partial | Number of partial batches processed after being divided on range boundaries | Partial Batches | COUNT |
| distsender.batches.async.sent | Number of partial batches sent asynchronously | Partial Batches | COUNT |
| distsender.batches.async.throttled | Number of partial batches not sent asynchronously due to throttling | Partial Batches | COUNT |
| distsender.rpc.sent | Number of RPCs sent | RPCs | COUNT |
| distsender.rpc.sent.local | Number of local RPCs sent | RPCs | COUNT |
| distsender.rpc.sent.nextreplicaerror | Number of RPCs sent due to per-replica errors | RPCs | COUNT |
| distsender.errors.notleaseholder | Number of NotLeaseHolderErrors encountered | Errors | COUNT |
| distsender.errors.inleasetransferbackoffs | Number of times backed off due to NotLeaseHolderErrors during lease transfer. | Errors | COUNT |
| distsender.rangelookups | Number of range lookups. | Range Lookups | COUNT |
| requests.slow.distsender | Number of RPCs stuck or retrying for a long time | Requests | COUNT |
| txn.aborts | Number of aborted KV transactions | KV Transactions | COUNT |
| txn.commits | Number of committed KV transactions (including 1PC) | KV Transactions | COUNT |
| txn.commits1PC | Number of KV transaction on-phase commit attempts | KV Transactions | COUNT |
| txn.parallelcommits | Number of KV transaction parallel commit attempts | KV Transactions | COUNT |
| txn.refresh.success | Number of successful refreshes | Refreshes | COUNT |
| txn.refresh.fail | Number of failed refreshes | Refreshes | COUNT |
| txn.refresh.fail_with_condensed_spans | Number of failed refreshes for transactions whose read tracking lost fidelity because of condensing. | Refreshes | COUNT |
| txn.refresh.memory_limit_exceeded | Number of transaction which exceed the refresh span bytes limit | Transactions | COUNT |
| txn.durations | KV transaction durations | KV Txn Duration | NANOSECONDS |
| txn.condensed_intent_spans | KV transactions that have exceeded their intent tracking memory budget | KV Transactions | COUNT |
| txn.condensed_intent_spans_gauge | KV transactions currently running that have exceeded their intent tracking memory budget | KV Transactions | COUNT |
| txn.restarts | Number of restarted KV transactions | KV Transactions | COUNT |
| txn.restarts.writetooold | Number of restarts due to a concurrent writer committing first | Restarted Transactions | COUNT |
| txn.restarts.writetoooldmulti | Number of restarts due to multiple concurrent writers committing first | Restarted Transactions | COUNT |
| txn.restarts.serializable | Number of restarts due to a forwarded commit timestamp and isolation=SERIALIZABLE | Restarted Transactions | COUNT |
| txn.restarts.asyncwritefailure | Number of restarts due to async consensus writes that failed to leave intents | Restarted Transactions | COUNT |
| txn.restarts.readwithinuncertainty | Number of restarts due to reading a new value within the uncertainty interval | Restarted Transactions | COUNT |
| txn.restarts.txnaborted | Number of restarts due to an abort by a concurrent transaction | Restarted Transactions | COUNT |
| txn.restarts.txnpush | Number of restarts due to a transaction push failure | Restarted Transactions | COUNT |
| txn.restarts.unknown | Number of restarts due to a unknown reasons | Restarted Transactions | COUNT |
| liveness.livenodes | Number of live nodes in the cluster | Nodes | COUNT |
| liveness.heartbeatsuccesses | Number of successful node liveness heartbeats from this node | Messages | COUNT |
| liveness.heartbeatfailures | Number of failed node liveness heartbeats from this node | Messages | COUNT |
| liveness.epochincrements | Number of times this node has incremented its liveness epoch | Epochs | COUNT |
| liveness.heartbeatlatency | Node liveness heartbeat latency | Latency | NANOSECONDS |
| sql.mem.internal.max | Memory usage per sql statement for internal | Memory | BYTES |
| sql.mem.internal.current | Current sql statement memory usage for internal | Memory | BYTES |
| sql.mem.internal.txn.max | Memory usage per sql transaction for internal | Memory | BYTES |
| sql.mem.internal.txn.current | Current sql transaction memory usage for internal | Memory | BYTES |
| sql.mem.internal.session.max | Memory usage per sql session for internal | Memory | BYTES |
| sql.mem.internal.session.current | Current sql session memory usage for internal | Memory | BYTES |
| sql.mem.bulk.max | Memory usage per sql statement for bulk operations | Memory | BYTES |
| sql.mem.bulk.current | Current sql statement memory usage for bulk operations | Memory | BYTES |
| sql.mem.admin.max | Memory usage per sql statement for admin | Memory | BYTES |
| sql.mem.admin.current | Current sql statement memory usage for admin | Memory | BYTES |
| sql.mem.admin.txn.max | Memory usage per sql transaction for admin | Memory | BYTES |
| sql.mem.admin.txn.current | Current sql transaction memory usage for admin | Memory | BYTES |
| sql.mem.admin.session.max | Memory usage per sql session for admin | Memory | BYTES |
| sql.mem.admin.session.current | Current sql session memory usage for admin | Memory | BYTES |
| timeseries.write.samples | Total number of metric samples written to disk | Metric Samples | COUNT |
| timeseries.write.bytes | Total size in bytes of metric samples written to disk | Storage | BYTES |
| timeseries.write.errors | Total errors encountered while attempting to write metrics to disk | Errors | COUNT |
| clock-offset.meannanos | Mean clock offset with other nodes | Clock Offset | NANOSECONDS |
| clock-offset.stddevnanos | Stddev clock offset with other nodes | Clock Offset | NANOSECONDS |
| round-trip-latency | Distribution of round-trip latencies with other nodes | Roundtrip Latency | NANOSECONDS |
| sys.cgocalls | Total number of cgo calls | cgo Calls | COUNT |
| sys.goroutines | Current number of goroutines | goroutines | COUNT |
| sys.go.allocbytes | Current bytes of memory allocated by go | Memory | BYTES |
| sys.go.totalbytes | Total bytes of memory allocated by go, but not released | Memory | BYTES |
| sys.cgo.allocbytes | Current bytes of memory allocated by cgo | Memory | BYTES |
| sys.cgo.totalbytes | Total bytes of memory allocated by cgo, but not released | Memory | BYTES |
| sys.kmalloc.totalbytes | Current bytes of memory allocated by Kmalloc | Kamlloc | BYTES |
| sys.memory.map.virtualbytes | Total virtual bytes of memory map | Memory | BYTES |
| sys.memory.map.physicalbytes | Total physical bytes of memory map allocated | Memory | BYTES |
| sys.memory.map.totalcount | Total region count of memory map allocated | Memory | COUNT |
| sys.gc.count | Total number of GC runs | GC Runs | COUNT |
| sys.gc.pause.ns | Total GC pause | GC Pause | NANOSECONDS |
| sys.gc.pause.percent | Current GC pause percentage | GC Pause | PERCENT |
| sys.cpu.user.ns | Total user cpu time | CPU Time | NANOSECONDS |
| sys.cpu.user.percent | Current user cpu percentage | CPU Time | PERCENT |
| sys.cpu.sys.ns | Total system cpu time | CPU Time | NANOSECONDS |
| sys.cpu.sys.percent | Current system cpu percentage | CPU Time | PERCENT |
| sys.cpu.combined.percent-normalized | Current user+system cpu percentage, normalized 0-1 by number of cores | CPU Time | PERCENT |
| sys.rss | Current process RSS | RSS | BYTES |
| sys.fd.open | Process open file descriptors | File Descriptors | COUNT |
| sys.fd.softlimit | Process open FD soft limit | File Descriptors | COUNT |
| sys.host.disk.read.bytes | Bytes read from all disks since this process started | Bytes | BYTES |
| sys.host.disk.read.count | Disk read operations across all disks since this process started | Operations | COUNT |
| sys.host.disk.read.time | Time spent reading from all disks since this process started | Time | NANOSECONDS |
| sys.host.disk.write.bytes | Bytes written to all disks since this process started | Bytes | BYTES |
| sys.host.disk.write.count | Disk write operations across all disks since this process started | Operations | COUNT |
| sys.host.disk.write.time | Time spent writing to all disks since this process started | Time | NANOSECONDS |
| sys.host.disk.io.time | Time spent reading from or writing to all disks since this process started | Time | NANOSECONDS |
| sys.host.disk.weightedio.time | Weighted time spent reading from or writing to all disks since this process started | Time | NANOSECONDS |
| sys.host.disk.iopsinprogress | IO operations currently in progress on this host | Operations | COUNT |
| sys.host.net.recv.bytes | Bytes received on all network interfaces since this process started | Bytes | BYTES |
| sys.host.net.recv.packets | Packets received on all network interfaces since this process started | Packets | COUNT |
| sys.host.net.send.bytes | Bytes sent on all network interfaces since this process started | Bytes | BYTES |
| sys.host.net.send.packets | Packets sent on all network interfaces since this process started | Packets | COUNT |
| sys.uptime | Process uptime | Uptime | SECONDS |
| build.timestamp | Build information | Build Time | TIMESTAMP_SEC |
| exec.latency | Latency of batch KV requests executed on this node | Latency | NANOSECONDS |
| exec.success | Number of batch KV requests executed successfully on this node | Batch KV Requests | COUNT |
| exec.error | Number of batch KV requests that failed to execute on this node | Batch KV Requests | COUNT |
| engine.stalls | Number of disk stalls detected on this node | Disk stalls detected | COUNT |
| wal.replica.data.latency | Latency histogram for wal replication lag | Latency | NANOSECONDS |
| wal.replica.data.apply.count | Applied wal count on secondary | Count | COUNT |
| rangefeed.replicating.events_ingested | Events ingested by all ingestion jobs | Events | COUNT |
| rangefeed.replicating.ingested_bytes | Bytes ingested by all ingestion jobs | Bytes | BYTES |
| rangefeed.replicating.flushes | Total flushes across all ingestion jobs | Flushes | COUNT |
| rangefeed.replicating.job_progress_updates | Total number of updates to the ingestion job progress | Job Updates | COUNT |
| rangefeed.replicating.resolved_events_ingested | Resolved events ingested by all ingestion jobs | Events | COUNT |
| rangefeed.replicating.flush_hist_nanos | Time spent flushing messages across all replication streams | Nanoseconds | NANOSECONDS |
| rangefeed.replicating.commit_latency | Event commit latency | Nanoseconds | NANOSECONDS |
| rangefeed.replicating.admit_latency | Event admission latency | Nanoseconds | NANOSECONDS |
| rangefeed.replicating.running | Number of currently running replication streams | Replication Streams | COUNT |
| rangefeed.replicating.earliest_data_checkpoint_span | The earliest timestamp of the last checkpoint forwarded by an ingestion data processor | Timestamp | TIMESTAMP_NS |
| rangefeed.replicating.latest_data_checkpoint_span | The latest timestamp of the last checkpoint forwarded by an ingestion data processor | Timestamp | TIMESTAMP_NS |
| rangefeed.replicating.data_checkpoint_span_count | The number of resolved spans in the last checkpoint forwarded by an ingestion data processor | Resolved Spans | COUNT |
| rangefeed.replicating.frontier_checkpoint_span_count | The number of resolved spans last persisted to the ingestion job's checkpoint record | Resolved Spans | COUNT |
| rangefeed.replicating.txn_received_count | Total number of received txns | Received Txns | COUNT |
| rangefeed.replicating.txn_replayed_counts | Total number of txn replayed counts | Txn Counts | COUNT |
| rangefeed.replicating.txn_overstock_ratio | Ratio of overstocked txns to replayer count | Overstocked Txns Ratio | COUNT |
| kv.protectedts.reconciliation.num_runs | number of successful reconciliation runs on this node | Count | COUNT |
| kv.protectedts.reconciliation.records_processed | number of records processed without error during reconciliation on this node | Count | COUNT |
| kv.protectedts.reconciliation.records_removed | number of records removed during reconciliation runs on this node | Count | COUNT |
| kv.protectedts.reconciliation.errors | number of errors encountered during reconciliation runs on this node | Count | COUNT |
| sql.distsql.queries.active | Number of distributed SQL queries currently active | Queries | COUNT |
| sql.distsql.queries.total | Number of distributed SQL queries executed | Queries | COUNT |
| sql.distsql.flows.active | Number of distributed SQL flows currently active | Flows | COUNT |
| sql.distsql.flows.total | Number of distributed SQL flows executed | Flows | COUNT |
| sql.distsql.flows.queued | Number of distributed SQL flows currently queued | Flows | COUNT |
| sql.distsql.flows.queue_wait | Duration of time flows spend waiting in the queue | Nanoseconds | NANOSECONDS |
| sql.mem.distsql.max | Memory usage per sql statement for distsql | Memory | BYTES |
| sql.mem.distsql.current | Current sql statement memory usage for distsql | Memory | BYTES |
| sql.distsql.vec.openfds | Current number of open file descriptors used by vectorized external storage | Files | COUNT |
| sql.disk.distsql.current | Current sql statement disk usage for distsql | Disk | BYTES |
| sql.disk.distsql.max | Disk usage per sql statement for distsql | Disk | BYTES |
| sql.mem.sql.max | Memory usage per sql statement for sql | Memory | BYTES |
| sql.mem.sql.current | Current sql statement memory usage for sql | Memory | BYTES |
| sql.mem.sql.txn.max | Memory usage per sql transaction for sql | Memory | BYTES |
| sql.mem.sql.txn.current | Current sql transaction memory usage for sql | Memory | BYTES |
| sql.mem.sql.session.max | Memory usage per sql session for sql | Memory | BYTES |
| sql.mem.sql.session.current | Current sql session memory usage for sql | Memory | BYTES |
| sql.bytesin | Number of sql bytes received | SQL Bytes | BYTES |
| sql.bytesout | Number of sql bytes sent | SQL Bytes | BYTES |
| sql.conns | Number of active sql connections | Connections | COUNT |
| sql.suc_conns | Number of active sql connections that have been successfully established | Connections | COUNT |
| sql.new_conns | Counter of the number of sql connections created | Connections | COUNT |
| sql.mem.conns.max | Memory usage per sql statement for conns | Memory | BYTES |
| sql.mem.conns.current | Current sql statement memory usage for conns | Memory | BYTES |
| sql.mem.conns.txn.max | Memory usage per sql transaction for conns | Memory | BYTES |
| sql.mem.conns.txn.current | Current sql transaction memory usage for conns | Memory | BYTES |
| sql.mem.conns.session.max | Memory usage per sql session for conns | Memory | BYTES |
| sql.mem.conns.session.current | Current sql session memory usage for conns | Memory | BYTES |
| sql.query.started.count | Number of SQL queries started | SQL Statements | COUNT |
| sql.select.started.count | Number of SQL SELECT statements started | SQL Statements | COUNT |
| sql.update.started.count | Number of SQL UPDATE statements started | SQL Statements | COUNT |
| sql.insert.started.count | Number of SQL INSERT statements started | SQL Statements | COUNT |
| sql.delete.started.count | Number of SQL DELETE statements started | SQL Statements | COUNT |
| sql.txn.begin.started.count | Number of SQL transaction BEGIN statements started | SQL Statements | COUNT |
| sql.txn.commit.started.count | Number of SQL transaction COMMIT statements started | SQL Statements | COUNT |
| sql.txn.rollback.started.count | Number of SQL transaction ROLLBACK statements started | SQL Statements | COUNT |
| sql.savepoint.started.count | Number of SQL SAVEPOINT statements started | SQL Statements | COUNT |
| sql.savepoint.release.started.count | Number of `RELEASE SAVEPOINT` statements started | SQL Statements | COUNT |
| sql.savepoint.rollback.started.count | Number of `ROLLBACK TO SAVEPOINT` statements started | SQL Statements | COUNT |
| sql.restart_savepoint.started.count | Number of `SAVEPOINT kwbase_restart` statements started | SQL Statements | COUNT |
| sql.restart_savepoint.release.started.count | Number of `RELEASE SAVEPOINT kwbase_restart` statements started | SQL Statements | COUNT |
| sql.restart_savepoint.rollback.started.count | Number of `ROLLBACK TO SAVEPOINT kwbase_restart` statements started | SQL Statements | COUNT |
| sql.ddl.started.count | Number of SQL DDL statements started | SQL Statements | COUNT |
| sql.misc.started.count | Number of other SQL statements started | SQL Statements | COUNT |
| sql.query.count | Number of SQL queries executed | SQL Statements | COUNT |
| sql.select.count | Number of SQL SELECT statements successfully executed | SQL Statements | COUNT |
| sql.update.count | Number of SQL UPDATE statements successfully executed | SQL Statements | COUNT |
| sql.insert.count | Number of SQL INSERT statements successfully executed | SQL Statements | COUNT |
| sql.delete.count | Number of SQL DELETE statements successfully executed | SQL Statements | COUNT |
| sql.txn.begin.count | Number of SQL transaction BEGIN statements successfully executed | SQL Statements | COUNT |
| sql.txn.commit.count | Number of SQL transaction COMMIT statements successfully executed | SQL Statements | COUNT |
| sql.txn.rollback.count | Number of SQL transaction ROLLBACK statements successfully executed | SQL Statements | COUNT |
| sql.savepoint.count | Number of SQL SAVEPOINT statements successfully executed | SQL Statements | COUNT |
| sql.savepoint.release.count | Number of `RELEASE SAVEPOINT` statements successfully executed | SQL Statements | COUNT |
| sql.savepoint.rollback.count | Number of `ROLLBACK TO SAVEPOINT` statements successfully executed | SQL Statements | COUNT |
| sql.restart_savepoint.count | Number of `SAVEPOINT kwbase_restart` statements successfully executed | SQL Statements | COUNT |
| sql.restart_savepoint.release.count | Number of `RELEASE SAVEPOINT kwbase_restart` statements successfully executed | SQL Statements | COUNT |
| sql.restart_savepoint.rollback.count | Number of `ROLLBACK TO SAVEPOINT kwbase_restart` statements successfully executed | SQL Statements | COUNT |
| sql.ddl.count | Number of SQL DDL statements successfully executed | SQL Statements | COUNT |
| sql.misc.count | Number of other SQL statements successfully executed | SQL Statements | COUNT |
| sql.distsql.select.count | Number of DistSQL SELECT statements | SQL Statements | COUNT |
| sql.optimizer.fallback.count | Number of statements which the cost-based optimizer was unable to plan | SQL Statements | COUNT |
| sql.optimizer.plan_cache.hits | Number of non-prepared statements for which a cached plan was used | SQL Statements | COUNT |
| sql.optimizer.plan_cache.misses | Number of non-prepared statements for which a cached plan was not used | SQL Statements | COUNT |
| sql.distsql.exec.latency | Latency of DistSQL statement execution | Latency | NANOSECONDS |
| sql.exec.latency | Latency of SQL statement execution | Latency | NANOSECONDS |
| sql.distsql.service.latency | Latency of DistSQL request execution | Latency | NANOSECONDS |
| sql.service.latency | Latency of SQL request execution | Latency | NANOSECONDS |
| sql.txn.latency | Latency of SQL transactions | Latency | NANOSECONDS |
| sql.txn.abort.count | Number of SQL transaction abort errors | SQL Statements | COUNT |
| sql.failure.count | Number of statements resulting in a planning or runtime error | SQL Statements | COUNT |
| sql.timeout.count | The summary number of sql running timeouts. | SQL Statements | COUNT |
| sql.timeout.duration | The summary duration of sql running timeout (nanoseconds). | SQL Statements | NANOSECONDS |
| sql.service.latency.avg | Average service Time of sql | Latency | NANOSECONDS |
| sql.query.started.count.internal | Number of SQL queries started (internal queries) | SQL Internal Statements | COUNT |
| sql.select.started.count.internal | Number of SQL SELECT statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.update.started.count.internal | Number of SQL UPDATE statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.insert.started.count.internal | Number of SQL INSERT statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.delete.started.count.internal | Number of SQL DELETE statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.txn.begin.started.count.internal | Number of SQL transaction BEGIN statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.txn.commit.started.count.internal | Number of SQL transaction COMMIT statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.txn.rollback.started.count.internal | Number of SQL transaction ROLLBACK statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.savepoint.started.count.internal | Number of SQL SAVEPOINT statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.savepoint.release.started.count.internal | Number of `RELEASE SAVEPOINT` statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.savepoint.rollback.started.count.internal | Number of `ROLLBACK TO SAVEPOINT` statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.restart_savepoint.started.count.internal | Number of `SAVEPOINT kwbase_restart` statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.restart_savepoint.release.started.count.internal | Number of `RELEASE SAVEPOINT kwbase_restart` statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.restart_savepoint.rollback.started.count.internal | Number of `ROLLBACK TO SAVEPOINT kwbase_restart` statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.ddl.started.count.internal | Number of SQL DDL statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.misc.started.count.internal | Number of other SQL statements started (internal queries) | SQL Internal Statements | COUNT |
| sql.query.count.internal | Number of SQL queries executed (internal queries) | SQL Internal Statements | COUNT |
| sql.select.count.internal | Number of SQL SELECT statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.update.count.internal | Number of SQL UPDATE statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.insert.count.internal | Number of SQL INSERT statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.delete.count.internal | Number of SQL DELETE statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.txn.begin.count.internal | Number of SQL transaction BEGIN statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.txn.commit.count.internal | Number of SQL transaction COMMIT statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.txn.rollback.count.internal | Number of SQL transaction ROLLBACK statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.savepoint.count.internal | Number of SQL SAVEPOINT statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.savepoint.release.count.internal | Number of `RELEASE SAVEPOINT` statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.savepoint.rollback.count.internal | Number of `ROLLBACK TO SAVEPOINT` statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.restart_savepoint.count.internal | Number of `SAVEPOINT kwbase_restart` statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.restart_savepoint.release.count.internal | Number of `RELEASE SAVEPOINT kwbase_restart` statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.restart_savepoint.rollback.count.internal | Number of `ROLLBACK TO SAVEPOINT kwbase_restart` statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.ddl.count.internal | Number of SQL DDL statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.misc.count.internal | Number of other SQL statements successfully executed (internal queries) | SQL Internal Statements | COUNT |
| sql.distsql.select.count.internal | Number of DistSQL SELECT statements (internal queries) | SQL Internal Statements | COUNT |
| sql.optimizer.fallback.count.internal | Number of statements which the cost-based optimizer was unable to plan (internal queries) | SQL Internal Statements | COUNT |
| sql.optimizer.plan_cache.hits.internal | Number of non-prepared statements for which a cached plan was used (internal queries) | SQL Internal Statements | COUNT |
| sql.optimizer.plan_cache.misses.internal | Number of non-prepared statements for which a cached plan was not used (internal queries) | SQL Internal Statements | COUNT |
| sql.distsql.exec.latency.internal | Latency of DistSQL statement execution (internal queries) | SQL Internal Statements | NANOSECONDS |
| sql.exec.latency.internal | Latency of SQL statement execution (internal queries) | SQL Internal Statements | NANOSECONDS |
| sql.distsql.service.latency.internal | Latency of DistSQL request execution (internal queries) | SQL Internal Statements | NANOSECONDS |
| sql.service.latency.internal | Latency of SQL request execution (internal queries) | SQL Internal Statements | NANOSECONDS |
| sql.txn.latency.internal | Latency of SQL transactions (internal queries) | SQL Internal Statements | NANOSECONDS |
| sql.txn.abort.count.internal | Number of SQL transaction abort errors (internal queries) | SQL Internal Statements | COUNT |
| sql.failure.count.internal | Number of statements resulting in a planning or runtime error (internal queries) | SQL Internal Statements | COUNT |
| sql.timeout.count.internal | The summary number of sql running timeouts. (internal queries) | SQL Internal Statements | COUNT |
| sql.timeout.duration.internal | The summary duration of sql running timeout (nanoseconds). (internal queries) | SQL Internal Statements | NANOSECONDS |
| ml.predict.total.count | Number of predictions | Predictions | COUNT |
| ml.predict.success.count | Number of success predictions | Predictions | COUNT |
| ml.predict.response.latency | Number of avg response latency | Time | NANOSECONDS |
| sql.temp_object_cleaner.active_cleaners | number of cleaner tasks currently running on this node | Count | COUNT |
| sql.temp_object_cleaner.schemas_to_delete | number of schemas to be deleted by the temp object cleaner on this node | Count | COUNT |
| sql.temp_object_cleaner.schemas_deletion_error | number of errored schema deletions by the temp object cleaner on this node | Count | COUNT |
| sql.temp_object_cleaner.schemas_deletion_success | number of successful schema deletions by the temp object cleaner on this node | Count | COUNT |
| audit.PRIVILEGE.GRANT | GRANTaPRIVILEGE | audit | COUNT |
| audit.PRIVILEGE.REVOKE | REVOKEaPRIVILEGE | audit | COUNT |
| audit.USER.CREATE | CREATEaUSER | audit | COUNT |
| audit.USER.ALTER | ALTERaUSER | audit | COUNT |
| audit.USER.DROP | DROPaUSER | audit | COUNT |
| audit.ROLE.REVOKE | REVOKEaROLE | audit | COUNT |
| audit.ROLE.ALTER | ALTERaROLE | audit | COUNT |
| audit.ROLE.CREATE | CREATEaROLE | audit | COUNT |
| audit.ROLE.DROP | DROPaROLE | audit | COUNT |
| audit.ROLE.GRANT | GRANTaROLE | audit | COUNT |
| audit.SCHEMA.CREATE | CREATEaSCHEMA | audit | COUNT |
| audit.SCHEMA.DROP | DROPaSCHEMA | audit | COUNT |
| audit.SCHEMA.ALTER | ALTERaSCHEMA | audit | COUNT |
| audit.SCHEMA.CHANGE | CHANGEaSCHEMA | audit | COUNT |
| audit.SCHEMA.ROLLBACK | ROLLBACKaSCHEMA | audit | COUNT |
| audit.TABLE.SELECT | SELECTaTABLE | audit | COUNT |
| audit.TABLE.UPDATE | UPDATEaTABLE | audit | COUNT |
| audit.TABLE.RESTORE | RESTOREaTABLE | audit | COUNT |
| audit.TABLE.DROP | DROPaTABLE | audit | COUNT |
| audit.TABLE.ALTER | ALTERaTABLE | audit | COUNT |
| audit.TABLE.IMPORT | IMPORTaTABLE | audit | COUNT |
| audit.TABLE.EXPORT | EXPORTaTABLE | audit | COUNT |
| audit.TABLE.TRUNCATE | TRUNCATEaTABLE | audit | COUNT |
| audit.TABLE.INSERT | INSERTaTABLE | audit | COUNT |
| audit.TABLE.DELETE | DELETEaTABLE | audit | COUNT |
| audit.TABLE.CREATE | CREATEaTABLE | audit | COUNT |
| audit.TABLE.FLASHBACK | FLASHBACKaTABLE | audit | COUNT |
| audit.TABLE.BACKUP | BACKUPaTABLE | audit | COUNT |
| audit.CHANGEFEED.CREATE | CREATEaCHANGEFEED | audit | COUNT |
| audit.SCHEDULE.CREATE | CREATEaSCHEDULE | audit | COUNT |
| audit.SCHEDULE.DROP | DROPaSCHEDULE | audit | COUNT |
| audit.SCHEDULE.ALTER | ALTERaSCHEDULE | audit | COUNT |
| audit.SCHEDULE.PAUSE | PAUSEaSCHEDULE | audit | COUNT |
| audit.SCHEDULE.RESUME | RESUMEaSCHEDULE | audit | COUNT |
| audit.NODE.JOIN | JOINaNODE | audit | COUNT |
| audit.NODE.QUIT | QUITaNODE | audit | COUNT |
| audit.NODE.RESTART | RESTARTaNODE | audit | COUNT |
| audit.NODE.DECOMMISSION | DECOMMISSIONaNODE | audit | COUNT |
| audit.NODE.RECOMMISSION | RECOMMISSIONaNODE | audit | COUNT |
| audit.CONN.LOGIN | LOGINaCONN | audit | COUNT |
| audit.CONN.LOGOUT | LOGOUTaCONN | audit | COUNT |
| audit.TSENGINE.BACKUP | BACKUPaTSENGINE | audit | COUNT |
| audit.TSENGINE.RESTORE | RESTOREaTSENGINE | audit | COUNT |
| audit.STORE.DISABLE | DISABLEaSTORE | audit | COUNT |
| audit.STORE.ENABLE | ENABLEaSTORE | audit | COUNT |
| audit.VIEW.UPDATE | UPDATEaVIEW | audit | COUNT |
| audit.VIEW.REFRESH | REFRESHaVIEW | audit | COUNT |
| audit.VIEW.CREATE | CREATEaVIEW | audit | COUNT |
| audit.VIEW.DROP | DROPaVIEW | audit | COUNT |
| audit.VIEW.ALTER | ALTERaVIEW | audit | COUNT |
| audit.VIEW.SELECT | SELECTaVIEW | audit | COUNT |
| audit.VIEW.INSERT | INSERTaVIEW | audit | COUNT |
| audit.VIEW.DELETE | DELETEaVIEW | audit | COUNT |
| audit.INDEX.CREATE | CREATEaINDEX | audit | COUNT |
| audit.INDEX.DROP | DROPaINDEX | audit | COUNT |
| audit.INDEX.ALTER | ALTERaINDEX | audit | COUNT |
| audit.JOB.RESUME | RESUMEaJOB | audit | COUNT |
| audit.JOB.CANCEL | CANCELaJOB | audit | COUNT |
| audit.JOB.PAUSE | PAUSEaJOB | audit | COUNT |
| audit.LEVEL.CREATE | CREATEaLEVEL | audit | COUNT |
| audit.LEVEL.DROP | DROPaLEVEL | audit | COUNT |
| audit.COMPARTMENT.CREATE | CREATEaCOMPARTMENT | audit | COUNT |
| audit.COMPARTMENT.DROP | DROPaCOMPARTMENT | audit | COUNT |
| audit.PIPE.DROP | DROPaPIPE | audit | COUNT |
| audit.PIPE.CREATE | CREATEaPIPE | audit | COUNT |
| audit.PIPE.ALTER | ALTERaPIPE | audit | COUNT |
| audit.CLUSTER.INIT | INITaCLUSTER | audit | COUNT |
| audit.SESSION.CANCEL | CANCELaSESSION | audit | COUNT |
| audit.SESSION.SET | SETaSESSION | audit | COUNT |
| audit.SESSION.RESET | RESETaSESSION | audit | COUNT |
| audit.QUERY.CANCEL | CANCELaQUERY | audit | COUNT |
| audit.QUERY.EXPLAIN | EXPLAINaQUERY | audit | COUNT |
| audit.SUBSCRIPTION.ALTER | ALTERaSUBSCRIPTION | audit | COUNT |
| audit.SUBSCRIPTION.DROP | DROPaSUBSCRIPTION | audit | COUNT |
| audit.SUBSCRIPTION.CREATE | CREATEaSUBSCRIPTION | audit | COUNT |
| audit.CLUSTERSETTINGS.SET | SETaCLUSTERSETTINGS | audit | COUNT |
| audit.CLUSTERSETTINGS.RESET | RESETaCLUSTERSETTINGS | audit | COUNT |
| audit.TRIGGER.CREATE | CREATEaTRIGGER | audit | COUNT |
| audit.TRIGGER.DROP | DROPaTRIGGER | audit | COUNT |
| audit.TRIGGER.ALTER | ALTERaTRIGGER | audit | COUNT |
| audit.SEQUENCE.CREATE | CREATEaSEQUENCE | audit | COUNT |
| audit.SEQUENCE.DROP | DROPaSEQUENCE | audit | COUNT |
| audit.SEQUENCE.ALTER | ALTERaSEQUENCE | audit | COUNT |
| audit.STREAM.ALTER | ALTERaSTREAM | audit | COUNT |
| audit.STREAM.DROP | DROPaSTREAM | audit | COUNT |
| audit.STREAM.CREATE | CREATEaSTREAM | audit | COUNT |
| audit.DATABASE.RESTORE | RESTOREaDATABASE | audit | COUNT |
| audit.DATABASE.CREATE | CREATEaDATABASE | audit | COUNT |
| audit.DATABASE.DROP | DROPaDATABASE | audit | COUNT |
| audit.DATABASE.ALTER | ALTERaDATABASE | audit | COUNT |
| audit.DATABASE.FLASHBACK | FLASHBACKaDATABASE | audit | COUNT |
| audit.DATABASE.IMPORT | IMPORTaDATABASE | audit | COUNT |
| audit.DATABASE.EXPORT | EXPORTaDATABASE | audit | COUNT |
| audit.DATABASE.BACKUP | BACKUPaDATABASE | audit | COUNT |
| audit.RANGE.ALTER | ALTERaRANGE | audit | COUNT |
| audit.LABEL.CREATE | CREATEaLABEL | audit | COUNT |
| audit.LABEL.DROP | DROPaLABEL | audit | COUNT |
| audit.LABEL.GRANT | GRANTaLABEL | audit | COUNT |
| audit.LABEL.REVOKE | REVOKEaLABEL | audit | COUNT |
| audit.AUDIT.ALTER | ALTERaAUDIT | audit | COUNT |
| audit.AUDIT.CREATE | CREATEaAUDIT | audit | COUNT |
| audit.AUDIT.DROP | DROPaAUDIT | audit | COUNT |
| audit.PUBLICATION.DROP | DROPaPUBLICATION | audit | COUNT |
| audit.PUBLICATION.CREATE | CREATEaPUBLICATION | audit | COUNT |
| audit.PUBLICATION.ALTER | ALTERaPUBLICATION | audit | COUNT |
| ts.blockcache.hit.count | Counter of ts engine block cache hit count | Ts Engine | COUNT |
| ts.blockcache.miss.count | Counter of ts engine block cache miss count | Ts Engine | COUNT |
| ts.blockcache.hit.ratio | Hit ratio of ts engine block cache | Ts Engine | PERCENT |
| ts.blockcache.memory.size | Bytes of ts engine block cache memory size | Ts Engine | BYTES |
| ts.delete.expired.count | Counter of schedulers currently running to delete the expired data | Ts Engine | COUNT |
| ts.compress.count | Counter of schedulers currently running to compress the ts table | Ts Engine | COUNT |
| ts.vacuum.count | Counter of schedulers currently running to vacuum the ts table | Ts Engine | COUNT |
| ts.delete.expired.processingnanos | Nanoseconds spent deleting the expired data | Ts Engine | NANOSECONDS |
| ts.compress.processingnanos | Nanoseconds spent compressing the ts table | Ts Engine | NANOSECONDS |
| ts.vacuum.processingnanos | Nanoseconds spent vacuuming the ts table | Ts Engine | NANOSECONDS |
| node-id | node ID with labels for advertised RPC and HTTP addresses | Node ID | CONST |
| schedules.round.schedules-ready-to-run | The number of jobs ready to execute | Schedules | COUNT |
| schedules.round.jobs-started | The number of jobs started | Jobs | COUNT |
| schedules.round.num-jobs-running | The number of jobs started by schedules that are currently running | Jobs | COUNT |
| schedules.round.reschedule-skip | The number of schedules rescheduled due to SKIP policy | Schedules | COUNT |
| schedules.round.reschedule-wait | The number of schedules rescheduled due to WAIT policy | Schedules | COUNT |
| schedules.corrupt | Number of corrupt/bad schedules | Schedules | COUNT |
| replicas | Number of replicas | Replicas | COUNT |
| replicas.reserved | Number of replicas reserved for snapshots | Replicas | COUNT |
| replicas.leaders | Number of raft leaders | Raft Leaders | COUNT |
| replicas.leaders_not_leaseholders | Number of replicas that are Raft leaders whose range lease is held by another store | Replicas | COUNT |
| replicas.leaseholders | Number of lease holders | Replicas | COUNT |
| replicas.quiescent | Number of quiesced replicas | Replicas | COUNT |
| ranges | Number of ranges | Ranges | COUNT |
| ranges.unavailable | Number of ranges with fewer live replicas than needed for quorum | Ranges | COUNT |
| ranges.underreplicated | Number of ranges with fewer live replicas than the replication target | Ranges | COUNT |
| ranges.overreplicated | Number of ranges with more live replicas than the replication target | Ranges | COUNT |
| leases.success | Number of successful lease requests | Lease Requests | COUNT |
| leases.error | Number of failed lease requests | Lease Requests | COUNT |
| leases.transfers.success | Number of successful lease transfers | Lease Transfers | COUNT |
| leases.transfers.error | Number of failed lease transfers | Lease Transfers | COUNT |
| leases.expiration | Number of replica leaseholders using expiration-based leases | Replicas | COUNT |
| leases.epoch | Number of replica leaseholders using epoch-based leases | Replicas | COUNT |
| livebytes | Number of bytes of live data (keys plus values) | Storage | BYTES |
| keybytes | Number of bytes taken up by keys | Storage | BYTES |
| valbytes | Number of bytes taken up by values | Storage | BYTES |
| totalbytes | Total number of bytes taken up by keys and values including non-live data | Storage | BYTES |
| intentbytes | Number of bytes in intent KV pairs | Storage | BYTES |
| livecount | Count of live keys | Keys | COUNT |
| keycount | Count of all keys | Keys | COUNT |
| valcount | Count of all values | MVCC Values | COUNT |
| intentcount | Count of intent keys | Keys | COUNT |
| intentage | Cumulative age of intents | Age | SECONDS |
| gcbytesage | Cumulative age of non-live data | Age | SECONDS |
| lastupdatenanos | Timestamp at which bytes/keys/intents metrics were last updated | Last Update | TIMESTAMP_NS |
| intents.resolve-attempts | Count of (point or range) intent commit evaluation attempts | Operations | COUNT |
| intents.abort-attempts | Count of (point or range) non-poisoning intent abort evaluation attempts | Operations | COUNT |
| intents.poison-attempts | Count of (point or range) poisoning intent abort evaluation attempts | Operations | COUNT |
| capacity | Total storage capacity | Storage | BYTES |
| capacity.available | Available storage capacity | Storage | BYTES |
| capacity.used | Used storage capacity | Storage | BYTES |
| capacity.reserved | Capacity reserved for snapshots | Storage | BYTES |
| sysbytes | Number of bytes in system KV pairs | Storage | BYTES |
| syscount | Count of system KV pairs | Keys | COUNT |
| capacity.tsdb.used | TSDB used storage capacity | Storage | BYTES |
| capacity.relational.used | Relational used storage capacity | Storage | BYTES |
| capacity.tsdb.hot.used | Total storage capacity (in bytes) currently occupied by hot-tier TSDB data | Storage | BYTES |
| capacity.tsdb.hot.available | Remaining allocatable storage capacity (in bytes) in hot-tier TSDB | Storage | BYTES |
| capacity.tsdb.warm.used | Total storage capacity (in bytes) currently occupied by warm-tier TSDB data | Storage | BYTES |
| capacity.tsdb.warm.available | Remaining allocatable storage capacity (in bytes) in warm-tier TSDB | Storage | BYTES |
| capacity.tsdb.cold.used | Total storage capacity (in bytes) currently occupied by cold-tier TSDB data | Storage | BYTES |
| capacity.tsdb.cold.available | Remaining allocatable storage capacity (in bytes) in cold-tier TSDB | Storage | BYTES |
| rebalancing.queriespersecond | Number of kv-level requests received per second by the store | Keys/Sec | COUNT |
| rebalancing.writespersecond | Number of keys written per second to the store | Keys/Sec | COUNT |
| follower_reads.success_count | Number of reads successfully processed by any replica | Read Ops | COUNT |
| rocksdb.block.cache.hits | Count of block cache hits | Cache Ops | COUNT |
| rocksdb.block.cache.misses | Count of block cache misses | Cache Ops | COUNT |
| rocksdb.block.cache.usage | Bytes used by the block cache | Memory | BYTES |
| rocksdb.block.cache.pinned-usage | Bytes pinned by the block cache | Memory | BYTES |
| rocksdb.bloom.filter.prefix.checked | Number of times the bloom filter was checked | Bloom Filter Ops | COUNT |
| rocksdb.bloom.filter.prefix.useful | Number of times the bloom filter helped avoid iterator creation | Bloom Filter Ops | COUNT |
| rocksdb.memtable.total-size | Current size of memtable in bytes | Memory | BYTES |
| rocksdb.flushes | Number of table flushes | Flushes | COUNT |
| rocksdb.flushed-bytes | Bytes written during flush | Bytes Written | BYTES |
| rocksdb.compactions | Number of table compactions | Compactions | COUNT |
| rocksdb.ingested-bytes | Bytes ingested | Bytes Ingested | BYTES |
| rocksdb.compacted-bytes-read | Bytes read during compaction | Bytes Read | BYTES |
| rocksdb.compacted-bytes-written | Bytes written during compaction | Bytes Written | BYTES |
| rocksdb.table-readers-mem-estimate | Memory used by index and filter blocks | Memory | BYTES |
| rocksdb.read-amplification | Number of disk reads per query | Disk Reads per Query | COUNT |
| rocksdb.num-sstables | Number of rocksdb SSTables | SSTables | COUNT |
| rocksdb.estimated-pending-compaction | Estimated pending compaction bytes | Storage | BYTES |
| range.splits | Number of range splits | Range Ops | COUNT |
| range.merges | Number of range merges | Range Ops | COUNT |
| range.adds | Number of range additions | Range Ops | COUNT |
| range.removes | Number of range removals | Range Ops | COUNT |
| range.snapshots.generated | Number of generated snapshots | Snapshots | COUNT |
| range.snapshots.normal-applied | Number of applied snapshots | Snapshots | COUNT |
| range.snapshots.learner-applied | Number of applied learner snapshots | Snapshots | COUNT |
| range.snapshots.durations | Range snapshot durations | Snapshots | NANOSECONDS |
| range.raftleadertransfers | Number of raft leader transfers | Leader Transfers | COUNT |
| raft.ticks | Number of Raft ticks queued | Ticks | COUNT |
| raft.process.workingnanos | Nanoseconds spent in store.processRaft() working | Processing Time | NANOSECONDS |
| raft.process.tickingnanos | Nanoseconds spent in store.processRaft() processing replica.Tick() | Processing Time | NANOSECONDS |
| raft.commandsapplied | Count of Raft commands applied | Commands | COUNT |
| raft.process.logcommit.latency | Latency histogram for committing Raft log entries | Latency | NANOSECONDS |
| raft.process.commandcommit.latency | Latency histogram for committing Raft commands | Latency | NANOSECONDS |
| raft.process.handleready.latency | Latency histogram for handling a Raft ready | Latency | NANOSECONDS |
| raft.process.applycommitted.latency | Latency histogram for applying all committed Raft commands in a Raft ready | Latency | NANOSECONDS |
| raft.replica.consistent.latency | Latency histogram for the Raft replicate consistent time | Latency | NANOSECONDS |
| ae.process.put.latency | AE put latency | Latency | NANOSECONDS |
| raft.rcvd.prop | Number of MsgProp messages received by this store | Messages | COUNT |
| raft.rcvd.app | Number of MsgApp messages received by this store | Messages | COUNT |
| raft.rcvd.appresp | Number of MsgAppResp messages received by this store | Messages | COUNT |
| raft.rcvd.vote | Number of MsgVote messages received by this store | Messages | COUNT |
| raft.rcvd.voteresp | Number of MsgVoteResp messages received by this store | Messages | COUNT |
| raft.rcvd.prevote | Number of MsgPreVote messages received by this store | Messages | COUNT |
| raft.rcvd.prevoteresp | Number of MsgPreVoteResp messages received by this store | Messages | COUNT |
| raft.rcvd.snap | Number of MsgSnap messages received by this store | Messages | COUNT |
| raft.rcvd.heartbeat | Number of MsgHeartbeat messages received by this store | Messages | COUNT |
| raft.rcvd.heartbeatresp | Number of MsgHeartbeatResp messages received by this store | Messages | COUNT |
| raft.rcvd.transferleader | Number of MsgTransferLeader messages received by this store | Messages | COUNT |
| raft.rcvd.timeoutnow | Number of MsgTimeoutNow messages received by this store | Messages | COUNT |
| raft.rcvd.dropped | Number of dropped incoming Raft messages | Messages | COUNT |
| raftlog.behind | Number of Raft log entries followers on other stores are behind | Log Entries | COUNT |
| raftlog.truncated | Number of Raft log entries truncated | Log Entries | COUNT |
| raft.enqueued.pending | Number of pending outgoing messages in the Raft Transport queue | Messages | COUNT |
| raft.heartbeats.pending | Number of pending heartbeats and responses waiting to be coalesced | Messages | COUNT |
| queue.gc.process.success | Number of replicas successfully processed by the GC queue | Replicas | COUNT |
| queue.gc.process.failure | Number of replicas which failed processing in the GC queue | Replicas | COUNT |
| queue.gc.pending | Number of pending replicas in the GC queue | Replicas | COUNT |
| queue.gc.processingnanos | Nanoseconds spent processing replicas in the GC queue | Processing Time | NANOSECONDS |
| queue.merge.process.success | Number of replicas successfully processed by the merge queue | Replicas | COUNT |
| queue.merge.process.failure | Number of replicas which failed processing in the merge queue | Replicas | COUNT |
| queue.merge.pending | Number of pending replicas in the merge queue | Replicas | COUNT |
| queue.merge.processingnanos | Nanoseconds spent processing replicas in the merge queue | Processing Time | NANOSECONDS |
| queue.merge.purgatory | Number of replicas in the merge queue's purgatory | Replicas | COUNT |
| queue.raftlog.process.success | Number of replicas successfully processed by the Raft log queue | Replicas | COUNT |
| queue.raftlog.process.failure | Number of replicas which failed processing in the Raft log queue | Replicas | COUNT |
| queue.raftlog.pending | Number of pending replicas in the Raft log queue | Replicas | COUNT |
| queue.raftlog.processingnanos | Nanoseconds spent processing replicas in the Raft log queue | Processing Time | NANOSECONDS |
| queue.raftsnapshot.process.success | Number of replicas successfully processed by the Raft repair queue | Replicas | COUNT |
| queue.raftsnapshot.process.failure | Number of replicas which failed processing in the Raft repair queue | Replicas | COUNT |
| queue.raftsnapshot.pending | Number of pending replicas in the Raft repair queue | Replicas | COUNT |
| queue.raftsnapshot.processingnanos | Nanoseconds spent processing replicas in the Raft repair queue | Processing Time | NANOSECONDS |
| queue.consistency.process.success | Number of replicas successfully processed by the consistency checker queue | Replicas | COUNT |
| queue.consistency.process.failure | Number of replicas which failed processing in the consistency checker queue | Replicas | COUNT |
| queue.consistency.pending | Number of pending replicas in the consistency checker queue | Replicas | COUNT |
| queue.consistency.processingnanos | Nanoseconds spent processing replicas in the consistency checker queue | Processing Time | NANOSECONDS |
| queue.replicagc.process.success | Number of replicas successfully processed by the replica GC queue | Replicas | COUNT |
| queue.replicagc.process.failure | Number of replicas which failed processing in the replica GC queue | Replicas | COUNT |
| queue.replicagc.pending | Number of pending replicas in the replica GC queue | Replicas | COUNT |
| queue.replicagc.processingnanos | Nanoseconds spent processing replicas in the replica GC queue | Processing Time | NANOSECONDS |
| queue.replicate.process.success | Number of replicas successfully processed by the replicate queue | Replicas | COUNT |
| queue.replicate.process.failure | Number of replicas which failed processing in the replicate queue | Replicas | COUNT |
| queue.replicate.pending | Number of pending replicas in the replicate queue | Replicas | COUNT |
| queue.replicate.processingnanos | Nanoseconds spent processing replicas in the replicate queue | Processing Time | NANOSECONDS |
| queue.replicate.purgatory | Number of replicas in the replicate queue's purgatory | Replicas | COUNT |
| queue.split.process.success | Number of replicas successfully processed by the split queue | Replicas | COUNT |
| queue.split.process.failure | Number of replicas which failed processing in the split queue | Replicas | COUNT |
| queue.split.pending | Number of pending replicas in the split queue | Replicas | COUNT |
| queue.split.processingnanos | Nanoseconds spent processing replicas in the split queue | Processing Time | NANOSECONDS |
| queue.split.purgatory | Number of replicas in the split queue's purgatory | Replicas | COUNT |
| queue.tsmaintenance.process.success | Number of replicas successfully processed by the time series maintenance queue | Replicas | COUNT |
| queue.tsmaintenance.process.failure | Number of replicas which failed processing in the time series maintenance queue | Replicas | COUNT |
| queue.tsmaintenance.pending | Number of pending replicas in the time series maintenance queue | Replicas | COUNT |
| queue.tsmaintenance.processingnanos | Nanoseconds spent processing replicas in the time series maintenance queue | Processing Time | NANOSECONDS |
| queue.gc.info.numkeysaffected | Number of keys with GC'able data | Keys | COUNT |
| queue.gc.info.intentsconsidered | Number of 'old' intents | Intents | COUNT |
| queue.gc.info.intenttxns | Number of associated distinct transactions | Txns | COUNT |
| queue.gc.info.transactionspanscanned | Number of entries in transaction spans scanned from the engine | Txn Entries | COUNT |
| queue.gc.info.transactionspangcaborted | Number of GC'able entries corresponding to aborted txns | Txn Entries | COUNT |
| queue.gc.info.transactionspangccommitted | Number of GC'able entries corresponding to committed txns | Txn Entries | COUNT |
| queue.gc.info.transactionspangcstaging | Number of GC'able entries corresponding to staging txns | Txn Entries | COUNT |
| queue.gc.info.transactionspangcpending | Number of GC'able entries corresponding to pending txns | Txn Entries | COUNT |
| queue.gc.info.abortspanscanned | Number of transactions present in the AbortSpan scanned from the engine | Txn Entries | COUNT |
| queue.gc.info.abortspanconsidered | Number of AbortSpan entries old enough to be considered for removal | Txn Entries | COUNT |
| queue.gc.info.abortspangcnum | Number of AbortSpan entries fit for removal | Txn Entries | COUNT |
| queue.gc.info.pushtxn | Number of attempted pushes | Pushes | COUNT |
| queue.gc.info.resolvetotal | Number of attempted intent resolutions | Intent Resolutions | COUNT |
| queue.gc.info.resolvesuccess | Number of successful intent resolutions | Intent Resolutions | COUNT |
| requests.slow.latch | Number of requests that have been stuck for a long time acquiring latches | Requests | COUNT |
| requests.slow.lease | Number of requests that have been stuck for a long time acquiring a lease | Requests | COUNT |
| requests.slow.raft | Number of requests that have been stuck for a long time in raft | Requests | COUNT |
| requests.backpressure.split | Number of backpressured writes waiting on a Range split | Writes | COUNT |
| addsstable.proposals | Number of SSTable ingestions proposed | Ingestions | COUNT |
| addsstable.applications | Number of SSTable ingestions applied | Ingestions | COUNT |
| addsstable.copies | number of SSTable ingestions that required copying files during application | Ingestions | COUNT |
| addsstable.delay.total | Amount by which evaluation of AddSSTable requests was delayed | Nanoseconds | NANOSECONDS |
| addsstable.delay.enginebackpressure | Amount by which evaluation of AddSSTable requests was delayed by storage-engine backpressure | Nanoseconds | NANOSECONDS |
| rocksdb.encryption.algorithm | algorithm in use for encryption-at-rest | Encryption At Rest | CONST |
| kv.rangefeed.catchup_scan_nanos | Time spent in RangeFeed catchup scan | Nanoseconds | NANOSECONDS |
| kv.closed_timestamp.max_behind_nanos | Largest latency between realtime and replica max closed timestamp | Nanoseconds | NANOSECONDS |
| raft.entrycache.size | Number of Raft entries in the Raft entry cache | Entry Count | COUNT |
| raft.entrycache.bytes | Aggregate size of all Raft entries in the Raft entry cache | Entry Bytes | BYTES |
| raft.entrycache.accesses | Number of cache lookups in the Raft entry cache | Accesses | COUNT |
| raft.entrycache.hits | Number of successful cache lookups in the Raft entry cache | Hits | COUNT |
| tscache.skl.pages | Number of pages in the timestamp cache | Pages | COUNT |
| tscache.skl.rotations | Number of page rotations in the timestamp cache | Page Rotations | COUNT |
| txnwaitqueue.pushee.waiting | Number of pushees on the txn wait queue | Waiting Pushees | COUNT |
| txnwaitqueue.pusher.waiting | Number of pushers on the txn wait queue | Waiting Pushers | COUNT |
| txnwaitqueue.query.waiting | Number of transaction status queries waiting for an updated transaction record | Waiting Queries | COUNT |
| txnwaitqueue.pusher.slow | The total number of cases where a pusher waited more than the excessive wait threshold | Slow Pushers | COUNT |
| txnwaitqueue.pusher.wait_time | Histogram of durations spent in queue by pushers | Pusher wait time | NANOSECONDS |
| txnwaitqueue.query.wait_time | Histogram of durations spent in queue by queries | Query wait time | NANOSECONDS |
| txnwaitqueue.deadlocks_total | Number of deadlocks detected by the txn wait queue | Deadlocks | COUNT |
| compactor.suggestionbytes.queued | Number of logical bytes in suggested compactions in the queue | Logical Bytes | BYTES |
| compactor.suggestionbytes.skipped | Number of logical bytes in suggested compactions which were not compacted | Logical Bytes | BYTES |
| compactor.suggestionbytes.compacted | Number of logical bytes compacted from suggested compactions | Logical Bytes | BYTES |
| compactor.compactions.success | Number of successful compaction requests sent to the storage engine | Compaction Requests | COUNT |
| compactor.compactions.failure | Number of failed compaction requests sent to the storage engine | Compaction Requests | COUNT |
| compactor.compactingnanos | Number of nanoseconds spent compacting ranges | Processing Time | NANOSECONDS |
| queue.replicate.addreplica | Number of replica additions attempted by the replicate queue | Replica Additions | COUNT |
| queue.replicate.removereplica | Number of replica removals attempted by the replicate queue | Replica Removals | COUNT |
| queue.replicate.removedeadreplica | Number of dead replica removals attempted by the replicate queue | Replica Removals | COUNT |
| queue.replicate.removelearnerreplica | Number of learner replica removals attempted by the replicate queue | Replica Removals | COUNT |
| queue.replicate.rebalancereplica | Number of replica rebalancer-initiated additions attempted by the replicate queue | Replica Additions | COUNT |
| queue.replicate.transferlease | Number of range lease transfers attempted by the replicate queue | Lease Transfers | COUNT |
| queue.replicagc.removereplica | Number of replica removals attempted by the replica gc queue | Replica Removals | COUNT |
| intentresolver.async.throttled | Number of intent resolution attempts not run asynchronously due to throttling | Intent Resolutions | COUNT |
| txnrecovery.attempts.pending | Number of transaction recovery attempts currently in-flight | Recovery Attempts | COUNT |
| txnrecovery.attempts.total | Number of transaction recovery attempts executed | Recovery Attempts | COUNT |
| txnrecovery.successes.committed | Number of transaction recovery attempts that committed a transaction | Recovery Attempts | COUNT |
| txnrecovery.successes.aborted | Number of transaction recovery attempts that aborted a transaction | Recovery Attempts | COUNT |
| txnrecovery.successes.pending | Number of transaction recovery attempts that left a transaction pending | Recovery Attempts | COUNT |
| txnrecovery.failures | Number of transaction recovery attempts that failed | Recovery Attempts | COUNT |
| rebalancing.lease.transfers | Number of lease transfers motivated by store-level load imbalances | Lease Transfers | COUNT |
| rebalancing.range.rebalances | Number of range rebalance operations motivated by store-level load imbalances | Range Rebalances | COUNT |
