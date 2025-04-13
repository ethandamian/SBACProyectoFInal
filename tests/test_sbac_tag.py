import os
import unittest
import tempfile
import shutil
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, TAGS_DIR, HEAD_FILE, HEADS_DIR

class TestTagCommand(unittest.TestCase):
    def setUp(self):
        # Crear directorio temporal
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Inicializar repositorio
        self.sbac = SBAC()
        self.sbac.init()
        
        # Crear archivo de prueba y commit inicial
        self.file1 = "file1.txt"
        with open(self.file1, 'w') as f:
            f.write("Contenido inicial")
        
        self.sbac.add([self.file1])
        self.sbac.commit("Commit inicial")

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_create_tag(self):
        # Crear tag
        result = self.sbac.tag("v1.0")
        self.assertTrue(result)
        
        # Verificar que el tag existe
        tag_file = os.path.join(TAGS_DIR, "v1.0")
        self.assertTrue(os.path.exists(tag_file))
        
        # Verificar que apunta al commit correcto
        with open(HEAD_FILE, 'r') as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith('ref: '):
            branch = head_ref.split('/')[-1]
            with open(os.path.join(HEADS_DIR, branch), 'r') as f:
                expected_commit = f.read().strip()
        else:
            expected_commit = head_ref
        
        with open(tag_file, 'r') as f:
            actual_commit = f.read().strip()
        
        self.assertEqual(expected_commit, actual_commit)
    
    def test_create_tag_without_repo(self):
        # Crear nuevo SBAC sin init
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        
        try:
            sbac = SBAC()
            result = sbac.tag("v1.0")
            self.assertFalse(result)
        finally:
            os.chdir(self.test_dir)
            shutil.rmtree(temp_dir)
    
    def test_create_duplicate_tag(self):
        # Crear tag por primera vez
        self.assertTrue(self.sbac.tag("v1.0"))
        
        # Intentar crear el mismo tag nuevamente
        result = self.sbac.tag("v1.0")
        self.assertTrue(result)  # Sobrescribe el tag existente
        
        # Verificar que sigue existiendo
        self.assertTrue(os.path.exists(os.path.join(TAGS_DIR, "v1.0")))
    
    def test_create_multiple_tags(self):
        # Crear varios tags
        self.assertTrue(self.sbac.tag("v1.0"))
        self.assertTrue(self.sbac.tag("v1.1"))
        self.assertTrue(self.sbac.tag("release"))
        
        # Verificar que todos existen
        self.assertTrue(os.path.exists(os.path.join(TAGS_DIR, "v1.0")))
        self.assertTrue(os.path.exists(os.path.join(TAGS_DIR, "v1.1")))
        self.assertTrue(os.path.exists(os.path.join(TAGS_DIR, "release")))
    
    def test_tag_output_message(self):
        # Capturar salida del comando tag
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.sbac.tag("v1.0")
        
        output = f.getvalue().strip()
        
        # Obtener commit actual para verificar el mensaje
        with open(HEAD_FILE, 'r') as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith('ref: '):
            branch = head_ref.split('/')[-1]
            with open(os.path.join(HEADS_DIR, branch), 'r') as f:
                commit_hash = f.read().strip()
        else:
            commit_hash = head_ref
        
        expected_output = f"Created tag 'v1.0' at {commit_hash[:7]}"
        self.assertEqual(output, expected_output)

if __name__ == '__main__':
    unittest.main()