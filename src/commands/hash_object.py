from objects.utils import object_hash
from utils import repo_find

def register_hash_object(subparsers):
    parser = subparsers.add_parser("hash-object", help="Compute object ID and optionally creates a blob from a file.")
    parser.add_argument("-t", metavar="type", choices=["blob", "tree", "commit", "tag"], help="Specify the type")
    parser.add_argument("-w", dest="write", action="store_true", help="Actually write the object into the database")
    parser.add_argument("path", help="Read object from <file> instead of stdin")

def cmd_hash_object(args):
    if args.write:
        repo = repo_find()
    else:
        repo = None

    with open(args.path, "rb") as f:
        sha = object_hash(fd, args.type.encode(), repo)
        print(sha)
    