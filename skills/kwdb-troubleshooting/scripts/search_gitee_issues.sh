#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat >&2 <<'EOF'
Usage: search_gitee_issues.sh [-p max_pages] <query>

Search the official Gitee repository issues for kwdb/kwdb by calling the
repository issues API and filtering title/body locally.

Options:
  -p max_pages   Number of API pages to scan. Default: 5

Environment:
  GITEE_OWNER    Default: kwdb
  GITEE_REPO     Default: kwdb
  STATE          Default: all
  PER_PAGE       Default: 100
EOF
}

max_pages=5
while getopts ":p:h" opt; do
  case "$opt" in
    p) max_pages="$OPTARG" ;;
    h)
      usage
      exit 0
      ;;
    :)
      echo "missing value for -$OPTARG" >&2
      usage
      exit 2
      ;;
    \?)
      echo "unknown option: -$OPTARG" >&2
      usage
      exit 2
      ;;
  esac
done
shift $((OPTIND - 1))

if [[ $# -lt 1 ]]; then
  usage
  exit 2
fi

query="$*"
owner="${GITEE_OWNER:-kwdb}"
repo="${GITEE_REPO:-kwdb}"
state="${STATE:-all}"
per_page="${PER_PAGE:-100}"
api="https://gitee.com/api/v5/repos/${owner}/${repo}/issues"

tmp="$(mktemp)"
trap 'rm -f "$tmp"' EXIT

for ((page = 1; page <= max_pages; page++)); do
  url="${api}?state=${state}&sort=created&direction=desc&per_page=${per_page}&page=${page}"
  body="$(curl -fsSL --max-time 20 -A 'Mozilla/5.0' "$url")"
  count="$(jq 'length' <<<"$body")"

  if [[ "$count" == "0" ]]; then
    break
  fi

  jq -r --arg q "$query" '
    .[]
    | select((((.title // "") + "\n" + (.body // "")) | ascii_downcase) | contains($q | ascii_downcase))
    | [.number, .state, .updated_at, .title, .html_url] | @tsv
  ' <<<"$body" >>"$tmp"
done

if [[ ! -s "$tmp" ]]; then
  echo "no matching issue found in ${owner}/${repo} within ${max_pages} page(s): ${query}" >&2
  exit 1
fi

awk -F '\t' '!seen[$1]++' "$tmp"
