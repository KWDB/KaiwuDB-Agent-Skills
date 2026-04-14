# Disambiguation

Clarify these points before final output:

- is this entity data, time-series data, or both
- are joins required
- is the timestamp the main query dimension
- does the user need retention-aware design

Useful follow-up questions:

- "Will most reads filter by time range?"
- "Do you need joins between business entities?"
- "Are updates common after insert?"
