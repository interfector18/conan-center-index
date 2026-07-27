# Folly 2026 Recipe Update Design

## Goal

Add Folly `2026.07.20.00` to Conan Center Index while retaining working support for `2024.08.12.00`.

## Recipe structure

Both versions remain in `recipes/folly/all`. Version checks in the shared recipe isolate the upstream changes without duplicating the recipe:

- `2024.08.12.00` keeps C++17, `double-conversion`, its existing Boost component list, CMake compatibility workaround, source rewrites, and component metadata.
- `2026.07.20.00` uses C++20, `fast_float`, the current platform-specific Boost component list, upstream's native CMake 4 behavior, current source rewrites, and metadata matching the restructured build outputs.

The dependency bridge in `conan_deps.cmake` will select `DoubleConversion` or `FastFloat` from a toolchain variable set by the recipe. All other dependency discovery remains shared.

## Source and build handling

The new release source URL and SHA-256 digest are added to `conandata.yml` and exposed through `config.yml`. Source patching remains strict but is gated where upstream text differs, so a missing expected replacement still exposes upstream drift.

The recipe will continue using upstream's CMake build and install rules. It will not carry a patch that attempts to restore the old Folly build layout.

## Package metadata

The main `Folly::folly` target remains the stable public entry point. Metadata for auxiliary libraries will be conditional where the 2026 CMake target restructuring changed library names or link relationships. Dependencies exported through the main component will match the selected Folly version.

## Validation

Validation will cover:

- recipe formatting and Conan recipe inspection;
- source retrieval and configuration for both versions;
- a local build and test-package run for `2026.07.20.00`;
- a regression build/test of `2024.08.12.00` when dependency availability permits;
- inspection of the packaged libraries and generated consumer link metadata.

No unrelated recipe refactoring or dependency modernization is in scope.
