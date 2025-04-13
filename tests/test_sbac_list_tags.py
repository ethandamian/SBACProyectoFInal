import unittest
import os
import shutil
import json
from src.classes.sbac import SBAC
from src.config import *

class TestListTags(unittest.TestCase):
    def setUp(self):
        # Limpiar cualquier repositorio existente antes de cada prueba
        if os.path.exists(SBAC_DIR):
            shutil.rmtree(SBAC_DIR)
        self.sbac = SBAC()

    def tearDown(self):
        # Limpiar después de cada prueba
        if os.path.exists(SBAC_DIR):
            shutil.rmtree(SBAC_DIR)

    def test_list_tags_no_repository(self):
        """Test list_tags cuando no hay repositorio SBAC"""
        result = self.sbac.list_tags()
        self.assertFalse(result)
        # Aquí podrías verificar también la salida impresa si es necesario

    def test_list_tags_empty_tags(self):
        """Test list_tags cuando no hay tags creados"""
        self.sbac.init()  # Inicializar repositorio
        
        # Asegurarse que el directorio de tags existe pero está vacío
        self.assertTrue(os.path.exists(TAGS_DIR))
        
        result = self.sbac.list_tags()
        self.assertFalse(result)
        # Verificar que se imprimió "No tags found"

    def test_list_tags_with_tags(self):
        """Test list_tags con tags existentes"""
        self.sbac.init()
        
        # Crear algunos tags de prueba
        test_tags = {
            "v1.0": "a1b2c3d4e5f6g7h8i9j0",
            "release": "b2c3d4e5f6g7h8i9j0a1",
            "test-tag": "c3d4e5f6g7h8i9j0a1b2"
        }
        
        # Crear archivos de tags manualmente
        for tag_name, commit_hash in test_tags.items():
            tag_path = os.path.join(TAGS_DIR, tag_name)
            with open(tag_path, 'w') as f:
                f.write(commit_hash)
        
        # Ejecutar list_tags y capturar la salida (usando unittest.mock)
        from io import StringIO
        import sys
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.list_tags()
        sys.stdout = sys.__stdout__  # Restaurar salida estándar
        
        self.assertTrue(result)
        
        # Verificar que la salida contiene todos los tags
        output = captured_output.getvalue()
        self.assertIn("Tags:", output)
        
        for tag_name, commit_hash in test_tags.items():
            self.assertIn(tag_name, output)
            self.assertIn(commit_hash[:7], output)

    def test_list_tags_with_special_chars(self):
        """Test list_tags con nombres de tags que tienen caracteres especiales"""
        self.sbac.init()
        
        special_tags = {
            "tag-with-hyphen": "a1b2c3d4e5f6g7h8i9j0",
            "tag.with.dot": "b2c3d4e5f6g7h8i9j0a1",
            "tag_with_underscore": "c3d4e5f6g7h8i9j0a1b2",
            "tag@version": "d4e5f6g7h8i9j0a1b2c3"
        }
        
        # Crear tags especiales
        for tag_name, commit_hash in special_tags.items():
            tag_path = os.path.join(TAGS_DIR, tag_name)
            with open(tag_path, 'w') as f:
                f.write(commit_hash)
        
        # Ejecutar list_tags
        from io import StringIO
        import sys
        
        captured_output = StringIO()
        sys.stdout = captured_output
        
        result = self.sbac.list_tags()
        sys.stdout = sys.__stdout__
        
        self.assertTrue(result)
        
        # Verificar que todos los tags especiales aparecen en la salida
        output = captured_output.getvalue()
        for tag_name in special_tags:
            self.assertIn(tag_name, output)

if __name__ == '__main__':
    unittest.main()