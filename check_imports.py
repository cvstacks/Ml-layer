import os
import sys
import importlib.util

def check_imports(directory):
    sys.path.insert(0, directory)
    has_errors = False
    
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py") and file != "check_imports.py":
                file_path = os.path.join(root, file)
                module_name = os.path.splitext(os.path.relpath(file_path, directory))[0].replace(os.path.sep, ".")
                
                try:
                    spec = importlib.util.spec_from_file_location(module_name, file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                except ImportError as e:
                    print(f"Import error in {file_path}: {e}")
                    has_errors = True
                except Exception as e:
                    # Catch other errors that might occur during import (like SyntaxError, which shouldn't happen, or runtime errors at module level)
                    pass 

    if not has_errors:
        print("No import errors found.")

if __name__ == "__main__":
    check_imports(r"d:\CvStack")
