import sys
import os
from pathlib import Path
import pandas as pd

class FileManager:
    def __init__(self,file_path):
        self.file_path = self.find_root_file(file_path)

    def find_root_file(self,file_path):
        currrent_dir = Path(__file__).resolve().parent
        for parent in [currrent_dir] + list(currrent_dir.parents):
            candidate = parent / file_path
            if candidate.exists():
                return candidate
        raise FileNotFoundError(f"File {file_path} not found")

    def read_file(self):
       try:
            return pd.read_csv(self.file_path)
       except Exception as e:
            print(f"Error reading file {self.file_path}: {e}")
            return None

    def save_data(self, dataFrame, relative_path):
    # Lấy root project (BTL_PYTHON)
        root_dir = Path(__file__).resolve().parent.parent

        full_path = root_dir / relative_path

        # Tạo folder nếu chưa có
        full_path.parent.mkdir(parents=True, exist_ok=True)

        dataFrame.to_csv(full_path, index=False)

        print(f"Saved to: {full_path}")
    
    