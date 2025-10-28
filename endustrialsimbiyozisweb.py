import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
import math
import os
import random
from datetime import date, timedelta
import streamlit as st
st.title("Başarılı! Streamlit uygulaman yüklendi.")
# Backend klasöründen sabit veri ve fonksiyonları import et
import sys
sys.path.append('./backend')

from backend.static_data import varsayilan_firmalar, turikler, firma_koordinatlari
from backend.optimize import optimize_waste_allocation, get_new_coordinates

excel_path = "kayitlar.xlsx"
if "excel_data" not in st.session_state:
    if os.path.exists(excel_path):
        st.session_state["excel_data"] = pd.read_excel(excel_path)
    else:
        st.session_state["excel_data"] = pd.DataFrame(
            columns=["Islem Tipi", "Firma Adı", "Sektör", "Atık Türü", "Miktar", "Fiyat", "Kullanıcı Adı"]
        )

TURKISH_MONTHS = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]

def format_tarih(d: date):
    ay_adi = TURKISH_MONTHS[d.month - 1]
    return f"{d.day} {ay_adi} {d.year}"

# -------------------- STATE YÖNETİMİ ----------------------
if "firma_bilgileri" not in st.session_state:
    st.session_state["firma_bilgileri"] = {k: v.copy() for k, v in varsayilan_firmalar.items()}
if "yeni_firmalar" not in st.session_state:
    st.session_state["yeni_firmalar"] = []
if "firma_koordinatlari" not in st.session_state:
    st.session_state["firma_koordinatlari"] = firma_koordinatlari.copy()

firma_bilgileri = st.session_state["firma_bilgileri"]
firma_koordinatlari = st.session_state["firma_koordinatlari"]
varsayilan_firma_isimleri = list(varsayilan_firmalar.keys())

# (Aşağıda kendi Streamlit uygulama kodunu olduğu gibi kullanabilirsin)
# ... Streamlit arayüzü, optimize, tablo, grafik vb. kodlar burada devam edecek ...

# ... (Geri kalan Streamlit kodunu olduğu gibi kullanabilirsin, sadece optimize fonksiyonunu ve sabit veri yapılarını artık backend'den çağırıyorsun.)


