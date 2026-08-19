import os
import shutil
import sys

# oqs-python looks for the shared library at OQS_INSTALL_PATH/bin/{oqs,liboqs}.dll
# directly - it does NOT check per-config subfolders. A Visual Studio build
# places the dll under bin/Release or bin/Debug instead, so without this fix
# oqs-python silently decides liboqs isn't installed and re-clones + rebuilds
# it from scratch into a temp directory on every run.
_DLL_NAMES = ("oqs.dll", "liboqs.dll")
_CONFIGS = ("Release", "Debug")


def _initialize_liboqs_path():
    crypto_dir = os.path.dirname(os.path.abspath(__file__))
    liboqs_target = os.path.abspath(os.path.join(crypto_dir, "..", "..", "libs", "liboqs"))

    build_target = os.path.join(liboqs_target, "build")
    os.environ["OQS_INSTALL_PATH"] = build_target

    if os.name != "nt" or sys.version_info < (3, 8):
        return

    bin_dir = os.path.join(build_target, "bin")

    if not any(os.path.exists(os.path.join(bin_dir, name)) for name in _DLL_NAMES):
        for config in _CONFIGS:
            config_dir = os.path.join(bin_dir, config)
            found = next(
                (name for name in _DLL_NAMES if os.path.exists(os.path.join(config_dir, name))),
                None,
            )
            if found:
                os.makedirs(bin_dir, exist_ok=True)
                shutil.copy2(os.path.join(config_dir, found), os.path.join(bin_dir, found))
                break

    for candidate in (bin_dir, *(os.path.join(bin_dir, c) for c in _CONFIGS)):
        if os.path.isdir(candidate):
            try:
                os.add_dll_directory(candidate)
            except OSError:
                pass


# Run the initialization the moment the crypto module is imported
_initialize_liboqs_path()
