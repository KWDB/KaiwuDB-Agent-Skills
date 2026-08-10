---
name: kwdb-mcp-server readiness check (skill-side, read-only)
description: Detect and verify kwdb-mcp-server availability, plus header semantics for query-metrics / query-slow-sql. The inspection skill should only READ this document; deployment and restart are operator-only (see docs/kwdb-mcp-server-deployment.md).
---

# `kwdb-mcp-server` — Readiness Check (skill-side)

This document is the **read-only** view of `kwdb-mcp-server` for the `kwdb-intelligent-inspection` skill. It covers what the skill is allowed to do automatically:

1. **Detect** whether `kwdb-mcp-server` is already running.
2. **Verify** that the running instance can actually serve metric queries.
3. **Header semantics** for the `query-metrics` / `query-slow-sql` tools.

It does **not** cover deployment or restart — those are operator-only. The skill must never invoke `kwdb-mcp-server` with a connection string or other credentials, because doing so would put the cluster's database credentials into the LLM context and defeat the security boundary the MCP server exists to provide.

If the readiness checks below fail, the skill should report the problem to the user (with the relevant error string) and **stop**. The user then escalates to the operator-side deployment guide (`docs/kwdb-mcp-server-deployment.md` in the project root) — the skill does not edit that document or run any deployment commands.

---

## 1. Detection

Before calling any tool, check whether `kwdb-mcp-server` is already running. Any one of the three signals below is sufficient:

```bash
# (a) Process exists
ps -ef | grep -F kwdb-mcp-server | grep -v grep

# (b) Listen socket exists on the configured -port (commonly 8003)
ss -tlnp 2>/dev/null | grep -F kwdb-mcp-server

# (c) MCP endpoint responds to `initialize`
curl -sS -X POST http://localhost:<port>/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"probe","version":"1.0"}}}' \
  | grep -o '"serverInfo":{"name":"KWDB (KaiwuDB) MCP Server"'
```

Capture from the process command line for use in §2 and §3 below:

| Field | Where to find it |
|---|---|
| `-port` (MCP listen port) | `-port 8003` (commonly 8003) |
| `-transport` | `-transport http` |
| `--admin-base-url` | `--admin-base-url=https://<host>:<port>` (the value the skill must honor) |
| Positional DSN | `postgresql://user:password@host:26257/dbname?sslmode=disable` |
| `serverInfo.version` from signal (c) | must be ≥ `3.2.0` |

If signal (c) returns a version lower than 3.2.0 or fails entirely, **stop the skill and report the error to the user** — do not attempt to upgrade, restart, or reconfigure the MCP server.

---

## 2. Verification

If detection passes, run a tool-level smoke test to confirm the MCP server can actually answer queries. The MCP Streamable HTTP transport requires `initialize` → `notifications/initialized` → `tools/call` in sequence, with `Mcp-Session-Id` carried between calls:

```bash
SESSION=$(curl -sS -i -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"verify","version":"1.0"}}}' \
  | grep -i 'mcp-session-id' | awk '{print $2}' | tr -d '\r')

curl -sS -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'

curl -sS -X POST http://localhost:8003/mcp \
  -H "Content-Type: application/json" -H "Accept: application/json, text/event-stream" \
  -H "mcp-session-id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"query-metrics","arguments":{"metric_names":["cr.node.liveness.livenodes"],"start_ms":<now-1h>,end_ms:<now>,"sample_ms":60000}}}'
```

Expect `"status":"success"` and a `data.results[]` array.

---

## 3. Reading tool-call error messages

When `query-metrics` or `query-slow-sql` returns an error, the skill must classify it as **deployment**, **connectivity**, or **data-shape** before deciding the next step:

