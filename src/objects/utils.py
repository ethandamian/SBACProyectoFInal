import hashlib
import os
import zlib

from .blob import GitBlob
# from .commit import GitCommit
# from .tag import GitTag
# from .tree import GitTree

from .utils import repo_file


def object_read(repo, sha):
    """Read object sha from Git repository repo.  Return a
    GitObject whose exact type depends on the object."""

    path = repo_file(repo, "objects", sha[0:2], sha[2:])

    if not os.path.isfile(path):
        return None

    with open (path, "rb") as f:
        raw = zlib.decompress(f.read())

        # Read object type
        space_position = raw.find(b' ')
        object_type = raw[0:space_position]

        # Read and validate object size
        null_position = raw.find(b'\x00', space_position)
        size = int(raw[space_position:null_position].decode("ascii"))
        if size != len(raw)-null_position-1:
            raise Exception(f"Malformed object {sha}: bad length")

        # Pick constructor
        match object_type:
            case b'commit' : object=GitCommit
            case b'tree'   : object=GitTree
            case b'tag'    : object=GitTag
            case b'blob'   : object=GitBlob
            case _:
                raise Exception(f"Unknown type {object_type.decode("ascii")} for object {sha}")

        # Call constructor and return object
        return object(raw[null_position+1:])

def object_write(obj, repo=None):
    # Serialize object data
    data = obj.serialize()
    # Add header
    result = obj.fmt + b' ' + str(len(data)).encode() + b'\x00' + data
    # Compute hash
    sha = hashlib.sha1(result).hexdigest()

    if repo:
        # Compute path
        path=repo_file(repo, "objects", sha[0:2], sha[2:], mkdir=True)

        if not os.path.exists(path):
            with open(path, 'wb') as f:
                # Compress and write
                f.write(zlib.compress(result))
    return sha

def object_find(repo, name, fmt=None, follow=True):
    return name

def object_hash(fd, fmt, repo=None):
    """ Hash object, writing it to repo if provided."""
    data = fd.read()

    # Choose constructor according to fmt argument
    match fmt:
        case b'commit' : object=GitCommit(data)
        case b'tree'   : object=GitTree(data)
        case b'tag'    : object=GitTag(data)
        case b'blob'   : object=GitBlob(data)
        case _: raise Exception(f"Unknown type {fmt}!")

    return object_write(object, repo)