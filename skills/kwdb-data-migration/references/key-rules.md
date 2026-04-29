# Core Migration Rules

1. Relational engine preserves DECIMAL precision.
   Time-series engine converts DECIMAL → FLOAT8.

2. Time-series engine unifies DATE/TIME/DATETIME → TIMESTAMP.

3. JSON/JSONB/CLOB → NVARCHAR in time-series engine.

4. UNSIGNED BIGINT:
   Relational: NUMERIC(20)
   Time-series: INT8 (risk of overflow)

5. Time-series mandatory params:
   time_column, start_time, end_time

6. Custom SQL is mutually exclusive with WHERE and time filters.

7. Write modes: INSERT (default), UPSERT.

8. Full database migration only supports relational engine.
