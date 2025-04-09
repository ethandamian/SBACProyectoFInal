from src.repository import repo_create

def register_init(subparsers):
    parser = subparsers.add_parser("init", help="Initialize a new, empty repository.")
    parser.add_argument("path", nargs="?", default=".", help="Where to create the repository.")
    parser.set_defaults(func=cmd_init)

def cmd_init(args):
    repo_create(args.path)