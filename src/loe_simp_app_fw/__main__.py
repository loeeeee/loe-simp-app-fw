from .logger import Logger
from .start import main as init_repo

import os
from argparse import ArgumentParser

# Setup flags
isCLI = False

Logger.set_log_level("ERROR")

# Parse CLI or not
def isNotebook() -> bool:
    try:
        shell = get_ipython().__class__.__name__ # het_python() is globally available when using jupyter notebook
        if shell == 'ZMQInteractiveShell':
            return True   # Jupyter notebook or qtconsole
        elif shell == 'TerminalInteractiveShell':
            return False  # Terminal running IPython
        else:
            return False  # Other type (?)
    except NameError:
        return False      # Probably standard Python interpreter

# CLI Parser (Only runs once)
if not isNotebook():
    # Create the main parser
    parser = ArgumentParser(description="This app builds a repo template for loe's simple app framework.")

    # Create subparsers for gather and search commands
    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand",
                                        help="Choose what to do")

    # Init subparser
    init_parser = subparsers.add_parser("init-project", help="Create folder structure")
    init_parser.add_argument("path", help="The path to the project root", default="./")

    # Search subparser
    # search_parser = subparsers.add_parser("search", help="Search for data")
    # search_parser.add_argument("query", help="Search query")
    # search_parser.add_argument("-l", "--limit", type=int, help="Maximum number of results")

    # Parse arguments
    args = parser.parse_args()

    # Handle subcommands based on 'subcommand' attribute
    if args.subcommand == "init-project":
        init_repo(os.path.abspath(args.path))

    # elif args.subcommand == "search":
    #     # Handle search arguments here (e.g., call a search function)
    #     print(f"Searching for: {args.query}")
    #     if args.limit:
    #         print(f"Limiting results to {args.limit}")
    else:
        parser.print_help()
else:
    Logger.info("Jupyter Notebook environment detected")