import sys
import argparse
from .commands import register_commands

def main():
    parser = argparse.ArgumentParser(description="The stupidest content tracker")
    subparsers = parser.add_subparsers(dest="command", required=True)
    register_commands(subparsers)

    args = parser.parse_args(sys.argv[1:])
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()