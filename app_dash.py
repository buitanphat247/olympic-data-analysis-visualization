"""
Ứng dụng Plotly Dash: Trực quan hóa Olympic với animation mượt mà.
Layout: sidebar (bộ lọc), nhiều trang với biểu đồ có animation.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output, State
import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate

from core.file import FileManager
from core.data_cleaner import DataCleaner
from core.analysis import DataAnalysis

# ============== Load & cache dữ liệu (chỉ load 1 lần mỗi nguồn) ==============
_DATA_CACHE = {"cleaned": None, "raw": None}

def _load_data_impl(use_cleaned=True):
    """Load từ file/cleaning — gọi trực tiếp chỉ khi cache miss."""
    cleaned_path = ROOT / "output" / "csv" / "cleaned_data.csv"
    if use_cleaned and cleaned_path.exists():
        return pd.read_csv(cleaned_path)
    fm = FileManager("data/athlete_events.csv")
    df = fm.read_file()
    if use_cleaned:
        cleaner = DataCleaner(df)
        cleaner.run_full_olympic_cleaning()
        return cleaner.get_data()
    return df

def get_cached_data(use_cleaned=True):
    """Lấy dataframe đã cache; nếu chưa có thì load 1 lần rồi cache."""
    key = "cleaned" if use_cleaned else "raw"
    if _DATA_CACHE[key] is None:
        label = "đã làm sạch" if use_cleaned else "gốc"
        print(f"[Cache] Đang tải dữ liệu {label} (chỉ lần đầu)...")
        _DATA_CACHE[key] = _load_data_impl(use_cleaned)
        print(f"[Cache] Xong. {len(_DATA_CACHE[key]):,} dòng.")
    return _DATA_CACHE[key]

# Load dữ liệu đã làm sạch 1 lần khi khởi động (dùng cho layout + dropdown)
df_global = get_cached_data(use_cleaned=True)
if df_global is None or df_global.empty:
    raise FileNotFoundError("Không tìm thấy dữ liệu. Đảm bảo có file `data/athlete_events.csv`.")

# ============== Tạo app Dash (Bootstrap) ==============
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.FLATLY],
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

app.title = "🏅 Olympic Data Explorer"

# CSS Reset: loại bỏ padding/margin mặc định
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            html, body {
                margin: 0 !important;
                padding: 0 !important;
                width: 100%;
                height: 100%;
                overflow-x: hidden;
            }
            #react-entry-point, #_dash-app-content {
                margin: 0;
                padding: 0;
            }
            .container-fluid.p-0, .container-fluid {
                padding-left: 0 !important;
                padding-right: 0 !important;
                --bs-gutter-x: 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# ============== Layout ==============
sidebar = dbc.Card([
    dbc.CardHeader(html.H5("🔍 Bộ lọc", className="mb-0 fw-bold text-primary")),
    dbc.CardBody([
        html.Label("Nguồn dữ liệu", className="fw-semibold small text-muted"),
        dcc.RadioItems(
            id='data-source',
            options=[
                {'label': ' Đã làm sạch (khuyến nghị)', 'value': True},
                {'label': ' Dữ liệu gốc', 'value': False}
            ],
            value=True,
            className="mb-3",
            inputStyle={"marginRight": "6px"}
        ),
        html.Label("Năm", className="fw-semibold small text-muted"),
        dcc.Dropdown(
            id='year-filter',
            options=[{'label': str(y), 'value': y} for y in sorted(df_global['Year'].dropna().unique())],
            multi=True,
            placeholder="Tất cả năm",
            className="mb-3"
        ),
        html.Label("Quốc gia (NOC)", className="fw-semibold small text-muted"),
        dcc.Dropdown(
            id='noc-filter',
            options=[{'label': n, 'value': n} for n in sorted(df_global['NOC'].dropna().unique())],
            multi=True,
            placeholder="Tất cả quốc gia",
            className="mb-3"
        ),
        html.Label("Môn thể thao", className="fw-semibold small text-muted"),
        dcc.Dropdown(
            id='sport-filter',
            options=[{'label': s, 'value': s} for s in sorted(df_global['Sport'].dropna().unique())],
            multi=True,
            placeholder="Tất cả môn",
            className="mb-3"
        ),
        html.Label("Giới tính", className="fw-semibold small text-muted"),
        dcc.Dropdown(
            id='sex-filter',
            options=[{'label': s, 'value': s} for s in sorted(df_global['Sex'].dropna().unique())],
            multi=True,
            placeholder="Tất cả",
            className="mb-3"
        ),
        html.Label("Huy chương", className="fw-semibold small text-muted"),
        dcc.Dropdown(
            id='medal-filter',
            options=[{'label': m, 'value': m} for m in sorted(df_global['Medal'].dropna().unique())],
            multi=True,
            placeholder="Tất cả",
            className="mb-3"
        ),
        html.Label("Top N", className="fw-semibold small text-muted"),
        dcc.Slider(
            id='top-n',
            min=5,
            max=30,
            step=5,
            value=15,
            marks={i: str(i) for i in range(5, 31, 5)},
            tooltip={"placement": "bottom", "always_visible": True}
        ),
        dbc.CardFooter(html.Small(f"📊 {len(df_global):,} bản ghi", className="text-muted"))
    ])
], className="shadow-sm")

app.layout = dbc.Container([
    # Navbar
    dbc.Navbar(
        dbc.Container([
            dbc.NavbarBrand("🏅 Olympic Data Explorer", className="fw-bold fs-4"),
            dbc.NavbarToggler(id="navbar-toggler"),
        ], fluid=True),
        color="primary",
        dark=True,
        className="mb-3 shadow",
        style={"marginBottom": "0.5rem"},
    ),
    dbc.Row([
        dbc.Col(sidebar, md=3, className="mb-4"),
        dbc.Col([
            dbc.Tabs(
                id='main-tabs',
                className="nav-fill nav-pills",
                children=[
                    dbc.Tab(label="Tổng quan", tab_id='overview', label_style={"fontWeight": "600"}),
                    dbc.Tab(label="Huy chương", tab_id='medals', label_style={"fontWeight": "600"}),
                    dbc.Tab(label="Giới tính", tab_id='gender', label_style={"fontWeight": "600"}),
                    dbc.Tab(label="Tuổi", tab_id='age', label_style={"fontWeight": "600"}),
                    dbc.Tab(label="Thể chất", tab_id='physique', label_style={"fontWeight": "600"}),
                    dbc.Tab(label="Bảng dữ liệu", tab_id='data', label_style={"fontWeight": "600"}),
                ],
                active_tab='overview',
            ),
            dcc.Loading(html.Div(id='tab-content', className="mt-4"), type="circle", fullscreen=False),
        ], md=9),
    ], className="g-4"),
], fluid=True, className="p-0")

# ============== Callbacks ==============
@app.callback(
    Output('tab-content', 'children'),
    [Input('main-tabs', 'active_tab'),
     Input('data-source', 'value'),
     Input('year-filter', 'value'),
     Input('noc-filter', 'value'),
     Input('sport-filter', 'value'),
     Input('sex-filter', 'value'),
     Input('medal-filter', 'value'),
     Input('top-n', 'value')]
)
def update_tab_content(tab, use_cleaned, years, nocs, sports, sexes, medals, top_n):
    if tab is None:
        tab = 'overview'
    top_n = top_n if top_n is not None else 15
    try:
        df = get_cached_data(use_cleaned if use_cleaned is not None else True)
        if years:
            df = df[df['Year'].isin(years)]
        if nocs:
            df = df[df['NOC'].isin(nocs)]
        if sports:
            df = df[df['Sport'].isin(sports)]
        if sexes:
            df = df[df['Sex'].isin(sexes)]
        if medals:
            df = df[df['Medal'].isin(medals)]
    except Exception as e:
        return dbc.Alert(f"Lỗi khi lọc dữ liệu: {e}", color="danger")
    
    if df.empty:
        return dbc.Alert("Không có dữ liệu sau khi lọc. Thử bỏ bớt bộ lọc.", color="warning")
    
    analysis = DataAnalysis(df)
    
    try:
        if tab == 'overview':
            overview = analysis.analyze_data_overview()
            return dbc.Container([
                dbc.Row([
                    dbc.Col(dbc.Card([dbc.CardBody([html.H3(f"{overview['total_athletes']:,}", className="text-primary mb-0"), html.P("Vận động viên", className="text-muted small mb-0")])], className="shadow-sm text-center"), xs=6, md=4, lg=2),
                    dbc.Col(dbc.Card([dbc.CardBody([html.H3(f"{overview['total_countries']:,}", className="text-info mb-0"), html.P("Quốc gia", className="text-muted small mb-0")])], className="shadow-sm text-center"), xs=6, md=4, lg=2),
                    dbc.Col(dbc.Card([dbc.CardBody([html.H3(f"{overview['total_olympic_games']:,}", className="text-success mb-0"), html.P("Kỳ Olympic", className="text-muted small mb-0")])], className="shadow-sm text-center"), xs=6, md=4, lg=2),
                    dbc.Col(dbc.Card([dbc.CardBody([html.H3(f"{overview['total_sports']:,}", className="text-warning mb-0"), html.P("Môn thể thao", className="text-muted small mb-0")])], className="shadow-sm text-center"), xs=6, md=4, lg=2),
                    dbc.Col(dbc.Card([dbc.CardBody([html.H3(f"{overview['total_medals']:,}", className="text-danger mb-0"), html.P("Tổng huy chương", className="text-muted small mb-0")])], className="shadow-sm text-center"), xs=6, md=4, lg=2),
                ], className="g-3 mb-4"),
                dbc.Row([
                    dbc.Col(dcc.Graph(id='overview-medal-pie', figure=create_animated_medal_pie(analysis), config={"displayModeBar": True}, style={'height': '400px'}), md=6, className="mb-3"),
                    dbc.Col(dcc.Graph(id='overview-gender', figure=create_animated_gender_bar(analysis), config={"displayModeBar": True}, style={'height': '400px'}), md=6, className="mb-3"),
                ]),
                dbc.Row(dbc.Col(dcc.Graph(id='overview-year-line', figure=create_animated_year_line(analysis), config={"displayModeBar": True}, style={'height': '450px'}), width=12)),
            ], fluid=True)
        elif tab == 'medals':
            return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id='medal-count-bar', figure=create_animated_medal_count(analysis), style={'height': '400px'}), md=6, className="mb-3"),
                dbc.Col(dcc.Graph(id='medal-country-bar', figure=create_animated_country_medals(analysis, top_n), style={'height': '400px'}), md=6, className="mb-3"),
            ]),
            dbc.Row(dbc.Col(dcc.Graph(id='medal-year-line', figure=create_animated_year_line(analysis), style={'height': '450px'}), width=12, className="mb-3")),
            dbc.Row(dbc.Col(dcc.Graph(id='medal-sport-bar', figure=create_animated_sport_medals(analysis, top_n), style={'height': '500px'}), width=12, className="mb-3")),
            dbc.Row(dbc.Col(dcc.Graph(id='medal-tally-stacked', figure=create_animated_medal_tally(analysis, top_n), style={'height': '500px'}), width=12)),
        ], fluid=True)
        elif tab == 'gender':
            gender = analysis.analyze_data_by_gender()
            return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(id='gender-pie', figure=create_animated_gender_pie(gender), style={'height': '400px'}), md=6, className="mb-3"),
                dbc.Col(dcc.Graph(id='gender-medal-bar', figure=create_animated_gender_medal(gender), style={'height': '400px'}), md=6, className="mb-3"),
            ]),
        ], fluid=True)
        elif tab == 'age':
            age_summary = analysis.age_summary()
            return dbc.Container([
            dbc.Alert([html.Strong("Tuổi trung bình: "), f"{age_summary['mean']} — Min: {age_summary['min']}, Max: {age_summary['max']}"], color="info", className="text-center mb-4"),
            dbc.Row(dbc.Col(dcc.Graph(id='age-distribution', figure=create_animated_age_distribution(analysis), style={'height': '450px'}), width=12, className="mb-3")),
            dbc.Row(dbc.Col(dcc.Graph(id='age-medal-ratio', figure=create_animated_age_medal_ratio(analysis), style={'height': '450px'}), width=12)),
        ], fluid=True)
        elif tab == 'physique':
            phys = analysis.medal_vs_non_medal_physique()
            if phys is None or phys.empty:
                return dbc.Alert("Không đủ dữ liệu Height/Weight để phân tích thể chất.", color="warning")
            return dbc.Container([
            dbc.Row(dbc.Col(dcc.Graph(id='physique-comparison', figure=create_animated_physique_comparison(phys), style={'height': '500px'}), width=12)),
        ], fluid=True)
        elif tab == 'data':
            return dbc.Container([
            dbc.Alert(html.Small(f"Hiển thị tối đa 1.000 dòng — Tổng {len(df):,} bản ghi sau lọc"), color="light", className="mb-3"),
            dbc.Card([
                dbc.CardBody(
                    dash_table.DataTable(
                        data=df.head(1000).to_dict('records'),
                        columns=[{"name": i, "id": i} for i in df.columns],
                        page_size=50,
                        style_table={'overflowX': 'auto'},
                        style_cell={'textAlign': 'left'},
                        style_header={'backgroundColor': 'var(--bs-primary)', 'color': 'white', 'fontWeight': '600'},
                        style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "rgba(0,0,0,.03)"}],
                    )
                )
            ], className="shadow-sm"),
        ], fluid=True)
        return html.Div("Tab không hợp lệ")
    except Exception as e:
        return dbc.Alert([html.Strong("Lỗi hiển thị: "), str(e)], color="danger")

# ============== Hàm tạo biểu đồ có animation ==============
def create_animated_medal_pie(analysis):
    medal_count = analysis.medal_count()
    if medal_count.empty:
        return {}
    
    fig = px.pie(
        values=medal_count.values,
        names=medal_count.index,
        title="Tỷ lệ huy chương (Gold / Silver / Bronze)",
        color_discrete_map={"Gold": "#FFC107", "Silver": "#E8E8E8", "Bronze": "#CD7F32"},
        hole=0.4
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value} huy chương<br>%{percent}<extra></extra>',
        marker=dict(line=dict(color='white', width=2))
    )
    fig.update_layout(
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        showlegend=True
    )
    return fig

def create_animated_gender_bar(analysis):
    gender = analysis.analyze_data_by_gender()
    counts = gender.get("gender_counts")
    if counts is None or counts.empty:
        return {}
    
    fig = px.bar(
        x=counts.index.astype(str),
        y=counts.values,
        title="Phân bố theo giới tính",
        labels={"x": "Giới tính", "y": "Số VĐV"},
        color=counts.values,
        color_continuous_scale="Blues"
    )
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y:,} VĐV<extra></extra>',
        marker_line_color='white',
        marker_line_width=2
    )
    fig.update_layout(
        showlegend=False,
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        yaxis_title="Số vận động viên"
    )
    return fig

def create_animated_year_line(analysis):
    by_year = analysis.medals_by_year().sort_index()
    if by_year.empty:
        return {}
    
    fig = px.line(
        x=by_year.index,
        y=by_year.values,
        title="Tổng số huy chương theo năm",
        labels={"x": "Năm", "y": "Số huy chương"}
    )
    fig.update_traces(
        line=dict(color='#667eea', width=3),
        mode='lines+markers',
        marker=dict(size=8, color='#764ba2'),
        hovertemplate='<b>Năm %{x}</b><br>%{y:,} huy chương<extra></extra>'
    )
    fig.update_layout(
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 800, 'easing': 'cubic-in-out'},
        hovermode='x unified',
        xaxis_title="Năm",
        yaxis_title="Số huy chương"
    )
    return fig

def create_animated_medal_count(analysis):
    medal_count = analysis.medal_count()
    if medal_count.empty:
        return {}
    
    colors = {"Gold": "#FFC107", "Silver": "#E8E8E8", "Bronze": "#CD7F32"}
    fig = go.Figure()
    for medal_type in medal_count.index:
        fig.add_trace(go.Bar(
            x=[medal_type],
            y=[medal_count[medal_type]],
            name=medal_type,
            marker_color=colors.get(medal_type, "gray"),
            hovertemplate=f'<b>{medal_type}</b><br>%{{y:,}} huy chương<extra></extra>'
        ))
    
    fig.update_layout(
        title="Số lượng Gold / Silver / Bronze",
        xaxis_title="Loại huy chương",
        yaxis_title="Số lượng",
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        showlegend=False
    )
    return fig

def create_animated_country_medals(analysis, top_n):
    by_country = analysis.medals_by_country().head(top_n)
    if by_country.empty:
        return {}
    
    fig = px.bar(
        y=by_country.index,
        x=by_country.values,
        orientation='h',
        title=f"Top {top_n} quốc gia theo tổng số huy chương",
        labels={"x": "Số huy chương", "y": "NOC"},
        color=by_country.values,
        color_continuous_scale="Viridis"
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 600, 'easing': 'cubic-in-out'},
        showlegend=False,
        xaxis_title="Số huy chương",
        yaxis_title="Quốc gia"
    )
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>%{x:,} huy chương<extra></extra>',
        marker_line_color='white',
        marker_line_width=1
    )
    return fig

def create_animated_sport_medals(analysis, top_n):
    by_sport = analysis.medals_by_sport().head(top_n)
    if by_sport.empty:
        return {}
    
    fig = px.bar(
        y=by_sport.index,
        x=by_sport.values,
        orientation='h',
        title=f"Top {top_n} môn thể thao theo số huy chương",
        labels={"x": "Số huy chương", "y": "Môn"},
        color=by_sport.values,
        color_continuous_scale="Plasma"
    )
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 600, 'easing': 'cubic-in-out'},
        showlegend=False,
        xaxis_title="Số huy chương",
        yaxis_title="Môn thể thao"
    )
    fig.update_traces(
        hovertemplate='<b>%{y}</b><br>%{x:,} huy chương<extra></extra>',
        marker_line_color='white',
        marker_line_width=1
    )
    return fig

def create_animated_medal_tally(analysis, top_n):
    tally = analysis.medal_tally_table().head(top_n)
    if tally.empty or "Gold" not in tally.columns:
        return {}
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Gold", x=tally.index, y=tally["Gold"], marker_color="#FFC107"))
    fig.add_trace(go.Bar(name="Silver", x=tally.index, y=tally["Silver"], marker_color="#9CA3AF"))
    fig.add_trace(go.Bar(name="Bronze", x=tally.index, y=tally["Bronze"], marker_color="#B45309"))
    
    fig.update_layout(
        barmode='stack',
        title=f"Top {top_n} quốc gia – Gold / Silver / Bronze",
        xaxis_title="Quốc gia",
        yaxis_title="Số huy chương",
        font_family='Inter',
        transition={'duration': 600, 'easing': 'cubic-in-out'},
        xaxis_tickangle=-45
    )
    return fig

def create_animated_gender_pie(gender):
    counts = gender.get("gender_counts")
    if counts is None or counts.empty:
        return {}
    
    fig = px.pie(
        values=counts.values,
        names=counts.index.astype(str),
        title="Tỷ lệ VĐV theo giới tính",
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4
    )
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>%{value:,} VĐV<br>%{percent}<extra></extra>',
        marker=dict(line=dict(color='white', width=2))
    )
    fig.update_layout(
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    return fig

def create_animated_gender_medal(gender):
    medal_by_gender = gender.get("medal_by_gender")
    if medal_by_gender is None or medal_by_gender.empty:
        return {}
    
    fig = px.bar(
        x=medal_by_gender.index.astype(str),
        y=medal_by_gender.values,
        title="Số huy chương theo giới tính",
        labels={"x": "Giới tính", "y": "Số huy chương"},
        color=medal_by_gender.index.astype(str),
        color_discrete_map={"M": "#4facfe", "F": "#f093fb"}
    )
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y:,} huy chương<extra></extra>',
        marker_line_color='white',
        marker_line_width=2
    )
    fig.update_layout(
        showlegend=False,
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        yaxis_title="Số huy chương"
    )
    return fig

def create_animated_age_distribution(analysis):
    age_dist = analysis.age_group_distribution()
    if age_dist.empty:
        return {}
    
    fig = px.bar(
        x=age_dist.index.astype(str),
        y=age_dist.values,
        title="Phân bố theo nhóm tuổi",
        labels={"x": "Nhóm tuổi", "y": "Số VĐV"},
        color=age_dist.values,
        color_continuous_scale="Teal"
    )
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>%{y:,} VĐV<extra></extra>',
        marker_line_color='white',
        marker_line_width=2
    )
    fig.update_layout(
        showlegend=False,
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        yaxis_title="Số vận động viên"
    )
    return fig

def create_animated_age_medal_ratio(analysis):
    ratio_age = analysis.medal_ratio_by_age_group()
    if ratio_age.empty:
        return {}
    
    fig = px.bar(
        x=ratio_age.index.astype(str),
        y=ratio_age.values,
        title="Tỷ lệ đạt huy chương theo nhóm tuổi",
        labels={"x": "Nhóm tuổi", "y": "Tỷ lệ"},
        color=ratio_age.values,
        color_continuous_scale="Purples"
    )
    fig.update_traces(
        hovertemplate='<b>%{x}</b><br>Tỷ lệ: %{y:.2%}<extra></extra>',
        marker_line_color='white',
        marker_line_width=2
    )
    fig.update_layout(
        showlegend=False,
        title_font_size=18,
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'},
        yaxis_title="Tỷ lệ đạt huy chương"
    )
    return fig

def create_animated_physique_comparison(phys):
    cols = ["Height", "Weight", "BMI"]
    labels = ["Chiều cao (cm)", "Cân nặng (kg)", "BMI"]
    
    if "Medalist" not in phys.index or "Non-Medalist" not in phys.index:
        return {}
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="Có huy chương",
        x=labels,
        y=[phys.loc["Medalist", c] for c in cols],
        marker_color="#FFC107",
        hovertemplate='<b>Có huy chương</b><br>%{x}: %{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Bar(
        name="Không huy chương",
        x=labels,
        y=[phys.loc["Non-Medalist", c] for c in cols],
        marker_color="#4B5563",
        hovertemplate='<b>Không huy chương</b><br>%{x}: %{y:.2f}<extra></extra>'
    ))
    
    fig.update_layout(
        barmode='group',
        title="Chiều cao / Cân nặng / BMI trung bình",
        xaxis_title="Chỉ số",
        yaxis_title="Giá trị trung bình",
        font_family='Inter',
        transition={'duration': 500, 'easing': 'cubic-in-out'}
    )
    return fig

# ============== Chạy app ==============
if __name__ == '__main__':
    print("Đang khởi động Dash... Mở trình duyệt: http://127.0.0.1:8050")
    app.run(debug=True, host='127.0.0.1', port=8050)
