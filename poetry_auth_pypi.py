import configparser
import subprocess
import os

# Path to the .pypirc file
pypirc_path = os.path.expanduser("./.pypirc")

# Read the .pypirc file
config = configparser.ConfigParser()
config.read(pypirc_path)

# Check if the pypi section and credentials are available
if "pypi" in config and "password" in config["pypi"]:
    token = config["pypi"]["password"]

    # Set the token in Poetry
    subprocess.run(["poetry", "config", f"pypi-token.pypi", token], check=True)
    print("Poetry token set successfully from .pypirc.")
else:
    print("PyPI credentials not found in .pypirc")
