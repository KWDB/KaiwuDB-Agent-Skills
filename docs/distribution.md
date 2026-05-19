# Distribution

This repository only publishes Ready Skills. Planned skills may become publishable later, so public documentation should describe installation generically and let discovery or manifests identify the currently available skills.

## Ready Skills

- `kwdb-install-deploy`
- `kwdb-text2sql-aiot`
- `kwdb-intelligent-inspection`

Planned skills may exist in `skills/`, but they are not part of the release boundary.

## skills.sh

List public skills:

```bash
npx skills add https://github.com/KWDB/KaiwuDB-Agent-Skills --list
```

Install a listed Ready Skill:

```bash
npx skills add https://github.com/KWDB/KaiwuDB-Agent-Skills \
  --skill <skill-name> \
  -g -y
```

`metadata.internal: true` is used for non-ready `SKILL.md` files so they do not appear in normal skills.sh discovery.

## Claude Code Plugin

The Claude Code marketplace manifest is:

```text
.claude-plugin/marketplace.json
```

It exposes the current Ready Skills. Add a plugin entry when a planned skill becomes ready for plugin distribution.

Install from the marketplace:

```bash
claude plugin marketplace add https://github.com/KWDB/KaiwuDB-Agent-Skills
claude plugin install <skill-name>@kaiwudb-agent-skills
```

Validate before release:

```bash
claude plugin validate .claude-plugin/marketplace.json
```

## ClawHub

Publish Ready Skills as individual skill packages.

```bash
scripts/publish-ready-clawhub.sh 1.0.0
```

Set `CLAWHUB_OWNER` when publishing under an organization or publisher handle:

```bash
CLAWHUB_OWNER=kwdb scripts/publish-ready-clawhub.sh 1.0.0
```

Do not publish the repository root as a ClawHub skill.
Do not use repository-wide `clawhub sync` for release publishing while non-ready skill directories remain under root `skills/`.

The root `.clawhubignore` reduces accidental root-level package content, but it is not a substitute for explicit Ready Skill publishing.

## Release Checklist

1. Confirm `README.md` describes installation generically.
2. Run `npx skills add . --list` and confirm only Ready Skills appear.
3. Run `npx skills add . --list --full-depth` and confirm internal/planned skills are hidden.
4. Run `claude plugin validate .claude-plugin/marketplace.json`.
5. Run `bash -n scripts/publish-ready-clawhub.sh`.
6. Publish only Ready Skill directories to ClawHub.
