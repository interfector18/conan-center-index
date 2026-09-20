#!/usr/bin/env python3
"""Select recipes since the last successful push publication, not upstream."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def select_recipes(root, pages, run_id, branch, recipe=""):
    root = Path(root)
    if recipe:
        if not re.fullmatch(r"[a-z0-9][a-z0-9_+.-]*", recipe):
            raise ValueError("Invalid recipe name")
        if not (root / "recipes" / recipe / "config.yml").is_file():
            raise ValueError(f"Unknown recipe: {recipe}")
        return [recipe]

    # Targeted manual runs do not publish all intervening changes. Only a
    # successful push is a safe baseline. Ignore this run and newer runs when
    # retrying an older workflow.
    runs = [
        run for page in pages for run in page["workflow_runs"]
        if run["event"] == "push" and run["conclusion"] == "success"
        and run["head_branch"] == branch and run["id"] < run_id
    ]
    baseline = max(runs, key=lambda run: run["id"])["head_sha"] if runs else None
    if baseline and subprocess.run(
        ["git", "cat-file", "-e", f"{baseline}^{{commit}}"],
        cwd=root, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0:
        print(f"Comparing recipes against published commit {baseline}", file=sys.stderr)
        changed = subprocess.check_output(
            ["git", "diff", "--no-renames", "--name-only", "-z", baseline,
             "HEAD", "--", "recipes/"], cwd=root,
        ).decode().split("\0")
        names = {path.split("/")[1] for path in changed if path}
    else:
        print("No usable publication baseline; selecting all recipes", file=sys.stderr)
        names = {path.parent.name for path in (root / "recipes").glob("*/config.yml")}
    # Deleted recipes cannot be exported. Keep their existing remote revisions
    # available to consumers that still pin them.
    return sorted(name for name in names if (root / "recipes" / name / "config.yml").is_file())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--history", type=Path, required=True)
    parser.add_argument("--run-id", type=int, required=True)
    parser.add_argument("--branch", required=True)
    parser.add_argument("--recipe", default="")
    args = parser.parse_args()
    with args.history.open() as history:
        recipes = select_recipes(Path.cwd(), json.load(history), args.run_id, args.branch, args.recipe)
    for name in recipes:
        print(name)
