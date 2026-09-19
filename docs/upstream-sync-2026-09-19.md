# Upstream sync — 2026-09-19

Base fork: `patchwork-master` at `ab3f470d2`.
Reviewed upstream range: `b9b7547e7..319023a7b` (28 commits, September 11–17).
Integration branch: `t3code/review-upstream-changes`.

All 28 upstream commits are accounted for. Version removals were deliberately
adapted to preserve pinned consumers. No remote publication is part of this sync.

## Compatibility decisions

- Retain every previously configured version in the 30 recipes covered by validation:
  121 existing versions plus 25 upstream additions and two restored dependencies.
- Preserve 56 historical versions in `pre_*` folders. Their recipe files, source
  metadata, patches and tests match the pre-update tree (`ca3b45ac3`) byte for byte.
  Newer versions continue to use `all`, keeping future upstream updates straightforward.
- Keep old versions alongside new versions for the metadata-only updates, including
  OpenVINO's version-specific dependency metadata and patches.
- Keep libcurl 8.21.0's original patch and TLS settings, and retain older libheif
  CMake options. These changes were made in the preceding integration batch.
- Retain the CMake < 4 bound on the SPIRV-Tools versions that upstream stopped
  maintaining; relax it for the versions still covered by upstream's update.
- Preserve all 56 fork-customized files other than CMake's source metadata exactly.
  The CMake metadata gains upstream's fallback mirrors and retains the fork's 3.31.9 entry.

## Fixes found during validation

- **LMDB:** publish `dl` only on Linux. FreeBSD's CMake platform sets
  `CMAKE_DL_LIBS` to an empty string; its `dlopen` implementation is in libc.
- **Flatbush:** use a minimum C++11 compile feature in the consumer test instead
  of overriding the profile with C++11. The override broke C++20 profiles because
  the recipe correctly omitted the fallback span definition for those profiles.
  The preserved 1.4.1 header also included `<span>` inside `namespace flatbush`;
  a version-specific patch moves that include outside the namespace. Both 1.4.1
  and 1.5.0 pass their consumer tests under C++11 and C++20.
- **Missing pins:** restore `fast_float/6.1.5` for SymEngine and
  `spirv-headers/1.3.236.0` for older SPIRV-Tools. Source URLs and SHA-256 hashes
  come from upstream history (`c106bb8e3^` and `e3ff534ca^` respectively).
- The serializer commit title says 1.7.0, but its recipe and source metadata
  consistently publish **mas-bandwidth-serialize/1.17.0**; that is the imported version.

## Validation

Environment: Linux x86_64, GCC 16, Conan 2.32.0, CMake 4.4.3.
Separate temporary Conan caches were used; the user's configured cache and remotes
were not modified. Builds ran against copies of the recipes outside the checkout.

- **148/148 exports**, covering all configured versions in the 30 relevant recipes.
- **56/56 dependency graphs:** 41 Linux and 15 FreeBSD configurations, including
  SQLGen with DuckDB, shared SOCI, and PoDoFo without fontconfig. Dependencies were
  resolved from this checkout via a `local-recipes-index` remote.
- Every upstream version/source entry in the reviewed range is represented.
  No existing version was removed. Frozen recipes were checked against the baseline.
- Source URLs and hashes were checked by Conan for the packages actually built.
  Export success alone does not establish source availability or build correctness.

