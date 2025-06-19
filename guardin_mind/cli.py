import argparse
import re
import platform
from colorama import init, Fore, Style
import asyncio
from guardin_mind import Mind
import requests
import shutil
import zipfile
from pathlib import Path
import io
import os

def install_command(args):
    init()  # Init colorama

    os_name: str = platform.system()  # Get OS
    author_minder:str = args.author_minder  # Minder name in the `author-MinderName` format

    # Parse minder name and author
    try:
        # Parse from author_minder only author and minder
        match = re.search(r'[A-Z][a-zA-Z]*$', author_minder)

        if match:
            minder:str = match.group() # Parse minder name
            author:str = author_minder[:match.start()].rstrip('_') # Parse author
        else:
            raise ValueError("Incorrect format")
    except:
        print(Fore.RED + "Error. Incorrect format. Use the format \"mind install <author_MinderName>\"" + Style.RESET_ALL)
        return None

    # Get install path
    if args.install_path:
        install_path = args.install_path
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
        print(Fore.GREEN + f"Requirement already satisfied: {minder} in {install_path}" + Style.RESET_ALL)
        return True

    def download_repo_zip(user_repo, destination_folder):
        zip_url = f"https://github.com/{user_repo}/archive/refs/heads/main.zip"

        print(Fore.CYAN + f"    Downloading {minder}" + Style.RESET_ALL)
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
                    print(Fore.RED + "Unexpected archive structure" + Style.RESET_ALL)
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
            print(Fore.RED + f"    Error when downloading the minder from github. Error code: {response.status_code} for {zip_url}" + Style.RESET_ALL)

    print(Fore.CYAN + f"Collecting {author_minder}" + Style.RESET_ALL)
    download_repo_zip(f"{author}/{minder}", install_path)

def run_command(args):
    mind = Mind()
    minder = getattr(mind, args.minder)()

    if args.is_async:
        result = asyncio.run(minder.ask_async(args.message))
    else:
        result = minder.ask_sync(args.message)

    print(f"Ответ от майндера '{args.minder}': {result}")


def list_command(args):
    mind = Mind()
    available = None # Предположим, есть такой метод
    print("Доступные майндеры:")
    for name in available:
        print(f" - {name}")

# Subcommands
def main():
    parser = argparse.ArgumentParser(description="Guardin Mind CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommands
    # Subcommand: install
    install_parser = subparsers.add_parser("install", help="Install minder")
    install_parser.add_argument("author_minder", help="The name of the minder to install. In the `author_MinderName` format.")
    install_parser.add_argument("--install-path", help="Folder for installing minders", default=None)
    install_parser.set_defaults(func=install_command)

    # Подкоманда: run
    run_parser = subparsers.add_parser("run", help="Запустить майндер с сообщением")
    run_parser.add_argument("minder", help="Имя майндера для запуска")
    run_parser.add_argument("message", help="Сообщение для отправки")
    run_parser.add_argument("--async", dest="is_async", action="store_true", help="Асинхронный режим")
    run_parser.set_defaults(func=run_command)

    # Подкоманда: list
    list_parser = subparsers.add_parser("list", help="Показать список доступных майндеров")
    list_parser.set_defaults(func=list_command)

    args = parser.parse_args()
    args.func(args)