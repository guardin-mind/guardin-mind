import argparse
from guardin_mind.package_manager import install_minder
from pydantic import ValidationError

def install_command(args):
    """
    Install minder
    """

    try:
        install_minder(args.author_minder, args.install_path)
    except ValidationError as e:
        print(e)
    except Exception as e:
        print(e)

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

    args = parser.parse_args()
    args.func(args)