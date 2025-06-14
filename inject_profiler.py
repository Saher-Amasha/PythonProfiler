"""
Code responsible for injecting the decorator into all .py files
"""

import os
import sys
import ast
import shutil
import astor

# Constant strings for marker and import line

INJECTION_MARKER: str = "# PROFILER_INJECTED"

# Excluded directories and files from injection process
EXCLUDED_DIRS = {
    "venv",
    "__pycache__",
    "site-packages",
    "env",
    ".venv",
    ".git",
    "profiler_internal_files",
}
EXCLUDED_FILES = {"__init__.py", "setup.py", "profiler.py"}


class DecoratorInjector(ast.NodeTransformer):
    """
    AST Transformer that injects the @profile decorator
    into every function and async function.
    """

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef: # pylint: disable=invalid-name
        """
        Visits all functions in the module
        """
        if not any(
            isinstance(d, ast.Name) and d.id == "profile" for d in node.decorator_list
        ):
            node.decorator_list.insert(0, ast.Name(id="profile", ctx=ast.Load()))
        return self.generic_visit(node)

    def visit_AsyncFunctionDef( # pylint: disable=invalid-name
        self, node: ast.AsyncFunctionDef
    ) -> ast.AsyncFunctionDef:
        """
        Visits all async functions in the module
        """
        if not any(
            isinstance(d, ast.Name) and d.id == "profile" for d in node.decorator_list
        ):
            node.decorator_list.insert(0, ast.Name(id="profile", ctx=ast.Load()))
        return self.generic_visit(node)


def should_process_file(filepath: str) -> bool:
    """
    Determine if the file should be processed:
    - Python file (.py)
    - Not in excluded files
    - Not already injected (check marker)
    """
    filename = os.path.basename(filepath)
    if filename in EXCLUDED_FILES or not filename.endswith(".py"):
        return False
    with open(filepath, "r", encoding="utf-8") as f:
        first_line = f.readline()
        if first_line.strip() == INJECTION_MARKER:
            return False
    return True


def copy_profiler_module(base_dir: str) -> None:
    """
    Copy profiler.py into the target project directory if not already exists.
    """
    dest_profiler_path = os.path.join(base_dir, "profiler.py")
    if os.path.exists(dest_profiler_path):
        print("profiler.py already exists in target project, skipping copy.")
        return

    # Determine path of this script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_profiler_path = os.path.join(current_dir, "profiler.py")

    if not os.path.exists(src_profiler_path):
        print("ERROR: Cannot find profiler.py next to injector!")
        sys.exit(1)

    shutil.copy2(src_profiler_path, dest_profiler_path)
    print(f"Copied profiler.py into {base_dir}")

def copy_file(base_dir: str,file_name) -> None:
    """
    Copy profiler.py into the target project directory if not already exists.
    """
    dest_profiler_path = os.path.join(base_dir, file_name)
    if os.path.exists(dest_profiler_path):
        print("file_name already exists in target project, skipping copy.")
        return

    # Determine path of this script's directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_profiler_path = os.path.join(current_dir, file_name)

    if not os.path.exists(src_profiler_path):
        print(f"ERROR: Cannot find {file_name} next to injector!")
        sys.exit(1)

    shutil.copy2(src_profiler_path, dest_profiler_path)
    print(f"Copied profiler.py into {base_dir}")


def backup_file(filepath: str, base_dir: str, backup_dir: str) -> None:
    """
    Backup the file to the backup directory before modification.
    """
    rel_path = os.path.relpath(filepath, base_dir)
    backup_path = os.path.join(backup_dir, rel_path)
    os.makedirs(os.path.dirname(backup_path), exist_ok=True)
    shutil.copy2(filepath, backup_path)


def process_file(filepath: str, profiler_import: str) -> None:
    """
    Parse file, inject decorators, backup, and overwrite file.
    """

    with open(filepath, "r", encoding="utf-8") as f:
        source = f.read()

    try:
        tree = ast.parse(source)
    except SyntaxError:
        print(f"Skipping invalid file (syntax error): {filepath}")
        return

    injector = DecoratorInjector()
    new_tree = injector.visit(tree)
    new_source = astor.to_source(new_tree)

    # Inject marker and import on top
    new_source = INJECTION_MARKER + "\n" + profiler_import + "\n" + new_source

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_source)

    print(f"Injected: {filepath}")


def restore_backups(base_dir: str, backup_dir: str, internal_dir: str) -> None:
    """
    Restore all backed-up files from backup directory to original state.
    """
    if not os.path.exists(backup_dir):
        print("No backup found.")
        return
    for root, _, files in os.walk(backup_dir):
        for file in files:
            src_path = os.path.join(root, file)
            rel_path = os.path.relpath(src_path, backup_dir)
            dest_path = os.path.join(base_dir, rel_path)
            shutil.copy2(src_path, dest_path)
            print(f"Restored: {dest_path}")
    shutil.rmtree(internal_dir)


def create_backup_all(internal_files: str, base_dir: str):
    """creates a backup for all files pre modification"""
    # Handle backup
    backup_dir = os.path.join(internal_files, "backup")
    os.makedirs(backup_dir, exist_ok=True)

    original_files = []
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            if should_process_file(full_path) and os.path.abspath(
                full_path
            ) != os.path.abspath(__file__):
                original_files.append((full_path, base_dir, backup_dir))

    for filepath, c_base_dir, backup_dir in original_files:
        backup_file(filepath, c_base_dir, backup_dir)


def inject_all(base_dir_path: str) -> None:
    """
    Walk through entire project directory and inject profiling
    into all eligible Python files.
    """
    # create internal dir
    internal_files_dir_name = "profiler_internal_files"
    internal_files_path = os.path.join(base_dir_path, internal_files_dir_name)
    os.makedirs(internal_files_path, exist_ok=True)

    # Add profiler code
    copy_profiler_module(internal_files_path)

    # Add ui code
    copy_file(base_dir_path,"profiler.js")
    copy_file(base_dir_path,"index.html")
    # create backup
    create_backup_all(internal_files_path, base_dir_path)

    # inject all files with decorator
    profiler_import: str = f"from {internal_files_dir_name}.profiler import profile"

    for root, dirs, files in os.walk(base_dir_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIRS]
        for file in files:
            full_path = os.path.join(root, file)
            if should_process_file(full_path) and os.path.abspath(
                full_path
            ) != os.path.abspath(__file__):
                process_file(full_path, profiler_import)
