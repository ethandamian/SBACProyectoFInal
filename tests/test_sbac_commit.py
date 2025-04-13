import os
import unittest
import tempfile
import shutil
import json
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, OBJECTS_DIR, INDEX_FILE, HEAD_FILE, HEADS_DIR

class TestCommitCommand(unittest.TestCase):
    def setUp(self):
        # Crear directorio temporal
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Inicializar repositorio
        self.sbac = SBAC()
        self.sbac.init()
        
        # Crear archivos de prueba
        self.file1 = "file1.txt"
        self.file2 = "file2.txt"
        
        with open(self.file1, 'w') as f:
            f.write("Contenido inicial")
            
        with open(self.file2, 'w') as f:
            f.write("Otro contenido")

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_commit_with_staged_changes(self):
        # Añadir archivo y hacer commit
        self.sbac.add([self.file1])
        result = self.sbac.commit("Primer commit")
        
        # Verificar que el commit fue exitoso
        self.assertTrue(result)
        
        # Obtener hash del commit correctamente
        with open(HEAD_FILE, 'r') as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith('ref: '):
            branch = head_ref.split('/')[-1]
            branch_file = os.path.join(HEADS_DIR, branch)
            with open(branch_file, 'r') as f:
                commit_hash = f.read().strip()
        else:
            commit_hash = head_ref
        
        # Verificar que se creó el objeto commit
        commit_path = os.path.join(OBJECTS_DIR, commit_hash)
        self.assertTrue(os.path.exists(commit_path), 
                    f"Commit object not found at {commit_path}")
        
        # Verificar que el staging area está limpio
        self.assertFalse(os.path.exists(INDEX_FILE))
    
    def test_commit_without_staged_changes(self):
        # Intentar commit sin cambios
        result = self.sbac.commit("Commit sin cambios")
        self.assertFalse(result)
    
    def test_commit_creates_tree_object(self):
        # Añadir archivos y hacer commit
        self.sbac.add([self.file1, self.file2])
        result = self.sbac.commit("Commit con dos archivos")
        self.assertTrue(result)
        
        # Obtener hash del commit
        with open(os.path.join(HEADS_DIR, "master"), 'r') as f:
            commit_hash = f.read().strip()
        
        # Leer objeto commit
        commit_path = os.path.join(OBJECTS_DIR, commit_hash)
        with open(commit_path, 'r') as f:
            commit_data = json.load(f)
        
        # Verificar que existe el tree object
        tree_path = os.path.join(OBJECTS_DIR, commit_data["tree"])
        self.assertTrue(os.path.exists(tree_path))
        
        # Verificar contenido del tree
        with open(tree_path, 'r') as f:
            tree_data = json.load(f)
        self.assertIn(self.file1, tree_data)
        self.assertIn(self.file2, tree_data)
    
    def test_commit_with_parent(self):
        # Primer commit
        self.sbac.add([self.file1])
        first_commit = self.sbac.commit("Primer commit")
        self.assertTrue(first_commit)
        
        # Segundo commit
        self.sbac.add([self.file2])
        second_commit = self.sbac.commit("Segundo commit")
        self.assertTrue(second_commit)
        
        # Verificar parent relationship
        with open(os.path.join(HEADS_DIR, "master"), 'r') as f:
            second_commit_hash = f.read().strip()
        
        with open(os.path.join(OBJECTS_DIR, second_commit_hash), 'r') as f:
            second_commit_data = json.load(f)
        
        self.assertIsNotNone(second_commit_data["parent"])
    
    def test_commit_without_repository(self):
        # Crear nuevo SBAC sin init
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        
        try:
            sbac = SBAC()
            result = sbac.commit("Commit sin repo")
            self.assertFalse(result)
        finally:
            os.chdir(self.test_dir)
            shutil.rmtree(temp_dir)
    
    def test_commit_author_from_config(self):
        # Modificar config para tener autor conocido
        config_file = os.path.join(SBAC_DIR, "config")
        with open(config_file, 'w') as f:
            json.dump({"author": "test_author"}, f)
        
        # Hacer commit
        self.sbac.add([self.file1])
        result = self.sbac.commit("Commit con autor")
        self.assertTrue(result)
        
        # Verificar autor en commit
        with open(os.path.join(HEADS_DIR, "master"), 'r') as f:
            commit_hash = f.read().strip()
        
        with open(os.path.join(OBJECTS_DIR, commit_hash), 'r') as f:
            commit_data = json.load(f)
        
        self.assertEqual(commit_data["author"], "test_author")

if __name__ == '__main__':
    unittest.main()