Build profiles declare the installed CMake as `[platform_tool_requires]`
`cmake/4.4.3`, following the [Conan profile documentation](https://docs.conan.io/2/reference/config_files/profiles.html#platform-tool-requires).
This exercises the real recipes with the system tool without changing their
build requirements. Recipes and dependencies are built from source.

**17/17 final build-and-consumer-test configurations passed** (15 distinct package versions):

| Package | Versions | C++ standard where applicable |
| --- | --- | --- |
| flatbush | 1.4.1, 1.5.0 | 11 and 20 for both |
| lmdb | 0.9.32, 1.0.2 | Default profile |
| lexbor | 2.7.0, 3.0.0 | Default profile |
| libcbor | 0.13.0, 0.14.0 | Default profile |
| mas-bandwidth-serialize | 1.17.0 | 20 |
| fast_float | 6.1.5 | 20 |
| spirv-headers | 1.3.236.0 | 20 |
| melon | 1.0.0 | 23 |
| mcap | 2.1.3 | 23 |
| symengine | 0.15.0 | 23 |
| shaderc | 2025.3 | 20 |

Shaderc's successful build also compiled SPIRV-Tools and glslang 1.4.313.0
from this checkout with CMake 4.4.3. SymEngine's build validated the restored
fast_float dependency and the new CMake package configuration.

Representative command, with `CONAN_HOME` pointing at an isolated cache:

```sh
conan create <copied-recipe-directory> --name=shaderc --version=2025.3 \
  --build=missing -r workspace -c tools.build:jobs=4
```


FreeBSD checks validate dependency graphs, not native compilation or linking.
Windows and macOS builds were not run. The heavier packages not listed as built
have export and graph coverage only. Archived recipes are preserved rather than
claimed to be universally compatible with current compilers and Conan versions.

## Reviewed upstream commits

| Commit | Change |
| --- | --- |
| `96364a6b6` | symengine: publish version 0.15.0; stop publishing revs for older versions (#30906) |
| `1bcb0e9e1` | sqlgen: publish version 0.6.0; add  `with_duckdb` option (#30430) |
| `b5612c32f` | scip: publish version 10.0.3 (#30876) |
| `a566d6212` | spirv-reflect: remove CMake < 4 restriction (#30930) |
| `7fc80e7d9` | shaderc,glslang: Stop publishing revisions for some older versions; refactor recipes (#30947) |
| `8fd6487ec` | openvino: publish version 2026.3.1 (#30931) |
| `b96b6e1a8` | spirv-tools: remove CMake < 4 restriction; stop publishing revs for some non-required vresions(#30929) |
| `80bae55b4` | mcap: publish version 2.1.3; stop publishing revs for older versions (#30983) |
| `956c2bc80` | cpp-httplib: publish version 0.56.0 (#30985) |
| `0bc30c51f` | lexbor: publish versions 3.0.0 and 2.7.0 (#30872) |
| `0ef2cd1e9` | readerwriterqueue: publish version 1.0.7 (#30955) |
| `e6f723d85` | libcbor: publish version 0.14.0; stop publishing revs for older versions (#30939) |
| `b5c2ac85f` | melon: publish version 1.0.0 (#30916) |
| `db0cb6be4` | libxml2: publish version 2.15.4 (#30941) |
| `38a1cc0f9` | librealsense: publish version 2.58.1 (#30972) |
| `98b4eaf58` | libheif: publish version 1.23.4 (#30924) |
| `e830b72a5` | tgbot: publish version 1.13 (#30974) |
| `6b8c8f7a0` | lmdb: publish version 1.0.2 (#30867) |
| `63a2611c8` | mas-bandwidth-serialize: publish version 1.7.0 (#30728) |
| `17f162a92` | doxygen: publish version 1.18 (#30999) |
| `a8a11ec0e` | soci: publish version 4.1.4 (#30956) |
| `32e1cf48a` | cmake: add github Kitware mirror source URL (#30996) |
| `f3fdc907d` | libcurl: publish version 8.22.0 (#30969) |
| `5151a2d03` | flatbush: publish version 1.5.0 (#30959) |
| `ac9a57163` | unordered_dense: publish version 4.11.0 (#30942) |
| `811e86570` | xz_utils: publish version 5.8.4 (#30978) |
| `50fa37e1c` | podofo: publish version 1.1.2 (#30853) |
| `319023a7b` | unordered_dense: publish version 5.0.1 (#30993) |
