#!/usr/bin/env python3
"""Fail unless every exported recipe revision can be found on the remote."""

import json
from pathlib import Path
import subprocess
import sys


def verify(remote, reference):
    result = subprocess.run(
        ["conan", "list", reference, "-r", remote, "--format=json"],
        check=True, capture_output=True, text=True,
    )
    data = json.loads(result.stdout)
    recipe, revision = reference.split("#", 1)
    # Conan may return exit code 0 with an error inside the JSON response.
    revisions = data.get(remote, {}).get(recipe, {}).get("revisions", {})
    if revision not in revisions:
        raise RuntimeError(f"Missing published revision: {reference}: {data}")
    print(f"Verified {reference} on {remote}")


if __name__ == "__main__":
    remote, references_file = sys.argv[1:]
    for reference in Path(references_file).read_text().splitlines():
        verify(remote, reference)
