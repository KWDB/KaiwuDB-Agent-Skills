---
audience: operators / cluster admins (NOT for LLM ingestion)
purpose: deployment reference for `kwdb-mcp-server` — sensitive credentials required
---

# `kwdb-mcp-server` — Operator Deployment Guide

This document is for **human operators** who provision and maintain `kwdb-mcp-server` in their environment. It is intentionally **not part of the `kwdb-intelligent-inspection` skill** — the LLM-driven inspection skill should never be asked to deploy the MCP server, because doing so would require exposing the database DSN (including credentials) to the LLM, defeating the security boundary the MCP server exists to provide.

If the inspection skill reports a deployment problem, point the operator at this document.

---

## What `kwdb-mcp-server` is

`kwdb-mcp-server` is a separate Go binary (≈ 10.7 MB ELF) at `/usr/local/bin/kwdb-mcp-server` that:

- Hosts the `query-metrics` and `query-slow-sql` MCP tools consumed by the inspection skill.
- Holds the KaiwuDB connection string (DSN) — including the database username and password — so the LLM calling the tools never sees raw credentials.
- Signs HTTP Basic Auth against the KWDB admin endpoint on the LLM's behalf (admin endpoints require credentials; the inspection skill cannot supply them through Claude Code's MCP HTTP transport).
- Acts as the single trust boundary between the LLM and the cluster's admin API.

---

## Why the LLM does not deploy

The skill's flow is:

```
LLM (Claude Code)
    ↓  MCP tool call (no headers visible to LLM)
kwdb-mcp-server
    ↓  HTTP + Basic Auth
KWDB cluster admin API
```

The credentials that authorize the admin call live **inside** `kwdb-mcp-server`. If the LLM were allowed to launch the server, it would need to either:

1. Read the DSN from the filesystem / vault / env vars and pass it on the command line — exposing it to its own context.
2. Receive the DSN from the user mid-session — putting credentials into the conversation history.

Both defeat the purpose. Operators deploy the MCP server out-of-band (shell, systemd, k8s manifest, etc.); the LLM only consumes the tools.

---

## Deployment

### Binary location

- Default install path: `/usr/local/bin/kwdb-mcp-server`
- Version requirement: `≥ 3.2.0` (this is the version the `kwdb-intelligent-inspection` skill expects; older versions are missing tools or credential-fallback behavior)

### Required flags

| Flag | Required | Default | Purpose |
|---|---|---|---|
| `-port` / `-p` | yes for HTTP/SSE | `8080` | Local listen port the inspection skill (Claude Code MCP config) points to. Pick a non-privileged port — `8003`, `8004`, etc. |
| `-transport` / `-t` | yes | `stdio` | Use `http` for the Claude Code MCP HTTP transport config. |
| `--admin-base-url` | **strongly recommended** | derived (`http://{DB-host}:8080`) | The KWDB admin endpoint the MCP server will call. Override whenever the default derivation is wrong. |
| Positional `<conn-string>` | yes | — | Full PostgreSQL DSN. Drives the SQL connection used by `query-slow-sql` and is the credential source for admin Basic Auth. |

### Start command template

```bash
/usr/local/bin/kwdb-mcp-server \
  -port <mcp_listen_port> \
  -transport http \
  --admin-base-url=<scheme>://<admin_host>:<admin_port> \
  "postgresql://<user>:<url_encoded_password>@<db_host>:26257/<database>?sslmode=disable"
```

Worked example:

```bash
/usr/local/bin/kwdb-mcp-server \
  -port 8003 -transport http \
  --admin-base-url=https://192.168.124.51:8081 \
  "postgresql://test:Znbase%231234@192.168.124.51:26257/defaultdb?sslmode=disable"
```

- `26257` is the KaiwuDB SQL port (DB-side).
- `8081` here is the **host-side** admin port. The kwbase container inside Docker maps `host:8081 → container:8080`; the MCP server needs the host mapping.
- The admin endpoint redirects HTTP → HTTPS, so `--admin-base-url` must use `https://` or the MCP server will fail with `auth failed` after the redirect.
- The positional DSN is also used by `query-slow-sql` for SQL access — without it, slow SQL queries will fail with `password authentication failed for user root`.

### Restart procedure

```bash
# 1. Stop the existing instance
ps -ef | grep -F kwdb-mcp-server | grep -v grep | awk '{print $2}' | xargs -r kill

# 2. Wait for the listen socket to free
ss -tlnp 2>/dev/null | grep -F 'kwdb-mcp-server' || echo "port-free"

# 3. Start the new instance in the background (see template above)
nohup /usr/local/bin/kwdb-mcp-server -port 8003 -transport http \
  --admin-base-url=https://192.168.124.51:8081 \
  "postgresql://test:Znbase%231234@192.168.124.51:26257/defaultdb?sslmode=disable" \
  > /tmp/kwdb-mcp-server.log 2>&1 & disown

# 4. Verify (see "Verifying the deployment" below)
```

Verifying the deployment:

