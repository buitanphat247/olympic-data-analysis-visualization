# 🏅 Olympic Data Explorer

Hệ thống trực quan hóa và phân tích dữ liệu Olympic với giao diện web hiện đại, animation mượt mà và khả năng lọc dữ liệu theo thời gian thực.

![Dashboard Overview](public/1.png)

## 📋 Mục lục

- [Tổng quan](#tổng-quan)
- [Tính năng](#tính-năng)
- [Cấu trúc dự án](#cấu-trúc-dự-án)
- [Cài đặt](#cài-đặt)
- [Sử dụng](#sử-dụng)
- [Pipeline xử lý dữ liệu](#pipeline-xử-lý-dữ-liệu)
- [Luồng hoạt động hệ thống](#luồng-hoạt-động-hệ-thống)
- [Kiến trúc hệ thống](#kiến-trúc-hệ-thống)
- [Các module chính](#các-module-chính)
- [Output](#output)

---

## 🎯 Tổng quan

Dự án này cung cấp một hệ thống hoàn chỉnh để:
- **Làm sạch dữ liệu** Olympic từ file CSV gốc
- **Phân tích thống kê** đa chiều (huy chương, giới tính, tuổi, thể chất, quốc gia)
- **Trực quan hóa** bằng biểu đồ tĩnh (matplotlib) và tương tác (Plotly)
- **Dashboard web** với Plotly Dash, Bootstrap UI, và animation mượt mà
- **Lọc dữ liệu** theo thời gian thực với cache thông minh

**Dữ liệu:** Dataset `athlete_events.csv` chứa thông tin về các vận động viên Olympic từ năm 1896 đến nay.

---

## ✨ Tính năng

### 📊 Phân tích dữ liệu
- **Tổng quan:** Thống kê tổng hợp (số VĐV, quốc gia, kỳ Olympic, môn thể thao, huy chương)
- **Huy chương:** Phân tích Gold/Silver/Bronze theo quốc gia, năm, môn thể thao
- **Giới tính:** Phân bố và thành tích theo giới tính
- **Tuổi:** Phân bố nhóm tuổi và tỷ lệ đạt huy chương
- **Thể chất:** So sánh chiều cao, cân nặng, BMI giữa người đạt huy chương và không đạt
- **Quốc gia:** Thành tích theo từng quốc gia qua các năm

### 🎨 Trực quan hóa
- **Biểu đồ tĩnh:** 12+ biểu đồ matplotlib lưu vào `output/chart/`
- **Dashboard tương tác:** Plotly Dash với animation transitions
- **Bộ lọc:** Năm, quốc gia (NOC), môn thể thao, giới tính, huy chương
- **Responsive:** Tự động điều chỉnh theo kích thước màn hình

![Interactive Dashboard](public/2.png)

### ⚡ Tối ưu hiệu năng
- **Cache dữ liệu:** Chỉ load 1 lần mỗi nguồn (cleaned/raw)
- **Lọc hiệu quả:** Pandas filtering thay vì serialize toàn bộ dataframe
- **Loading states:** Hiển thị spinner khi callback đang chạy

---

## 📁 Cấu trúc dự án

```
BTL_PYTHON/
├── main.py                 # Pipeline chính: cài đặt → xử lý → web
├── app_dash.py            # Ứng dụng Dash web với Bootstrap UI
├── data/
│   └── athlete_events.csv # Dữ liệu gốc Olympic
├── core/
│   ├── file.py            # FileManager: đọc/ghi CSV
│   ├── data_cleaner.py    # DataCleaner: làm sạch dữ liệu
│   ├── analysis.py        # DataAnalysis: phân tích thống kê
│   └── visualization.py   # Visualization: vẽ biểu đồ matplotlib
├── lib/
│   ├── install.py         # RequirementsInstaller: tự động cài packages
│   └── requirements.txt   # Danh sách dependencies
└── output/
    ├── csv/               # Kết quả phân tích CSV
    │   ├── overview/
    │   ├── gender/
    │   ├── medal/
    │   ├── age/
    │   ├── physique/
    │   └── country/
    └── chart/              # Biểu đồ matplotlib (PNG)
```

---

## 🚀 Cài đặt

### Yêu cầu hệ thống
- Python 3.8+
- pip

### Tạo môi trường ảo (khuyến nghị)

```bash
# Tạo virtual environment
python3 -m venv venv

# Kích hoạt môi trường ảo
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate
```

### Cài đặt

Sau khi kích hoạt môi trường ảo, chạy một lệnh duy nhất:

```bash
python main.py
```

Script sẽ **tự động cài đặt** tất cả packages cần thiết từ `lib/requirements.txt` và chạy toàn bộ pipeline:
1. Tự động cài packages (pandas, plotly, dash, ...)
2. Đọc và làm sạch dữ liệu
3. Phân tích và xuất CSV
4. Tạo biểu đồ matplotlib
5. Khởi động web Dash tại `http://127.0.0.1:8050` (nếu không dùng `--no-web`)

**Lưu ý:** Nếu muốn cài packages thủ công trước:
```bash
pip install -r lib/requirements.txt
```

**Dependencies:**
- `pandas` - Xử lý dữ liệu
- `scikit-learn` - Machine learning utilities
- `matplotlib` - Biểu đồ tĩnh
- `plotly` - Biểu đồ tương tác
- `dash` - Web framework
- `dash-bootstrap-components` - Bootstrap UI components

---

## 💻 Sử dụng

### Chạy pipeline đầy đủ (kèm web)

```bash
python main.py
```

Sẽ tự động:
- Cài packages (nếu chưa có)
- Chạy toàn bộ pipeline
- Mở trình duyệt tại `http://127.0.0.1:8050`

### Chạy chỉ pipeline (không mở web)

```bash
python main.py --no-web
```

### Chạy web riêng

```bash
python app_dash.py
```

Mở trình duyệt: `http://127.0.0.1:8050`

### Chạy từng bước trong Jupyter Notebook

Xem `main.ipynb` để chạy từng step riêng lẻ.

---

## 🔄 Pipeline xử lý dữ liệu

### Sequence Diagram: Luồng xử lý chính

```mermaid
sequenceDiagram
    participant User
    participant main.py
    participant RequirementsInstaller
    participant FileManager
    participant DataCleaner
    participant DataAnalysis
    participant Visualization
    participant DashApp

    User->>main.py: python main.py
    main.py->>RequirementsInstaller: install_packages()
    RequirementsInstaller->>RequirementsInstaller: pip install -r requirements.txt
    
    main.py->>FileManager: FileManager("data/athlete_events.csv")
    FileManager->>FileManager: find_root_file()
    FileManager->>FileManager: read_file() → pd.read_csv()
    FileManager-->>main.py: DataFrame (raw)
    
    main.py->>DataCleaner: DataCleaner(dataFrame)
    DataCleaner->>DataCleaner: run_full_olympic_cleaning()
    Note over DataCleaner: 1. Strip whitespace<br/>2. Clean Medal<br/>3. Remove duplicates<br/>4. Clip outliers<br/>5. Fill missing values<br/>6. Clip to valid ranges<br/>7. Clean categorical<br/>8. Clean Team/Event<br/>9. Convert types
    DataCleaner-->>main.py: Cleaned DataFrame
    
    main.py->>FileManager: save_data(cleaned_data.csv)
    FileManager->>FileManager: to_csv() → output/csv/cleaned_data.csv
    
    main.py->>DataAnalysis: DataAnalysis(cleaned_df)
    DataAnalysis->>DataAnalysis: ingest(output_dir)
    Note over DataAnalysis: Phân tích:<br/>- Overview<br/>- Gender<br/>- Medal<br/>- Age<br/>- Physique<br/>- Country
    DataAnalysis->>FileManager: Lưu CSV vào output/csv/
    
    main.py->>Visualization: Visualization(data_analysis)
    Visualization->>Visualization: run_all(output_dir)
    Note over Visualization: Vẽ 12+ biểu đồ:<br/>- Bar charts<br/>- Pie charts<br/>- Line charts<br/>- Stacked bars
    Visualization->>Visualization: savefig() → output/chart/*.png
    
    main.py->>DashApp: subprocess.Popen(app_dash.py)
    DashApp->>DashApp: Load & cache data
    DashApp->>DashApp: Create Dash app with Bootstrap
    DashApp-->>User: http://127.0.0.1:8050
```

### Pipeline Flow Diagram

```mermaid
flowchart TD
    Start([Bắt đầu: python main.py]) --> Install[Step 0: Cài packages<br/>RequirementsInstaller]
    Install --> Read[Step 1: Đọc dữ liệu<br/>FileManager.read_file]
    Read --> Clean[Step 2: Làm sạch dữ liệu<br/>DataCleaner.run_full_olympic_cleaning]
    
    Clean --> CleanSteps{Quy trình làm sạch}
    CleanSteps --> C1[1. Strip whitespace]
    C1 --> C2[2. Clean Medal values]
    C2 --> C3[3. Remove duplicates]
    C3 --> C4[4. Clip outliers IQR]
    C4 --> C5[5. Fill missing values<br/>median/group mean]
    C5 --> C6[6. Clip to valid ranges]
    C6 --> C7[7. Clean categorical]
    C7 --> C8[8. Clean Team/Event names]
    C8 --> C9[9. Convert data types]
    C9 --> Save[Step 3: Lưu cleaned data<br/>output/csv/cleaned_data.csv]
    
    Save --> Analyze[Step 4: Phân tích<br/>DataAnalysis.ingest]
    Analyze --> AnalyzeSteps{Phân tích đa chiều}
    AnalyzeSteps --> A1[Overview: tổng hợp]
    AnalyzeSteps --> A2[Gender: giới tính]
    AnalyzeSteps --> A3[Medal: huy chương]
    AnalyzeSteps --> A4[Age: tuổi]
    AnalyzeSteps --> A5[Physique: thể chất]
    AnalyzeSteps --> A6[Country: quốc gia]
    A1 --> CSV[Lưu CSV vào output/csv/]
    A2 --> CSV
    A3 --> CSV
    A4 --> CSV
    A5 --> CSV
    A6 --> CSV
    
    CSV --> Visualize[Step 5: Trực quan hóa<br/>Visualization.run_all]
    Visualize --> Charts[12+ biểu đồ matplotlib<br/>output/chart/*.png]
    
    Charts --> Web{--no-web?}
    Web -->|Không| Launch[Step 6: Khởi động Dash<br/>app_dash.py]
    Web -->|Có| End1([Kết thúc])
    
    Launch --> Cache[Load & cache data<br/>cleaned/raw]
    Cache --> UI[Render Bootstrap UI<br/>Navbar + Sidebar + Tabs]
    UI --> Ready[Dash server ready<br/>http://127.0.0.1:8050]
    Ready --> End2([Hoàn thành])
    
    style Start fill:#e1f5ff
    style End1 fill:#c8e6c9
    style End2 fill:#c8e6c9
    style Clean fill:#fff3e0
    style Analyze fill:#f3e5f5
    style Visualize fill:#e8f5e9
    style Launch fill:#e3f2fd
```

---

## 🏗️ Luồng hoạt động hệ thống

### Sequence Diagram: Web Dashboard (Dash App)

```mermaid
sequenceDiagram
    participant Browser
    participant DashApp
    participant Cache
    participant DataAnalysis
    participant Plotly

    Browser->>DashApp: GET http://127.0.0.1:8050
    DashApp->>DashApp: Load layout (Navbar + Sidebar + Tabs)
    DashApp->>Cache: get_cached_data(use_cleaned=True)
    Cache->>Cache: Check _DATA_CACHE["cleaned"]
    alt Cache miss
        Cache->>Cache: _load_data_impl(True)
        Cache->>Cache: pd.read_csv(cleaned_data.csv)
        Cache->>Cache: Store in _DATA_CACHE["cleaned"]
    end
    Cache-->>DashApp: DataFrame (cached)
    DashApp->>DashApp: Populate dropdowns (Year, NOC, Sport...)
    DashApp-->>Browser: Render HTML với Bootstrap

    Browser->>DashApp: User thay đổi filter (Year, NOC...)
    Browser->>DashApp: Callback trigger: update_tab_content()
    DashApp->>Cache: get_cached_data(use_cleaned)
    Cache-->>DashApp: DataFrame (cached, không reload)
    DashApp->>DashApp: Apply filters (pandas filtering)
    DashApp->>DataAnalysis: DataAnalysis(filtered_df)
    DataAnalysis->>DataAnalysis: analyze_data_overview()
    DataAnalysis->>DataAnalysis: medal_count()
    DataAnalysis->>DataAnalysis: medals_by_country()
    DataAnalysis-->>DashApp: Analysis results
    
    DashApp->>Plotly: create_animated_medal_pie()
    DashApp->>Plotly: create_animated_country_medals()
    Plotly-->>DashApp: Plotly Figure objects
    
    DashApp->>DashApp: Wrap figures in dbc.Container + dbc.Row/Col
    DashApp-->>Browser: Update tab-content với biểu đồ mới
    Note over Browser: Animation transition<br/>500-800ms cubic-in-out
```

### Data Flow: Từ Raw CSV đến Dashboard

```mermaid
flowchart LR
    Raw[athlete_events.csv<br/>Raw data] --> FM[FileManager<br/>read_file]
    FM --> DC[DataCleaner<br/>run_full_olympic_cleaning]
    DC --> Cleaned[cleaned_data.csv<br/>Cleaned data]
    
    Cleaned --> DA[DataAnalysis<br/>ingest]
    DA --> CSV1[overview.csv]
    DA --> CSV2[gender/*.csv]
    DA --> CSV3[medal/*.csv]
    DA --> CSV4[age/*.csv]
    DA --> CSV5[physique/*.csv]
    DA --> CSV6[country/*.csv]
    
    Cleaned --> Vis[Visualization<br/>run_all]
    Vis --> PNG1[medal_count.png]
    Vis --> PNG2[medals_by_country.png]
    Vis --> PNG3[gender_distribution.png]
    Vis --> PNG4[...12+ charts]
    
    Cleaned --> Dash[Dash App<br/>app_dash.py]
    Dash --> Cache[_DATA_CACHE<br/>Memory cache]
    Cache --> Filter[User filters<br/>Year, NOC, Sport...]
    Filter --> Analysis[DataAnalysis<br/>on filtered data]
    Analysis --> Plotly[Plotly Figures<br/>Interactive charts]
    Plotly --> Browser[Browser<br/>http://127.0.0.1:8050]
    
    style Raw fill:#ffcdd2
    style Cleaned fill:#c8e6c9
    style Dash fill:#e1f5ff
    style Browser fill:#fff9c4
```

---

## 🏛️ Kiến trúc hệ thống

### Component Diagram

```mermaid
graph TB
    subgraph "Entry Points"
        Main[main.py<br/>Pipeline orchestrator]
        Dash[app_dash.py<br/>Web dashboard]
        Notebook[main.ipynb<br/>Interactive notebook]
    end
    
    subgraph "Core Modules"
        FM[core/file.py<br/>FileManager]
        DC[core/data_cleaner.py<br/>DataCleaner]
        DA[core/analysis.py<br/>DataAnalysis]
        Vis[core/visualization.py<br/>Visualization]
    end
    
    subgraph "Utilities"
        Install[lib/install.py<br/>RequirementsInstaller]
    end
    
    subgraph "Data Layer"
        CSV[data/athlete_events.csv<br/>Raw data]
        CleanedCSV[output/csv/cleaned_data.csv<br/>Cleaned data]
        OutputCSV[output/csv/*/<br/>Analysis results]
        Charts[output/chart/*.png<br/>Static charts]
    end
    
    subgraph "Web Layer"
        DashApp[Dash Application]
        Bootstrap[Bootstrap UI]
        Plotly[Plotly Charts]
        Cache[Memory Cache]
    end
    
    Main --> Install
    Main --> FM
    Main --> DC
    Main --> DA
    Main --> Vis
    Main --> Dash
    
    Dash --> FM
    Dash --> DC
    Dash --> DA
    Dash --> Cache
    Dash --> DashApp
    DashApp --> Bootstrap
    DashApp --> Plotly
    
    FM --> CSV
    FM --> CleanedCSV
    FM --> OutputCSV
    DC --> CleanedCSV
    DA --> OutputCSV
    Vis --> Charts
    
    Notebook --> FM
    Notebook --> DC
    Notebook --> DA
    Notebook --> Vis
```

---

## 📦 Các module chính

### 1. `core/file.py` - FileManager

**Chức năng:** Quản lý đọc/ghi file CSV

**Phương thức chính:**
- `find_root_file(file_path)`: Tìm file từ project root
- `read_file()`: Đọc CSV thành pandas DataFrame
- `save_data(dataFrame, relative_path)`: Lưu DataFrame ra CSV

**Ví dụ:**
```python
fm = FileManager("data/athlete_events.csv")
df = fm.read_file()
fm.save_data(df, "output/csv/cleaned_data.csv")
```

### 2. `core/data_cleaner.py` - DataCleaner

**Chức năng:** Làm sạch dữ liệu Olympic

**Các bước trong `run_full_olympic_cleaning()`:**
1. **Strip whitespace:** Loại bỏ khoảng trắng thừa
2. **Clean Medal:** Chuẩn hóa giá trị Medal (Gold/Silver/Bronze/No Medal)
3. **Remove duplicates:** Xóa bản ghi trùng lặp
4. **Clip outliers:** Gán giá trị ngoại lai về biên (IQR method)
5. **Fill missing values:** Điền NA bằng median hoặc group mean (theo Sport+Sex)
6. **Clip to valid ranges:** 
   - Age: 5-100
   - Height: 100-250 cm
   - Weight: 25-300 kg
   - Year: 1896-2030
7. **Clean categorical:** Chuẩn hóa Sex, Season
8. **Clean Team/Event:** Loại bỏ ký tự đặc biệt
9. **Convert types:** Chuyển Age → int, Height/Weight → float

**Ví dụ:**
```python
cleaner = DataCleaner(df)
cleaner.run_full_olympic_cleaning()
cleaned_df = cleaner.get_data()
```

### 3. `core/analysis.py` - DataAnalysis

**Chức năng:** Phân tích thống kê đa chiều

**Các nhóm phân tích:**

#### Overview
- `analyze_data_overview()`: Tổng hợp (VĐV, quốc gia, kỳ Olympic, môn, huy chương)

#### Gender
- `analyze_data_by_gender()`: Phân bố và huy chương theo giới tính

#### Medal
- `medal_count()`: Tổng Gold/Silver/Bronze
- `medals_by_country()`: Top quốc gia
- `medals_by_year()`: Huy chương theo năm
- `medals_by_sport()`: Huy chương theo môn
- `medal_tally_table()`: Bảng tổng sắp (pivot table)

#### Age
- `age_summary()`: Tuổi trung bình/min/max
- `age_group_distribution()`: Phân bố nhóm tuổi (U20, 20-30, ...)
- `medal_ratio_by_age_group()`: Tỷ lệ đạt huy chương theo tuổi

#### Physique
- `physique_by_sport()`: Chiều cao/cân nặng/BMI theo môn
- `medal_vs_non_medal_physique()`: So sánh thể chất

#### Country
- `medals_by_country_year()`: Huy chương theo quốc gia + năm
- `country_performance(noc_code)`: Thành tích 1 quốc gia

**Ví dụ:**
```python
analysis = DataAnalysis(df)
overview = analysis.analyze_data_overview()
medal_count = analysis.medal_count()
analysis.ingest(output_dir="output/csv")  # Xuất tất cả CSV
```

### 4. `core/visualization.py` - Visualization

**Chức năng:** Vẽ biểu đồ matplotlib

**Các biểu đồ:**
- `plot_medals_by_country()`: Bar chart top quốc gia
- `plot_medal_count()`: Bar chart Gold/Silver/Bronze
- `plot_medal_count_pie()`: Pie chart tỷ lệ huy chương
- `plot_gender_distribution()`: Bar chart giới tính
- `plot_medals_by_year()`: Line chart theo năm
- `plot_medals_by_sport()`: Bar chart theo môn
- `plot_age_group_distribution()`: Bar chart nhóm tuổi
- `plot_medal_tally_stacked()`: Stacked bar Gold/Silver/Bronze
- `plot_physique_medal_vs_non_medal()`: So sánh thể chất

**Ví dụ:**
```python
vis = Visualization(analysis)
vis.run_all(output_dir=Path("output/chart"))
```

### 5. `app_dash.py` - Web Dashboard

**Chức năng:** Ứng dụng web tương tác với Plotly Dash

**Tính năng:**
- **Cache thông minh:** `_DATA_CACHE` lưu cleaned/raw data trong memory
- **Bootstrap UI:** Navbar, Sidebar (filters), Tabs
- **Callbacks:** Tự động cập nhật biểu đồ khi filter thay đổi
- **Animation:** Plotly transitions (500-800ms cubic-in-out)

**Cấu trúc:**
- **Sidebar:** Bộ lọc (Năm, NOC, Sport, Sex, Medal, Top N)
- **Tabs:** Tổng quan, Huy chương, Giới tính, Tuổi, Thể chất, Bảng dữ liệu
- **Biểu đồ:** Plotly Express và Graph Objects với animation

**Ví dụ callback:**
```python
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('year-filter', 'value'),
     ...]
)
def update_tab_content(tab, years, ...):
    df = get_cached_data(use_cleaned)  # Lấy từ cache
    df = df[df['Year'].isin(years)]  # Lọc
    analysis = DataAnalysis(df)
    # Tạo biểu đồ với animation
    return dbc.Container([...])
```

---

## 📊 Output

### CSV Files (`output/csv/`)

```
output/csv/
├── cleaned_data.csv              # Dữ liệu đã làm sạch
├── overview/
│   └── overview.csv              # Tổng hợp
├── gender/
│   ├── gender_counts.csv
│   ├── gender_percentage.csv
│   └── medal_by_gender.csv
├── medal/
│   ├── medal_count.csv
│   ├── medals_by_country.csv
│   ├── medals_by_year.csv
│   ├── medals_by_sport.csv
│   └── medal_tally_table.csv
├── age/
│   ├── age_summary.csv
│   ├── age_group_distribution.csv
│   ├── medal_ratio_by_age_group.csv
│   └── average_age_gold.csv
├── physique/
│   ├── physique_by_sport.csv
│   └── medal_vs_non_medal_physique.csv
└── country/
    ├── medals_by_country_year.csv
    └── country_performance_*.csv  # Mỗi quốc gia 1 file
```

### Charts (`output/chart/`)

- `medals_by_country.png` - Top quốc gia
- `medal_count.png` - Bar chart Gold/Silver/Bronze
- `medal_count_pie.png` - Pie chart tỷ lệ
- `gender_distribution.png` - Phân bố giới tính
- `medals_by_gender.png` - Huy chương theo giới tính
- `medals_by_year.png` - Line chart theo năm
- `medals_by_sport.png` - Top môn thể thao
- `country_most_gold.png` - Top quốc gia nhiều Gold
- `age_group_distribution.png` - Phân bố tuổi
- `medal_ratio_by_age_group.png` - Tỷ lệ huy chương theo tuổi
- `medal_tally_stacked.png` - Stacked bar Gold/Silver/Bronze
- `physique_medal_vs_non_medal.png` - So sánh thể chất

### Web Dashboard

- **URL:** `http://127.0.0.1:8050`
- **Tính năng:** Tương tác, lọc real-time, animation mượt mà

![Data Table View](public/3.png)

---

## 🔧 Troubleshooting

### Lỗi "Module not found"
```bash
pip install -r lib/requirements.txt
```

### Lỗi "File not found"
Đảm bảo có file `data/athlete_events.csv` trong thư mục project.

### Dash không khởi động
```bash
# Chạy trực tiếp để xem lỗi
python app_dash.py
```

### Port 8050 đã được sử dụng
Thay đổi port trong `app_dash.py`:
```python
app.run(debug=True, host='127.0.0.1', port=8051)
```

---

## 📝 License

Dự án này được phát triển cho mục đích học tập và nghiên cứu.

---

## 👥 Tác giả

BTL Python - Olympic Data Visualization Project

---

## 🙏 Tài liệu tham khảo

- [Pandas Documentation](https://pandas.pydata.org/)
- [Plotly Dash Documentation](https://dash.plotly.com/)
- [Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai/)
- [Matplotlib Documentation](https://matplotlib.org/)
