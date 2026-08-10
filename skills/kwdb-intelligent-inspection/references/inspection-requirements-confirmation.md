## Inspection Requirements Confirmation

⚠️ **These steps MUST be executed in the following order. Do not skip or reorder any step.**

### Step 1: Parse User Intent

When user provides a target (e.g., "inspect 10.110.10.146 26257 8080"), extract and confirm:
- Node address(es)
- Database port (default 26257)
- Admin console port (default 8080)

**Do NOT proceed to Step 2 until target info is confirmed with user.**

---

### Step 2: Probe Connectivity

After confirming target info with user, call
`scripts/probe_ports.py` via `python3 scripts/probe_ports.py` with one entry per port
that needs to be reachable. The script's argparse enforces a non-loopback
`--host` — give it the remote IP / DNS name. See
`probe-ports-script-usage.md` for full options.

- Pass `--port 26257` and `--port 8080` in a single call.
- A port that returns `reachable: false` is **not** an exception. Re-read
  the result, report it to the user, and ask them to verify network /
  firewall / service.
- Only proceed if all required ports are reachable.

**Do NOT proceed to Step 3 until ports are confirmed reachable.**

---

### Step 3: Choose Data Collection Path

This skill supports **two** data collection paths. Pick the right one before any further work:

1. **MCP tools path (preferred — works for insecure and TLS)**:
   - If `kwdb-mcp-server` v3.2.0+ is connected to this session, it will expose `query-metrics` and `query-slow-sql`. Check your current tool list.
   - If both tools are present, take this path and skip Step 4 (TLS detection). The MCP server handles TLS + Basic Auth internally — it works regardless of the cluster's deployment mode.
   - After MCP collection, the SKILL.md workflow continues at its Step 4 (anomaly rules) and Step 5 (report).

2. **Legacy script path (fallback — insecure only)**:
   - If `query-metrics` / `query-slow-sql` are **not** in the current tool list (older `kwdb-mcp-server` build, MCP server down, or tool call errored out), fall back to the legacy Python scripts.
   - **Before** calling any legacy script, you MUST proceed to Step 4 to verify the cluster is plaintext. The legacy scripts hard-code plain HTTP and lack Basic Auth; calling them against a TLS cluster will fail.

**Do NOT proceed to Step 4 or Step 5 until you have decided which path applies.**

---

### Step 4: TLS Mode Detection (legacy script path only)

Only when the legacy script path was selected in Step 3, call
`scripts/detect_tls_mode.py` via `python3 scripts/detect_tls_mode.py` against the admin
port (`8080` by default). See `detect-tls-mode-script-usage.md`.

Decision rules based on the JSON result:

| `determined` | `tls_enabled` | Action |
|--------------|---------------|--------|
| `true` | `true`  | TLS is enforced. **Stop — legacy scripts cannot work here.** Ask the user to install `kwdb-mcp-server` v3.2.0+ and configure a database URL with username + password; then re-run this skill so it can take the MCP path in Step 3. |
| `true` | `false` | Server returned `wrong version number` / `0A00010B`. Plaintext. **Proceed — use `scripts/get_kwdb_ts_metrics.py` and `scripts/get_kwdb_statements.py`** per their usage docs. |
| `false` | (any) | Could not classify (refused, timeout, unknown SSL error). Do not assume plaintext. Stop and ask the user / re-probe. |

**Do NOT call legacy collection scripts against a TLS cluster.** If `tls_enabled` is `true`, abort regardless of MCP tool availability — legacy scripts are plain HTTP with no auth.

---

### Step 5: Present Scope Menu

Read `references/report-template.md` and `references/anomaly-rules.md`,
then show the user:
- Full inspection scope (Sections 1-6)
- Default rules and configurable rules (only applied if user requests alerting)
- Ask the user to confirm which metrics to inspect and whether to enable alerting

**Do NOT proceed to metrics collection until user confirms the scope.**
