import os
import unittest
import tempfile
import shutil
import json
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, OBJECTS_DIR, HEAD_FILE, HEADS_DIR

class TestLogCommand(unittest.TestCase):
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
        with open(self.file1, 'w') as f:
            f.write("Contenido inicial")

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def create_commit(self, message, author="test_author"):
        # Helper para crear commits de prueba
        self.sbac.add([self.file1])
        
        # Actualizar autor en config
        config_file = os.path.join(SBAC_DIR, "config")
        with open(config_file, 'w') as f:
            json.dump({"author": author}, f)
        
        return self.sbac.commit(message)
    
    def test_log_empty_repo(self):
        # Ejecutar log en repositorio sin commits
        result = self.sbac.log()
        
        # Verificar que devuelve False
        self.assertFalse(result)
    
    def test_log_single_commit(self):
        # Crear un commit
        commit_message = "Primer commit"
        self.assertTrue(self.create_commit(commit_message))
        
        # Ejecutar log
        result = self.sbac.log()
        self.assertTrue(result)
        
        # Verificar que se muestra el commit
        # (Para verificar salida, podríamos usar mock)
    
    def test_log_multiple_commits(self):
        # Crear varios commits
        messages = ["Primer commit", "Segundo commit", "Tercer commit"]
        for msg in messages:
            self.assertTrue(self.create_commit(msg))
        
        # Ejecutar log
        result = self.sbac.log()
        self.assertTrue(result)
        
        # Verificar que se muestran todos los commits
        # (Para verificar salida, podríamos usar mock)
    
    def test_log_without_repository(self):
        # Crear nuevo SBAC sin init
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        
        try:
            sbac = SBAC()
            result = sbac.log()
            
            # Verificar que devuelve False cuando no hay repositorio
            self.assertFalse(result)
        finally:
            os.chdir(self.test_dir)
            shutil.rmtree(temp_dir)
    
    def test_log_commit_details(self):
        # Crear commit con autor específico
        author = "test_user"
        message = "Commit de prueba"
        self.assertTrue(self.create_commit(message, author))
        
        # Capturar salida del log
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.sbac.log()
        output = f.getvalue()
        
        # Verificar detalles en la salida
        self.assertIn("commit", output)
        self.assertIn(author, output)
        self.assertIn(message, output)

if __name__ == '__main__':
    unittest.main()