

import pandas as pd
import numpy as np
from typing import Optional, List, Union, Callable

try:
    from sklearn.preprocessing import StandardScaler
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class DataCleaner:
    # Định nghĩa khoảng giá trị hợp lệ cho các cột số
    VALID_RANGES = {
        "Age": (5, 100),       # Tuổi VĐV: 5-100
        "Height": (100, 250),  # Chiều cao (cm): 100-250
        "Weight": (25, 300),   # Cân nặng (kg): 25-300
        "Year": (1896, 2030),  # Năm Olympic
    }

    def __init__(self, dataFrame):
        self.dataFrame = dataFrame.copy()
        self._cleaning_log: List[str] = []

    def _log(self, msg: str):
        self._cleaning_log.append(msg)

    # ==========================
    # 1. MISSING VALUES (Giá trị thiếu)
    # ==========================

    def remove_missing_values(self, columns: Optional[List[str]] = None) -> "DataCleaner":
        """Loại bỏ các dòng có giá trị thiếu (NA)."""
        before = len(self.dataFrame)
        if columns:
            self.dataFrame = self.dataFrame.dropna(subset=columns)
        else:
            self.dataFrame = self.dataFrame.dropna()
        removed = before - len(self.dataFrame)
        self._log(f"remove_missing_values: Xóa {removed} dòng có NA")
        return self

    def fill_missing_with_mean(self, column: str) -> "DataCleaner":
        """Điền giá trị thiếu bằng giá trị trung bình (Mean)."""
        count = self.dataFrame[column].isna().sum()
        if count > 0 and pd.api.types.is_numeric_dtype(self.dataFrame[column]):
            self.dataFrame[column] = self.dataFrame[column].fillna(self.dataFrame[column].mean())
            self._log(f"fill_missing_with_mean({column}): Điền {count} giá trị")
        return self

    def fill_missing_with_median(self, column: str) -> "DataCleaner":
        """Điền giá trị thiếu bằng giá trị trung vị (Median) - ít bị ảnh hưởng bởi outlier."""
        count = self.dataFrame[column].isna().sum()
        if count > 0 and pd.api.types.is_numeric_dtype(self.dataFrame[column]):
            self.dataFrame[column] = self.dataFrame[column].fillna(self.dataFrame[column].median())
            self._log(f"fill_missing_with_median({column}): Điền {count} giá trị")
        return self

    def fill_missing_with_mode(self, column: str) -> "DataCleaner":
        """Điền giá trị thiếu bằng giá trị xuất hiện nhiều nhất (Mode)."""
        count = self.dataFrame[column].isna().sum()
        if count > 0:
            mode_val = self.dataFrame[column].mode()
            if not mode_val.empty:
                self.dataFrame[column] = self.dataFrame[column].fillna(mode_val.iloc[0])
                self._log(f"fill_missing_with_mode({column}): Điền {count} giá trị")
        return self

    def fill_missing_with_value(self, column: str, value: Union[str, int, float]) -> "DataCleaner":
        """Điền giá trị thiếu bằng giá trị cố định."""
        count = self.dataFrame[column].isna().sum()
        if count > 0:
            self.dataFrame[column] = self.dataFrame[column].fillna(value)
            self._log(f"fill_missing_with_value({column}, {value}): Điền {count} giá trị")
        return self

    def fill_missing_numeric_with_group_mean(
        self, column: str, group_by: List[str]
    ) -> "DataCleaner":
        """Điền NA bằng mean theo nhóm (VD: theo Sport, Sex)."""
        count = self.dataFrame[column].isna().sum()
        if count > 0 and pd.api.types.is_numeric_dtype(self.dataFrame[column]):
            group_mean = self.dataFrame.groupby(group_by)[column].transform("mean")
            self.dataFrame[column] = self.dataFrame[column].fillna(group_mean)
            # Nếu vẫn còn NA (nhóm không có dữ liệu), điền mean toàn cục
            self.dataFrame[column] = self.dataFrame[column].fillna(self.dataFrame[column].mean())
            self._log(f"fill_missing_numeric_with_group_mean({column}, {group_by}): Điền {count} giá trị")
        return self

    # ==========================
    # 2. DUPLICATES (Trùng lặp)
    # ==========================

    def remove_duplicates(
        self, subset: Optional[List[str]] = None, keep: str = "first"
    ) -> "DataCleaner":
        """Loại bỏ bản ghi trùng lặp. subset=None: trùng toàn bộ cột."""
        before = len(self.dataFrame)
        self.dataFrame = self.dataFrame.drop_duplicates(subset=subset, keep=keep)
        removed = before - len(self.dataFrame)
        self._log(f"remove_duplicates: Xóa {removed} dòng trùng lặp")
        return self

    # ==========================
    # 3. OUTLIERS (Giá trị ngoại lai)
    # ==========================

    def remove_outliers_iqr(self, column: str, multiplier: float = 1.5) -> "DataCleaner":
        """Loại bỏ outlier theo phương pháp IQR (Interquartile Range)."""
        Q1 = self.dataFrame[column].quantile(0.25)
        Q3 = self.dataFrame[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        before = len(self.dataFrame)
        self.dataFrame = self.dataFrame[
            (self.dataFrame[column] >= lower_bound) & (self.dataFrame[column] <= upper_bound)
        ]
        removed = before - len(self.dataFrame)
        self._log(f"remove_outliers_iqr({column}): Xóa {removed} dòng ngoại lai")
        return self

    def clip_outliers_iqr(self, column: str, multiplier: float = 1.5) -> "DataCleaner":
        """Clipping: Gán outlier về giá trị biên, không xóa (giữ kích thước mẫu)."""
        Q1 = self.dataFrame[column].quantile(0.25)
        Q3 = self.dataFrame[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - multiplier * IQR
        upper_bound = Q3 + multiplier * IQR
        count_clipped = (
            (self.dataFrame[column] < lower_bound) | (self.dataFrame[column] > upper_bound)
        ).sum()
        self.dataFrame[column] = self.dataFrame[column].clip(lower=lower_bound, upper=upper_bound)
        if count_clipped > 0:
            self._log(f"clip_outliers_iqr({column}): Clip {count_clipped} giá trị")
        return self

    def clip_to_valid_range(self, column: str) -> "DataCleaner":
        """Clip giá trị vào khoảng hợp lệ đã định nghĩa (Age, Height, Weight, Year)."""
        if column in self.VALID_RANGES:
            low, high = self.VALID_RANGES[column]
            before_invalid = (
                (self.dataFrame[column] < low) | (self.dataFrame[column] > high)
            ).sum()
            self.dataFrame[column] = self.dataFrame[column].clip(lower=low, upper=high)
            if before_invalid > 0:
                self._log(f"clip_to_valid_range({column}): Clip {before_invalid} giá trị vào [{low},{high}]")
        return self

    # ==========================
    # 4. INVALID VALUES (Giá trị không hợp lệ)
    # ==========================

    def remove_invalid_values(
        self, column: str, condition: Callable
    ) -> "DataCleaner":
        """Loại bỏ các dòng không thỏa điều kiện. condition: lambda x: x > 0."""
        before = len(self.dataFrame)
        self.dataFrame = self.dataFrame[self.dataFrame[column].apply(condition)]
        removed = before - len(self.dataFrame)
        self._log(f"remove_invalid_values({column}): Xóa {removed} dòng không hợp lệ")
        return self

    def replace_invalid_categorical(
        self, column: str, valid_values: List, replacement: str = "Unknown"
    ) -> "DataCleaner":
        """Thay thế giá trị categorical không hợp lệ bằng replacement."""
        mask = ~self.dataFrame[column].isin(valid_values) & self.dataFrame[column].notna()
        count = mask.sum()
        if count > 0:
            self.dataFrame.loc[mask, column] = replacement
            self._log(f"replace_invalid_categorical({column}): Thay {count} giá trị bằng '{replacement}'")
        return self

    # ==========================
    # 5. TEXT CLEANING (Làm sạch chuỗi)
    # ==========================

    def strip_whitespace(self, columns: Optional[List[str]] = None) -> "DataCleaner":
        """Loại bỏ khoảng trắng thừa đầu/cuối."""
        cols = columns or self.dataFrame.select_dtypes(include=["object", "string"]).columns.tolist()
        for col in cols:
            if col in self.dataFrame.columns:
                self.dataFrame[col] = self.dataFrame[col].astype(str).str.strip()
        self._log(f"strip_whitespace: Chuẩn hóa {len(cols)} cột")
        return self

    def normalize_text(
        self, column: str, lowercase: bool = False, remove_extra_spaces: bool = True
    ) -> "DataCleaner":
        """Chuẩn hóa chuỗi: lowercase, gộp khoảng trắng thừa."""
        if column not in self.dataFrame.columns:
            return self
        s = self.dataFrame[column].astype(str).str.strip()
        if remove_extra_spaces:
            s = s.str.replace(r"\s+", " ", regex=True)
        if lowercase:
            s = s.str.lower()
        self.dataFrame[column] = s
        self._log(f"normalize_text({column}): lowercase={lowercase}, remove_extra_spaces={remove_extra_spaces}")
        return self

    def replace_empty_string_with_na(self, columns: Optional[List[str]] = None) -> "DataCleaner":
        """Chuyển chuỗi rỗng/whitespace thành NA."""
        cols = columns or self.dataFrame.select_dtypes(include=["object", "string"]).columns.tolist()
        for col in cols:
            if col in self.dataFrame.columns:
                mask = self.dataFrame[col].astype(str).str.strip() == ""
                self.dataFrame.loc[mask, col] = np.nan
        self._log("replace_empty_string_with_na: Chuỗi rỗng -> NA")
        return self

    # ==========================
    # 6. DATA TYPE CONVERSION
    # ==========================

    def convert_to_numeric(
        self, column: str, errors: str = "coerce"
    ) -> "DataCleaner":
        """Chuyển cột sang kiểu số. errors='coerce': giá trị lỗi -> NaN."""
        self.dataFrame[column] = pd.to_numeric(self.dataFrame[column], errors=errors)
        self._log(f"convert_to_numeric({column})")
        return self

    def convert_to_int(self, column: str, fillna: Optional[float] = None) -> "DataCleaner":
        """Chuyển cột sang integer. Có thể fillna trước khi convert."""
        if fillna is not None and self.dataFrame[column].isna().any():
            self.dataFrame[column] = self.dataFrame[column].fillna(fillna)
        self.dataFrame[column] = self.dataFrame[column].astype("Int64")  # Nullable int
        self._log(f"convert_to_int({column})")
        return self

    def convert_to_datetime(self, column: str, format: Optional[str] = None) -> "DataCleaner":
        """Chuyển cột sang datetime."""
        self.dataFrame[column] = pd.to_datetime(self.dataFrame[column], format=format, errors="coerce")
        self._log(f"convert_to_datetime({column})")
        return self

    # ==========================
    # 7. OLYMPIC-SPECIFIC CLEANING (Cho athlete_events.csv)
    # ==========================

    def clean_olympic_medal(self) -> "DataCleaner":
        """Chuẩn hóa cột Medal: NaN/NA -> 'No Medal'."""
        count = self.dataFrame["Medal"].isna().sum()
        self.dataFrame["Medal"] = self.dataFrame["Medal"].fillna("No Medal")
        # Chuẩn hóa string "NA" nếu có
        self.dataFrame["Medal"] = self.dataFrame["Medal"].replace(["NA", "nan", ""], "No Medal")
        self._log(f"clean_olympic_medal: Điền {count} giá trị thiếu bằng 'No Medal'")
        return self

    def fix_medal_label(self) -> "DataCleaner":
        """
        Sửa gán nhãn sai: chuẩn hóa các biến thể Gold/Silver/Bronze.
        VD: 'Gold ', 'gold' -> 'Gold'; 'SILVER' -> 'Silver'; 'BRONZE' -> 'Bronze'
        """
        if "Medal" not in self.dataFrame.columns:
            return self
        replace_map = {
            "Gold ": "Gold",
            "gold": "Gold",
            "Silver ": "Silver",
            "silver": "Silver",
            "SILVER": "Silver",
            "Bronze ": "Bronze",
            "bronze": "Bronze",
            "BRONZE": "Bronze",
        }
        before = self.dataFrame["Medal"].value_counts()
        self.dataFrame["Medal"] = self.dataFrame["Medal"].replace(replace_map)
        self._log("fix_medal_label: Chuẩn hóa nhãn Medal (Gold/Silver/Bronze)")
        return self

    def clean_team_name(self) -> "DataCleaner":
        """
        Làm sạch cột Team: loại bỏ số và dấu gạch ngang thừa ở cuối.
        VD: 'China-1' -> 'China', 'Denmark/Sweden-2' -> 'Denmark/Sweden'
        Mục đích: Thống kê thành tích quốc gia chính xác, tránh chia một nước thành nhiều team.
        """
        if "Team" not in self.dataFrame.columns:
            return self
        before = self.dataFrame["Team"].nunique()
        self.dataFrame["Team"] = self.dataFrame["Team"].astype(str).str.replace(r"-\d+$", "", regex=True)
        after = self.dataFrame["Team"].nunique()
        self._log(f"clean_team_name: Chuẩn hóa Team (số team unique: {before} -> {after})")
        return self

    def clean_event_name(self) -> "DataCleaner":
        """
        Làm sạch cột Event: cắt bỏ tên Sport bị lặp ở đầu.
        VD: Sport='Basketball', Event='Basketball Men's Basketball' -> 'Men's Basketball'
        Mục đích: Rút gọn tên sự kiện, hiển thị gọn hơn.
        """
        if "Event" not in self.dataFrame.columns or "Sport" not in self.dataFrame.columns:
            return self

        def remove_sport_prefix(row):
            ev = str(row["Event"]) if pd.notna(row["Event"]) else ""
            sp = str(row["Sport"]) if pd.notna(row["Sport"]) else ""
            if ev.startswith(sp):
                return ev[len(sp) :].strip()
            return ev

        self.dataFrame["Event"] = self.dataFrame.apply(remove_sport_prefix, axis=1)
        self._log("clean_event_name: Cắt bỏ Sport lặp ở đầu Event")
        return self

    def scale_data(self, numeric_cols: Optional[List[str]] = None) -> "DataCleaner":
        """
        Chuẩn hóa các cột số (Age, Height, Weight) bằng StandardScaler.
        Cần sklearn. Yêu cầu: requirements.txt có scikit-learn.
        """
        if not HAS_SKLEARN:
            self._log("scale_data: Bỏ qua (chưa cài scikit-learn)")
            return self
        cols = numeric_cols or ["Age", "Height", "Weight"]
        cols = [c for c in cols if c in self.dataFrame.columns]
        if not cols:
            return self
        scaler = StandardScaler()
        self.dataFrame[cols] = scaler.fit_transform(self.dataFrame[cols])
        self._log(f"scale_data: Chuẩn hóa {cols} bằng StandardScaler")
        return self

    def clean_olympic_numeric_columns(
        self,
        fill_strategy: str = "median",
        use_group_imputation: bool = True,
        group_by: Optional[List[str]] = None,
    ) -> "DataCleaner":
        """
        Xử lý Age, Height, Weight: điền NA theo chiến lược.
        fill_strategy: 'mean' | 'median'
        use_group_imputation: điền theo nhóm Sport+Sex (chính xác hơn)
        """
        numeric_cols = ["Age", "Height", "Weight"]
        group_by = group_by or ["Sport", "Sex"]

        for col in numeric_cols:
            if col not in self.dataFrame.columns:
                continue
            count = self.dataFrame[col].isna().sum()
            if count == 0:
                continue

            if use_group_imputation and all(g in self.dataFrame.columns for g in group_by):
                agg = "mean" if fill_strategy == "mean" else "median"
                group_vals = self.dataFrame.groupby(group_by)[col].transform(agg)
                self.dataFrame[col] = self.dataFrame[col].fillna(group_vals)
            # Điền phần còn lại (nhóm không có dữ liệu)
            if fill_strategy == "mean":
                self.dataFrame[col] = self.dataFrame[col].fillna(self.dataFrame[col].mean())
            else:
                self.dataFrame[col] = self.dataFrame[col].fillna(self.dataFrame[col].median())

            self._log(
                f"clean_olympic_numeric({col}): Điền {count} NA (strategy={fill_strategy}, group={use_group_imputation})"
            )
        return self

    def clean_olympic_categorical(self) -> "DataCleaner":
        """Chuẩn hóa Sex, Season: đảm bảo giá trị hợp lệ."""
        if "Sex" in self.dataFrame.columns:
            self.replace_invalid_categorical("Sex", ["M", "F"], "Unknown")
        if "Season" in self.dataFrame.columns:
            self.replace_invalid_categorical("Season", ["Summer", "Winter"], "Unknown")
        return self

    # ==========================
    # 8. PIPELINE - Chạy toàn bộ làm sạch cho Olympic
    # ==========================

    def run_full_olympic_cleaning(
        self,
        remove_exact_duplicates: bool = True,
        fill_numeric: str = "median",
        use_group_imputation: bool = True,
        handle_outliers: str = "clip",  # "clip" | "remove" | "none"
        clip_to_valid: bool = True,
    ) -> "DataCleaner":
        """
        Pipeline làm sạch đầy đủ cho athlete_events.csv.

        - remove_exact_duplicates: Xóa bản ghi trùng hoàn toàn
        - fill_numeric: 'mean' | 'median' cho Age, Height, Weight
        - use_group_imputation: Điền theo nhóm Sport+Sex
        - handle_outliers: 'clip' (gán về biên), 'remove' (xóa), 'none'
        - clip_to_valid: Clip vào khoảng hợp lệ (Age 5-100, Height 100-250, Weight 25-300)
        """
        self._cleaning_log = []

        # 1. Strip whitespace cho cột chuỗi
        self.strip_whitespace()

        # 2. Chuẩn hóa Medal
        if "Medal" in self.dataFrame.columns:
            self.clean_olympic_medal()
            self.fix_medal_label()

        # 3. Xóa duplicate
        if remove_exact_duplicates:
            self.remove_duplicates()

        # 4. Clip outliers TRƯỚC khi điền NA (để mean/median không bị lệch)
        if handle_outliers == "clip":
            for col in ["Age", "Height", "Weight"]:
                if col in self.dataFrame.columns:
                    self.clip_outliers_iqr(col)
        elif handle_outliers == "remove":
            for col in ["Age", "Height", "Weight"]:
                if col in self.dataFrame.columns:
                    self.remove_outliers_iqr(col)

        # 5. Điền giá trị thiếu cho cột số
        self.clean_olympic_numeric_columns(
            fill_strategy=fill_numeric,
            use_group_imputation=use_group_imputation,
        )

        # 6. Clip vào khoảng hợp lệ
        if clip_to_valid:
            for col in ["Age", "Height", "Weight", "Year"]:
                if col in self.dataFrame.columns:
                    self.clip_to_valid_range(col)

        # 7. Chuẩn hóa categorical
        self.clean_olympic_categorical()

        # 8. Làm sạch Team, Event
        self.clean_team_name()
        self.clean_event_name()

        # 9. Convert kiểu dữ liệu
        if "Age" in self.dataFrame.columns:
            self.dataFrame["Age"] = self.dataFrame["Age"].astype(int)
        if "Height" in self.dataFrame.columns:
            self.dataFrame["Height"] = self.dataFrame["Height"].astype(float)
        if "Weight" in self.dataFrame.columns:
            self.dataFrame["Weight"] = self.dataFrame["Weight"].astype(float)

        self._log("run_full_olympic_cleaning: Hoàn tất pipeline")



        return self

    # ==========================
    # UTILITY
    # ==========================

    def get_data(self) -> pd.DataFrame:
        return self.dataFrame

    def get_cleaning_log(self) -> List[str]:
        return self._cleaning_log.copy()

    def print_cleaning_log(self) -> "DataCleaner":
        for msg in self._cleaning_log:
            print(f"  • {msg}")
        return self

    def summary(self) -> "DataCleaner":
        """In thông tin cơ bản sau khi làm sạch."""
        print("=== DataFrame Info ===")
        print(self.dataFrame.info())
        print("\n=== Null counts ===")
        print(self.dataFrame.isnull().sum())
        print("\n=== Describe (numeric) ===")
        print(self.dataFrame.describe())
        return self
