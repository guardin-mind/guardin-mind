import argparse
import asyncio
from guardin_mind import Mind


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
    available = mind.available_minders()  # Предположим, есть такой метод
    print("Доступные майндеры:")
    for name in available:
        print(f" - {name}")


def main():
    parser = argparse.ArgumentParser(description="Guardin Mind CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Подкоманда: install
    install_parser = subparsers.add_parser("install", help="Install minder")
    install_parser.add_argument("minder", help="Имя майндера для запуска")
    install_parser.add_argument("message", help="Сообщение для отправки")
    install_parser.add_argument("--async", dest="is_async", action="store_true", help="Асинхронный режим")
    install_parser.set_defaults(func=run_command)

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