# Upstream sync — 2026-11-08

Base fork: `master` at `5b9da3d6c` (the branch the publication workflow runs on;
it contains `patchwork-master`).
Reviewed upstream range: `319023a7b..08d9ba53f` (257 commits, September 21 – November 6).
Integration branch: `sync/upstream-2026-11-08`.

All 257 upstream commits are merged. Version removals were adapted to preserve
pinned consumers, following the 2026-09-19 rules.

## Compatibility decisions

- Every version configured on the fork before the merge is still configured.
  A version is kept in its original folder when upstream left that folder's recipe
  files (everything except `conandata.yml`) unchanged; its `sources`/`patches`
  entries and patch files are re-added to `conandata.yml`. Otherwise the fork's
  folder is copied byte for byte into `pre_<newest upstream version>`, so the
  exported recipe revision of those versions is unchanged.
- 131 restorations: 78 versions across 40 recipes in their original folder,
  233 versions in 90 new `pre_*` folders, and the whole `samarium` recipe, which
  upstream delisted (#31288).
- Conflicts in `config.yml`/`conandata.yml` were resolved by taking upstream and
  then applying the same restoration, so fork-only versions (for example
  `drogon/1.9.14-pw.1`, `libcurl/8.21.0`, `flatbush/1.4.1`, `tgbot/1.12.3`, the
  SPIRV pins) are kept.
- `cmake/binary` keeps the fork's source-build fallback and gains upstream's
  `trim_conandata` export and `required_conan_version >=2.2`. The new 4.4.4 entry
  gets a `source` archive (sha256 from Kitware's `cmake-4.4.4-SHA-256.txt`), like the
  other fork versions; 4.4.3, 3.31.12 and 3.31.9 keep their fork entries.
- `drogon`: upstream's 1.9.14 recipe adds a `with_spdlog` option. The fork's
  `1.9.14-pw.1`, 1.9.13 and 1.9.11 stay on the previous recipe in `pre_1.9.14`.

## Fork additions

- **libvips 8.18.7** (upstream still only has 8.16.0). Source from the libvips
  GitHub release, sha256 `5baaead3…b3bf94`. Version-gated recipe changes for >= 8.17:
  the `doxygen`/`gtk_doc` Meson options were renamed to `cpp-docs`/`docs`; the new
  `uhdr` and `raw` loaders are disabled so system libraries are never picked up;
  `libheif` requirement is `[>=1.23.4 <2]` (8.16.0 keeps `libheif/1.16.2`).
  8.18.7 already contains the glib `VIPS_FREEF` fix that the 8.16.0 patch carries.

## Known pre-existing issue

- `wasmtime/6.0.1` is configured but has no `sources` entry; this was already the
  case on the fork before this sync and is left unchanged.
- `imagemagick/7.0.11-14` is a Conan 1 recipe (`from conans import`) that the fork
  kept. It was never on the remote and cannot be exported by Conan 2, so the publish
  workflow now skips Conan 1 recipes with a warning, as
  `scripts/export_and_upload_all.sh` already did. Without this, the first publish
  after the merge would fail and the baseline would never advance.

## Fixes found during validation

- **libheif ≥ 1.23:** the internal `heifio` helper is always configured and runs
  `find_package` for TIFF, PNG, WebP and JPEG. On a host with system libtiff it found
  the library without the `TIFF::TIFF` target and configuration failed. The recipe
  now disables those lookups (JPEG only when `with_jpeg` is off); `heifio` is not
  installed, so the package content is unchanged.

## Validation

Environment: Linux x86_64 (scar-17), GCC 14 with `compiler.cppstd=23` (the
ExperimentalFbois backend CI compiler), Conan 2.34.0, CMake 4.4.5 declared as
`[platform_tool_requires]`. A separate temporary Conan cache was used with only a
`local-recipes-index` remote pointing at this checkout; everything was built from
source. The user's cache and remotes were not modified.

- **972/973 exports** of every configured version in the 245 changed recipes (plus
  libvips/libheif re-exported after the final edits). The only failure is the Conan 1
  `imagemagick/7.0.11-14` recipe described above.
- **Every fork version is still configured**, and every configured folder has a
  `conanfile.py`, a `sources` entry for its version and all referenced patch files
  (except the pre-existing `wasmtime/6.0.1`).
- **Build and test_package passed** (`conan create`):

| Package | Version | Options |
| --- | --- | --- |
| openssl | 3.6.5 | default |
| libxml2 | 2.15.4 (`cmake` folder) | default |
| libheif | 1.23.4 | `with_libaomav1=True`, `with_libde265=False` |
| libvips | 8.18.7 | `cpp=True`, `with_webp=True`, `with_heif=True`, `with_jpeg_xl=False` |

The libvips build resolved and compiled from this checkout: glib 2.86.5,
expat 2.10.0, libtiff 4.7.2, xz_utils 5.8.4, zlib 1.3.2, libwebp 1.6.0, libspng 0.7.4,
libjpeg 9f, lcms 2.16, fftw 3.3.10, libaom-av1 3.13.3. glib still pins
`pcre2/10.42`; consumers that need pcre2 10.49 must override it.
`libvips/8.16.0` was export-checked only.

Publication regression tests (`scripts/test_recipe_publication.py`) pass.

## Fork-restored versions

| Recipe | Restored versions | Location |
| --- | --- | --- |
| 7zip | 26.02 | `all` (same folder) |
| aws-c-auth | 0.9.1 | `pre_0.10.4` (fork copy of `all`) |
| aws-c-cal | 0.9.8 | `pre_0.9.15` (fork copy of `all`) |
| aws-c-common | 0.12.5 | `all` (same folder) |
| aws-c-compression | 0.3.1 | `pre_0.3.2` (fork copy of `all`) |
| aws-c-event-stream | 0.5.7 | `pre_0.7.1` (fork copy of `all`) |
| aws-c-http | 0.10.5 | `pre_0.11.0` (fork copy of `all`) |
| aws-c-io | 0.23.2 | `pre_0.27.6` (fork copy of `all`) |
| aws-c-mqtt | 0.13.3 | `pre_0.16.1` (fork copy of `all`) |
| aws-c-s3 | 0.9.2 | `pre_0.13.5` (fork copy of `all`) |
| aws-c-sdkutils | 0.2.4 | `pre_0.2.9` (fork copy of `all`) |
| aws-checksums | 0.2.6 | `pre_0.2.10` (fork copy of `all`) |
| aws-crt-cpp | 0.35.2 | `pre_0.43.9` (fork copy of `all`) |
| aws-sdk-cpp | 1.11.692 | `pre_1.11.915` (fork copy of `all`) |
| blend2d | 0.11.4, 0.11.3, 0.11.1, 0.10.6, 0.10.5, 0.10.4, 0.10, 0.9, 0.8 | `pre_0.21.2` (fork copy of `all`) |
| botan | 3.12.0 | `all` (same folder) |
| brotli | 1.2.0 | `pre_1.2.1` (fork copy of `all`) |
| c-ares | 1.34.8 | `all` (same folder) |
| c-blosc2 | 3.1.2 | `all` (same folder) |
| catch2 | 3.16.0 | `3.x.x` (same folder) |
| ccache | 4.14 | `pre_4.14.2` (fork copy of `all`) |
| charls | 2.4.1, 2.4.0, 2.3.4, 2.2.0, 2.1.0 | `pre_2.4.5` (fork copy of `all`) |
| cjson | 1.7.18, 1.7.17, 1.7.15, 1.7.14, 1.7.13, 1.7.12 | `pre_1.7.19` (fork copy of `all`) |
| cli11 | 2.6.2, 2.6.0, 2.5.0, 2.4.2, 2.4.1, 2.4.0, 2.3.1, 2.3.0, 2.2.0, 2.1.1, 2.0.0, 1.9.1 | `pre_2.7.2` (fork copy of `all`) |
| cloudini | 1.2.3 | `pre_1.4.1` (fork copy of `all`) |
| cmake | 4.4.3 | `pre_4.4.4` (fork copy of `binary`) |
| cmocka | 1.1.7, 1.1.5 | `pre_2.0.2` (fork copy of `all`) |
| coal | 3.0.2 | `all` (same folder) |
| cpp-httplib | 0.56.0, 0.47.0 | `pre_0.65.0` (fork copy of `all`) |
| d3d12-memory-allocator | 3.0.1 | `pre_3.2.1` (fork copy of `all`) |
| dcmtk | 3.7.0 | `pre_3.7.1` (fork copy of `all`) |
| diligent-core | api.252009, api.252005, api.252004, api.252003, 2.5.2, 2.5.1, api.250014 | `pre_api.256019` (fork copy of `all`) |
| drogon | 1.9.14-pw.1, 1.9.13, 1.9.11 | `pre_1.9.14` (fork copy of `all`) |
| ensmallen | 2.19.1 | `pre_3.11.1` (fork copy of `all`) |
| entt | 3.15.0, 3.14.0, 3.13.2, 3.12.2, 3.11.1, 3.10.3 | `pre_4.0.0` (fork copy of `3.x.x`) |
| etl | 20.48.1 | `all` (same folder) |
| exiv2 | 0.28.2, 0.28.1, 0.27.5 | `pre_0.28.3` (fork copy of `all`) |
| expat | 2.8.4, 2.8.3 | `all` (same folder) |
| ffmpeg | 9.0.1 | `pre_9.0.2` (fork copy of `all`) |
| flatbush | 1.5.0, 1.4.1 | `all` (same folder) |
| fmi2 | 2.0.4 | `all` (same folder) |
| foonathan-memory | 0.7.2, 0.7.1, 0.7.0 | `pre_0.7.3` (fork copy of `all`) |
| freetype | 2.14.1, 2.13.3 | `pre_2.15.0` (fork copy of `meson`) |
| freetype | 2.12.1, 2.11.1, 2.10.4 | `pre_2.15.0_2` (fork copy of `all`) |
| gaia-ecs | 0.9.2, 0.8.6 | `pre_1.0.0` (fork copy of `all`) |
| glaze | 8.3.0 | `all` (same folder) |
| glslang | 1.4.350.0 | `all` (same folder) |
| gnutls | 3.7.8 | `pre_3.8.7` (fork copy of `all`) |
| godot-cpp | 3.3.4, cci.3.2-20200130 | `all` (same folder) |
| grpc | 1.83.1 | `pre_1.84.0` (fork copy of `all`) |
| harfbuzz | 12.3.0 | `pre_15.0.0` (fork copy of `all`) |
| hazelcast-cpp-client | 5.7.0 | `all` (same folder) |
| hiredis | 1.3.0 | `all` (same folder) |
| hunspell | 1.7.0 | `pre_1.7.5` (fork copy of `all`) |
| hwloc | 2.14.0 | `all` (same folder) |
| icey | 2.4.11 | `pre_2.5.1` (fork copy of `all`) |
| imagemagick | 7.0.11-14 | `pre_7.1.2.35` (fork copy of `all`) |
| isl | 0.25, 0.24 | `pre_0.28` (fork copy of `all`) |
| joltphysics | 5.2.0 | `pre_5.6.0` (fork copy of `5.x`) |
| joltphysics | 3.0.1, 2.0.1 | `pre_5.6.0_2` (fork copy of `3.x`) |
| json-schema-validator | 2.4.0, 2.2.0, 2.1.0, 2.0.0 | `pre_2.4.1` (fork copy of `all`) |
| libalsa | 1.2.13, 1.2.12, 1.2.7, 1.2.4, 1.2.2, 1.1.9 | `pre_1.2.16.1` (fork copy of `all`) |
| libcurl | 8.22.0, 8.21.0 | `pre_8.23.0` (fork copy of `all`) |
| libde265 | 1.0.15, 1.0.12 | `pre_1.1.3` (fork copy of `all`) |
| libgd | 2.3.2, 2.3.1, 2.3.0, 2.2.5 | `pre_2.3.3` (fork copy of `all`) |
| libnghttp2 | 1.66.0 | `pre_1.68.1` (fork copy of `all`) |
| libpng | 1.6.58 | `all` (same folder) |
| libpq | 16.14, 15.18, 15.4, 14.23 | `all` (same folder) |
| libqasm | 1.4.1 | `all` (same folder) |
| libusb | 1.0.25, 1.0.24, 1.0.23 | `pre_1.0.30` (fork copy of `all`) |
| libuv | 1.51.0, 1.49.2, 1.49.1, 1.49.0 | `pre_1.53.0` (fork copy of `all`) |
| libxlsxwriter | 1.2.2, 1.1.9, 1.1.8, 1.1.7, 1.1.5, 1.1.4, 1.1.3, 1.0.0 | `pre_1.2.4` (fork copy of `all`) |
| llama-cpp | b6565 | `pre_0.6.0` (fork copy of `all`) |
| lmdb | 0.9.32 | `pre_1.0.2` (fork copy of `all`) |
| luajit | 2.1.0-beta3 | `pre_2.1.1792527110` (fork copy of `all`) |
| md4c | 0.5.2, 0.5.1, 0.4.8 | `pre_0.6.0` (fork copy of `all`) |
| md4qt | 5.1.3 | `pre_5.4.0` (fork copy of `all`) |
| mexce | 1.0.1 | `pre_1.2.2` (fork copy of `all`) |
| moltenvk | 1.3.0, 1.2.2, 1.2.1, 1.2.0, 1.1.11 | `pre_1.4.2` (fork copy of `all`) |
| mongo-c-driver | 2.2.1, 2.2.0, 1.30.6, 1.29.2, 1.29.1, 1.29.0, 1.28.1, 1.27.6, 1.26.2, 1.24.3 | `pre_2.5.8` (fork copy of `all`) |
| mongo-cxx-driver | 4.0.0 | `pre_4.6.0` (fork copy of `all`) |
| mujoco | 3.12.0 | `pre_3.14.0` (fork copy of `all`) |
| nameof | 0.10.2, 0.10.1, 0.10.0, 0.9.4 | `pre_0.10.6` (fork copy of `all`) |
| nanodbc | 2.14.0, 2.13.0 | `pre_2.20.0` (fork copy of `all`) |
| ncurses | 6.5 | `pre_6.6` (fork copy of `all`) |
| net-snmp | 5.9.4 | `pre_5.9.5.2` (fork copy of `all`) |
| netcode | 1.4.5, 1.4.3 | `all` (same folder) |
| nmos-cpp | cci.20260812 | `pre_cci.20261005` (fork copy of `all`) |
| omath | 5.6.0, 5.0.0 | `pre_5.7.0` (fork copy of `all`) |
| open62541 | 1.5.0, 1.4.14 | `pre_1.5.8` (fork copy of `all`) |
| openssl | 4.0.2 | `4.x.x` (same folder) |
| openssl | 3.6.4, 3.5.8, 3.4.7, 3.0.22 | `3.x.x` (same folder) |
| opentelemetry-cpp | 1.22.0 | `pre_1.26.0` (fork copy of `all`) |
| ouster_sdk | 0.15.0, 0.14.0 | `pre_1.0.1` (fork copy of `all`) |
| pagmo2 | 2.19.0 | `pre_2.20.0` (fork copy of `all`) |
| perfetto | 52.0, 50.1, 48.1, 47.0, 45.0, 44.0, 43.1, 42.0, 41.0, 40.0 | `pre_58.2` (fork copy of `all`) |
| pipewire | 1.5.85 | `all` (same folder) |
| poco | 1.15.2 | `pre_1.15.4` (fork copy of `all`) |
| protobuf | 7.35.0 | `all` (same folder) |
| qt | 6.11.1, 6.10.3 | `pre_6.12.0` (fork copy of `6.x.x`) |
| reduct-cpp | 1.19.1 | `all` (same folder) |
| reliable | 1.4.2 | `all` (same folder) |
| rmlui | 6.2 | `pre_6.3` (fork copy of `all`) |
| s2n | 1.5.27 | `all` (same folder) |
| samarium | all | whole recipe restored (delisted upstream) |
| sdl | 3.4.14 | `3.x` (same folder) |
| sentry-native | 0.14.2 | `pre_0.16.8` (fork copy of `all`) |
| sfml | 2.6.1, 2.6.0, 2.5.1 | `pre_3.0.2` (fork copy of `all`) |
| shaderc | 2025.3 | `pre_2026.4` (fork copy of `all`) |
| simdutf | 9.0.0 | `all` (same folder) |
| spirv-cross | 1.4.350.0, 1.4.321.0, 1.4.313.0, 1.4.309.0, 1.3.296.0, 1.3.268.0, 1.3.261.1, 1.3.250.1, 1.3.246.1, 1.3.243.0, 1.3.239.0 | `all` (same folder) |
| spirv-headers | 1.4.350.0, 1.4.309.0, 1.3.296.0, 1.3.268.0, 1.3.261.1, 1.3.243.0, 1.3.239.0, 1.3.236.0 | `all` (same folder) |
| spirv-reflect | 1.4.350.0, 1.4.313.0 | `all` (same folder) |
| spirv-tools | 1.4.350.0, 1.4.309.0, 1.3.268.0, 1.3.261.1, 1.3.243.0, 1.3.239.0, 1.3.236.0 | `pre_1.4.357.0` (fork copy of `all`) |
| tgbot | 1.12.3 | `all` (same folder) |
| tracy | 0.13.1 | `pre_0.14.1` (fork copy of `all`) |
| upa-url | 2.5.0 | `pre_2.6.0` (fork copy of `all`) |
| utf8proc | 2.7.0, 2.6.1, 2.6.0, 2.5.0 | `pre_2.12.0` (fork copy of `all`) |
| utfcpp | 4.2.0, 4.1.1, 4.0.9 | `all` (same folder) |
| vincentlaucsb-csv-parser | 2.2.3, 2.2.2, 2.2.0, 2.1.3 | `pre_5.3.0` (fork copy of `all`) |
| volk | 1.4.350.0, 1.4.313.0, 1.3.296.0, 1.3.268.0, 1.3.261.1, 1.3.250.0, 1.3.243.0, 1.3.239.0 | `pre_1.4.357.0` (fork copy of `all`) |
| vulkan-headers | 1.4.313.0, 1.4.309.0, 1.3.290.0, 1.3.261.1, 1.3.250.0 | `all` (same folder) |
| vulkan-loader | 1.4.350.0, 1.4.313.0, 1.4.309.0, 1.3.290.0, 1.3.250.0 | `all` (same folder) |
| vulkan-utility-libraries | 1.4.350.0 | `all` (same folder) |
| vulkan-validationlayers | 1.4.350.0 | `all` (same folder) |
| vulkan-validationlayers | 1.3.243.0, 1.3.239.0, 1.3.236.0, 1.3.231.1, 1.3.224.1, 1.3.216.0, 1.3.211.0 | `pre_1.4.357.0` (fork copy of `1.3.x`) |
| wasmtime | 6.0.1 | `all` (same folder) |
| yojimbo | 1.2.5 | `pre_1.14.0` (fork copy of `all`) |
| zint | 2.10.0 | `pre_2.16.0` (fork copy of `all`) |
| zxc | 0.13.3 | `pre_0.15.0` (fork copy of `all`) |
| zxing-cpp | 2.3.0, 2.2.1, 2.1.0, 2.0.0, 1.4.0, 1.3.0, 1.0.8 | `pre_3.1.1` (fork copy of `all`) |

## Reviewed upstream commits

| Commit | Change |
| --- | --- |
| `fcd83376a` | apr-util: publish version 1.6.5 (#30857) |
| `cbc7243f6` | variant-lite: publish version 3.0.0 (#30984) |
| `363fd20ad` | ouster_sdk: publish version 1.0.1 (#30971) |
| `d7a39e2cc` | opentelemetry-cpp: fix validation without protobuf exporters (#30938) |
| `a6eb49aa3` | boost: remove execution monitors from unit_test_framework dependencies (#30932) |
| `192e20085` | coal: publish version 3.0.4 (#30943) |
| `4d67419d6` | libpq: publish versions 14.24 15.19 16.15 (#30954) |
| `0cd994cb5` | several recipes: publish latest version 1.4.357.0; stop publishing revs for some older versions (#30979) |
| `be753252d` | dqlite: add recipe at version 1.18.7 (#30552) |
| `eda200b64` | glaze: publish version 8.4.0 (#30994) |
| `0bcae4925` | expat: publish version 2.8.5 (#31033) |
| `e4bcfbc12` | soplex: publish version 8.1.0 (#31010) |
| `ba23582d7` | 7zip: publish version 26.03 (#31026) |
| `3a9ea1696` | scip: publish version 10.1.0 (#31037) |
| `d8742a50f` | grpc: publish version 1.84.0 (#30968) |
| `285b3cbca` | spirv-tools: expose private headers in order to build Diligent-Core (#31036) |
| `182d14e00` | mongo c and cxx drivers: publish most recent versions (#31032) |
| `be4476698` | shaderc: publish version 2026.4; bump dependencies (#31038) |
| `79142ee9c` | godot-cpp: publish version 10.0.0 (#30961) (#30966) |
| `723e205ea` | pcre2: publish version 10.48, disable unnecessary calls to find_package (#31030) |
| `bf420fea6` | moltenvk: publish version 1.4.2 (#30980) |
| `960c13f47` | utfcpp: publish version 4.2.1 (#31018) |
| `07389b8fa` | zxc: publish version 0.14.1 (#30901) |
| `c4aad3383` | lmdb: fix Emscripten robust mutex configuration (#31005) |
| `642ae211d` | kokkos: publish version 5.2.2 (new recipe) (#31022) |
| `4b6a535b5` | unordered-dense: publish version 5.2.0 (#31069) |
| `04c827a37` | openssl: publish versions 3.4.8, 3.5.9, 3.6.5, 4.0.3 (#31070) |
| `12d462807` | libaec: fix source URLs (#30882) |
| `b7d6e9a07` | poco: publish version 1.15.4 (#31075) |
| `c176134a6` | pcre2: publish version 10.49 (#31076) |
| `f7a539909` | mongo-c-driver: add version 2.5.5 (#31046) |
| `9bbe39b2b` | xkbcommon: configure default locale and config for Linux (#30899) |
| `03d11cc62` | automake: publish version 1.19 (#30963) |
| `63b646ba3` | redis-plus-plus: disable werror by default (#30897) |
| `0659c5fd5` | flatbush: publish version 1.6.0 (#31079) |
| `b0b43c371` | hiredis: publish version 1.3.1 (#31077) |
| `09070c640` | utf8proc: publish version 2.12.0 (#31078) |
| `9eed5d312` | mujoco: publish version 3.14.0 (#31068) |
| `79d772e61` | zxing-cpp: publish version 3.1.1 (#31056) |
| `9ffed67f5` | open62541: publish version 1.5.8 (#30587) |
| `269a0e2e2` | vincentlaucsb-csv-parser: publish version 5.3.0 (#31024) |
| `c72753086` | jemalloc: publish version 5.4.0 (#31064) |
| `a2ff5e014` | nanobind: publish version 3.1.0 (#31051) |
| `8f8ee6c7e` | libalsa: use official releases and consume pre-built configure (#31028) |
| `e664647eb` | hazelcast-cpp-client: publish version 5.7.1 (#31031) |
| `82f20074d` | cli11: publish version 2.7.2 (#31013) |
| `b6665fe12` | md4qt: publish version 5.2.0 (#30997) |
| `18965226b` | rsync/3.2.7: honor $(STRIP) in install-strip for cross-compilation (#30602) |
| `1e96417bc` | sparrow: publish version 2.5; changed homepage/source URL (#30533) |
| `88aeefbe8` | pango: fix dependencies versions (#31082) |
| `11968d274` | cnats: publish version 3.14 (#31016) |
| `341296366` | graaf: publish version 1.2.0 (#30973) |
| `4c4ac13f1` | zserio: publish version 2.19.0 (#31021) |
| `0041956ad` | opencascade: publish version 8.0.1 (#30663) |
| `38de3c07f` | etl: publish version 20.49.0 (#31039) |
| `43cfa821d` | cloudini: publish version 1.4.1 (#31066) |
| `0433dbc39` | nameof: publish version 0.10.6 (#31002) |
| `fd90f8b26` | reduct-cpp: publish version 1.21.0 (#31059) |
| `21cbe2297` | doxygen: set `cmake_file_name_variants` property (#31001) |
| `8335bb1d5` | fastgltf: publish version 0.9.1 (#31105) |
| `298b98a20` | cjson: set ENABLE_PUBLIC_SYMBOLS only for shared builds; stop publishing revs for some older versions (#30859) |
| `939a3b7f5` | cmake: publish version 4.4.4 (#31101) |
| `6182ad188` | libultrahdr: publish version 2.0.2 (#30775) |
| `2be089e67` | openimagio: rename USE_LIBWEBP to USE_WEBP; add USE_LIBUHDR (#31063) |
| `e89eac4e4` | poppler-data: publish version 0.4.12 (#31099) |
| `0190eb253` | expat: publish version 2.9.0 (#31115) |
| `2dcdfa1f4` | cpp-httplib: publish version 0.59.0 (#31102) |
| `6a3520ccc` | perfetto: publish version 58.2 (#31094) |
| `30f5b61d2` | sdl: publish version 3.4.16 (#31061) |
| `e284d27dc` | libqasm: publish version 1.5.0. (#31108) |
| `8757de50a` | xxHash: publish version 0.8.4 (#31015) |
| `4ffccd9df` | crashcatch: publish version 1.6.0 (#30818) |
| `014aa4c19` | librats: publish version 2.3.7 (#30910) |
| `51da4de87` | crashcatch : use cmake install instead of copying files (#31129) |
| `4149625bc` | libtomcrypt: publish version 1.18.2 (new recipe) (#29642) |
| `8fc4a8c41` | psqlodbc: publish version 18.00.0004 and 16.00.0005 (#30495) |
| `b70d36f33` | nmos-cpp: publish version cci.20261005 (#31120) |
| `bc44e861a` | protobuf: publish versions 7.36.2 and 7.35.1 (#31123) |
| `6051d7e00` | freeimage: fix only shared deps are propagated (#31006) |
| `d0041ad04` | thrift: publish version 0.25.0 (#31121) |
| `dafd56b23` | chore(icey): publish version 2.5.1 (#31128) |
| `ff1a11b73` | boost: fix dependencies for wave (#31057) (#31058) |
| `780d5510f` | charls: publish version 2.4.4 (#31124) |
| `cb5edffad` | hunspell: publish version 1.7.4 (#31096) |
| `6ec00e22c` | lodepng: publish version cci.20260102 (#31003) |
| `990ef02af` | sqlite3: publish version 3.54.0 (#31144) |
| `a2d02eb88` | omath: publish version 5.7.0; update source URL (#31085) |
| `e365dda1f` | aixlog: publish version 1.5.0 (#30029) |
| `cc79c3c33` | sz: add recipe for 3.4.0 (#31106) |
| `1eb6c1fa6` | proj/9.3.1: fix compiler flag appends for IntelLLVM builds (#31088) |
| `a73f2206e` | perf-cpp: add new recipe (1.1.1) (#30835) |
| `118612af3` | zziplib: publish version 0.13.80 (#31014) |
| `5874896cd` | lunasvg: fix version range for plutovg dependency (#31152) |
| `38d223a21` | libfn: publish version 0.1.0 (#30871) |
| `83307c6d8` | jasper: publish version 4.2.9 (#31148) |
| `f8e06f3f5` | ms-gsl: publish version 5.0.1 (#31150) |
| `22a6d52e7` | zxc: publish version 0.15.0 (#31154) |
| `bf51adc0a` | gaia-ecs: publish version 1.0.0 (#30833) |
| `ca6c1ec80` | raygui: publish version 5.0 (#30090) |
| `1e77ae7ee` | plutovg: add define `PLUTOVG_BUILD_STATIC` for static builds (#31156) |
| `36df390a6` | curl: publish version 8.23.0 (#31161) |
| `f6d5cfa34` | ccache: publish version 4.14.1 (#31163) |
| `f269c66e2` | rubberband: publish version 4.0.0 (#30038) |
| `e7b3084fc` | cpp-httplib: publish version 0.61.0 (#31141) |
| `769c74926` | libiconv: publish version 1.19 (#31170) |
| `58111fd78` | zmqpp: use version range for zeromq (#31173) |
| `6f881804c` | z3: publish version 4.13.4 (#31139) |
| `c3ec48c33` | pffft: fix the bitbucket sha (#31111) |
| `9dba03866` | netcode: publish version 1.4.8 (#31176) |
| `015d715f1` | libqasm: publish version 1.6.0 (#31158) |
| `e3e075880` | reliable: publish version 1.4.5 (#31177) |
| `2f2a8be33` | reduct-cpp: publish version 1.21.1 (#31167) |
| `1c90a5cb2` | libuv: publish version 1.53.0 (#31164) |
| `c0ed97aed` | entt: publish version 4.0.0 (#31092) |
| `c8546b509` | simdjson: publish version 5.0.5 (#31143) |
| `8161ffddd` | libtool: publish version 2.6.2 (#30964) |
| `bc5bd9675` | isl: publish version 0.28 (#31140) |
| `b3b48622f` | zycore & zydis: add new recipes (#29994) |
| `ff4cd6e37` | openblas: remove C++ settings (#31188) |
| `0edf3874b` | llama-cpp: publish version 0.6.0 (#30988) |
| `f18334a04` | msquic: publish version 2.6.3 (new recipe) (#29565) |
| `7166d8f0a` | cmocka: publish version 2.0.2 (#31182) |
| `305bf1fa3` | openusd: add recipe for 26.08 (#31116) |
| `d79d52d8f` | md4qt: publish version 5.3.0 (#31175) |
| `41395b3e6` | ensmallen: publish version 3.11.1 (#31187) |
| `543567ca2` | sobjectizer: publish version 5.8.6.2 (#31179) |
| `9a4dc4769` | tracy: publish version 0.14.1 (#31181) |
| `d5b6385dc` | libpng: publish version 1.6.59 (#31104) |
| `c510ea822` | tree-sitter-cuda: publish version 0.21.2 (#31011) |
| `3fb88cf90` | zmij: publish version 1.2 (new recipe) (#31071) |
| `529e47bed` | zycore: set cmake_build_modules property to populate some CMake helpers (#31201) |
| `74899008a` | libxml2:  add cmake_file_name_variants name for CMakeConfigDeps (#31203) |
| `63f37b0e1` | libjpeg-turbo: Force CMAKE_INSTALL_LIBDIR to lib (#31200) |
| `ee4a7c028` | cpp-httplib: publish version 0.62.0 (#31189) |
| `60dbd6c30` | foonathan-memory: set CMAKE_BUILD_TYPE for multi-config generators (#31146) |
| `136fc057a` | dataframe: publish version 4.2.0 (#31185) |
| `777398bee` | enchantum: add new recipe (#29999) |
| `e3fcc81ab` | pkgconf: publish version 3.0.7 (#30737) |
| `8f3942600` | wxwidgets: publish most recent versions (#31147) |
| `f3c6cda7a` | trng: publish version 4.28 (new recipe) (#31052) |
| `b7fe152d8` | sciplot: add new recipe (#29746) |
| `42c4bbb8a` | opus: presume NEON on armv8 (#31180) |
| `e2e3b645d` | pdfium: add missing includes (#31007) |
| `6ea1d66ab` | casadi: new recipe (#31023) |
| `01045104c` | armadillo: add version 15.6.2 (#31186) |
| `d88278ef6` | yojimbo: add 1.40.0, migrate the recipe to CMake (#30676) |
| `a46563876` | c-ares: publish version 1.34.9 (#31212) |
| `6acde0f58` | jom: publish version 1.1.7 (#31205) |
| `d41080572` | arrow: publish version 26.0.0 (#31153) |
| `614b3b984` | blend2d: publish version 0.21.2 (#31138) |
| `dfe33814d` | libfido2: add version 1.17.0 (#31184) |
| `b6d5561f8` | speexdsp: publish version 1.2.1 (new recipe) (#29908) |
| `285f4566b` | luajit: use rolling releases from git commits (#31227) |
| `efe4694d3` | fmi2: publish version 2.0.5 (#31216) |
| `187e31c37` | ccache: explicitly disable dev mode (#31230) |
| `b05cd1797` | casadi: bump fmi2 (#31217) |
| `e90cf2034` | sparrow-ipc: publish version 2.0.0 (new recipe) (#29943) |
| `9e97250bf` | zserio: publish version 2.20.0 (#31196) |
| `ea6f80aa8` | brotli: publish versions 1.0.10, 1.1.1, 1.2.1 (#31226) |
| `c033977ab` | ccache: publish version 4.14.2 (#31231) |
| `d0eca47c3` | upa-url: publish version 2.6.0 (#31223) |
| `44537eadd` | freetype: publish version 2.15.0 (#31220) |
| `3a5129af4` | pagmo2: publish v2.20.0 with nlopt 2.11.0 (#31166) |
| `d51690692` | mongo-c-driver: publish version 2.5.7 (#31229) |
| `eb2435fe3` | quill: publish version 13.1.0 (#31245) |
| `915064e52` | add documented inclusion criteria for new recipes (#31236) |
| `f3ef3d8ee` | json-schema-validator: use the namespaced target (#31202) |
| `ea1e5292b` | nanodbc: publish version 2.20.0 (#31233) |
| `e9a98f5f1` | icu: publish version 79.1 (#31248) |
| `19e73cd82` | xtl: publish version 0.8.2 (#31240) |
| `93cbb8698` | strawberryperl: publish version 5.42.3.1 (#31206) |
| `44172b21a` | libdeflate: publish version 1.26 (#31239) |
| `f6ad67048` | abseil: publish version 20260817.0 (#31242) |
| `a9ab99787` | openssl: publish version 4.1.0 (#31258) |
| `bf96544dd` | b2: publish version 5.6.1 (#31259) |
| `e4dca938d` | catch2: publish version 3.16.1 (#31256) |
| `3be9b715f` | qt: publish version 6.11.3 (#31125) |
| `aaf9758ee` | simdutf: publish version 9.3.2 (#31254) |
| `6156963ef` | qt: add version 6.12.0 (#31127) |
| `7c08d4a9c` | libde265: add version 1.1.3 (#30970) |
| `7c8c0581c` | libzip: publish version 1.12.1 (#31253) |
| `013f735ea` | pipewire: publish version 1.6.10 (#31273) |
| `ce4ac45cf` | aws-sdk-cpp: publish version 1.11.915 (#31228) |
| `9fda80103` | libvpx: remove pre-calculated `AutotoolsToolchain.asflags` for Intel platforms (#30946) |
| `4caa1253e` | hwloc: publish version 2.15.0 (#31269) |
| `18b168df4` | nanodbc: publish version 3.0.8 (#31264) |
| `dda75b5dc` | lmdb: add source download mirrors (#31261) |
| `3eca2cf73` | xad: add new recipe (#31249) |
| `bfbb51c08` | stb: add new version (#31214) |
| `254f15ae6` | opentelemetry-cpp: add OPENTELEMETRY_PROTO_API public macro (#31198) |
| `4a55139fb` | bison: Remove compiler settings from package_id (#31199) |
| `7fd57530c` | libusb: publish version 1.0.30 (#30562) |
| `8b4e849b3` | volk: fix WSI entry points for statically linked volk::volk (#31042) |
| `d0da7f4ef` | libcurl/8.23.0: update the cacert store to a newer version that does not contain eMudhra CA certificate (#31282) |
| `d998334b8` | drogon: add version 1.9.14 and with_spdlog option (#31232) |
| `1f3e608c8` | trantor: publish version 1.5.29 (#31235) |
| `9d77f4501` | msys2: update base tarball from 2025-12-13 to 2026-09-27 (#31208) |
| `14225d673` | joltphysics: publish version 5.6.0; stop publishing revisions for older versions (#30778) |
| `cb39c3036` | samarium: delist recipe (#31288) |
| `b9411174b` | zint: publish 2.1.60 version (#30415) |
| `3cf34c5b2` | mariadb-connector-c: publish version 3.4.11 (#31270) |
| `2a2230183` | sqlite3: publish version 3.54.1 (#31290) |
| `dac572736` | tesseract: add support for Android build (#28592) |
| `001305761` | simdjson: publish version 5.1.1 (#31305) |
| `fc19f80a6` | benchmark: publish version 1.10.0 (#31304) |
| `be66c9cfb` | libserialport: publish version 0.1.2 (#30384) |
| `b006d9250` | dcmtk: publish version 3.7.1 (#31266) |
| `cb9913eb3` | imagemagick: Conan 2 recipe support (#30345) |
| `29c7a4ef1` | cmake test_package: don't use python six (#31310) |
| `4b3932066` | ncurses: publish version 6.6 (#31100) |
| `f5d802efe` | net-snmp: publish version 5.9.5.2 (#30416) |
| `3604c4c62` | d3d12-memory-allocator: publish version 3.2.1 (#31019) |
| `ce66e8fa0` | mexce: add 1.2.2 with Apple Silicon and protected expressions (#31145) |
| `4eff30134` | hdf5: publish version 2.2.0 (#29199) |
| `cf080e3cb` | charls: publish version 2.4.5 (#31312) |
| `b7420a039` | multiple recipes: align freetype/fontconfig (#31276) |
| `d5e0ffacc` | expat: publish version 2.10.0 (#31308) |
| `d2d35216d` | libzippp: use version range for libzip (#31284) |
| `43f7c378f` | flatbush: publish version 1.7.0 (#31293) |
| `a158c0952` | rtm: publish version 2.4.0 (#31299) |
| `db8236fe4` | reduct-cpp: publish version 1.21.2 (#31280) |
| `1c0a1ca72` | libmodbus: publish version 3.2.0 (#31274) |
| `7615075d6` | alpaka: publish version 2.2.0 (#31271) |
| `567e4beb7` | glaze: publish version 9.1.0 (#31315) |
| `f7bac7df3` | cppmicroservices/3.8.13: Add initial recipe with minimal build (#31048) |
| `b18edfd70` | sentry-native: publish version 0.16.4 (#30874) |
| `44a0c5f6e` | libxlsxwriter: publish version 1.2.4 (#31268) |
| `3ca3b7283` | nmos-cpp: allow CMake 4 (#31314) |
| `5dfbbeaa7` | mongo-c-driver: publish version 2.5.8 (#31328) |
| `db7b3ffdc` | nanobench: publish version 4.6.0 (#31257) |
| `4098af049` | c-blosc2: publish version 3.4.1 (#31324) |
| `fd96a3719` | libmp3lame: quote CC path for clang-cl in Makefile.MSVC (#29916) |
| `150d5daf8` | json-schema-validator: publish version 2.4.1 (#31275) |
| `d65c021de` | msys2: explicitly install perl as default package (#31350) |
| `6c9f06cb6` | msys2: explicitly install perl as default package (#31350) |
| `79956692d` | harfbuzz: publish version 15.0.0 (#31301) |
| `685051d73` | brotli: use version ranges for dependencies - Part I (#31250) |
| `76d0e5aa8` | brotli: use version ranges for dependencies - Part II (#31251) |
| `7b9b919ba` | arrow: publish version 26.0.1 (#31323) |
| `0d0915892` | nodeeditor: publish version 3.0.16 (#31215) |
| `179568aa4` | rmlui: publish version 6.3 (#31244) |
| `ae8d2ca32` | qt/6.x.x: use version ranges for double-conversion and brotli, and cap md4c below 0.6 (#31303) |
| `ecad1b14f` | xsimd: publish version 14.3.0, bump xtl (#31241) |
| `2e10ced90` | notcurses: publish version 3.0.17 (new recipe) (#31221) |
| `16ab4eec7` | lmdb: publish version 0.9.36, stop publishing revisions for 0.9.32 (#31260) |
| `eff846be0` | botan: publish version 3.14.0 (#31352) |
| `9a17612a1` | tgbot: publish version 1.13.1 (#31321) |
| `7ee868d87` | md4qt: publish version 5.4.0 (#31343) |
| `a394402b1` | md4c: publish 0.5.3 and 0.6.0 (#31302) |
| `fbc5aaa4e` | diligent-core: bump dependencies to keep using maintained versions (#30952) |
| `0201f533d` | qt-advanced-docking-system: publish version 5.1.1 (#31210) |
| `e58da2292` | pulseaudio: use gettext 1.0 when building pulseaudio 14.2 (#31355) |
| `dbfaf1c01` | cmake: update download URLs in conandata.yml (#31338) |
| `a766dcf91` | libsystemd: publish version 262.2 (#30860) |
| `11e673b56` | base64: publish version 0.5.3 (#31356) |
| `72a6b817c` | implot: publish version 1.1 (#31291) |
| `08d9ba53f` | cpp-httplib: publish 0.65.0 (#31364) |
