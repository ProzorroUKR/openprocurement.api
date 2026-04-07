#!/usr/bin/env bash
set -euo pipefail

usage() {
    echo "Usage: $0 <new_version> [previous_version]"
    echo "Example: $0 2.4.1 2.4.0"
}

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    usage
    exit 1
fi

new_version=$1
prev_version=${2:-}

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Error: current directory is not a git repository."
    exit 1
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "Error: working tree is not clean. Commit or stash changes first."
    exit 1
fi

if git rev-parse -q --verify "refs/tags/${new_version}" >/dev/null; then
    echo "Error: tag ${new_version} already exists."
    exit 1
fi

if [ -z "${prev_version}" ]; then
    prev_version=$(git describe --tags --abbrev=0 2>/dev/null || true)
fi

if [ -n "${prev_version}" ] && ! git rev-parse -q --verify "refs/tags/${prev_version}" >/dev/null; then
    echo "Error: previous tag ${prev_version} does not exist."
    exit 1
fi

changelog_file=$(mktemp "/tmp/${new_version}.XXXXXX.txt")
trap 'rm -f "${changelog_file}"' EXIT

{
    echo "Tagged release ${new_version}"
    echo
    if [ -n "${prev_version}" ]; then
        echo "Changes since ${prev_version}:"
        git log --oneline --no-decorate --no-merges "${prev_version}..HEAD"
    else
        echo "Changes in repository history:"
        git log --oneline --no-decorate --no-merges
    fi
} > "${changelog_file}"

git tag -a -e -F "${changelog_file}" "${new_version}"
echo "Created tag ${new_version}"