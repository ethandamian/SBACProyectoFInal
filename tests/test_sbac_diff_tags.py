import unittest
import os
import shutil
import json
import hashlib
from unittest.mock import patch  # Importamos patch para hacer el mock correctamente
from src.classes.sbac import SBAC
from src.config import *

class TestDiffTags(unittest.TestCase):
    def setUp(self):
        # Limpiar cualquier repositorio existente antes de cada prueba
        if os.path.exists(SBAC_DIR):
            shutil.rmtree(SBAC_DIR)
        self.sbac = SBAC()
        self.sbac.init()  # Inicializar repositorio

        # Crear estructura básica para pruebas
        os.makedirs(TAGS_DIR, exist_ok=True)
        os.makedirs(OBJECTS_DIR, exist_ok=True)

        # Crear algunos tags y commits de prueba
        self.tag1 = "v1.0"
        self.tag2 = "v2.0"
        self.commit1 = "a1b2c3d4e5f6g7h8i9j0"
        self.commit2 = "b2c3d4e5f6g7h8i9j0a1"

        # Crear archivos de tags
        with open(os.path.join(TAGS_DIR, self.tag1), 'w') as f:
            f.write(self.commit1)
        with open(os.path.join(TAGS_DIR, self.tag2), 'w') as f:
            f.write(self.commit2)

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

    def test_diff_tags_no_repository(self):
        """Test cuando no hay repositorio SBAC"""
        sbac = SBAC()  # No inicializado
        result = sbac.diff_tags("any", "any")
        self.assertFalse(result)

    def test_diff_tags_invalid_tags(self):
        """Test con tags que no existen"""
        # Tag 1 no existe
        result = self.sbac.diff_tags("invalid", self.tag2)
        self.assertFalse(result)
        
        # Tag 2 no existe
        result = self.sbac.diff_tags(self.tag1, "invalid")
        self.assertFalse(result)
        
        # Ambos tags no existen
        result = self.sbac.diff_tags("invalid1", "invalid2")
        self.assertFalse(result)

    @patch.object(SBAC, 'diff_commits')  # Forma correcta de hacer patch
    def test_diff_tags_valid_tags(self, mock_diff_commits):
        """Test con tags válidos"""
        # Configurar el mock
        mock_diff_commits.return_value = True
        
        result = self.sbac.diff_tags(self.tag1, self.tag2)
        
        self.assertTrue(result)
        mock_diff_commits.assert_called_once_with(self.commit1, self.commit2)

    def test_diff_tags_with_changes(self):
        """Test integración completa con cambios reales"""
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
        
        self.create_test_commit(self.commit1, tree1)
        self.create_test_commit(self.commit2, tree2)
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_tags(self.tag1, self.tag2)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        
        # Verificar que se muestra el mensaje de comparación
        self.assertIn(f"Comparing changes between tag '{self.tag1}' and '{self.tag2}':", output)
        
        # Verificar que se muestran las diferencias
        self.assertIn("Changes in test.txt:", output)
        self.assertIn("-line2", output)
        self.assertIn("+line2 changed", output)

    def test_diff_tags_same_tags(self):
        """Test comparando el mismo tag consigo mismo"""
        # Crear tree y commit
        tree_data = {"file1.txt": "hash1"}
        self.create_test_commit(self.commit1, tree_data)
        
        # Capturar salida
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.diff_tags(self.tag1, self.tag1)
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        output = captured_output.getvalue()
        
        # Verificar que no hay cambios mostrados
        self.assertIn(f"Comparing changes between tag '{self.tag1}' and '{self.tag1}':", output)
        self.assertNotIn("Changes in", output)

if __name__ == '__main__':
    unittest.main()