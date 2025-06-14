"""
Main function of the profiler
"""
import os
import sys

from inject_profiler import inject_all, restore_backups


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Inject: python inject_profiler.py <project_dir>")
        print("  Restore: python inject_profiler.py <project_dir> restore")
        sys.exit(1)

    provided_base_dir: str = os.path.abspath(sys.argv[1])
     
    generated_internal_dir: str = os.path.join(provided_base_dir, "profiler_internal_files")
    generated_backup_dir: str = os.path.join(generated_internal_dir, "backup")

    if len(sys.argv) == 3 and sys.argv[2] == "restore":
        restore_backups(provided_base_dir, generated_backup_dir, generated_internal_dir)
    else:
        inject_all(provided_base_dir)
