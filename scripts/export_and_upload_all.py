#!/usr/bin/env python3
"""Export all recipes and upload them to the Artifactory remote."""

import json
import os
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
LOGFILE = REPO_ROOT / "scripts" / "export.log"
REMOTE_NAME = "patchwork"
REMOTE_URL = "https://conan.conan-hdc2h2x0up.eu/artifactory/api/conan/conan"
MAX_WORKERS = os.cpu_count() or 4


def load_env():
    env_file = REPO_ROOT / ".env"
    if not env_file.exists():
        print(f"Error: .env file not found at {env_file}")
        sys.exit(1)
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" in line:
                key, _, value = line.partition("=")
                os.environ[key.strip()] = value.strip().strip('"').strip("'")


def get_cached_recipes():
    result = subprocess.run(
        ["conan", "list", "*", "--format=json"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return set()
    data = json.loads(result.stdout)
    return set(data.get("Local Cache", {}).keys())


def collect_recipes():
    """Collect all (name, version, folder) tuples to export."""
    recipes = []
    for config_path in sorted(REPO_ROOT.glob("recipes/*/config.yml")):
        recipe_name = config_path.parent.name
        with open(config_path) as f:
            cfg = yaml.safe_load(f)
        for ver, data in cfg.get("versions", {}).items():
            folder = data.get("folder", "all")
            recipes.append((recipe_name, str(ver), folder))
    return recipes


def is_conan1_recipe(recipe_name, folder):
    conanfile = REPO_ROOT / "recipes" / recipe_name / folder / "conanfile.py"
    if not conanfile.exists():
        return False
    with open(conanfile) as f:
        head = f.read(2048)
    return bool(re.search(r"from conans import", head))


def export_recipe(recipe_name, version, folder):
    result = subprocess.run(
        ["conan", "export", f"recipes/{recipe_name}/{folder}",
         f"--name={recipe_name}", f"--version={version}"],
        capture_output=True, text=True, cwd=REPO_ROOT
    )
    return result.returncode == 0, result.stdout + result.stderr


def setup_remote():
    result = subprocess.run(
        ["conan", "remote", "list"], capture_output=True, text=True
    )
    if f"{REMOTE_NAME}:" in result.stdout:
        print(f"Remote '{REMOTE_NAME}' already configured")
    else:
        print(f"Adding remote '{REMOTE_NAME}'...")
        subprocess.run(
            ["conan", "remote", "add", REMOTE_NAME, REMOTE_URL, "--index", "0"],
            check=True
        )

    password = os.environ.get("CONAN_PASSWORD", "")
    subprocess.run(
        ["conan", "remote", "login", REMOTE_NAME, "patchwork", "-p", password],
        check=True
    )


def upload_all():
    subprocess.run(
        ["conan", "upload", "*", "--remote", REMOTE_NAME, "--confirm", "--only-recipe"],
        check=True
    )


def main():
    load_env()

    print("Building cache index...")
    cached = get_cached_recipes()
    print(f"Found {len(cached)} recipes already in cache")

    recipes = collect_recipes()
    print(f"Found {len(recipes)} total recipe versions")

    # Filter
    to_export = []
    skipped = 0
    conan1_skipped = 0
    for name, ver, folder in recipes:
        if f"{name}/{ver}" in cached:
            skipped += 1
        elif is_conan1_recipe(name, folder):
            conan1_skipped += 1
        else:
            to_export.append((name, ver, folder))

    print(f"Skipping {skipped} already cached, {conan1_skipped} Conan 1.x recipes")
    print(f"Exporting {len(to_export)} recipes with {MAX_WORKERS} workers...")

    ok = 0
    fail = 0
    failed_list = []

    with open(LOGFILE, "w") as log:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(export_recipe, name, ver, folder): (name, ver)
                for name, ver, folder in to_export
            }
            for future in as_completed(futures):
                name, ver = futures[future]
                success, output = future.result()
                if success:
                    ok += 1
                else:
                    fail += 1
                    failed_list.append(f"{name}/{ver}")
                    log.write(f"FAIL: {name}/{ver}\n")
                    log.write(output)
                    log.write("---\n")

                done = ok + fail
                if done % 50 == 0:
                    print(f"  Progress: {done}/{len(to_export)}")

    total = skipped + conan1_skipped + len(to_export)
    print()
    print("========== Export Summary ==========")
    print(f"Total: {total}  OK: {ok}  Skipped: {skipped + conan1_skipped} (cached: {skipped}, conan1: {conan1_skipped})  Failed: {fail}")
    if failed_list:
        print()
        print("Failed recipes:")
        for entry in sorted(failed_list):
            print(f"  {entry}")
        print(f"Full error details in: {LOGFILE}")

    # Upload
    setup_remote()
    upload_all()


if __name__ == "__main__":
    main()
