from .logger import Logger
from .start import main as init_repo
from .notebook import isNotebook

import os
from argparse import ArgumentParser

# Setup flags
isCLI = False

Logger.set_log_level("ERROR")

# CLI Parser (Only runs once)
if not isNotebook():
    # Create the main parser
    parser = ArgumentParser(description="This app builds a repo template for loe's simple app framework.")

    subparsers = parser.add_subparsers(title="subcommands", dest="subcommand",
                                        help="Choose what to do")

    # Init subparser
    init_parser = subparsers.add_parser("init-project", help="Create folder structure")
    init_parser.add_argument("path", type=str, help="The path to the project root", default="./")
    init_parser.add_argument("--no-code", help="Do not create files in src folder", dest="no_code")

    # Parse arguments
    args = parser.parse_args()

    # Handle subcommands based on 'subcommand' attribute
    if args.subcommand == "init-project":
        init_repo(os.path.abspath(args.path), no_code=args.no_code)

    else:
        parser.print_help()
else:
    Logger.info("Jupyter Notebook environment detected")