import calendar
from datetime import datetime
import io
import openpyxl
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
import pandas as pd
import streamlit as st

# Bọc an toàn import Supabase
try:
    from supabase import create_client
except ImportError:
    create_client = None

# Danh mục ký hiệu chấm công chuẩn đầy đủ
DEFAULT_RULES = [
    ("X", "Làm việc cả ngày (Tính 1 công)"),
    ("P", "Nghỉ phép năm có hưởng lương"),
    ("ÔM", "Nghỉ ốm đau có xác nhận của cơ sở y tế"),
    ("CO", "Nghỉ con ốm có xác nhận y tế"),
    ("CT", "Đi công tác / Học tập ngoài đơn vị"),
    ("T", "Trực / Ca trực theo phân công"),
    ("TS", "Nghỉ thai sản theo quy định"),
    ("KL", "Nghỉ không hưởng lương"),
    ("R", "Nghỉ việc riêng (được duyệt)"),
    ("H", "Học tập / Bồi dưỡng chuyên môn"),
    ("F", "Nghỉ Lễ / Tết hưởng nguyên lương"),
]

VALID_CODES_MAP = {
    "X": "X",
    "1": "X",
    "+": "X",
    "x": "X",
    "P": "P",
    "p": "P",
    "OM": "ÔM",
    "ÔM": "ÔM",
    "om": "ÔM",
    "ôm": "ÔM",
    "CO": "CO",
    "co": "CO",
    "CT": "CT",
    "ct": "CT",
    "T": "T",
    "t": "T",
    "TS": "TS",
    "ts": "TS",
    "KL": "KL",
    "kl": "KL",
    "R": "R",
    "r": "R",
    "H": "H",
    "h": "H",
    "F": "F",
    "f": "F",
    "": "",
}

VALID_OPTIONS = ["", "X", "P", "ÔM", "CO", "CT", "T", "TS", "KL", "R", "H", "F"]


# ---------------------------------------------------------
# 1. KẾT NỐI SUPABASE AN TOÀN
# ---------------------------------------------------------
@st.cache_resource
def init_supabase():
    if create_client is None:
        return None
    try:
        url = st.secrets.get("SUPABASE_URL", "").
