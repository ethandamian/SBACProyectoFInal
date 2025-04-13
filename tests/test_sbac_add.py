import os
import unittest
import tempfile
import shutil
import json
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, OBJECTS_DIR, INDEX_FILE

class TestAddCommand(unittest.TestCase):
    def setUp(self):
        # Crear un directorio temporal para las pruebas
        self.test_dir = tempfile.mkdtemp()
        self.original_dir = os.getcwd()
        os.chdir(self.test_dir)
        
        # Inicializar un repositorio SBAC
        self.sbac = SBAC()
        self.sbac.init()
        
        # Crear algunos archivos de prueba
        self.file1 = "test_file1.txt"
        self.file2 = "test_file2.txt"
        self.nonexistent_file = "nonexistent.txt"
        
        with open(self.file1, 'w') as f:
            f.write("Contenido del archivo 1")
            
        with open(self.file2, 'w') as f:
            f.write("Contenido diferente del archivo 2")
    
    def tearDown(self):
        # Volver al directorio original y limpiar
        os.chdir(self.original_dir)
        shutil.rmtree(self.test_dir)
    
    def test_add_single_file(self):
        # Ejecutar el comando add con un archivo
        result = self.sbac.add([self.file1])
        
        # Verificar que devuelve True
        self.assertTrue(result)
        
        # Verificar que el archivo se añadió al staging area
        self.assertTrue(os.path.exists(INDEX_FILE))
        
        with open(INDEX_FILE, 'r') as f:
            staged_files = json.load(f)
        
        self.assertIn(self.file1, staged_files)
        
        # Verificar que el objeto se creó en OBJECTS_DIR
        object_hash = staged_files[self.file1]
        object_path = os.path.join(OBJECTS_DIR, object_hash)
        self.assertTrue(os.path.exists(object_path))
        
        # Verificar el contenido del objeto
        with open(object_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Contenido del archivo 1")
    
    def test_add_multiple_files(self):
        # Ejecutar el comando add con múltiples archivos
        result = self.sbac.add([self.file1, self.file2])
        
        # Verificar que devuelve True
        self.assertTrue(result)
        
        # Verificar que ambos archivos se añadieron al staging area
        with open(INDEX_FILE, 'r') as f:
            staged_files = json.load(f)
        
        self.assertIn(self.file1, staged_files)
        self.assertIn(self.file2, staged_files)
        
        # Verificar que los objetos se crearon en OBJECTS_DIR
        for file in [self.file1, self.file2]:
            object_hash = staged_files[file]
            object_path = os.path.join(OBJECTS_DIR, object_hash)
            self.assertTrue(os.path.exists(object_path))
    
    def test_add_nonexistent_file(self):
        # Ejecutar el comando add con un archivo que no existe
        result = self.sbac.add([self.nonexistent_file])
        
        # Verificar que devuelve False (porque hubo un error)
        self.assertFalse(result)
            
        # Verificar que no se añadió ningún archivo al staging
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, 'r') as f:
                staged_files = json.load(f)
            self.assertNotIn(self.nonexistent_file, staged_files)
    
    def test_add_updates_existing_staging(self):
        # Añadir un archivo primero
        self.sbac.add([self.file1])
        
        # Verificar el estado inicial del staging
        with open(INDEX_FILE, 'r') as f:
            initial_staged = json.load(f)
        initial_hash = initial_staged[self.file1]
        
        # Modificar el archivo
        with open(self.file1, 'w') as f:
            f.write("Contenido modificado del archivo 1")
        
        # Añadir el archivo modificado
        result = self.sbac.add([self.file1])
        self.assertTrue(result)
        
        # Verificar que el staging se actualizó
        with open(INDEX_FILE, 'r') as f:
            updated_staged = json.load(f)
        updated_hash = updated_staged[self.file1]
        
        # El hash debería ser diferente
        self.assertNotEqual(initial_hash, updated_hash)
        
        # Verificar que el nuevo objeto existe
        new_object_path = os.path.join(OBJECTS_DIR, updated_hash)
        self.assertTrue(os.path.exists(new_object_path))
        
        # Verificar el contenido del nuevo objeto
        with open(new_object_path, 'r') as f:
            content = f.read()
        self.assertEqual(content, "Contenido modificado del archivo 1")
    
    def test_add_without_init(self):
        # Crear un directorio temporal completamente nuevo solo para este test
        temp_dir = tempfile.mkdtemp()
        original_dir = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Crear un archivo de prueba en este nuevo directorio limpio
            test_file = "test_file.txt"
            with open(test_file, 'w') as f:
                f.write("Test content")
            
            # Crear un nuevo SBAC sin init
            sbac = SBAC()
            
            # Intentar añadir un archivo
            result = sbac.add([test_file])
            
            # Verificar que devuelve False
            self.assertFalse(result)
            
            # Verificar que no se creó el archivo de staging
            self.assertFalse(os.path.exists(INDEX_FILE))
        finally:
            # Volver y limpiar
            os.chdir(original_dir)
            shutil.rmtree(temp_dir)

if __name__ == '__main__':
    unittest.main()