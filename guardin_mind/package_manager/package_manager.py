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

@validate_arguments
def install_minder(author_minder: str, minders_install_path: str | None):
    """
    Accepts arguments for installing the minder, and installs it
    """

    init()  # Init colorama

    os_name: str = platform.system()  # Get OS

    def parse_author_minder(author_and_minder: str):
        """
        Gets a string in the `author_MinderName` format and returns a split string in the tuple: (author, minder)
        """

        # Parse from author_minder only author and minder
        match = re.search(r'[A-Z][a-zA-Z]*$', author_and_minder)

        if match:
            minder: str = match.group() # Parse minder name
            author: str = author_and_minder[:match.start()].rstrip('_') # Parse author
        else:
            print(Fore.WHITE + f"Collecting {author_minder}" + Style.RESET_ALL)
            print(Fore.RED + "    ERROR: Incorrect format. Use the format \"mind install <author_MinderName>\"" + Style.RESET_ALL)
            raise ValueError("Incorrect format. Use the format \"mind install <author_MinderName>\"")
            
        return author, minder
        
    author, minder = parse_author_minder(author_minder)

    # Get install path
    if minders_install_path:
        install_path = minders_install_path
    else:
        if os_name == "Windows":
            # Get inviron USERPROFILE and build path
            user_profile = os.environ.get("USERPROFILE", "")
            install_path = os.path.join(user_profile, ".guardin_mind", "minders")
        else:
            # For Linux/macOS expanding ~ to home folder
            install_path = os.path.expanduser("~/.guardin_mind/minders")

    def check_minder_installed(parent_folder, folder_name):
        """
        Checking that the miner is not installed yet
        """
        path = Path(parent_folder) / folder_name
        return path.is_dir()
    
    # Checking if the minder is installed
    if check_minder_installed(install_path, minder):
        print(Fore.GREEN + f"Requirement already satisfied: {author_minder} in {install_path}" + Style.RESET_ALL)
        return True

    def download_repo_zip(user_repo, destination_folder):
        zip_url = f"https://github.com/{user_repo}/archive/refs/heads/main.zip"

        print(Fore.WHITE + f"    Downloading {author_minder}" + Style.RESET_ALL)
        response = requests.get(zip_url)

        if response.status_code == 200:
            with zipfile.ZipFile(io.BytesIO(response.content)) as z:
                # Временная папка для распаковки
                temp_extract_path = Path(destination_folder) / "__temp_extract"
                temp_extract_path.mkdir(parents=True, exist_ok=True)

                z.extractall(temp_extract_path)

                # Внутри temp_extract_path будет одна папка с именем repo-branch, например HelloWorld-main
                extracted_dirs = [d for d in temp_extract_path.iterdir() if d.is_dir()]
                if len(extracted_dirs) != 1:
                    print(Fore.RED + "    ERROR: Unexpected archive structure" + Style.RESET_ALL)
                    return

                extracted_dir = extracted_dirs[0]
                final_path = Path(destination_folder) / minder

                # Если итоговая папка уже есть, удалить её (или можно спросить пользователя)
                if final_path.exists():
                    shutil.rmtree(final_path)

                # Переместить содержимое из распакованной папки в итоговую
                extracted_dir.rename(final_path)

                # Удалить временную папку
                shutil.rmtree(temp_extract_path)

        else:
            print(Fore.RED + f"    ERROR: Error when downloading the minder from github. Error code: {response.status_code} for {zip_url}" + Style.RESET_ALL)

    print(Fore.WHITE + f"Collecting {author_minder}" + Style.RESET_ALL)
    download_repo_zip(f"{author}/{minder}", install_path) # Download minder from github to minders folder

    minder_folder_path = f"{install_path}/{minder}"

    # Open and parse the TOML config file inside the minder directory
    with open(f"{minder_folder_path}/minder_config.toml", "rb") as f:
        config = tomllib.load(f)

    try:
        # Checking for required parameters
        name = config["minder"]["name"]
        version = config["minder"]["version"]

        del name
        del version
    except KeyError as e:
        print(Fore.RED + f"    ERROR: Minder '{author_minder}' requires a {e} field in minder_config.toml")
        raise ValueError(f"ERROR: Minder '{author_minder}' requires a {e} field in minder_config.toml")

    # Check Python version
    try:
        condition = config["minder"]["python"]
        current_version = ".".join(map(str, sys.version_info[:3])) # Get current Python version

        spec = SpecifierSet(condition)

        if not current_version in spec:
            print(Fore.RED + f"    ERROR: Minder '{author_minder}' requires a different Python: {current_version} not in '{condition}'" + Style.RESET_ALL)
            raise PythonVersionError(f"ERROR: Minder '{author_minder}' requires a different Python: {current_version} not in '{condition}'")
        
        del condition
        del current_version
    except KeyError:
        pass

    # Check Mind version
    try:
        condition = config["minder"]["mind"]
        from guardin_mind import __version__ as current_version # get Mind version

        spec = SpecifierSet(condition)

        if not current_version in spec:
            print(Fore.RED + f"    ERROR: Minder '{author_minder}' requires a different Mind: {current_version} not in '{condition}'" + Style.RESET_ALL)
            raise MindVersionError(f"ERROR: Minder '{author_minder}' requires a different Mind: {current_version} not in '{condition}'")
        
        del condition
        del current_version
    except KeyError:
        pass

    # Installing minder dependencies

    # Installing Python packages
    try:
        dependencies = config["minder"]["install-requires"]

        for lib in dependencies:
            spec = importlib.util.find_spec(lib)
            if spec is None:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                spec = importlib.util.find_spec(lib)  # update spec before install

                continue

            if spec is not None and spec.origin is not None:
                if spec.origin.endswith('__init__.py'):
                    lib_path = os.path.abspath(os.path.dirname(spec.origin))
                else:
                    lib_path = os.path.abspath(spec.origin)
                print(Fore.GREEN + f"Requirement already satisfied: {lib} in {lib_path}" + Style.RESET_ALL)
            else:
                print(Fore.YELLOW + f"Requirement already satisfied: {lib}" + Style.RESET_ALL)
    except KeyError:
        pass

    # Installing Mind minders
    try:
        dependencies = config["minder"]["requires-minders"] # Read the requires of minder

        for lib in dependencies:
            if not check_minder_installed(install_path, lib): # Checking if the minder is installed
                install_minder(lib, install_path)
            else:
                print(Fore.GREEN + f"Requirement already satisfied: {lib} in {install_path}" + Style.RESET_ALL)
    except KeyError:
        pass

    print(Fore.GREEN + f"Successfully installed {author_minder}" + Style.RESET_ALL)

    return True