from conan import ConanFile
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeToolchain, cmake_layout
from conan.tools.files import copy, get
import os

required_conan_version = ">=2.0"


class FastTextConan(ConanFile):
    name = "fasttext"
    description = "Library for efficient learning of word representations and sentence classification"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/facebookresearch/fastText"
    topics = ("machine-learning", "nlp", "word-embeddings", "text-classification")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "build_cli": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "build_cli": False,
    }

    exports_sources = "cmake/*"

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def layout(self):
        cmake_layout(self, src_folder="src")

    def validate(self):
        check_min_cppstd(self, 17)

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["FASTTEXT_BUILD_CLI"] = self.options.build_cli
        tc.generate()

    def build(self):
        # Replace upstream CMakeLists.txt with portable version shipped in the recipe
        copy(self, "CMakeLists.txt",
             src=os.path.join(self.export_sources_folder, "cmake"),
             dst=self.source_folder)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "fasttext")
        self.cpp_info.set_property("cmake_target_name", "fasttext::fasttext")
        self.cpp_info.set_property("pkg_config_name", "fasttext")
        self.cpp_info.libs = ["fasttext"]

        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["pthread", "m"])
