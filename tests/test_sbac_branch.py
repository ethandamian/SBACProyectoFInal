import os
import unittest
import tempfile
import shutil
from src.classes.sbac import SBAC
from src.config import SBAC_DIR, HEADS_DIR, HEAD_FILE, TAGS_DIR  # Añadir TAGS_DIR

class TestBranchCommands(unittest.TestCase):
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
    
    def test_create_branch_success(self):
        # Crear nueva rama
        result = self.sbac.create_branch("nueva-rama")
        self.assertTrue(result)
        
        # Verificar que el archivo de rama existe
        branch_file = os.path.join(HEADS_DIR, "nueva-rama")
        self.assertTrue(os.path.exists(branch_file))
        
        # Verificar que tiene el mismo commit que master
        with open(os.path.join(HEADS_DIR, "master"), 'r') as f:
            master_commit = f.read().strip()
        with open(branch_file, 'r') as f:
            branch_commit = f.read().strip()
        self.assertEqual(master_commit, branch_commit)
    
    def test_create_branch_already_exists(self):
        # Crear rama por primera vez
        self.assertTrue(self.sbac.create_branch("nueva-rama"))
        
        # Intentar crear la misma rama nuevamente
        result = self.sbac.create_branch("nueva-rama")
        self.assertFalse(result)
    
    def test_create_branch_with_start_point(self):
        # Crear un tag para usar como start point
        self.assertTrue(self.sbac.tag("v1.0"))
        
        # Crear rama desde el tag
        result = self.sbac.create_branch("rama-desde-tag", "v1.0")
        self.assertTrue(result)
        
        # Verificar que la rama apunta al commit correcto
        with open(os.path.join(TAGS_DIR, "v1.0"), 'r') as f:
            tag_commit = f.read().strip()
        with open(os.path.join(HEADS_DIR, "rama-desde-tag"), 'r') as f:
            branch_commit = f.read().strip()
        self.assertEqual(tag_commit, branch_commit)
    
    def test_list_branches(self):
        # Crear algunas ramas
        self.assertTrue(self.sbac.create_branch("rama1"))
        self.assertTrue(self.sbac.create_branch("rama2"))
        
        # Cambiar a una rama para probar el marcador de rama actual
        self.assertTrue(self.sbac.checkout("rama1"))
        
        # Capturar salida del listado
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = self.sbac.list_branches()
        
        output = f.getvalue()
        
        # Verificar resultados
        self.assertTrue(result)
        self.assertIn("* rama1", output)  # Rama actual marcada
        self.assertIn("  master", output)
        self.assertIn("  rama2", output)
    
    def test_list_branches_empty_repo(self):
        # En un repo nuevo solo debería estar master
        result = self.sbac.list_branches()
        self.assertTrue(result)
        
        # Verificar que master está listado
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            self.sbac.list_branches()
        
        output = f.getvalue()
        self.assertIn("* master", output)
    
    def test_delete_branch_success(self):
        # Crear y luego eliminar una rama
        self.assertTrue(self.sbac.create_branch("rama-a-eliminar"))
        self.assertTrue(self.sbac.delete_branch("rama-a-eliminar"))
        
        # Verificar que la rama ya no existe
        self.assertFalse(os.path.exists(os.path.join(HEADS_DIR, "rama-a-eliminar")))
    
    def test_delete_branch_current(self):
        # Intentar eliminar la rama actual
        self.assertTrue(self.sbac.create_branch("rama-actual"))
        self.assertTrue(self.sbac.checkout("rama-actual"))
        
        result = self.sbac.delete_branch("rama-actual")
        self.assertFalse(result)
        
        # Verificar que la rama sigue existiendo
        self.assertTrue(os.path.exists(os.path.join(HEADS_DIR, "rama-actual")))
    
    def test_delete_master_branch(self):
        # Intentar eliminar master
        result = self.sbac.delete_branch("master")
        self.assertFalse(result)
        
        # Verificar que master sigue existiendo
        self.assertTrue(os.path.exists(os.path.join(HEADS_DIR, "master")))
    
    def test_delete_nonexistent_branch(self):
        # Intentar eliminar rama que no existe
        result = self.sbac.delete_branch("no-existe")
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()