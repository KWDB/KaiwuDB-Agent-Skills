# Key Rules

Required inputs:

- what data is being stored
- how the data will be queried
- whether time is the primary access path
- whether retention or lifecycle control is required

Decision order:

1. identify the workload type
2. define entities or measurements
3. choose the simplest table layout that matches the query path
4. output minimal DDL
5. add a validation query or schema check
