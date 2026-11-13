#!/usr/bin/env bash
# Repository consistency checks for the KaiwuDB Agent Skills monorepo.
#
# Usage: bash scripts/validate-repo.sh
# Exit code 0 when every check passes, 1 otherwise.
set -uo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

failed=0

pass() { echo "PASS  $1"; }

fail() {
  echo "FAIL  $1"
  failed=1
}

# Ready skills are the directories that ship a SKILL.md.
ready_skills() {
  for dir in skills/*/; do
    [[ -f "${dir}SKILL.md" ]] && basename "${dir%/}"
  done | sort
}

readme_skills() {
  sed -n '/^## Ready Skills/,/^## /p' README.md \
    | sed -nE 's/^- `([a-z0-9-]+)`.*/\1/p' | sort
}

agents_skills() {
  sed -n '/^The repository currently maintains these Ready Skills:/,/^The following skill directories are still planned:/p' AGENTS.md \
    | sed -nE 's/^- `([a-z0-9-]+)`.*/\1/p' | sort
}

marketplace_skills() {
  sed -nE 's|.*"source": "\./skills/([a-z0-9-]+)".*|\1|p' .claude-plugin/marketplace.json | sort
}

publish_skills() {
  sed -nE 's|.*clawhub skill publish skills/([a-z0-9-]+).*|\1|p' scripts/publish-ready-clawhub.sh | sort
}

as_line() { tr '\n' ' ' | sed -e 's/ *$//'; }

echo "== Skill layout"
for dir in skills/*/; do
  name="$(basename "${dir%/}")"
  if [[ ! -f "${dir}SKILL.md" ]]; then
    echo "SKIP  $name (planned, no SKILL.md)"
    continue
  fi

  if [[ ! "$name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
    fail "$name: skill directory name is not kebab-case"
  else
    pass "$name: skill directory name"
  fi

  frontmatter="$(tr -d '\r' < "${dir}SKILL.md")"
  fm_name="$(echo "$frontmatter" | sed -nE 's/^name:[[:space:]]*//p' | head -1)"
  fm_desc="$(echo "$frontmatter" | sed -nE 's/^description:[[:space:]]*//p' | head -1)"

  if [[ -z "$fm_name" ]]; then
    fail "$name: frontmatter is missing 'name'"
  elif [[ "$fm_name" != "$name" ]]; then
    fail "$name: frontmatter name '$fm_name' does not match directory name"
  else
    pass "$name: frontmatter name"
  fi

  if [[ -z "$fm_desc" ]]; then
    fail "$name: frontmatter is missing 'description'"
  else
    pass "$name: frontmatter description"
  fi
done

echo
echo "== Python scripts"
while IFS= read -r script; do
  if python3 -m py_compile "$script" 2>/dev/null; then
    pass "$script: compiles"
  else
    fail "$script: does not compile"
  fi
done < <(find skills internal -name '*.py' -not -path '*/__pycache__/*' | sort)

echo
echo "== Skill manifests"
expected="$(ready_skills | as_line)"
check_list() {
  local desc="$1" actual="$2"
  if [[ "$actual" == "$expected" ]]; then
    pass "$desc"
  else
    fail "$desc"
    echo "      expected: $expected"
    echo "      actual:   $actual"
  fi
}

check_list "README.md Ready Skills list matches skills/" "$(readme_skills | as_line)"
check_list "AGENTS.md Ready Skills list matches skills/" "$(agents_skills | as_line)"
check_list ".claude-plugin/marketplace.json plugins match skills/" "$(marketplace_skills | as_line)"
check_list "scripts/publish-ready-clawhub.sh covers skills/" "$(publish_skills | as_line)"

echo
if [[ "$failed" -eq 0 ]]; then
  echo "All repository checks passed."
else
  echo "Repository checks failed."
fi
exit "$failed"
