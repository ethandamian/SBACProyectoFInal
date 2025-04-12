import os

SBAC_DIR = ".sbac"
OBJECTS_DIR = os.path.join(SBAC_DIR, "objects")
REFS_DIR = os.path.join(SBAC_DIR, "refs")
HEADS_DIR = os.path.join(REFS_DIR, "heads")
TAGS_DIR = os.path.join(REFS_DIR, "tags")
HEAD_FILE = os.path.join(SBAC_DIR, "HEAD")
INDEX_FILE = os.path.join(SBAC_DIR, "index")
CONFIG_FILE = os.path.join(SBAC_DIR, "config")