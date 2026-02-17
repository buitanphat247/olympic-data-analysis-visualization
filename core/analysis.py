import pandas as pd
import numpy as np
from pathlib import Path
from typing import Optional

class DataAnalysis:
    def __init__(self, dataframe: pd.DataFrame):
        self.dataframe = dataframe

    def analyze_data_overview(self):
        overview = {}
        # Tổng số vận động viên (ID duy nhất)
        overview["total_athletes"] = self.dataframe["ID"].nunique()
        # Tổng số quốc gia (NOC duy nhất)
        overview["total_countries"] = self.dataframe["NOC"].nunique()
        # Tổng số kỳ Olympic (Year duy nhất)
        overview["total_olympic_games"] = self.dataframe["Year"].nunique()
        # Tổng số môn thể thao
        overview["total_sports"] = self.dataframe["Sport"].nunique()
        # Tổng số huy chương (không tính No Medal)
        if "Medal" in self.dataframe.columns:
            overview["total_medals"] = (
                self.dataframe[self.dataframe["Medal"] != "No Medal"]["Medal"].count()
            )
        else:
            overview["total_medals"] = 0
        return overview

    def analyze_data_by_gender(self):
        result = {}
        # Số lượng vận động viên theo giới tính
        gender_counts = self.dataframe["Sex"].value_counts()

        # Tỷ lệ %
        gender_percentage = (
            self.dataframe["Sex"].value_counts(normalize=True) * 100
        ).round(2)

        # Số huy chương theo giới tính (không tính No Medal)
        if "Medal" in self.dataframe.columns:
            medal_by_gender = (
                self.dataframe[self.dataframe["Medal"] != "No Medal"]
                .groupby("Sex")["Medal"]
                .count()
            )
        else:
            medal_by_gender = None

        result["gender_counts"] = gender_counts
        result["gender_percentage"] = gender_percentage
        result["medal_by_gender"] = medal_by_gender

        return result
  

    # =====================================================
    #  MEDAL ANALYSIS
    # =====================================================

    def medal_count(self):
        """Tổng số Gold / Silver / Bronze"""
        return self.dataframe[self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"])]["Medal"].value_counts()

    def medals_by_country(self):
        """Top quốc gia nhiều huy chương"""
        return (
            self.dataframe[self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"])]
            .groupby("NOC")["Medal"]
            .count()
            .sort_values(ascending=False)
        )

    def country_most_gold(self):
        """Quốc gia nhiều Gold nhất"""
        gold = self.dataframe[self.dataframe["Medal"] == "Gold"]
        return gold.groupby("NOC")["Medal"].count().sort_values(ascending=False)

    def medals_by_year(self):
        """Huy chương theo năm"""
        return (
            self.dataframe[self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"])]
            .groupby("Year")["Medal"]
            .count()
        )

    def medals_by_sport(self):
        """Huy chương theo môn"""
        return (
            self.dataframe[self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"])]
            .groupby("Sport")["Medal"]
            .count()
            .sort_values(ascending=False)
        )

    def medal_tally_table(self):
        """Bảng tổng sắp huy chương (pivot table)"""
        subset = self.dataframe[self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"])]
        medal_table = subset.pivot_table(
            index="NOC",
            columns="Medal",
            values="Event",
            aggfunc="count",
            fill_value=0
        )
        medal_table["Total"] = medal_table.sum(axis=1)
        return medal_table.sort_values("Gold", ascending=False)

    # =====================================================
    #  AGE ANALYSIS
    # =====================================================

    def age_summary(self):
        """Tuổi trung bình / min / max"""
        return {
            "mean": round(self.dataframe["Age"].mean(), 2),
            "min": self.dataframe["Age"].min(),
            "max": self.dataframe["Age"].max()
        }

    def age_group_distribution(self):
        """Nhóm tuổi (U20, 20–30…)"""
        bins = [0, 20, 30, 40, 50, 100]
        labels = ["U20", "20-30", "30-40", "40-50", "Over 50"]
        temp = self.dataframe.dropna(subset=["Age"]).copy()
        temp["AgeGroup"] = pd.cut(temp["Age"], bins=bins, labels=labels, right=False)
        return temp["AgeGroup"].value_counts()

    def medal_ratio_by_age_group(self):
        """Tỷ lệ đạt huy chương theo tuổi"""
        temp = self.dataframe.dropna(subset=["Age"]).copy()
        bins = [0, 20, 30, 40, 50, 100]
        labels = ["U20", "20-30", "30-40", "40-50", "Over 50"]
        temp["AgeGroup"] = pd.cut(temp["Age"], bins=bins, labels=labels, right=False)

        participants = temp.groupby("AgeGroup")["ID"].nunique()
        medals = temp[temp["Medal"].isin(["Gold", "Silver", "Bronze"])].groupby("AgeGroup")["Medal"].count()

        ratio = (medals / participants).fillna(0)
        return ratio.round(4)

    def average_age_gold(self):
        """Tuổi trung bình người đạt Gold"""
        return round(
            self.dataframe[self.dataframe["Medal"] == "Gold"]["Age"].mean(), 2
        )

    # =====================================================
    #  PHYSIQUE ANALYSIS
    # =====================================================

    def physique_by_sport(self):
        """Chiều cao, cân nặng, BMI trung bình theo môn"""
        valid = self.dataframe.dropna(subset=["Height", "Weight"])
        stats = valid.groupby("Sport")[["Height", "Weight"]].mean()
        stats["BMI"] = stats["Weight"] / ((stats["Height"] / 100) ** 2)
        return stats.sort_values("Weight", ascending=False).round(2)

    def medal_vs_non_medal_physique(self):
        """So sánh thể chất người đạt huy chương vs không đạt"""
        valid = self.dataframe.dropna(subset=["Height", "Weight"])
        valid["MedalStatus"] = np.where(
            valid["Medal"].isin(["Gold", "Silver", "Bronze"]),
            "Medalist",
            "Non-Medalist"
        )
        result = valid.groupby("MedalStatus")[["Height", "Weight"]].mean()
        result["BMI"] = result["Weight"] / ((result["Height"] / 100) ** 2)
        return result.round(2)

    # =====================================================
    #  COUNTRY ANALYSIS
    # =====================================================

    def medals_by_country_year(self):
        """Huy chương theo quốc gia từng năm"""
        return (
            self.dataframe[self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"])]
            .groupby(["Year", "NOC"])["Medal"]
            .count()
            .reset_index(name="Medal_Count")
        )

    def country_performance(self, noc_code):
        """Thành tích theo năm của 1 quốc gia"""
        country_dataframe = self.dataframe[
            (self.dataframe["NOC"] == noc_code) &
            (self.dataframe["Medal"].isin(["Gold", "Silver", "Bronze"]))
        ]
        return (
            country_dataframe.groupby("Year")["Medal"]
            .count()
            .reset_index(name="Medal_Count")
        )

    def host_country_years(self, city_to_noc):
        """Danh sách năm làm chủ nhà"""
        host_dataframe = self.dataframe[self.dataframe["City"].map(city_to_noc).notna()]
        return host_dataframe.groupby("City")["Year"].unique()

    def vietnam_analysis(self):
        """Phân tích riêng Việt Nam"""
        dataframe_vn = self.dataframe[self.dataframe["NOC"] == "VIE"]
        if dataframe_vn.empty:
            return None

        medal_count = dataframe_vn[dataframe_vn["Medal"].isin(["Gold", "Silver", "Bronze"])].shape[0]
        athlete_count = dataframe_vn["ID"].nunique()

        return {
            "Total Athletes": athlete_count,
            "Total Medals": medal_count
        }

    # =====================================================
    #  INGEST: chạy full phân tích và xuất CSV
    # =====================================================

    def _save_result(self, obj, filepath: Path, index: bool = False):
        """Ghi kết quả (DataFrame, Series, dict) ra CSV."""
        if obj is None:
            return
        if isinstance(obj, pd.DataFrame):
            obj.to_csv(filepath, index=index)
        elif isinstance(obj, pd.Series):
            obj.to_frame().to_csv(filepath, index=True)
        elif isinstance(obj, dict):
            pd.DataFrame([obj]).to_csv(filepath, index=False)
        else:
            pd.DataFrame([{"value": obj}]).to_csv(filepath, index=False)
        print(f"  Saved: {filepath.name}")

    def ingest(
        self,
        output_dir: str = "output/csv/analysis",
        top_noc_count: int = 20,
    ) -> "DataAnalysis":
        root_dir = Path(__file__).resolve().parent.parent
        out_path = root_dir / output_dir
        out_path.mkdir(parents=True, exist_ok=True)
        print(f"Analysis output folder: {out_path}")

        # 1. Overview -> output/csv/overview/
        overview_path = out_path / "overview"
        overview_path.mkdir(parents=True, exist_ok=True)
        self._save_result(
            pd.DataFrame([self.analyze_data_overview()]),
            overview_path / "overview.csv",
        )

        # 2. Gender -> output/csv/gender/
        gender_path = out_path / "gender"
        gender_path.mkdir(parents=True, exist_ok=True)
        gender = self.analyze_data_by_gender()
        if gender.get("gender_counts") is not None:
            gender["gender_counts"].to_frame("count").to_csv(gender_path / "gender_counts.csv", index=True)
            print(f"  Saved: gender/gender_counts.csv")
        if gender.get("gender_percentage") is not None:
            gender["gender_percentage"].to_frame("percentage").to_csv(gender_path / "gender_percentage.csv", index=True)
            print(f"  Saved: gender/gender_percentage.csv")
        if gender.get("medal_by_gender") is not None:
            gender["medal_by_gender"].to_frame("medal_count").to_csv(gender_path / "medal_by_gender.csv", index=True)
            print(f"  Saved: gender/medal_by_gender.csv")

        # 3. Medal -> output/csv/medal/
        medal_path = out_path / "medal"
        medal_path.mkdir(parents=True, exist_ok=True)
        self._save_result(self.medal_count(), medal_path / "medal_count.csv", index=True)
        self._save_result(self.medals_by_country(), medal_path / "medals_by_country.csv", index=True)
        self._save_result(self.country_most_gold(), medal_path / "country_most_gold.csv", index=True)
        self._save_result(self.medals_by_year(), medal_path / "medals_by_year.csv", index=True)
        self._save_result(self.medals_by_sport(), medal_path / "medals_by_sport.csv", index=True)
        self._save_result(self.medal_tally_table(), medal_path / "medal_tally_table.csv", index=True)

        # 4. Age -> output/csv/age/
        age_path = out_path / "age"
        age_path.mkdir(parents=True, exist_ok=True)
        self._save_result(pd.DataFrame([self.age_summary()]), age_path / "age_summary.csv")
        self._save_result(self.age_group_distribution(), age_path / "age_group_distribution.csv", index=True)
        self._save_result(self.medal_ratio_by_age_group(), age_path / "medal_ratio_by_age_group.csv", index=True)
        self._save_result(pd.DataFrame([{"average_age_gold": self.average_age_gold()}]), age_path / "average_age_gold.csv")

        # 5. Physique -> output/csv/physique/
        physique_path = out_path / "physique"
        physique_path.mkdir(parents=True, exist_ok=True)
        self._save_result(self.physique_by_sport(), physique_path / "physique_by_sport.csv", index=True)
        self._save_result(self.medal_vs_non_medal_physique(), physique_path / "medal_vs_non_medal_physique.csv", index=True)

        # 6. Country -> output/csv/country/
        country_path = out_path / "country"
        country_path.mkdir(parents=True, exist_ok=True)
        self._save_result(self.medals_by_country_year(), country_path / "medals_by_country_year.csv")
        try:
            top_noc = self.medals_by_country().head(top_noc_count).index.tolist()
            for noc in top_noc:
                perf = self.country_performance(noc)
                safe_name = noc.replace("/", "_").replace("\\", "_")
                self._save_result(perf, country_path / f"country_performance_{safe_name}.csv")
        except Exception:
            pass

        # 7. Vietnam -> output/csv/vietnam/
        vietnam_path = out_path / "vietnam"
        vietnam_path.mkdir(parents=True, exist_ok=True)
        vn = self.vietnam_analysis()
        if vn is not None:
            self._save_result(pd.DataFrame([vn]), vietnam_path / "vietnam_analysis.csv")

        print("Ingest done: all analysis CSVs written in subfolders.")
        return self