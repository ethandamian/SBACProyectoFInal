import hashlib
from datetime import datetime

class Commit:
    def __init__(self, message, author, parent=None, tree=None):
        self.message = message
        self.author = author
        self.timestamp = datetime.now().isoformat()
        self.parent = parent
        self.tree = tree
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        data = f"{self.message}{self.author}{self.timestamp}{self.parent}{self.tree}"
        return hashlib.sha1(data.encode()).hexdigest()

    def to_dict(self):
        return {
            "message": self.message,
            "author": self.author,
            "timestamp": self.timestamp,
            "parent": self.parent,
            "tree": self.tree,
            "hash": self.hash
        }