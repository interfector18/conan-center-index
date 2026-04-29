from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get, rmdir
import os

required_conan_version = ">=2.0"


class SentencePieceConan(ConanFile):
    name = "sentencepiece"
    description = "Unsupervised text tokenizer for neural network-based text generation"
    license = "Apache-2.0"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/google/sentencepiece"
    topics = ("nlp", "tokenizer", "bpe", "unigram", "text-processing")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_nfkc_compile": [True, False],
        "with_tcmalloc": [True, False],
        "tcmalloc_static": [True, False],
        "build_tools": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_nfkc_compile": False,
        "with_tcmalloc": False,
        "tcmalloc_static": False,
        "build_tools": False,
    }

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        if self.options.with_nfkc_compile:
            self.requires("icu/[>=74.2]")

    def validate(self):
        check_min_cppstd(self, 17)
        if self.settings.os == "Windows" and self.options.shared:
            raise ConanInvalidConfiguration(
                f"{self.ref}: shared build is not supported on Windows"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        tc.variables["SPM_ENABLE_SHARED"] = self.options.shared
        tc.variables["SPM_ENABLE_NFKC_COMPILE"] = self.options.with_nfkc_compile
        tc.variables["SPM_ENABLE_TCMALLOC"] = self.options.with_tcmalloc
        tc.variables["SPM_TCMALLOC_STATIC"] = self.options.tcmalloc_static
        tc.variables["SPM_BUILD_TEST"] = False
        # Use bundled protobuf-lite and absl (no CCI packages for those variants)
        tc.variables["SPM_PROTOBUF_PROVIDER"] = "internal"
        tc.variables["SPM_ABSL_PROVIDER"] = "internal"
        tc.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "share"))
        if not self.options.build_tools:
            # Strip CLI tools when not requested
            bindir = os.path.join(self.package_folder, "bin")
            if os.path.isdir(bindir):
                rmdir(self, bindir)

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "sentencepiece")
        self.cpp_info.set_property("pkg_config_name", "sentencepiece")

        # Main processor library
        self.cpp_info.components["sentencepiece_"].set_property(
            "cmake_target_name", "sentencepiece::sentencepiece")
        self.cpp_info.components["sentencepiece_"].libs = ["sentencepiece"]

        # Training library
        self.cpp_info.components["train"].set_property(
            "cmake_target_name", "sentencepiece::sentencepiece_train")
        self.cpp_info.components["train"].libs = ["sentencepiece_train"]
        self.cpp_info.components["train"].requires = ["sentencepiece_"]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.components["sentencepiece_"].system_libs.extend(
                ["pthread", "m"])

        if self.options.with_nfkc_compile:
            self.cpp_info.components["sentencepiece_"].requires.extend(
                ["icu::icu-i18n", "icu::icu-data", "icu::icu-uc"])
