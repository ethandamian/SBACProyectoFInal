import os
import unittest
import tempfile
import shutil
import json
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, OBJECTS_DIR, HEAD_FILE, HEADS_DIR, TAGS_DIR

class TestCheckoutCommand(unittest.TestCase):
    def setUp(self):
        # Crear directorio temporal
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Inicializar repositorio
        self.sbac = SBAC()
        self.sbac.init()
        
        # Crear archivo de prueba y commit inicial en master
        self.file1 = "file1.txt"
        with open(self.file1, 'w') as f:
            f.write("Contenido inicial")
        
        self.sbac.add([self.file1])
        self.sbac.commit("Commit inicial en master")
        
        # Crear rama newbranch usando el nuevo método
        self.assertTrue(self.sbac.create_branch("newbranch"))
        
        # Hacer checkout a newbranch y hacer un commit allí
        self.assertTrue(self.sbac.checkout("newbranch"))
        
        self.file2 = "file2.txt"
        with open(self.file2, 'w') as f:
            f.write("Contenido en newbranch")
        
        self.sbac.add([self.file2])
        self.sbac.commit("Commit en newbranch")
        
        # Volver a master
        self.assertTrue(self.sbac.checkout("master"))
        
        # Crear tag
        self.assertTrue(self.sbac.tag("v1.0"))

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_checkout_existing_branch(self):
        # Cambiar a rama existente
        result = self.sbac.checkout("newbranch")
        self.assertTrue(result)
        
        # Verificar que HEAD apunta a la rama correcta
        with open(HEAD_FILE, 'r') as f:
            head_ref = f.read().strip()
        self.assertEqual(head_ref, "ref: refs/heads/newbranch")
    
    def test_checkout_nonexistent_branch(self):
        # Intentar cambiar a rama que no existe
        result = self.sbac.checkout("noexiste")
        self.assertFalse(result)
    
    def test_checkout_by_commit_hash(self):
        # Obtener hash del commit actual
        with open(os.path.join(HEADS_DIR, "master"), 'r') as f:
            commit_hash = f.read().strip()
        
        # Hacer checkout directamente al commit
        result = self.sbac.checkout(commit_hash)
        self.assertTrue(result)
        
        # Verificar que HEAD apunta directamente al commit
        with open(HEAD_FILE, 'r') as f:
            head_ref = f.read().strip()
        self.assertEqual(head_ref, commit_hash)
    
    def test_checkout_by_tag(self):
        # Hacer checkout al tag
        result = self.sbac.checkout("v1.0")
        self.assertTrue(result)
        
        # Verificar que HEAD apunta al commit del tag
        with open(os.path.join(TAGS_DIR, "v1.0"), 'r') as f:
            tag_hash = f.read().strip()
        
        with open(HEAD_FILE, 'r') as f:
            head_ref = f.read().strip()
        self.assertEqual(head_ref, tag_hash)
    
    def test_checkout_invalid_reference(self):
        # Intentar checkout con referencia inválida
        result = self.sbac.checkout("invalid-ref")
        self.assertFalse(result)
    
    def test_checkout_without_repository(self):
        # Crear nuevo SBAC sin init
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        
        try:
            sbac = SBAC()
            result = sbac.checkout("master")
            self.assertFalse(result)
        finally:
            os.chdir(self.test_dir)
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main()