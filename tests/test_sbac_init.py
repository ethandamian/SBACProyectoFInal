import os
import unittest
import tempfile
import shutil
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, OBJECTS_DIR, REFS_DIR, HEADS_DIR, TAGS_DIR, HEAD_FILE, CONFIG_FILE

class TestInitCommand(unittest.TestCase):
    def setUp(self):
        # Crear un directorio temporal para las pruebas
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
    def tearDown(self):
        # Volver al directorio original y limpiar
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_init_creates_required_directories_and_files(self):
        sbac = SBAC()
        result = sbac.init()
        
        # Verificar que la función devuelve True
        self.assertTrue(result)
        
        # Verificar que se crearon todos los directorios necesarios
        self.assertTrue(os.path.exists(SBAC_DIR))
        self.assertTrue(os.path.exists(OBJECTS_DIR))
        self.assertTrue(os.path.exists(REFS_DIR))
        self.assertTrue(os.path.exists(HEADS_DIR))
        self.assertTrue(os.path.exists(TAGS_DIR))
        
        # Verificar que se crearon los archivos necesarios
        self.assertTrue(os.path.exists(HEAD_FILE))
        self.assertTrue(os.path.exists(CONFIG_FILE))
        
        # Verificar el contenido del archivo HEAD
        with open(HEAD_FILE, 'r') as f:
            head_content = f.read().strip()
        self.assertEqual(head_content, "ref: refs/heads/master")
        
        # Verificar que existe el archivo de la rama master
        master_file = os.path.join(HEADS_DIR, "master")
        self.assertTrue(os.path.exists(master_file))
        
        # Verificar que el archivo de la rama master está vacío
        with open(master_file, 'r') as f:
            master_content = f.read().strip()
        self.assertEqual(master_content, "")
    
    def test_init_fails_when_repository_already_exists(self):
        sbac = SBAC()
        
        # Primera ejecución debería tener éxito
        first_result = sbac.init()
        self.assertTrue(first_result)
        
        # Segunda ejecución debería fallar
        second_result = sbac.init()
        self.assertFalse(second_result)
    
    def test_init_creates_config_with_author(self):
        sbac = SBAC()
        sbac.init()
        
        # Verificar que el archivo config existe y tiene el campo author
        self.assertTrue(os.path.exists(CONFIG_FILE))
        
        with open(CONFIG_FILE, 'r') as f:
            config_content = f.read().strip()
        
        # Verificar que es un JSON válido
        import json
        config = json.loads(config_content)
        self.assertIn("author", config)
        
        # Verificar que el autor no es "unknown" (a menos que no haya variable USER)
        # Esto depende del entorno, así que podrías omitirlo o mockear os.getenv
        if "USER" in os.environ:
            self.assertEqual(config["author"], os.getenv("USER"))
        else:
            self.assertEqual(config["author"], "unknown")

if __name__ == '__main__':
    unittest.main()