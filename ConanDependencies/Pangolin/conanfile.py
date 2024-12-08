from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.build import check_min_cppstd
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
from conan.tools.files import (
    apply_conandata_patches,
    collect_libs,
    copy,
    export_conandata_patches,
    get,
    rename,
    rm,
    rmdir,
    save,
)
from conan.tools.microsoft import check_min_vs, is_msvc_static_runtime, is_msvc, msvc_runtime_flag
from conan.tools.scm import Version
import os
import textwrap

required_conan_version = ">=2.0.6"
class PangolinBuilder(ConanFile):
    name = "pangolin"
    version = "0.9.2"
    license = "Apache-2.0"
    homepage = "https://fast-dds.docs.eprosima.com/"
    url = "https://github.com/conan-io/conan-center-index"
    description = "The most complete OSS DDS implementation for embedded systems."
    topics = ("dds", "middleware", "ipc")
    package_type = "library"
    settings = "os", "arch", "compiler", "build_type"

    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "BUILD_TOOLS": [True, False],
        "BUILD_EXAMPLES": [True, False],
        "BUILD_TESTS": [True, False]
    }

    default_options = {
        "shared": False,
        "fPIC": True,
        "BUILD_TOOLS": True,
        "BUILD_EXAMPLES": False,
        "BUILD_TESTS": False
    }
    def export_sources(self):
        export_conandata_patches(self)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC
            
    def layout(self):
        cmake_layout(self, src_folder="src")
            
    def requirements(self):
        self.requires("eigen/3.4.0")
        self.requires("glew/2.2.0")
        # TODO: Handle test dependencies required for BUILD_TESTS
            
    def configure(self):
        if self.options.shared:
            self.options.rm_safe("fPIC")

    def source(self):
        get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.variables["BUILD_TOOLS"] = self.options.BUILD_TOOLS
        tc.variables["BUILD_EXAMPLES"] = self.options.BUILD_EXAMPLES
        tc.variables["BUILD_TESTS"] = self.options.BUILD_TESTS
        tc.generate()
        tc = CMakeDeps(self)
        tc.check_components_exist = True
        tc.generate()

    def build(self):
        apply_conandata_patches(self)
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        copy(self, "LICENSE.txt", src=self.source_folder,
                                  dst=os.path.join(self.package_folder, "licenses"))
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info = collect_libs(self)
