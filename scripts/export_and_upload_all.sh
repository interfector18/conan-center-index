#!/usr/bin/env bash
# Export all recipes and upload them to the Artifactory remote.
# Run this once to seed a clean remote with all recipes.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

LOGFILE="${REPO_ROOT}/scripts/export.log"
> "$LOGFILE"

log() {
  echo "$@" | tee -a "$LOGFILE"
}

# Load .env
if [[ -f "${REPO_ROOT}/.env" ]]; then
  set -a
  source "${REPO_ROOT}/.env"
  set +a
else
  echo "Error: .env file not found at ${REPO_ROOT}/.env"
  exit 1
fi

cd "${REPO_ROOT}"

# Build set of already-exported recipes for fast lookup
log "Building cache index..."
CACHED=$(conan list "*" --format=json 2>/dev/null | python3 -c "
import sys, json
data = json.load(sys.stdin)
for ref in data.get('Local Cache', {}):
    print(ref)
")
declare -A CACHE_MAP
for ref in $CACHED; do
  CACHE_MAP["$ref"]=1
done
log "Found ${#CACHE_MAP[@]} recipes already in cache"

# Parse all config.yml files in one shot
log "Collecting all recipe versions..."
ALL_ENTRIES=$(python3 -c "
import os, re, yaml
recipes_dir = 'recipes'
for name in sorted(os.listdir(recipes_dir)):
    config = os.path.join(recipes_dir, name, 'config.yml')
    if not os.path.isfile(config):
        continue
    with open(config) as f:
        cfg = yaml.safe_load(f)
    for ver, data in cfg.get('versions', {}).items():
        folder = data.get('folder', 'all')
        conanfile = os.path.join(recipes_dir, name, folder, 'conanfile.py')
        if os.path.isfile(conanfile):
            with open(conanfile) as f:
                head = f.read(2048)
            if re.search(r'from conans import', head):
                continue
        print(f'{name}:{ver}:{folder}')
")

TOTAL=0
OK=0
FAIL=0
SKIP=0
FAILED_LIST=""

for entry in $ALL_ENTRIES; do
  IFS=: read -r RECIPE_NAME VERSION FOLDER <<< "$entry"
  TOTAL=$((TOTAL + 1))
  if [[ -n "${CACHE_MAP["${RECIPE_NAME}/${VERSION}"]:-}" ]]; then
    SKIP=$((SKIP + 1))
    continue
  fi
  if OUTPUT=$(conan export "recipes/${RECIPE_NAME}/${FOLDER}" --name="${RECIPE_NAME}" --version="${VERSION}" 2>&1); then
    OK=$((OK + 1))
  else
    FAIL=$((FAIL + 1))
    FAILED_LIST="${FAILED_LIST}  ${RECIPE_NAME}/${VERSION}\n"
    log "FAIL: ${RECIPE_NAME}/${VERSION}"
    echo "$OUTPUT" >> "$LOGFILE"
    echo "---" >> "$LOGFILE"
  fi
done

log ""
log "========== Export Summary =========="
log "Total: ${TOTAL}  OK: ${OK}  Skipped: ${SKIP}  Failed: ${FAIL}"
if [[ $FAIL -gt 0 ]]; then
  log ""
  log "Failed recipes:"
  echo -e "$FAILED_LIST" | tee -a "$LOGFILE"
  log "Full error details in: ${LOGFILE}"
fi

# Set up remote if needed and upload
REMOTE_NAME="patchwork"
REMOTE_URL="https://conan.conan-hdc2h2x0up.eu/artifactory/api/conan/conan"

if conan remote list | grep -q "^${REMOTE_NAME}:"; then
  log "Remote '${REMOTE_NAME}' already configured"
else
  log "Adding remote '${REMOTE_NAME}'..."
  conan remote add "$REMOTE_NAME" "$REMOTE_URL" --index 0
fi

if conan remote auth "$REMOTE_NAME" 2>&1 | grep -q "user:"; then
  log "Already authenticated to '${REMOTE_NAME}'"
else
  conan remote login "$REMOTE_NAME" patchwork -p "$CONAN_PASSWORD"
fi
conan upload "*" --remote "$REMOTE_NAME" --confirm --only-recipe
