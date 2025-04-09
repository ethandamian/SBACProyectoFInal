from .init import register_init
from .cat_file import register_cat_file
from .hash_object import register_hash_object



def register_commands(subparsers):
    register_init(subparsers)
    register_cat_file(subparsers)
    register_hash_object(subparsers)