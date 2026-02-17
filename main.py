"""
Pipeline chính: cài package → đọc data → làm sạch → phân tích → trực quan hóa → (tùy chọn) bật web Dash.
Chạy: python main.py
      python main.py --no-web   (chỉ chạy pipeline, không mở Dash)
"""

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

# step 0: cài packages từ requirements.txt (lib/requirements.txt)
from lib import install
installer = install.RequirementsInstaller()
installer.install_packages()

from core import file, data_cleaner, analysis, visualization

# step 1: set up file manager and read file
file_manager = file.FileManager("data/athlete_events.csv")
dataFrame = file_manager.read_file()

# step 2: clean data
cleaner = data_cleaner.DataCleaner(dataFrame)
cleaner.run_full_olympic_cleaning()

# step 3: save data
dataFrame = cleaner.get_data()
file_manager.save_data(dataFrame, "output/csv/cleaned_data.csv")

# step 4: analysis data + chạy full phân tích và lưu CSV vào output/csv
data_analysis = analysis.DataAnalysis(dataFrame)
data_analysis.ingest(output_dir="output/csv")

# step 5: visualization - xuất biểu đồ vào output/chart
vis = visualization.Visualization(data_analysis)
vis.run_all(output_dir=Path("output/chart"))

# step 6: (tùy chọn) Bật web Dash với animation mượt mà
def main():
    parser = argparse.ArgumentParser(description="BTL Olympic: pipeline + web Dash")
    parser.add_argument("--no-web", action="store_true", help="Chỉ chạy pipeline, không mở Dash")
    args = parser.parse_args()

    if args.no_web:
        print("Đã xong pipeline. Bật web sau với: python app_dash.py")
        return

    root = Path(__file__).resolve().parent
    proc = subprocess.Popen(
        [sys.executable, "app_dash.py"],
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    time.sleep(7)
    if proc.poll() is not None:
        err = proc.stderr.read() or proc.stdout.read()
        print("❌ Dash thoát ngay. Chạy trong terminal:")
        print("   cd", root)
        print("   ", sys.executable, "app_dash.py")
        if err:
            print("\n--- Lỗi ---\n", err)
    else:
        webbrowser.open("http://127.0.0.1:8050")
        print("✅ Web Dash đã bật: http://127.0.0.1:8050")
        print("   (Animation mượt mà khi thay đổi bộ lọc!)")


if __name__ == "__main__":
    main()
