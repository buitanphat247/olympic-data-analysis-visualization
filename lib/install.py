import subprocess
import sys
import os
from pathlib import Path


class RequirementsInstaller:
    def __init__(self,file_name="requirements.txt"):
        self.requirements_path = self.find_root_file(file_name)

    def find_root_file(self,file_name):
        current = Path(__file__).resolve()
        for parent in [current] + list(current.parents):
            file_path = parent / file_name
            if file_path.exists():
                return file_path
        raise FileNotFoundError(f"File {file_name} not found")


    def check_file_exists(self):
        return self.requirements_path.exists()

    def install_packages(self):
        if not self.check_file_exists():
            return False
        try:
            # comment: install packages from requirements.txt
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(self.requirements_path)])
            print(f"Packages installed successfully from {self.requirements_path}")
        except Exception as e:
            print(f"Error installing packages from {self.requirements_path}: {e}")
        # end try


