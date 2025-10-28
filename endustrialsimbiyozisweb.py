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

# Modüller ve fonksiyonlar backend klasöründen import edildi
import sys
sys.path.append('./backend')

from backend.models import varsayilan_firmalar, turikler, firma_koordinatlari
from backend.optimize import optimize_waste_allocation, get_new_coordinates

# Excel işlemleri ve state yönetimi aynı şekilde kalabilir

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

# (Devamındaki Streamlit kodları ve arayüz aynı şekilde kalabilir)

# Artık optimize fonksiyonu ve sabit veri yapısı backend klasöründen çağrılıyor!
# Eklediğin yeni firma ve koordinat fonksiyonları da optimize.py'den import edilir.

# ... (Geri kalan Streamlit kodunu olduğu gibi kullanabilirsin, sadece optimize fonksiyonunu ve sabit veri yapılarını artık backend'den çağırıyorsun.)
