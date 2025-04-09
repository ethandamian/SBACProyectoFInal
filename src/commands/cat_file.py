import sys

from src.utils import repo_find
from src.objects.utils import object_read

def register_cat_file(subparsers):
    parser = subparsers.add_parser("cat-file", help="Provide content of repository objects.")
    parser.add_argument("type", metavar="type", choices=["blob", "tree", "commit", "tag"], help="Specify the type")
    parser.add_argument("object", metavar="object", help="The object to display.")

def cmd_cat_file(args):
    repo = repo_find()
    cat_file(repo, args.object, fmt=args.type.encode())

def cat_file(repo, obj, fmt=None):
    obj = object_read(repo, object_find(repo, obj, fmt=fmt))
    sys.stdout.buffer.write(obj.serialize())
    