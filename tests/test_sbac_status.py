import os
import unittest
import tempfile
import shutil
import json
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, INDEX_FILE

class TestStatusCommand(unittest.TestCase):
    def setUp(self):
        # Crear un directorio temporal para las pruebas
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Inicializar un repositorio SBAC
        self.sbac = SBAC()
        self.sbac.init()
        
        # Crear archivos de prueba
        self.tracked_file = "tracked.txt"
        self.staged_file = "staged.txt"
        self.untracked_file = "untracked.txt"
        
        for filename in [self.tracked_file, self.staged_file, self.untracked_file]:
            with open(filename, 'w') as f:
                f.write(f"Contenido de {filename}")
    
    def tearDown(self):
        # Volver al directorio original y limpiar
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_status_empty_repo(self):
        # Ejecutar status en un repositorio recién inicializado
        result = self.sbac.status()
        
        # Verificar que devuelve True
        self.assertTrue(result)
        
        # Verificar que no hay archivos en staging
        self.assertFalse(os.path.exists(INDEX_FILE))
        
        # En un repo vacío, todos los archivos deberían ser untracked
        # (pero esto depende de tu implementación de get_untracked_files)
    
    def test_status_with_staged_files(self):
        # Añadir un archivo al staging
        self.sbac.add([self.staged_file])
        
        # Ejecutar status
        result = self.sbac.status()
        self.assertTrue(result)
        
        # Verificar que el archivo está en staging
        self.assertTrue(os.path.exists(INDEX_FILE))
        with open(INDEX_FILE, 'r') as f:
            staged_files = json.load(f)
        self.assertIn(self.staged_file, staged_files)
    
    def test_status_with_untracked_files(self):
        # Añadir un archivo al staging (tracked)
        self.sbac.add([self.tracked_file])
        
        # Ejecutar status
        result = self.sbac.status()
        self.assertTrue(result)
        
        # Verificar que el archivo no añadido aparece como untracked
        # (esto depende de tu implementación de get_untracked_files)
    
    def test_status_without_repo(self):
        # Crear un nuevo SBAC sin init en otro directorio
        temp_dir = tempfile.mkdtemp()
        os.chdir(temp_dir)
        
        try:
            sbac = SBAC()
            result = sbac.status()
            
            # Verificar que devuelve False cuando no hay repositorio
            self.assertFalse(result)
        finally:
            os.chdir(self.test_dir)
            shutil.rmtree(temp_dir)
    
    def test_status_after_modification(self):
        # Añadir archivo al staging
        self.sbac.add([self.tracked_file])
        
        # Modificar el archivo
        with open(self.tracked_file, 'a') as f:
            f.write("\nNuevo contenido")
        
        # Ejecutar status
        result = self.sbac.status()
        self.assertTrue(result)
        
        # Verificar que el archivo modificado se detecta correctamente
        # (esto depende de cómo implementes la detección de cambios)

if __name__ == '__main__':
    unittest.main()