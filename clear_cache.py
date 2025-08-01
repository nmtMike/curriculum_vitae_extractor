import os
import shutil

def clear_python_cache(directory):
    for root, dirs, files in os.walk(directory):
        if '__pycache__' in dirs:
            cache_path = os.path.join(root, '__pycache__')
            print(f"Deleting: {cache_path}")
            shutil.rmtree(cache_path)
        for file in files:
            if file.endswith('.pyc'):
                pyc_path = os.path.join(root, file)
                print(f"Deleting: {pyc_path}")
                os.remove(pyc_path)

# Example usage: clear cache in the current directory
clear_python_cache('.')