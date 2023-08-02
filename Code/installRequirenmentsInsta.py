import importlib, sys

# List of required modules
required_modules = [
    'instaloader',
    'webbrowser',
    'requests'
]

# Function to install missing modules
def install_module(module_name):
    try:
        importlib.import_module(module_name)
    except ImportError:
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

# Check and install missing modules
for module in required_modules:
    install_module(module)