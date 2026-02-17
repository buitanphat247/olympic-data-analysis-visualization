"""
Module trực quan hóa dữ liệu Olympic bằng matplotlib.
Nhận DataAnalysis, vẽ các biểu đồ thống kê và lưu ra file ảnh.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator
import numpy as np
from pathlib import Path
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from core.analysis import DataAnalysis


# Màu Olympic: vàng, bạc, đồng (đậm, dễ nhìn)
COLORS = {
    "Gold": "#E6B800",
    "Silver": "#9CA3AF",
    "Bronze": "#B45309",
}

# Bảng màu đậm cho biểu đồ
PALETTE = {
    "blue": "#1E40AF",
    "orange": "#C2410C",
    "teal": "#0D9488",
    "purple": "#6D28D9",
    "coral": "#DC2626",
    "navy": "#1E3A5F",
    "gray": "#4B5563",
}


class Visualization:
    """Vẽ biểu đồ thống kê từ kết quả DataAnalysis (matplotlib)."""

    def __init__(self, data_analysis: "DataAnalysis"):
        self.analysis = data_analysis

    def _ensure_output_dir(self, output_dir: Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def _setup_grid(self, ax, minor_y=True, minor_x=False):
        """Lưới chi tiết (major + minor) để dễ đọc, khoảng cách nhỏ hơn."""
        ax.grid(True, which="major", alpha=0.5, linestyle="-", linewidth=0.8)
        ax.grid(True, which="minor", alpha=0.3, linestyle="--", linewidth=0.5)
        if minor_y:
            ax.yaxis.set_minor_locator(AutoMinorLocator(5))
        if minor_x:
            try:
                ax.xaxis.set_minor_locator(AutoMinorLocator(5))
            except Exception:
                pass

    def plot_medals_by_country(self, top_n: int = 15, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Top quốc gia theo tổng số huy chương."""
        series = self.analysis.medals_by_country().head(top_n)
        if series.empty:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(series)), series.values, color=PALETTE["navy"], edgecolor="#0F172A", linewidth=1)
        ax.set_yticks(range(len(series)))
        ax.set_yticklabels(series.index, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel("Số huy chương")
        ax.set_title("Top {} quốc gia theo tổng số huy chương".format(top_n))
        self._setup_grid(ax, minor_y=False, minor_x=True)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medals_by_country.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medal_count(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Số lượng Gold / Silver / Bronze."""
        series = self.analysis.medal_count()
        if series.empty:
            return None
        colors = [COLORS.get(k, "gray") for k in series.index]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(series.index, series.values, color=colors, edgecolor="black", linewidth=1.2)
        ax.set_ylabel("Số lượng")
        ax.set_title("Phân bố huy chương (Gold / Silver / Bronze)")
        ax.set_ylim(0, max(series.values) * 1.25)
        self._setup_grid(ax)
        for i, v in enumerate(series.values):
            ax.text(i, v + max(series.values) * 0.02, str(v), ha="center", fontsize=11)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medal_count.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medal_count_pie(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Pie chart: Tỷ lệ Gold / Silver / Bronze - trang trí đẹp."""
        series = self.analysis.medal_count()
        if series.empty:
            return None
        # Màu Olympic đẹp, rõ nét: Vàng sáng, Bạc, Đồng
        color_map = {"Gold": "#FFC107", "Silver": "#E8E8E8", "Bronze": "#CD7F32"}
        colors = [color_map.get(k, "#9CA3AF") for k in series.index]
        fig, ax = plt.subplots(figsize=(8, 8), facecolor="#FAFAFA")
        fig.patch.set_facecolor("#FAFAFA")
        ax.set_facecolor("#FAFAFA")
        explode = (0.05, 0.02, 0.05)
        wedges, texts, autotexts = ax.pie(
            series.values,
            labels=series.index,
            autopct=lambda pct: f"{pct:.1f}%",
            colors=colors[: len(series)],
            startangle=90,
            explode=explode[: len(series)],
            shadow=True,
            wedgeprops=dict(edgecolor="white", linewidth=2.5),
            textprops=dict(fontsize=14, fontweight="bold", color="#1F2937"),
            pctdistance=0.75,
            labeldistance=1.05,
        )
        for t in autotexts:
            t.set_fontsize(13)
            t.set_fontweight("bold")
            t.set_color("#1F2937")
        ax.set_title("Tỷ lệ huy chương theo loại", fontsize=16, fontweight="bold", pad=20)
        plt.tight_layout(pad=2)
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medal_count_pie.png"
            fig.savefig(path, dpi=150, bbox_inches="tight", pad_inches=0.5, facecolor="#FAFAFA", edgecolor="none")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_gender_distribution(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Số lượng VĐV theo giới tính."""
        gender = self.analysis.analyze_data_by_gender()
        counts = gender.get("gender_counts")
        if counts is None or counts.empty:
            return None
        fig, ax = plt.subplots(figsize=(5, 4))
        colors = [PALETTE["blue"], PALETTE["orange"]]
        ax.bar(counts.index.astype(str), counts.values, color=colors[: len(counts)], edgecolor="black", linewidth=1.2)
        ax.set_ylabel("Số vận động viên")
        ax.set_title("Phân bố theo giới tính")
        ax.set_ylim(0, max(counts.values) * 1.25)
        self._setup_grid(ax)
        for i, v in enumerate(counts.values):
            ax.text(i, v + max(counts.values) * 0.03, str(v), ha="center", fontsize=10)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "gender_distribution.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medals_by_gender(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Số huy chương theo giới tính."""
        gender = self.analysis.analyze_data_by_gender()
        medal_by_gender = gender.get("medal_by_gender")
        if medal_by_gender is None or medal_by_gender.empty:
            return None
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(medal_by_gender.index.astype(str), medal_by_gender.values, color=[PALETTE["blue"], PALETTE["orange"]], edgecolor="black", linewidth=1.2)
        ax.set_ylabel("Số huy chương")
        ax.set_title("Huy chương theo giới tính")
        ax.set_ylim(0, max(medal_by_gender.values) * 1.2)
        self._setup_grid(ax)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medals_by_gender.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medals_by_year(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Line chart: Số huy chương theo năm."""
        series = self.analysis.medals_by_year().sort_index()
        if series.empty:
            return None
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(series.index, series.values, marker="o", markersize=5, linewidth=2, color=PALETTE["navy"])
        ax.set_xlabel("Năm")
        ax.set_ylabel("Số huy chương")
        ax.set_title("Tổng số huy chương qua các kỳ Olympic")
        self._setup_grid(ax, minor_x=True)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medals_by_year.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medals_by_sport(self, top_n: int = 15, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Top môn thể thao theo số huy chương."""
        series = self.analysis.medals_by_sport().head(top_n)
        if series.empty:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(series)), series.values, color=PALETTE["coral"], edgecolor="#991B1B", linewidth=1)
        ax.set_yticks(range(len(series)))
        ax.set_yticklabels(series.index, fontsize=9)
        ax.invert_yaxis()
        ax.set_xlabel("Số huy chương")
        ax.set_title("Top {} môn thể thao theo số huy chương".format(top_n))
        self._setup_grid(ax, minor_y=False, minor_x=True)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medals_by_sport.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_country_most_gold(self, top_n: int = 15, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Top quốc gia nhiều huy chương Vàng nhất."""
        series = self.analysis.country_most_gold().head(top_n)
        if series.empty:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(series)), series.values, color=COLORS["Gold"], edgecolor="#92400E", linewidth=1)
        ax.set_yticks(range(len(series)))
        ax.set_yticklabels(series.index, fontsize=10)
        ax.invert_yaxis()
        ax.set_xlabel("Số huy chương Vàng")
        ax.set_title("Top {} quốc gia nhiều huy chương Vàng".format(top_n))
        self._setup_grid(ax, minor_y=False, minor_x=True)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "country_most_gold.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_age_group_distribution(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Phân bố số VĐV theo nhóm tuổi."""
        series = self.analysis.age_group_distribution()
        if series.empty:
            return None
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(series.index.astype(str), series.values, color=PALETTE["teal"], edgecolor="#0F766E", linewidth=1.2)
        ax.set_xlabel("Nhóm tuổi")
        ax.set_ylabel("Số vận động viên")
        ax.set_title("Phân bố theo nhóm tuổi")
        ax.set_ylim(0, max(series.values) * 1.15)
        self._setup_grid(ax)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "age_group_distribution.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medal_ratio_by_age_group(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: Tỷ lệ đạt huy chương theo nhóm tuổi."""
        series = self.analysis.medal_ratio_by_age_group()
        if series.empty:
            return None
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(series.index.astype(str), series.values, color=PALETTE["purple"], edgecolor="#4C1D95", linewidth=1.2)
        ax.set_xlabel("Nhóm tuổi")
        ax.set_ylabel("Tỷ lệ đạt huy chương")
        ax.set_title("Tỷ lệ đạt huy chương theo nhóm tuổi")
        ax.set_ylim(0, max(series.values) * 1.2 if series.values.max() > 0 else 1)
        self._setup_grid(ax)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medal_ratio_by_age_group.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_medal_tally_stacked(self, top_n: int = 15, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Stacked bar: Top quốc gia với Gold/Silver/Bronze chồng lớp."""
        tally = self.analysis.medal_tally_table()
        if tally.empty or "Gold" not in tally.columns:
            return None
        top = tally.head(top_n)
        x = np.arange(len(top))
        w = 0.6
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(x, top["Gold"], w, label="Gold", color=COLORS["Gold"], edgecolor="black", linewidth=0.3)
        ax.bar(x, top["Silver"], w, bottom=top["Gold"], label="Silver", color=COLORS["Silver"], edgecolor="black", linewidth=0.3)
        ax.bar(x, top["Bronze"], w, bottom=top["Gold"] + top["Silver"], label="Bronze", color=COLORS["Bronze"], edgecolor="black", linewidth=0.3)
        ax.set_xticks(x)
        ax.set_xticklabels(top.index, rotation=45, ha="right")
        ax.set_ylabel("Số huy chương")
        ax.set_title("Top {} quốc gia theo Gold / Silver / Bronze".format(top_n))
        ax.legend(loc="upper right")
        self._setup_grid(ax)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "medal_tally_stacked.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def plot_physique_medal_vs_non_medal(self, output_dir: Optional[Path] = None) -> Optional[Path]:
        """Bar chart: So sánh Chiều cao / Cân nặng / BMI giữa người đạt huy chương và không."""
        df = self.analysis.medal_vs_non_medal_physique()
        if df is None or df.empty:
            return None
        fig, ax = plt.subplots(figsize=(8, 4))
        x = np.arange(3)
        width = 0.35
        cols = ["Height", "Weight", "BMI"]
        labels = ["Chiều cao (cm)", "Cân nặng (kg)", "BMI"]
        if "Medalist" in df.index and "Non-Medalist" in df.index:
            medalist = [df.loc["Medalist", c] for c in cols]
            non_medalist = [df.loc["Non-Medalist", c] for c in cols]
        else:
            return None
        ax.bar(x - width / 2, medalist, width, label="Có huy chương", color=COLORS["Gold"], edgecolor="#92400E", linewidth=1)
        ax.bar(x + width / 2, non_medalist, width, label="Không huy chương", color=PALETTE["gray"], edgecolor="#1F2937", linewidth=1)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_ylabel("Giá trị trung bình")
        ax.set_title("Thể chất: so sánh người đạt huy chương vs không đạt")
        ax.set_ylim(0, max(max(medalist), max(non_medalist)) * 1.2)
        ax.legend()
        self._setup_grid(ax)
        plt.tight_layout()
        if output_dir is not None:
            out = self._ensure_output_dir(output_dir)
            path = out / "physique_medal_vs_non_medal.png"
            fig.savefig(path, dpi=150, bbox_inches="tight")
            plt.close(fig)
            return path
        plt.show()
        return None

    def run_all(
        self,
        output_dir: Optional[Path] = None,
        base_dir: Optional[Path] = None,
    ) -> list:
        """
        Chạy tất cả biểu đồ và lưu ra thư mục.
        Nếu base_dir None thì dùng project root / output / charts.
        """
        if base_dir is None:
            base_dir = Path(__file__).resolve().parent.parent / "output" / "charts"
        out = self._ensure_output_dir(base_dir if output_dir is None else output_dir)
        saved = []
        methods = [
            ("medals_by_country", lambda: self.plot_medals_by_country(output_dir=out)),
            ("medal_count", lambda: self.plot_medal_count(output_dir=out)),
            ("medal_count_pie", lambda: self.plot_medal_count_pie(output_dir=out)),
            ("gender_distribution", lambda: self.plot_gender_distribution(output_dir=out)),
            ("medals_by_gender", lambda: self.plot_medals_by_gender(output_dir=out)),
            ("medals_by_year", lambda: self.plot_medals_by_year(output_dir=out)),
            ("medals_by_sport", lambda: self.plot_medals_by_sport(output_dir=out)),
            ("country_most_gold", lambda: self.plot_country_most_gold(output_dir=out)),
            ("age_group_distribution", lambda: self.plot_age_group_distribution(output_dir=out)),
            ("medal_ratio_by_age_group", lambda: self.plot_medal_ratio_by_age_group(output_dir=out)),
            ("medal_tally_stacked", lambda: self.plot_medal_tally_stacked(output_dir=out)),
            ("physique_medal_vs_non_medal", lambda: self.plot_physique_medal_vs_non_medal(output_dir=out)),
        ]
        for name, fn in methods:
            try:
                path = fn()
                if path is not None:
                    saved.append(path)
                    print(f"  Saved: {path.name}")
            except Exception as e:
                print(f"  Skip {name}: {e}")
        print(f"Visualization done: {len(saved)} charts saved to {out}")
        return saved