```bash
# (a) Process and port
ps -ef | grep kwdb-mcp-server | grep -v grep
ss -tlnp 2>/dev/null | grep -F kwdb-mcp-server

# (b) MCP handshake
curl -sS -X POST http://localhost:<port>/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"verify","version":"1.0"}}}' \
  | grep -E '"serverInfo"|"protocolVersion"'
# Expect: serverInfo.version ≥ 3.2.0; protocolVersion 2025-03-26 or compatible.

# (c) End-to-end tool smoke test (see `references/kwdb-mcp-server-setup.md` §3.3
#     in the inspection skill for the full session-id dance, OR use any
#     MCP client to invoke query-metrics once and confirm a successful response)
```

---

## Deployment-time pitfalls

### P1. `#` and other reserved characters in the connection-string password

The positional DSN is parsed as a URL by Go's `net/url`. The most common bug is `#`, which the parser treats as the fragment delimiter and stops reading the password at that point:

| Character | Encoded as | Notes |
|---|---|---|
| `#` | `%23` | **most common bug** |
| `@` | `%40` | otherwise splits userinfo from host |
| `/` | `%2F` | otherwise splits path |
| `:` | `%3A` | otherwise re-opens the port field |
| `?` | `%3F` | otherwise opens the query string |
| ` ` (space) | `%20` | path segment separator |
| `%` (literal) | `%25` | escape itself |

**Symptom**: log shows `parse "postgresql://<user>:<truncated>": invalid port ":..." after host` repeating on every reconnect, and every tool call fails. The MCP server will report `Database connection pool reinitialized` in a tight loop.

**Fix**: re-encode the password (e.g. `Znbase#1234` → `Znbase%231234`) and restart. Other characters (`@`, `:`, `/`, `?`, `=`) are URL syntax separators and need **no** encoding when they appear in their natural positions — only encode characters that appear *inside* the password / user / path.

### P2. Admin port ≠ 8080 (container port mapping)

`--admin-base-url` defaults to `http://{DB-host}:8080`, derived from the connection string's host and the hardcoded `defaultAdminPort = 8080`. When kwbase runs inside Docker (or any container) and admin is exposed on a different host port (e.g. `docker run -p 8081:8080`), the default is wrong.

**Symptom**: `admin request failed: dial tcp <host>:8080: connect: connection refused` (TCP refused) or `admin API server error: status=502` (reverse proxy).

**Fix**: pass `--admin-base-url=http://<admin_host>:<actual_admin_host_port>` or `https://<admin_host>:<actual_admin_host_port>` per P3.

### P3. Admin endpoint forces HTTPS (HTTP→HTTPS redirect)

`kwbase` configured with `--certs-dir` redirects the admin port from HTTP → HTTPS with `307 Temporary Redirect`. The MCP server's `doAdminRequest` does not follow this redirect with Basic Auth — it sends the request to HTTP, gets 307, and a follow-up to HTTPS without credentials returns 401.

**Symptom**: `Metrics query failed: auth failed: wrong username or password, please check` even though the cluster username and password are correct.

**Fix**: pass `--admin-base-url=https://<admin_host>:<admin_port>`. The MCP server will then sign Basic Auth automatically using the credentials extracted from the connection string. The MCP server's HTTP client has `InsecureSkipVerify: true` (matches the Python tooling's `ssl._create_unverified_context()`), so self-signed cluster certificates are accepted.

### P4. Empty-credential stub header from the MCP client (server-side fix in place)

Some MCP clients auto-inject an `X-Database-URI` request header containing a stub DSN like `postgresql://root:@127.0.0.1:26257/defaultdb?sslmode=disable`. The current `kwdb-mcp-server` source tree includes a server-side credential sanity check that falls back to the registration-time default DSN when the header carries empty credentials — so this should not require operator action. If `Metrics query failed: TLS admin endpoint requires credentials, but DB URL has no password` or `query kwdb_internal.node_statement_statistics: ... pq: password authentication failed for user root` is observed, confirm the deployed binary is from a current source tree (not an older release without the fallback) and restart.

---

## What the operator hands off to the user

After deployment, the operator tells the user:

- The MCP listen port (e.g. `8003`).
- The deployment status (healthy / degraded).
- Any non-default `--admin-base-url` value the inspection skill must honor (rare; usually the default is correct).

That is enough for the user to register the MCP server in Claude Code's `~/.claude.json` and run the `kwdb-intelligent-inspection` skill. The DSN itself stays inside the MCP server.

---

## Quick-reference checklist

- [ ] Binary `/usr/local/bin/kwdb-mcp-server` exists and reports `version ≥ 3.2.0`.
- [ ] Password contains no unencoded reserved characters (`#`, `@`, `:`, `/`, `?`, space).
- [ ] `--admin-base-url` matches the **host-side** admin port; uses `https://` if the cluster forces HTTPS redirect.
- [ ] `ps -ef | grep kwdb-mcp-server` shows one process.
- [ ] `ss -tlnp | grep kwdb-mcp-server` shows the configured listen port.
- [ ] `curl` against `/mcp` returns `"serverInfo":{"name":"KWDB (KaiwuDB) MCP Server", "version":"3.2.0"}`.
- [ ] End-to-end `tools/call` on `query-metrics` returns `"status":"success"` for a single trivial metric.