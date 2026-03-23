"""
Minimal setup.py for native library compilation.

All package metadata lives in pyproject.toml. This file only exists to provide
a custom build_ext command that compiles libsocketify via the native Makefile.
"""

import os
import platform
import subprocess
import sys

from setuptools import Distribution, Extension, setup
from setuptools.command.build_ext import build_ext as _build_ext

NATIVE_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "src", "socketify", "native"
)
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "src", "socketify")


def _detect_target():
    """Return (make_target, env_overrides) for the current platform."""
    system = platform.system().lower()
    machine = platform.machine().lower()
    is_arm = machine in ("aarch64", "arm64")

    if system == "linux":
        env = {"PLATFORM": "arm64"} if is_arm else {}
        return "linux", env
    elif system == "darwin":
        return ("macos-arm64" if is_arm else "macos"), {}
    elif system == "windows":
        return "windows", {}
    else:
        raise RuntimeError(f"Unsupported platform: {system}")


class build_ext(_build_ext):
    """Custom build_ext that compiles libsocketify via make."""

    def run(self):
        target, env_overrides = _detect_target()

        if target == "windows":
            self._build_windows()
        else:
            env = os.environ.copy()
            env.update(env_overrides)
            subprocess.check_call(["make", target], cwd=NATIVE_DIR, env=env)

    def _build_windows(self):
        """Windows build using cl.exe directly (mirrors windows.yml workflow)."""
        socketify_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "src", "socketify"
        )

        boringssl_dir = os.path.join(
            socketify_dir, "uWebSockets", "uSockets", "boringssl"
        )
        boringssl_build = os.path.join(boringssl_dir, "amd64")

        # Find libuv from vcpkg — search multiple known locations
        from pathlib import Path

        libuv_include = None
        libuv_lib = None
        vcpkg_roots = [
            os.environ.get("VCPKG_ROOT", ""),
            r"C:\vcpkg",
            os.environ.get("VCPKG_INSTALLATION_ROOT", ""),
        ]
        subdirs = [
            Path("installed", "x64-windows-static-md"),
            Path("packages", "libuv_x64-windows-static-md"),
        ]
        for root in vcpkg_roots:
            if not root:
                continue
            for subdir in subdirs:
                base = Path(root) / subdir
                inc = base / "include" / "uv.h"
                # vcpkg names it libuv.lib (static-md) or uv_a.lib depending on triplet
                lib = base / "lib" / "libuv.lib"
                if not lib.is_file():
                    lib = base / "lib" / "uv_a.lib"
                if inc.is_file():
                    libuv_include = str(base / "include")
                if lib.is_file():
                    libuv_lib = str(lib)
                if libuv_include and libuv_lib:
                    break
            if libuv_include and libuv_lib:
                break

        if not libuv_include or not libuv_lib:
            raise RuntimeError(
                f"Could not find libuv headers/lib. "
                f"VCPKG_ROOT={os.environ.get('VCPKG_ROOT', 'unset')}, "
                f"VCPKG_INSTALLATION_ROOT={os.environ.get('VCPKG_INSTALLATION_ROOT', 'unset')}"
            )

        # Build boringssl if not already built
        if not os.path.isdir(boringssl_build):
            os.makedirs(boringssl_build, exist_ok=True)
            subprocess.check_call(
                ["cmake", "-DCMAKE_BUILD_TYPE=Release", "-GNinja", ".."],
                cwd=boringssl_build,
            )
            subprocess.check_call(["ninja", "crypto", "ssl"], cwd=boringssl_build)

        # Build libsocketify
        cl_args = [
            "cl",
            "/MD", "/W3", "/D", "/EHsc", "/Zc:__cplusplus", "/Ox",
            "/DLL", "/D_WINDLL", "/LD",
            "/D", "NOMINMAX",
            "/D", "WIN32_LEAN_AND_MEAN",
            "/D", "UWS_NO_ZLIB",
            "/D", "UWS_WITH_PROXY",
            "/D", "LIBUS_USE_LIBUV",
            "/D", "LIBUS_USE_OPENSSL",
            "/std:c++20",
            f"/I{os.path.join(socketify_dir, 'native', 'src')}",
            f"/I{os.path.join(socketify_dir, 'uWebSockets', 'src')}",
            f"/I{os.path.join(socketify_dir, 'uWebSockets', 'capi')}",
            f"/I{os.path.join(socketify_dir, 'uWebSockets', 'uSockets', 'boringssl', 'include')}",
            f"/I{os.path.join(socketify_dir, 'uWebSockets', 'uSockets', 'src')}",
            f"/I{libuv_include}",
            f"/Fe{os.path.join(socketify_dir, 'libsocketify_windows_amd64.dll')}",
            os.path.join(socketify_dir, "native", "src", "libsocketify.cpp"),
            *_glob_sources(os.path.join(socketify_dir, "uWebSockets", "uSockets", "src"), "*.c"),
            *_glob_sources(os.path.join(socketify_dir, "uWebSockets", "uSockets", "src", "crypto"), "*.cpp"),
            *_glob_sources(os.path.join(socketify_dir, "uWebSockets", "uSockets", "src", "eventing"), "*.c"),
            *_glob_sources(os.path.join(socketify_dir, "uWebSockets", "uSockets", "src", "crypto"), "*.c"),
            "advapi32.lib",
            os.path.join(boringssl_build, "ssl", "ssl.lib"),
            os.path.join(boringssl_build, "crypto", "crypto.lib"),
            libuv_lib,
            "iphlpapi.lib", "userenv.lib", "psapi.lib",
            "user32.lib", "shell32.lib", "dbghelp.lib",
            "ole32.lib", "uuid.lib", "ws2_32.lib",
        ]
        subprocess.check_call(cl_args, cwd=socketify_dir)


def _glob_sources(directory, pattern):
    """Return list of files matching a glob pattern in a directory."""
    import glob
    return glob.glob(os.path.join(directory, pattern))


class BinaryDistribution(Distribution):
    """Force platform-specific wheel even though we don't use distutils extensions."""

    def has_ext_modules(self):
        return True


setup(
    ext_modules=[Extension("socketify._native_marker", sources=[])],
    cmdclass={"build_ext": build_ext},
    distclass=BinaryDistribution,
)
