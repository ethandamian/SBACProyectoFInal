import json
import hashlib
import difflib
from .commit import Commit
from src.config import *

class SBAC:
    def __init__(self):
        self.staged_files = {}
        self.branches = {}
        self.current_branch = None
        self.tags = {}

    def init(self):
        if os.path.exists(SBAC_DIR):
            print("SBAC repository already exists.")
            return False

        os.makedirs(SBAC_DIR)
        os.makedirs(OBJECTS_DIR)
        os.makedirs(REFS_DIR)
        os.makedirs(HEADS_DIR)
        os.makedirs(TAGS_DIR)

        with open(HEAD_FILE, "w") as f:
            f.write("ref: refs/heads/master")

        with open(CONFIG_FILE, "w") as f:
            json.dump({"author": os.getenv("USER", "unknown")}, f)

        with open(os.path.join(HEADS_DIR, "master"), "w") as f:
            f.write("")

        self.current_branch = "master"
        print("Initialized empty SBAC repository.")
        return True

    def add(self, files):
        if not os.path.exists(SBAC_DIR):
            print("Entra a add")
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False  # Asegurar que devuelve False cuando no hay repositorio

        # Cargar archivos ya existentes en staging
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r") as f:
                self.staged_files = json.load(f)
        else:
            self.staged_files = {}

        added_files = 0
        has_errors = False  # Bandera para detectar errores
        
        for file in files:
            if not os.path.exists(file):
                print(f"fatal: pathspec '{file}' did not match any files")
                has_errors = True  # Marcar que hubo un error
                continue

            with open(file, "rb") as f:
                content = f.read()
            file_hash = hashlib.sha1(content).hexdigest()

            # Almacenar el contenido en objetos
            object_path = os.path.join(OBJECTS_DIR, file_hash)
            if not os.path.exists(object_path):
                with open(object_path, "wb") as f:
                    f.write(content)

            self.staged_files[file] = file_hash
            added_files += 1

        # Guardar el estado actualizado
        with open(INDEX_FILE, "w") as f:
            json.dump(self.staged_files, f)

        print(f"Added {added_files} file(s) to staging area.")
        
        # Devolver False si hubo errores (archivos no existentes)
        return not has_errors
    
    def get_untracked_files(self):
        """Retorna una lista de archivos en el directorio que no están siendo rastreados"""
        if not os.path.exists(SBAC_DIR):
            return []

        # Obtener todos los archivos en el directorio actual (excepto .sbac)
        all_files = set()
        for root, dirs, files in os.walk("."):
            # Ignorar el directorio .sbac
            if SBAC_DIR in root.split(os.path.sep):
                continue
            for file in files:
                path = os.path.relpath(os.path.join(root, file))
                all_files.add(path)

        # Obtener archivos rastreados (en staging o en commits)
        tracked_files = set()

        # Archivos en staging
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r") as f:
                staged_files = json.load(f)
                tracked_files.update(staged_files.keys())

        # Archivos en el último commit (con comprobación de existencia)
        with open(HEAD_FILE, "r") as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith("ref: "):
            branch = head_ref.split("/")[-1]
            branch_file = os.path.join(HEADS_DIR, branch)
            if os.path.exists(branch_file):
                with open(branch_file, "r") as f:
                    commit_hash = f.read().strip()
                if commit_hash:  # Solo si hay un commit
                    commit_path = os.path.join(OBJECTS_DIR, commit_hash)
                    if os.path.exists(commit_path) and not os.path.isdir(commit_path):
                        with open(commit_path, "r") as f:
                            try:
                                commit_data = json.load(f)
                                if "tree" in commit_data:
                                    tree_path = os.path.join(OBJECTS_DIR, commit_data["tree"])
                                    if os.path.exists(tree_path) and not os.path.isdir(tree_path):
                                        with open(tree_path, "r") as f:
                                            tracked_files.update(json.load(f).keys())
                            except json.JSONDecodeError:
                                pass  # Si el archivo no es un JSON válido

        return sorted(all_files - tracked_files)

    def status(self):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        try:
            # Archivos en staging
            staged_files = {}
            if os.path.exists(INDEX_FILE):
                with open(INDEX_FILE, "r") as f:
                    staged_files = json.load(f)

            print("Staged files:")
            if staged_files:
                for file in staged_files:
                    print(f"  {file}")
            else:
                print("  (no files staged)")

            # Archivos no rastreados
            untracked_files = self.get_untracked_files()
            print("\nUntracked files:")
            if untracked_files:
                for file in untracked_files:
                    print(f"  {file}")
            else:
                print("  (no untracked files)")

            return True
        except Exception as e:
            print(f"Error checking status: {str(e)}")
            return False

    def commit(self, message):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        # Cargar archivos en staging
        if os.path.exists(INDEX_FILE):
            with open(INDEX_FILE, "r") as f:
                self.staged_files = json.load(f)
        
        if not self.staged_files:
            print("No changes staged for commit.")
            return False

        # Get current branch and last commit
        with open(HEAD_FILE, "r") as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith("ref: "):
            branch = head_ref.split("/")[-1]
            branch_file = os.path.join(HEADS_DIR, branch)
            parent = None
            if os.path.exists(branch_file):
                with open(branch_file, "r") as f:
                    parent = f.read().strip()
        else:
            parent = head_ref

        # Get author from config
        author = "unknown"
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                config = json.load(f)
                author = config.get("author", "unknown")

        # Create tree object
        tree_hash = hashlib.sha1(json.dumps(self.staged_files).encode()).hexdigest()
        tree_path = os.path.join(OBJECTS_DIR, tree_hash)
        with open(tree_path, "w") as f:
            json.dump(self.staged_files, f)

        # Create commit - asegurando que la ruta existe
        commit = Commit(message, author, parent, tree_hash)
        commit_path = os.path.join(OBJECTS_DIR, commit.hash)
        
        # Crear directorio si no existe (por si acaso)
        os.makedirs(os.path.dirname(commit_path), exist_ok=True)
        
        with open(commit_path, "w") as f:
            json.dump(commit.to_dict(), f)

        # Update branch reference
        with open(branch_file, "w") as f:
            f.write(commit.hash)

        # Clear staging area
        self.staged_files = {}
        if os.path.exists(INDEX_FILE):
            os.remove(INDEX_FILE)

        print(f"[{branch} {commit.hash[:7]}] {message}")
        return True

    def log(self):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        with open(HEAD_FILE, "r") as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith("ref: "):
            branch = head_ref.split("/")[-1]
            branch_file = os.path.join(HEADS_DIR, branch)
            if not os.path.exists(branch_file):
                print("No commits yet.")
                return False  # Cambiado de return False a return True
            
            with open(branch_file, "r") as f:
                commit_hash = f.read().strip()
        else:
            commit_hash = head_ref

        if not commit_hash:  # Si no hay commit hash
            print("No commits yet.")
            return False

        found_commits = False
        while commit_hash:
            commit_path = os.path.join(OBJECTS_DIR, commit_hash)
            if not os.path.exists(commit_path):
                break

            with open(commit_path, "r") as f:
                commit_data = json.load(f)

            print(f"commit {commit_data['hash']}")
            print(f"Author: {commit_data['author']}")
            print(f"Date:   {commit_data['timestamp']}")
            print(f"\n    {commit_data['message']}\n")

            commit_hash = commit_data["parent"]
            found_commits = True

        if not found_commits:
            print("No commits yet.")
            return False
            
        return True
    
    def create_branch(self, branch_name, start_point=None):
        """Crea una nueva rama pero no cambia a ella"""
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        # Verificar si la rama ya existe
        branch_file = os.path.join(HEADS_DIR, branch_name)
        if os.path.exists(branch_file):
            print(f"Branch '{branch_name}' already exists.")
            return False

        # Obtener el commit de inicio (start_point)
        if start_point:
            # Verificar si es un tag
            tag_file = os.path.join(TAGS_DIR, start_point)
            if os.path.exists(tag_file):
                with open(tag_file, "r") as f:
                    commit_hash = f.read().strip()
            else:
                # Verificar si es un commit hash o nombre de rama
                commit_path = os.path.join(OBJECTS_DIR, start_point)
                if os.path.exists(commit_path):
                    commit_hash = start_point
                else:
                    # Verificar si es una rama existente
                    other_branch_file = os.path.join(HEADS_DIR, start_point)
                    if os.path.exists(other_branch_file):
                        with open(other_branch_file, "r") as f:
                            commit_hash = f.read().strip()
                    else:
                        print(f"error: unknown revision or path '{start_point}'")
                        return False
        else:
            # Usar el commit actual
            with open(HEAD_FILE, "r") as f:
                head_ref = f.read().strip()
            
            if head_ref.startswith("ref: "):
                current_branch = head_ref.split("/")[-1]
                with open(os.path.join(HEADS_DIR, current_branch), "r") as f:
                    commit_hash = f.read().strip()
            else:
                commit_hash = head_ref

        # Crear la nueva rama
        with open(branch_file, "w") as f:
            f.write(commit_hash)
        
        print(f"Created branch '{branch_name}'")
        return True
    
    def create_branch(self, branch_name, start_point=None):
        """Crea una nueva rama pero no cambia a ella"""
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        # Verificar si la rama ya existe
        branch_file = os.path.join(HEADS_DIR, branch_name)
        if os.path.exists(branch_file):
            print(f"Branch '{branch_name}' already exists.")
            return False

        # Obtener el commit de inicio (start_point)
        if start_point:
            # Verificar si es un tag
            tag_file = os.path.join(TAGS_DIR, start_point)
            if os.path.exists(tag_file):
                with open(tag_file, "r") as f:
                    commit_hash = f.read().strip()
            else:
                # Verificar si es un commit hash o nombre de rama
                commit_path = os.path.join(OBJECTS_DIR, start_point)
                if os.path.exists(commit_path):
                    commit_hash = start_point
                else:
                    # Verificar si es una rama existente
                    other_branch_file = os.path.join(HEADS_DIR, start_point)
                    if os.path.exists(other_branch_file):
                        with open(other_branch_file, "r") as f:
                            commit_hash = f.read().strip()
                    else:
                        print(f"error: unknown revision or path '{start_point}'")
                        return False
        else:
            # Usar el commit actual
            with open(HEAD_FILE, "r") as f:
                head_ref = f.read().strip()
            
            if head_ref.startswith("ref: "):
                current_branch = head_ref.split("/")[-1]
                with open(os.path.join(HEADS_DIR, current_branch), "r") as f:
                    commit_hash = f.read().strip()
            else:
                commit_hash = head_ref

        # Crear la nueva rama
        with open(branch_file, "w") as f:
            f.write(commit_hash)
        
        print(f"Created branch '{branch_name}'")
        return True
    
    def list_branches(self):
        """Lista todas las ramas disponibles"""
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        if not os.path.exists(HEADS_DIR):
            print("No branches found.")
            return False

        branches = os.listdir(HEADS_DIR)
        if not branches:
            print("No branches found.")
            return False

        # Obtener rama actual
        current_branch = None
        with open(HEAD_FILE, "r") as f:
            head_ref = f.read().strip()
            if head_ref.startswith("ref: "):
                current_branch = head_ref.split("/")[-1]

        print("Branches:")
        for branch in sorted(branches):
            prefix = "* " if branch == current_branch else "  "
            print(f"{prefix}{branch}")

        return True

    def delete_branch(self, branch_name):
        """Elimina una rama"""
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        if branch_name == "master":
            print("error: Cannot delete branch 'master'")
            return False

        branch_file = os.path.join(HEADS_DIR, branch_name)
        if not os.path.exists(branch_file):
            print(f"error: branch '{branch_name}' not found.")
            return False

        # Verificar si estamos en la rama que queremos eliminar
        with open(HEAD_FILE, "r") as f:
            head_ref = f.read().strip()
            if head_ref == f"ref: refs/heads/{branch_name}":
                print(f"error: Cannot delete branch '{branch_name}' because you are on it.")
                return False

        os.remove(branch_file)
        print(f"Deleted branch {branch_name}")
        return True

    def checkout(self, branch_or_commit):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        # Check if it's a branch
        branch_file = os.path.join(HEADS_DIR, branch_or_commit)
        if os.path.exists(branch_file):
            with open(HEAD_FILE, "w") as f:
                f.write(f"ref: refs/heads/{branch_or_commit}")
            self.current_branch = branch_or_commit
            print(f"Switched to branch '{branch_or_commit}'")
            return True

        # Check if it's a commit hash
        commit_path = os.path.join(OBJECTS_DIR, branch_or_commit)
        if os.path.exists(commit_path) and not os.path.isdir(commit_path):
            with open(HEAD_FILE, "w") as f:
                f.write(branch_or_commit)
            print(f"HEAD is now at {branch_or_commit[:7]}")
            return True

        # Check if it's a tag
        tag_file = os.path.join(TAGS_DIR, branch_or_commit)
        if os.path.exists(tag_file):
            with open(tag_file, "r") as f:
                commit_hash = f.read().strip()
            with open(HEAD_FILE, "w") as f:
                f.write(commit_hash)
            print(f"HEAD is now at tag '{branch_or_commit}' ({commit_hash[:7]})")
            return True

        print(f"error: pathspec '{branch_or_commit}' did not match any branch, commit or tag")
        return False

    def tag(self, tag_name):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        with open(HEAD_FILE, "r") as f:
            head_ref = f.read().strip()
        
        if head_ref.startswith("ref: "):
            branch = head_ref.split("/")[-1]
            branch_file = os.path.join(HEADS_DIR, branch)
            with open(branch_file, "r") as f:
                commit_hash = f.read().strip()
        else:
            commit_hash = head_ref

        tag_file = os.path.join(TAGS_DIR, tag_name)
        with open(tag_file, "w") as f:
            f.write(commit_hash)

        print(f"Created tag '{tag_name}' at {commit_hash[:7]}")
        return True

    def list_tags(self):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        if not os.path.exists(TAGS_DIR):
            print("No tags found.")
            return False

        tags = os.listdir(TAGS_DIR)
        if not tags:
            print("No tags found.")
            return False

        print("Tags:")
        for tag in tags:
            with open(os.path.join(TAGS_DIR, tag), "r") as f:
                commit_hash = f.read().strip()
            print(f"{tag} ({commit_hash[:7]})")

        return True

    def diff_commits(self, commit1, commit2):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        def get_files_from_commit(commit_hash):
            commit_path = os.path.join(OBJECTS_DIR, commit_hash)
            if not os.path.exists(commit_path):
                return None

            with open(commit_path, "r") as f:
                commit_data = json.load(f)
            
            tree_path = os.path.join(OBJECTS_DIR, commit_data["tree"])
            with open(tree_path, "r") as f:
                return json.load(f)

        files1 = get_files_from_commit(commit1)
        files2 = get_files_from_commit(commit2)

        if not files1 or not files2:
            print("Invalid commit hashes.")
            return False

        all_files = set(files1.keys()).union(set(files2.keys()))
        for file in sorted(all_files):
            hash1 = files1.get(file)
            hash2 = files2.get(file)

            if hash1 == hash2:
                continue

            print(f"Changes in {file}:")
            if not hash1:
                print(f"  File added in {commit2[:7]}")
                continue
            if not hash2:
                print(f"  File removed in {commit2[:7]}")
                continue

            # Compare file contents
            path1 = os.path.join(OBJECTS_DIR, hash1)
            path2 = os.path.join(OBJECTS_DIR, hash2)

            with open(path1, "r") as f:
                content1 = f.read().splitlines()
            with open(path2, "r") as f:
                content2 = f.read().splitlines()

            diff = difflib.unified_diff(
                content1, content2,
                fromfile=f"{file} ({commit1[:7]})",
                tofile=f"{file} ({commit2[:7]})",
                lineterm=""
            )
            print("\n".join(diff))

        return True

    def diff_tags(self, tag1, tag2):
        if not os.path.exists(SBAC_DIR):
            print("Not a SBAC repository. Run 'sbac init' first.")
            return False

        tag1_file = os.path.join(TAGS_DIR, tag1)
        tag2_file = os.path.join(TAGS_DIR, tag2)

        if not os.path.exists(tag1_file) or not os.path.exists(tag2_file):
            print("One or both tags not found.")
            return False

        with open(tag1_file, "r") as f:
            commit1 = f.read().strip()
        with open(tag2_file, "r") as f:
            commit2 = f.read().strip()

        print(f"Comparing changes between tag '{tag1}' and '{tag2}':")
        return self.diff_commits(commit1, commit2)