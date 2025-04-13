import unittest
import os
import hashlib
import shutil
import json
from src.classes.sbac import SBAC
from src.config import *

class TestDiffCommits(unittest.TestCase):
    def setUp(self):
        # Limpiar cualquier repositorio existente antes de cada prueba
        if os.path.exists(SBAC_DIR):
            shutil.rmtree(SBAC_DIR)
        self.sbac = SBAC()
        self.sbac.init()  # Inicializar repositorio para la mayoría de pruebas

        # Crear estructura básica de commits para pruebas
        self.commit1 = "a1b2c3d4e5f6g7h8i9j0"
        self.commit2 = "b2c3d4e5f6g7h8i9j0a1"
        
        # Crear objetos commit y tree de prueba
        os.makedirs(OBJECTS_DIR, exist_ok=True)
        
    def tearDown(self):
        # Limpiar después de cada prueba
        if os.path.exists(SBAC_DIR):
            shutil.rmtree(SBAC_DIR)

    def create_test_commit(self, commit_hash, tree_data):
        """Helper para crear un commit de prueba con su tree"""
        # Crear tree object
        tree_hash = hashlib.sha1(json.dumps(tree_data).encode()).hexdigest()
        tree_path = os.path.join(OBJECTS_DIR, tree_hash)
        with open(tree_path, 'w') as f:
            json.dump(tree_data, f)
        
        # Crear commit object
        commit_data = {
            "message": "Test commit",
            "author": "test",
            "timestamp": "2023-01-01T00:00:00",
            "parent": None,
            "tree": tree_hash,
            "hash": commit_hash
        }
        commit_path = os.path.join(OBJECTS_DIR, commit_hash)
        with open(commit_path, 'w') as f:
            json.dump(commit_data, f)
        
        return commit_hash

    def test_diff_no_repository(self):
        """Test cuando no hay repositorio SBAC"""
        sbac = SBAC()  # No inicializado
        result = sbac.diff_commits("any", "any")
        self.assertFalse(result)

    def test_diff_invalid_commits(self):
        """Test con commits que no existen"""
        result = self.sbac.diff_commits("invalid1", "invalid2")
        self.assertFalse(result)

    def test_diff_identical_commits(self):
        """Test con commits idénticos"""
        tree_data = {"file1.txt": "hash1", "file2.txt": "hash2"}
        commit1 = self.create_test_commit(self.commit1, tree_data)
        commit2 = self.create_test_commit(self.commit2, tree_data)
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_commits(commit1, commit2)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        self.assertNotIn("Changes in", captured_output.getvalue())

    def test_diff_added_file(self):
        """Test cuando se añade un archivo"""
        tree1 = {"file1.txt": "hash1"}
        tree2 = {"file1.txt": "hash1", "newfile.txt": "hash2"}
        
        commit1 = self.create_test_commit(self.commit1, tree1)
        commit2 = self.create_test_commit(self.commit2, tree2)
        
        # Crear archivo objeto para el nuevo archivo
        with open(os.path.join(OBJECTS_DIR, "hash2"), 'w') as f:
            f.write("content")
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_commits(commit1, commit2)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        self.assertIn("Changes in newfile.txt:", output)
        self.assertIn(f"File added in {commit2[:7]}", output)

    def test_diff_removed_file(self):
        """Test cuando se elimina un archivo"""
        tree1 = {"file1.txt": "hash1", "to_delete.txt": "hash2"}
        tree2 = {"file1.txt": "hash1"}
        
        commit1 = self.create_test_commit(self.commit1, tree1)
        commit2 = self.create_test_commit(self.commit2, tree2)
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_commits(commit1, commit2)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        self.assertIn("Changes in to_delete.txt:", output)
        self.assertIn(f"File removed in {commit2[:7]}", output)

    def test_diff_modified_file(self):
        """Test cuando se modifica un archivo"""
        # Crear contenidos de archivos
        content1 = "line1\nline2\nline3\n"
        content2 = "line1\nline2 changed\nline3\nnew line\n"
        
        # Calcular hashes
        hash1 = hashlib.sha1(content1.encode()).hexdigest()
        hash2 = hashlib.sha1(content2.encode()).hexdigest()
        
        # Crear archivos objeto
        with open(os.path.join(OBJECTS_DIR, hash1), 'w') as f:
            f.write(content1)
        with open(os.path.join(OBJECTS_DIR, hash2), 'w') as f:
            f.write(content2)
        
        # Crear trees y commits
        tree1 = {"test.txt": hash1}
        tree2 = {"test.txt": hash2}
        
        commit1 = self.create_test_commit(self.commit1, tree1)
        commit2 = self.create_test_commit(self.commit2, tree2)
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_commits(commit1, commit2)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        self.assertIn("Changes in test.txt:", output)
        self.assertIn("-line2", output)
        self.assertIn("+line2 changed", output)
        self.assertIn("+new line", output)

    def test_diff_multiple_changes(self):
        """Test con múltiples tipos de cambios"""
        # Crear contenidos
        content1 = "original content"
        content2 = "modified content"
        
        # Calcular hashes
        hash1 = hashlib.sha1(content1.encode()).hexdigest()
        hash2 = hashlib.sha1(content2.encode()).hexdigest()
        hash3 = hashlib.sha1(b"new file content").hexdigest()
        
        # Crear archivos objeto
        with open(os.path.join(OBJECTS_DIR, hash1), 'w') as f:
            f.write(content1)
        with open(os.path.join(OBJECTS_DIR, hash2), 'w') as f:
            f.write(content2)
        with open(os.path.join(OBJECTS_DIR, hash3), 'w') as f:
            f.write("new file content")
        
        # Crear trees y commits
        tree1 = {
            "file1.txt": hash1,
            "file2.txt": "other_hash",  # Este será eliminado
            "common.txt": "common_hash"  # Sin cambios
        }
        tree2 = {
            "file1.txt": hash2,  # Modificado
            "newfile.txt": hash3,  # Añadido
            "common.txt": "common_hash"  # Sin cambios
        }
        
        commit1 = self.create_test_commit(self.commit1, tree1)
        commit2 = self.create_test_commit(self.commit2, tree2)
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_commits(commit1, commit2)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        
        # Verificar todos los cambios esperados
        self.assertIn("Changes in file1.txt:", output)
        self.assertIn("Changes in file2.txt:", output)
        self.assertIn("Changes in newfile.txt:", output)
        self.assertNotIn("Changes in common.txt:", output)
        
        # Verificar tipos de cambios
        self.assertIn(f"File removed in {commit2[:7]}", output)  # file2.txt
        self.assertIn(f"File added in {commit2[:7]}", output)    # newfile.txt
        self.assertIn("-original content", output)              # file1.txt (removed)
        self.assertIn("+modified content", output)              # file1.txt (added)

if __name__ == '__main__':
    unittest.main()