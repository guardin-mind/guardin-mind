import argparse
from guardin_mind.package_manager import install_minder, uninstall_minder
from pydantic import ValidationError
from colorama import Fore, Style, init
from guardin_mind import __version__

def install_command(args):
    # Iterate through the list of minders to install each one
    for minder in args.author_minder:
        try:
            install_minder(minder, args.path)
        except ValidationError as e:
            print(e)
        except:
            pass

def uninstall_command(args):
    # Iterate through the list of minders to uninstall each one
    for minder in args.author_minder:
        try:
            uninstall_minder(minder, args.path, args.y)
        except ValidationError as e:
            print(e)
        except:
            pass

def version_command(args):
    init(autoreset=True)

    print(f"{Style.BRIGHT}Guardin Mind{Style.RESET_ALL} (version {Fore.CYAN}{__version__}{Style.RESET_ALL})")

def main():
    # Create the top-level parser
    parser = argparse.ArgumentParser(description="Guardin Mind CLI")

    parser.add_argument(
        '--version',
        action='store_true',
        help='Show Mind version and exit'
    )

    # Add subparsers for 'install' and 'uninstall' commands
    subparsers = parser.add_subparsers(dest="command", required=False)

    # Define 'install' subcommand parser
    install_parser = subparsers.add_parser("install", help="Install minder")
    install_parser.add_argument(
        "author_minder",
        nargs="+",  # One or more minders can be provided
        help="The name(s) of the minder(s) to install. Format: `author_MinderName`."
    )
    install_parser.add_argument(
        "--path", 
        help="Absolute path to the folder for installing minders", 
        default=None
    )
    install_parser.set_defaults(func=install_command)

    # Define 'uninstall' subcommand parser
    uninstall_parser = subparsers.add_parser("uninstall", help="Uninstall minder")
    uninstall_parser.add_argument(
        "author_minder",
        nargs="+",  # One or more minders can be provided
        help="The name(s) of the minder(s) to uninstall. Format: `author_MinderName`."
    )
    uninstall_parser.add_argument(
        "--path", 
        help="Absolute path to the folder with installed minders", 
        default=None
    )
    uninstall_parser.add_argument(
        "-y", 
        action="store_true", 
        help="Automatically confirm the action without prompting"
    )
    uninstall_parser.set_defaults(func=uninstall_command)

    # Parse the CLI arguments and execute the selected subcommand function
    args = parser.parse_args()

    if args.version:
        version_command(args)
    elif hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()