# kwdb-schema-design Activation Design

## Should Trigger

- requests to design a KWDB schema
- requests to write KWDB DDL
- requests to choose relational vs time-series modeling in KWDB

## Should Not Trigger

- deployment questions
- troubleshooting questions
- migration questions
- pure performance review questions

## False Positive Risks

- generic SQL design requests with no KWDB context

## False Negative Risks

- prompts that say "how should I store this in KWDB"

## First Decision After Activation

Determine whether the request is relational, time-series, or mixed.
