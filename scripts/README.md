# Recipe publication

`.github/workflows/publish.yml` publishes recipes on pushes to `master` and
supports manually publishing a named recipe. Automatic selection compares the
current tree to the last successful **push** run of that workflow on the same
branch. It does not compare to Conan Center upstream: an upstream recipe update
also needs publishing to our private remote.

Failed, cancelled, and targeted manual runs do not advance the baseline. Runs
are serialized, and the next successful push includes changes from skipped or
failed pushes. If the baseline commit is unavailable, all current recipes are
selected. Deleted recipes are not removed from the remote, so consumers can
continue using their pinned revisions.

After uploading, every revision returned by `conan export` is looked up on the
remote. A missing revision fails the workflow even if Conan returns exit code 0
with an error in its JSON output.

Run the regression checks with:

```sh
python3 -m unittest discover -s scripts -p 'test_recipe_publication.py' -v
```

## Recovering an already missing lockfile revision

The new selection rule prevents future upstream updates from being skipped; it
does not backfill omissions from earlier successful runs. A consumer may also
pin a revision exported with different metadata normalization. Exporting the
current recipe is not guaranteed to recreate that exact revision.

When the exact revision exists in a trusted local cache, verify and upload it
explicitly, then retry dependency preparation:

```sh
conan upload 'name/version#revision' -r patchwork --only-recipe --check --dry-run
conan upload 'name/version#revision' -r patchwork --only-recipe --check --confirm
conan list 'name/version#revision' -r patchwork --format=json
```

Do not replace consumer lockfile revisions merely to match a fresh export.
