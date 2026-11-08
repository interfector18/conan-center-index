import os

from conan import ConanFile
from conan.tools.build import build_jobs, check_min_cppstd
from conan.tools.files import chdir, copy, get, rmdir, save, load
from conan.tools.gnu import Autotools, AutotoolsToolchain, AutotoolsDeps
from conan.tools.scm import Version
from conan.errors import ConanInvalidConfiguration

import json

required_conan_version = ">=2"

class CMakeConan(ConanFile):
    name = "cmake"
    package_type = "application"
    description = "CMake, the cross-platform, open-source build system."
    topics = ("build", "installer")
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/Kitware/CMake"
    license = "BSD-3-Clause"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "with_openssl": [True, False],
    }
    default_options = {
        "with_openssl": True,
    }

    @property
    def _is_binary_available(self):
        os_name = str(self.settings.os)
        arch = str(self.settings.arch) if os_name != "Macos" else "universal"
        try:
            self.conan_data["sources"][self.version][os_name][arch]
            return True
        except KeyError:
            return False

    def config_options(self):
        if self._is_binary_available:
            del self.options.with_openssl
        elif self.settings.os == "Windows":
            self.options.with_openssl = False

    def requirements(self):
        if not self._is_binary_available:
            self.requires("zlib/[>=1.2.11 <2]")
            if self.options.get_safe("with_openssl", default=False):
                self.requires("openssl/[>=1.1 <4]")

    def validate(self):
        if self._is_binary_available:
            if self.settings.arch not in ["x86_64", "armv8"]:
                raise ConanInvalidConfiguration(
                    "CMake binaries are only provided for x86_64 and armv8 architectures. "
                    "Consider using the system cmake with [platform_tool_requires] section in your profile.")
            if self.settings.os == "Windows" and self.settings.arch == "armv8" and Version(self.version) < "3.24":
                raise ConanInvalidConfiguration("CMake only supports ARM64 binaries on Windows starting from 3.24")
        else:
            minimal_cpp_standard = "11"
            if self.settings.get_safe("compiler.cppstd"):
                check_min_cppstd(self, minimal_cpp_standard)

    def generate(self):
        if self.settings.os == "FreeBSD" and not self.conf.get("tools.gnu:make_program"):
            self.conf.define("tools.gnu:make_program", "gmake")
        if self._is_binary_available:
            return
        tc = AutotoolsToolchain(self)
        tc.generate()
        tc = AutotoolsDeps(self)
        tc.generate()
        bootstrap_cmake_options = ["--"]
        cppstd = str(self.settings.get_safe("compiler.cppstd") or "11")
        if cppstd.startswith("gnu"):
            cppstd = cppstd[3:]
        bootstrap_cmake_options.append(f"-DCMAKE_CXX_STANDARD={cppstd}")
        bootstrap_cmake_options.append("-DCMAKE_USE_SYSTEM_ZLIB=ON")
        if self.options.get_safe("with_openssl", default=False):
            openssl = self.dependencies["openssl"]
            bootstrap_cmake_options.append("-DCMAKE_USE_OPENSSL=ON")
            bootstrap_cmake_options.append(f'-DOPENSSL_USE_STATIC_LIBS={"FALSE" if openssl.options.shared else "TRUE"}')
            bootstrap_cmake_options.append(f"-DOPENSSL_ROOT_DIR={openssl.package_path}")
        else:
            bootstrap_cmake_options.append("-DCMAKE_USE_OPENSSL=OFF")
        save(self, "bootstrap_args", json.dumps({"options": " ".join(bootstrap_cmake_options)}))

    @property
    def _unzipped_folder(self):
        return os.path.join(self.build_folder, "unzipped")
        
    def build(self):
        if self._is_binary_available:
            arch = str(self.settings.arch) if self.settings.os != "Macos" else "universal"
            get(self, **self.conan_data["sources"][self.version][str(self.settings.os)][arch],
                destination=self._unzipped_folder, strip_root=True)
        else:
            get(self, **self.conan_data["sources"][self.version]["source"],
                destination=self.source_folder, strip_root=True)
            bootstrap_args = json.loads(load(self, os.path.join(self.generators_folder, "bootstrap_args")))
            with chdir(self, self.source_folder):
                self.run(f'./bootstrap --prefix="" --parallel={build_jobs(self)} {bootstrap_args["options"]}')
                autotools = Autotools(self)
                autotools.make()

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type
        if self.info.settings.os == "Macos":
            del self.info.settings.arch

    def package(self):
        if self._is_binary_available:
            copy(self, "*", src=self._unzipped_folder, dst=self.package_folder)

            if self.settings.os == "Macos":
                docs_folder = os.path.join(self._unzipped_folder, "CMake.app", "Contents", "doc", "cmake")
            else:
                docs_folder = os.path.join(self._unzipped_folder, "doc", "cmake")

            licensefile = "LICENSE.rst" if Version(self.version) >= "4.0.0" else "Copyright.txt"
            copy(self, licensefile, src=docs_folder, dst=os.path.join(self.package_folder, "licenses"), keep_path=False)

            if self.settings.os != "Macos":
                rmdir(self, os.path.join(self.package_folder, "doc"))
                rmdir(self, os.path.join(self.package_folder, "man"))
        else:
            licensefile = "LICENSE.rst" if Version(self.version) >= "4.0.0" else "Copyright.txt"
            copy(self, licensefile, self.source_folder, os.path.join(self.package_folder, "licenses"), keep_path=False)
            with chdir(self, self.source_folder):
                autotools = Autotools(self)
                autotools.install()
            rmdir(self, os.path.join(self.package_folder, "doc"))
            rmdir(self, os.path.join(self.package_folder, "man"))

    def package_info(self):
        self.cpp_info.includedirs = []
        self.cpp_info.libdirs = []

        if self.settings.os == "Macos" and self._is_binary_available:
            bindir = os.path.join(self.package_folder, "CMake.app", "Contents", "bin")
            self.cpp_info.bindirs = [bindir]
