import os
import sys

def _initialize_liboqs_path():
    # 1. Map the path out to libs/liboqs
    crypto_dir = os.path.dirname(os.path.abspath(__file__))
    liboqs_target = os.path.abspath(os.path.join(crypto_dir, '..', '..', 'libs', 'liboqs'))
    
    # 2. Set the environment variable for the wrapper
    # We point this to the 'build' folder because that is where your 'bin' folder lives
    build_target = os.path.join(liboqs_target, 'build')
    os.environ["OQS_INSTALL_PATH"] = build_target
    print(f"--- DEBUG: Routing liboqs to {build_target} ---")
    
    # 3. THE WINDOWS FIX: Whitelist the exact folder containing the .dll
    if os.name == 'nt' and sys.version_info >= (3, 8):
        # Using the exact path you provided: libs/liboqs/build/bin/Debug
        exact_dll_path = os.path.join(build_target, 'bin', 'Debug')
        
        try:
            if os.path.exists(exact_dll_path):
                os.add_dll_directory(exact_dll_path)
                print(f"--- DEBUG: Whitelisted DLL path: {exact_dll_path} ---")
            else:
                print(f"--- DEBUG WARNING: Could not find exact DLL path: {exact_dll_path} ---")
                
        except Exception as e:
            print(f"DEBUG: Failed to add DLL directory: {e}")

# Run the initialization the moment the crypto module is imported
_initialize_liboqs_path()