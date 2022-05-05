import sys

from src.modules.commands_parser import ManageCommandParser


def main(argv: list[str]):
    commands_parser = ManageCommandParser()
    commands_parser.parse(argv)


if __name__ == "__main__":
    main(sys.argv)
