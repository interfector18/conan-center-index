from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import apply_conandata_patches, copy, export_conandata_patches, get, rmdir
import os

required_conan_version = ">=2.0"


class CTranslate2Conan(ConanFile):
    name = "ctranslate2"
    description = "Fast inference engine for Transformer models"
    license = "MIT"
    url = "https://github.com/conan-io/conan-center-index"
    homepage = "https://github.com/OpenNMT/CTranslate2"
    topics = ("machine-learning", "inference", "transformer", "nlp", "translation")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "cpu_backend": ["mkl", "dnnl", "openblas", "accelerate", "none"],
        "with_cuda": [True, False],
        "with_cudnn": [True, False],
        "cuda_dynamic_loading": [True, False],
        "with_hip": [True, False],
        "with_tensor_parallel": [True, False],
        "with_flash_attn": [True, False],
        "cpu_dispatch": [True, False],
        "build_cli": [True, False],
    }
    default_options = {
        "shared": True,
        "fPIC": True,
        "cpu_backend": "none",
        "with_cuda": False,
        "with_cudnn": False,
        "cuda_dynamic_loading": False,
        "with_hip": False,
        "with_tensor_parallel": False,
        "with_flash_attn": False,
        "cpu_dispatch": True,
        "build_cli": False,
    }

    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")
        # Force compiled spdlog so spdlog::spdlog target exists
        self.options["spdlog"].header_only = False
        # Thrust must use CUDA device system, not TBB default
        if self.options.with_cuda:
            self.options["thrust"].device_system = "cuda"

    def layout(self):
        cmake_layout(self, src_folder="src")

    def requirements(self):
        # Unbundled from third_party/ (submodules absent in tarball)
        self.requires("spdlog/[>=1.9 <2]")
        if self.settings.compiler in ("clang", "apple-clang"):
            self.requires("llvm-openmp/20.1.6")
        if self.settings.arch in ("x86", "x86_64"):
            self.requires("cpu_features/[>=0.9]")

        # CPU backends
        if self.options.cpu_backend == "openblas":
            self.requires("openblas/[>=0.3]")
        # dnnl/mkl: system deps, not managed by Conan (onednn not in local CCI)
        # accelerate: Apple framework, no package needed

        # CUDA deps (submodules absent in tarball — must come from Conan)
        if self.options.with_cuda:
            self.requires("thrust/[>=1.16]")
            self.requires("cutlass/[>=3.1]")

        # CLI dependency (submodule absent in tarball)
        if self.options.build_cli:
            self.requires("cxxopts/[>=3.0 <4]")

    def build_requirements(self):
        self.tool_requires("cmake/[>=3.18]")

    def validate(self):
        check_min_cppstd(self, 17)

        if self.options.with_cudnn and not self.options.with_cuda:
            raise ConanInvalidConfiguration(
                f"{self.ref}: with_cudnn requires with_cuda=True"
            )
        if self.options.cuda_dynamic_loading and not self.options.with_cuda:
            raise ConanInvalidConfiguration(
                f"{self.ref}: cuda_dynamic_loading requires with_cuda=True"
            )
        if self.options.with_flash_attn and not self.options.with_cuda:
            raise ConanInvalidConfiguration(
                f"{self.ref}: with_flash_attn requires with_cuda=True"
            )
        if self.options.with_cuda and self.options.with_hip:
            raise ConanInvalidConfiguration(
                f"{self.ref}: with_cuda and with_hip are mutually exclusive"
            )
        if self.options.with_tensor_parallel and not self.options.with_cuda:
            raise ConanInvalidConfiguration(
                f"{self.ref}: with_tensor_parallel requires with_cuda=True"
            )
        if self.options.with_tensor_parallel and self.options.with_hip:
            raise ConanInvalidConfiguration(
                f"{self.ref}: with_tensor_parallel is incompatible with with_hip=True"
            )
        if self.options.cpu_backend == "accelerate" and self.settings.os != "Macos":
            raise ConanInvalidConfiguration(
                f"{self.ref}: cpu_backend=accelerate requires macOS"
            )

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        deps = CMakeDeps(self)
        deps.generate()

        tc = CMakeToolchain(self)
        # CPU backends
        tc.variables["WITH_MKL"] = self.options.cpu_backend == "mkl"
        tc.variables["WITH_DNNL"] = self.options.cpu_backend == "dnnl"
        tc.variables["WITH_OPENBLAS"] = self.options.cpu_backend == "openblas"
        tc.variables["WITH_RUY"] = False  # ruy submodule not in tarball, no CCI package
        tc.variables["WITH_ACCELERATE"] = self.options.cpu_backend == "accelerate"
        # GPU
        tc.variables["WITH_CUDA"] = self.options.with_cuda
        tc.variables["WITH_CUDNN"] = self.options.with_cudnn
        tc.variables["CUDA_DYNAMIC_LOADING"] = self.options.cuda_dynamic_loading
        tc.variables["WITH_HIP"] = self.options.with_hip
        tc.variables["WITH_TENSOR_PARALLEL"] = self.options.with_tensor_parallel
        tc.variables["WITH_FLASH_ATTN"] = self.options.with_flash_attn
        # OpenMP runtime — use compiler default to avoid Intel libiomp5 dependency
        tc.variables["OPENMP_RUNTIME"] = "COMP"
        # Other
        tc.variables["ENABLE_CPU_DISPATCH"] = self.options.cpu_dispatch
        tc.variables["BUILD_CLI"] = self.options.build_cli
        tc.variables["BUILD_TESTS"] = False
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE",
             src=self.source_folder,
             dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()
        rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "ctranslate2")
        self.cpp_info.set_property("cmake_target_name", "CTranslate2::ctranslate2")
        self.cpp_info.set_property("pkg_config_name", "ctranslate2")
        self.cpp_info.libs = ["ctranslate2"]

        # System libs
        if self.settings.os in ("Linux", "FreeBSD"):
            self.cpp_info.system_libs.extend(["pthread", "dl"])

        # CUDA libs — conditional on dynamic loading
        if self.options.with_cuda:
            cuda_path = os.environ.get("CUDA_PATH", os.environ.get("CUDA_HOME", "/opt/cuda"))
            cuda_libdir = os.path.join(cuda_path, "lib64")
            if os.path.isdir(cuda_libdir):
                self.cpp_info.libdirs.append(cuda_libdir)
            if not self.options.cuda_dynamic_loading:
                self.cpp_info.system_libs.extend(["cudart", "cublas", "cublasLt"])
            else:
                self.cpp_info.system_libs.append("cudart")

        if self.options.with_cudnn:
            self.cpp_info.system_libs.append("cudnn")

        # HIP libs
        if self.options.with_hip:
            self.cpp_info.system_libs.extend(["hiprand", "hipblas"])

        # Apple frameworks
        if self.options.cpu_backend == "accelerate":
            self.cpp_info.frameworks.append("Accelerate")

        # MKL system libs (ILP64 mode, COMP OpenMP runtime on Linux)
        if self.options.cpu_backend == "mkl":
            mkl_root = os.environ.get("MKLROOT", "/opt/intel/mkl")
            mkl_libdir = os.path.join(mkl_root, "lib", "intel64")
            if os.path.isdir(mkl_libdir):
                self.cpp_info.libdirs.append(mkl_libdir)
            self.cpp_info.system_libs.extend([
                "mkl_intel_ilp64", "mkl_gnu_thread", "mkl_core",
            ])
