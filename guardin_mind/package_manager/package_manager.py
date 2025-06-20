from colorama import Fore, Style, init
import io
import requests
import zipfile
import platform
import re
import sys
import importlib.util
from guardin_mind import PythonVersionError, MindVersionError
import os
from pathlib import Path
import subprocess
import shutil
import tomllib
from pydantic import validate_arguments
from packaging.specifiers import SpecifierSet

def init_install_uninstall(author_minder: str, default_install_path: str | None) -> tuple[str, str, str]:
    """
    Init package manager. Install and uninstall modes.
    """

    init() # Initialize colorama for colored terminal output
    
    os_name: str = platform.system()  # Get the operating system name

    """
    Accepts a string in the `author_MinderName` format and returns a tuple: (author, minder)
    """

    # Parse only the author and minder from the author_minder string
    match = re.search(r'[A-Z][a-zA-Z]*$', author_minder)

    if match:
        minder: str = match.group()  # Extract minder name
        author: str = author_minder[:match.start()].rstrip('_')  # Extract author name
    else:
        print(Fore.WHITE + f"Collecting {author_minder}" + Style.RESET_ALL)
        print(Fore.RED + "    ERROR: Incorrect format. Use the format \"mind install <author_MinderName>\"" + Style.RESET_ALL)
        raise ValueError("Incorrect format. Use the format \"mind install <author_MinderName>\"")

    # Determine install path
    if default_install_path:
        install_path = default_install_path
    else:
        if os_name == "Windows":
            # Get the USERPROFILE environment variable and build default path
            user_profile = os.environ.get("USERPROFILE", "")
            install_path = os.path.join(user_profile, ".guardin_mind", "minders")
        else:
            # Expand '~' to the home directory on Linux/macOS
            install_path = os.path.expanduser("~/.guardin_mind/minders")

    return author, minder, install_path

def check_minder_installed(install_path: str, minder_name: str) -> bool:
    """
    Checks if the minder is already installed
    """
    path = Path(install_path) / minder_name
    return path.is_dir()

