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
`scripts/probe_ports.py` directly with `python3` and one `--port` flag
per port that needs to be reachable. The script does not accept a
loopback host — give it the remote IP / DNS name. See
`probe-ports-script-usage.md` for full options.

- Pass `--port 26257` and `--port 8080` in a single call.
- A port that returns `reachable: false` is **not** an exception. Re-read
  the result, report it to the user, and ask them to verify network /
  firewall / service.
- Only proceed if all required ports are reachable.

**Do NOT proceed to Step 3 until ports are confirmed reachable.**

---

### Step 3: TLS Mode Detection

Only after connectivity is confirmed, call
`scripts/detect_tls_mode.py` directly with `python3` against the admin
port (`8080` by default). See `detect-tls-mode-script-usage.md`.

Decision rules based on the JSON result:

| `determined` | `tls_enabled` | Action |
|--------------|---------------|--------|
| `true` | `true`  | TLS is enforced. **Inspection not supported — stop here.** |
| `true` | `false` | Server returned `wrong version number` / `0A00010B`. Plaintext. Proceed. |
| `false` | (any) | Could not classify (refused, timeout, unknown SSL error). Do not assume plaintext. Stop and ask the user / re-probe. |

**Do NOT proceed to Step 4 until TLS mode is determined.**

---

### Step 4: Present Scope Menu

Read `references/report-template.md` and `references/anomaly-rules.md`,
then show the user:
- Full inspection scope (Sections 1-6)
- Default rules and configurable rules (only applied if user requests alerting)
- Ask the user to confirm which metrics to inspect and whether to enable alerting

**Do NOT proceed to metrics collection until user confirms the scope.**