| Error string (substring) | Class | Skill action |
|---|---|---|
| `connection refused` (in `admin request failed: ... dial tcp ...`) | Deployment — admin port unreachable | Stop, report to user, ask them to engage the operator |
| `auth failed: wrong username or password` | Deployment — admin endpoint rejected credentials | Stop, report to user, ask them to engage the operator |
| `invalid port ":..." after host` | Deployment — DSN mis-parsed (likely unencoded `#`) | Stop, report to user, ask them to engage the operator |
| `TLS admin endpoint requires credentials, but DB URL has no password` | Deployment — server fallback missed (binary too old) | Stop, report to user, ask them to engage the operator |
| `password authentication failed for user root` | Deployment — stale binary or stub-header regression | Stop, report to user, ask them to engage the operator |
| `missing X-Database-URI` | Data — multi-tenant mode expected an explicit header | Stop, do not silently fall back; the skill calls without per-request DSN by design |
| `unknown metric:` | Data — caller passed a metric name outside the closed catalog | Fix the call (the catalog is in `references/metric-types.md`); retry once |
| `unknown sort_by:` / `Invalid * arguments` | Data — caller passed an out-of-range enum | Fix the call; retry once |

The skill does **not** attempt to fix deployment-class errors. It does fix data-class errors and retry once.

---

## 4. Header semantics for `query-metrics` / `query-slow-sql`

Both tools optionally accept two request headers. The Claude Code MCP HTTP transport does **not** surface header parameters through its tool-call interface, so most callers cannot pass these explicitly; they exist for advanced / multi-tenant integrations. The skill's normal calling pattern relies on the MCP server's startup defaults.

### 4.1 `X-Database-URI` (full PostgreSQL DSN)

Per-request override of the connection string used by the MCP server. Source priority for credentials and SQL connection:

| Priority | Source | When it wins |
|---|---|---|
| 1 | `X-Database-URI` request header with non-empty user AND non-empty password | multi-tenant caller overriding per call |
| 2 | Registration-time default DSN (the positional `<conn-string>` passed to `kwdb-mcp-server`) | single-DB deployment (typical) |

The fallback in tier 1 → tier 2 only triggers when the header DSN is missing **or** carries empty credentials. This guards against MCP clients that inject an empty-credentials stub header (`postgresql://root:@127.0.0.1:26257/defaultdb?sslmode=disable`); the server detects the empty credentials and uses the operator-supplied DSN instead.

### 4.2 `X-Admin-Base-URL` (admin endpoint base URL)

Per-request override of the admin endpoint the MCP server calls for `/restapi/ts/query`. Only meaningful for `query-metrics` (`query-slow-sql` uses SQL, not the admin API). Three-tier resolution inside `resolveAdminBaseURL`:

| Priority | Source | When it wins |
|---|---|---|
| 1 | `X-Admin-Base-URL` request header | explicit per-call override |
| 2 | `--admin-base-url` startup flag | the value passed when launching `kwdb-mcp-server` (typical) |
| 3 | DB URL derivation `http://{info.Host}:8080` (port hardcoded) | when neither of the above is provided |

The header scheme also drives the `isTLS` flag for Basic Auth attachment — `https://...` always signs credentials, `http://...` never does. This is why the operator's `--admin-base-url` must be `https://...` whenever the cluster forces an HTTP→HTTPS redirect on the admin port.

### 4.3 Multi-tenant usage

For an advanced integration that points different `query-metrics` calls at different clusters, the calling code (or upstream MCP client with header-injection capability) sets both headers per request:

```
X-Database-URI: postgresql://user:password@cluster-b:26257/dbname?sslmode=disable
X-Admin-Base-URL: https://cluster-b-admin:8081
```

The MCP server honors these over the startup defaults for that single call, then reverts to startup defaults on the next call where the headers are absent.

The `kwdb-intelligent-inspection` skill does **not** need to set these headers — Claude Code's MCP HTTP transport does not expose header parameters, and the MCP server's startup DSN + `--admin-base-url` are correct for the typical single-cluster inspection.

---

## 5. Quick-reference decision tree

```
Is kwdb-mcp-server running and healthy (this doc §1 + §2)?
├── yes → continue to Step 2 of the skill (call query-metrics / query-slow-sql)
└── no  → STOP the skill. Report the failure class to the user
         (per §3). The user escalates to the operator, who consults
         docs/kwdb-mcp-server-deployment.md (project root, NOT this skill).
         The skill does NOT auto-deploy or auto-restart the MCP server.
```

Never call `query-metrics` / `query-slow-sql` until the verification in §2 passes.