@validate_arguments
def install_minder(author_minder: str, minders_install_path: str | None) -> bool | None:
    """
    Accepts arguments for installing the minder, and installs it
    """
        
    # Init
    author, minder, install_path = init_install_uninstall(author_minder, minders_install_path)
    
    # Check if the minder is already installed
    if check_minder_installed(install_path, minder):
        print(Fore.LIGHTGREEN_EX + f"Requirement already satisfied: {author_minder} in {install_path}" + Style.RESET_ALL)
        return True

    def download_repo_zip(user_repo, destination_folder):
        """
        Downloads the GitHub repository as a zip and extracts it into the destination folder
        """
        zip_url = f"https://github.com/{user_repo}/archive/refs/heads/main.zip"

        print(Fore.WHITE + f"    Downloading {author_minder}" + Style.RESET_ALL)
        response = requests.get(zip_url)

        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Temporary folder for extraction
                temp_extract_path = Path(destination_folder) / "__temp_extract"
                temp_extract_path.mkdir(parents=True, exist_ok=True)

                z.extractall(temp_extract_path)

                # Expecting a single top-level folder inside the archive (e.g., HelloWorld-main)
                extracted_dirs = [d for d in temp_extract_path.iterdir() if d.is_dir()]
                if len(extracted_dirs) != 1:
                    print(Fore.RED + "    ERROR: Unexpected archive structure" + Style.RESET_ALL)
                    return

                extracted_dir = extracted_dirs[0]
                final_path = Path(destination_folder) / minder

                # If target directory already exists, delete it
                if final_path.exists():
                    shutil.rmtree(final_path)

                # Move extracted content to the final directory
                extracted_dir.rename(final_path)

                # Delete temporary folder
                shutil.rmtree(temp_extract_path)

        else:
            print(Fore.RED + f"    ERROR: Error when downloading the minder from GitHub. Error code: {response.status_code} for {zip_url}" + Style.RESET_ALL)

    print(Fore.WHITE + f"Collecting {author_minder}" + Style.RESET_ALL)
    download_repo_zip(f"{author}/{minder}", install_path)  # Download minder from GitHub to minders folder

    minder_folder_path = f"{install_path}/{minder}"

    # Open and parse the TOML config file inside the minder directory
    with open(f"{minder_folder_path}/minder_config.toml", "rb") as f:
        config = tomllib.load(f)

    try:
        # Check for required parameters in config
        name = config["minder"]["name"]
        version = config["minder"]["version"]

        # Clean up variables
        del name
        del version
    except KeyError as e:
        print(Fore.RED + f"    ERROR: Minder '{author_minder}' requires a {e} field in minder_config.toml")
        raise ValueError(f"ERROR: Minder '{author_minder}' requires a {e} field in minder_config.toml")

    # Check for required Python version
    try:
        condition = config["minder"]["python"]
        current_version = ".".join(map(str, sys.version_info[:3]))  # Get current Python version

        spec = SpecifierSet(condition)

        if not current_version in spec:
            print(Fore.RED + f"    ERROR: Minder '{author_minder}' requires a different Python: {current_version} not in '{condition}'" + Style.RESET_ALL)
            raise PythonVersionError(f"ERROR: Minder '{author_minder}' requires a different Python: {current_version} not in '{condition}'")
        
        del condition
        del current_version
    except KeyError:
        # No Python version requirement specified
        pass

    # Check for required Mind version
    try:
        condition = config["minder"]["mind"]
        from guardin_mind import __version__ as current_version  # Get installed Mind version

        spec = SpecifierSet(condition)

        if not current_version in spec:
            print(Fore.RED + f"    ERROR: Minder '{author_minder}' requires a different Mind: {current_version} not in '{condition}'" + Style.RESET_ALL)
            raise MindVersionError(f"ERROR: Minder '{author_minder}' requires a different Mind: {current_version} not in '{condition}'")
        
        del condition
        del current_version
    except KeyError:
        # No Mind version requirement specified
        pass

    # Install Python package dependencies listed in the config
    try:
        dependencies = config["minder"]["install-requires"]

        for lib in dependencies:
            spec = importlib.util.find_spec(lib)
            if spec is None:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                spec = importlib.util.find_spec(lib)  # Update spec after installation
                continue

            # Show where the package is already installed
            if spec is not None and spec.origin is not None:
                if spec.origin.endswith('__init__.py'):
                    lib_path = os.path.abspath(os.path.dirname(spec.origin))
                else:
                    lib_path = os.path.abspath(spec.origin)
                print(Fore.LIGHTGREEN_EX + f"Requirement already satisfied: {lib} in {lib_path}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"Requirement already satisfied: {lib}" + Style.RESET_ALL)
    except KeyError:
        # No Python dependencies specified
        pass

    # Install required minders listed in the config
    try:
        dependencies = config["minder"]["requires-minders"]  # Read required minders

        for lib in dependencies:
            if not check_minder_installed(install_path, lib):  # Check if the minder is already installed
                install_minder(lib, install_path)  # Recursively install the required minder
            else:
                print(Fore.LIGHTGREEN_EX + f"Requirement already satisfied: {lib} in {install_path}" + Style.RESET_ALL)
    except KeyError:
        # No dependent minders specified
        pass

    print(Fore.LIGHTGREEN_EX + f"Successfully installed {author_minder}" + Style.RESET_ALL)

    return True

@validate_arguments
def uninstall_minder(author_minder: str, minders_install_path: str | None, confirm: bool = False) -> bool | None:
    """
    Accepts arguments for uninstalling the minder, and uninstalls it
    """

    # Init
    author, minder, install_path = init_install_uninstall(author_minder, minders_install_path)

    # Check minder installed
    if not check_minder_installed(install_path, minder):
        print(Fore.LIGHTYELLOW_EX + f"WARNING: Skipping {author_minder} as it is not installed in {install_path}" + Style.RESET_ALL)
        return True
    
    print(Fore.WHITE + f"Uninstalling {author_minder}" + Style.RESET_ALL)

    if not confirm:
        is_confirm = input(Fore.WHITE + "Proceed (Y/n)? " + Style.RESET_ALL)
        if is_confirm.lower() == "n":
            return True
    
    folder_path = Path(install_path) / minder # Build minder install path

    # # Check if the folder exists and is indeed a directory
    if folder_path.exists() and folder_path.is_dir():
        shutil.rmtree(folder_path)
        print(Fore.LIGHTGREEN_EX + f"    Successfully uninstalled {author_minder}" + Style.RESET_ALL)
    else:
        print(Fore.RED + f"    ERROR: Minder {author_minder} not found in {install_path}." + Style.RESET_ALL)
        raise FileNotFoundError(f"ERROR: Minder {author_minder} not found in {install_path}.")