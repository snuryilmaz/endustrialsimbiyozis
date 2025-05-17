import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
import json
import os

# ======== KALICI EK FİRMA JSON DOSYASI ========
JSON_PATH = "firma_data.json"

def load_ek_firmalar():
    if not os.path.exists(JSON_PATH):
        return []
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_ek_firmalar(firmalar):
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(firmalar, f, ensure_ascii=False, indent=2)

# ======== SABİT 8 FİRMA TANIMI ========
default_firmalar = {
    "Firma 1": {"sektor": "Demir-Çelik", "atik": "Metal Talaşı", "fiyat": 5, "miktar": 100},
    "Firma 2": {"sektor": "Demir-Çelik", "atik": "Çelik Parçaları", "fiyat": 4, "miktar": 200},
    "Firma 3": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 15, "miktar": 150},
    "Firma 4": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 10, "miktar": 300},
    "Firma 5": {"sektor": "Plastik Enjeksiyon", "atik": "HDPE", "fiyat": 12, "miktar": 250},
    "Firma 6": {"sektor": "Makine İmalat", "atik": "Elektronik Atıklar", "fiyat": 20, "miktar": 100},
    "Firma 7": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 18, "miktar": 200},
    "Firma 8": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 8, "miktar": 400},
}

# ======== EK FİRMALARI JSON'DAN YÜKLE ========
eklenenler = load_ek_firmalar()
ek_firmalar = {}
for f in eklenenler:
    ek_firmalar[f['firma_adi']] = {
        "sektor": f["sektor"],
        "atik": f["atik"],
        "fiyat": f["fiyat"],
        "miktar": f["miktar"]
    }

# ======== FİRMALARI BİRLEŞTİR ========
firma_bilgileri = default_firmalar.copy()
firma_bilgileri.update(ek_firmalar)

# ======== SABİT VERİLER ========
turikler = {
    "Demir-Çelik": ["Metal Talaşı", "Çelik Parçaları"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalat": ["Makine Parçaları", "Elektronik Atıklar"]
}
firma_koordinatlari = {
    "Firma 1": (41.0105, 39.7266),
    "Firma 2": (40.9900, 39.7200),
    "Firma 3": (41.0200, 39.7400),
    "Firma 4": (41.0005, 39.7050),
    "Firma 5": (41.0150, 39.7300),
    "Firma 6": (41.0250, 39.7350),
    "Firma 7": (41.0300, 39.7400),
    "Firma 8": (41.0350, 39.7450),
}

# Yeni eklenen firmalara rastgele koordinat verelim
for i, firma in enumerate(ek_firmalar.keys()):
    firma_koordinatlari[firma] = (41.04 + 0.001 * i, 39.74 + 0.001 * i)

# ========== STİL ==========
st.markdown("""
    <style>
    body {
        background-image: url('https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/arsinosb.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(255, 255, 255, 0.6);
        padding-top: 80px;
    }
    .logo-container {
        position: fixed;
        top: 15px;
        right: 15px;
        z-index: 9999;
        background-color: white;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 0 10px rgba(0,0,0,0.2);
    }
    .logo-container img {
        height: 100px;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2e7d32 !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown(
    """
    <div class="logo-container">
        <img src="https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/streamlitLogo.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# ========== BAŞLIK ==========
st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")
st.subheader("Endüstriyel Simbiyoz Nedir?")
st.write("""
    Endüstriyel simbiyoz, bir üretim sürecinde açığa çıkan atık veya yan ürünlerin başka bir üretim sürecinde girdi olarak kullanılmasıdır.
    Bu araç, firmaların atık ürünlerini en uygun maliyetle paylaşabileceği bir platform sunar.
""")

# ========== SIDEBAR ==========
with st.sidebar:
    st.title("Kullanıcı Seçimi")

    secim = st.radio(
        "Ne yapmak istiyorsunuz?",
        ["Ürün almak istiyorum", "Satıcı kaydı yapmak istiyorum"],
        index=0
    )

    if secim == "Ürün almak istiyorum":
        st.header("Alıcı Bilgileri")
        ad_soyad = st.text_input("Ad Soyad")
        sirket_adi = st.text_input("Şirket Adı")
        sektor = st.selectbox("Şirketin Sektörü", list(turikler.keys()))
        atik_turu = st.selectbox("Atık Türü", turikler[sektor])
        miktar = st.number_input("Alınacak Miktar (kg)", min_value=1, max_value=1000)
        koordinatlar = st.text_input("Kullanıcı GPS Koordinatları (enlem, boylam)", "41.0000,39.7000")
        uygulama_butonu = st.button("Uygulamayı Çalıştır")

    elif secim == "Satıcı kaydı yapmak istiyorum":
        st.header("Satıcı Kaydı")
        firma_adi = st.text_input("Firma Adı")
        sektor_sec = st.selectbox("Sektör", list(turikler.keys()))
        atik_secenekleri = turikler[sektor_sec]
        atik_turu = st.selectbox("Satmak istediğiniz Atık Ürün", atik_secenekleri)
        miktar = st.number_input("Satmak istediğiniz ürün miktarı (kg)", min_value=1)
        fiyat = st.number_input("Ürünü ne kadara satmak istiyorsunuz? (TL/kg)", min_value=0.0)
        kaydet_buton = st.button("KAYDIMI TAMAMLA")
        if kaydet_buton and firma_adi.strip():
            yeni_id = firma_adi.strip()
            yeni_firma = {
                "firma_adi": yeni_id,
                "sektor": sektor_sec,
                "atik": atik_turu,
                "fiyat": fiyat,
                "miktar": miktar
            }
            # JSON'a kaydet
            eklenenler = load_ek_firmalar()
            # aynı isim varsa güncelle
            eklenenler = [f for f in eklenenler if f["firma_adi"] != yeni_id]
            eklenenler.append(yeni_firma)
            save_ek_firmalar(eklenenler)
            st.success(f"{yeni_id} başarıyla eklendi!")
           st.rerun() 

    st.markdown("### Firma Silme")
    eklenenler = load_ek_firmalar()
    eklenen_firma_adlari = [f["firma_adi"] for f in eklenenler]
    silinecek = st.selectbox("Silinecek Firma", [""] + eklenen_firma_adlari)
    if st.button("Firmayı Sil") and silinecek:
        eklenenler = [f for f in eklenenler if f["firma_adi"] != silinecek]
        save_ek_firmalar(eklenenler)
        st.warning(f"{silinecek} silindi!")
       st.rerun() 

# ========== FİRMA TABLOSU ==========
firma_bilgileri_tablo = {
    "Firma Adı": list(firma_bilgileri.keys()),
    "Sektör": [v["sektor"] for v in firma_bilgileri.values()],
    "Ürün": [v["atik"] for v in firma_bilgileri.values()],
    "Miktar (kg)": [v["miktar"] for v in firma_bilgileri.values()],
    "Fiyat (TL/kg)": [v["fiyat"] for v in firma_bilgileri.values()]
}
df = pd.DataFrame(firma_bilgileri_tablo)
st.subheader("Firma Bilgileri")
st.write("Aşağıdaki tablo, sistemde kayıtlı firmaların sektör, ürün, miktar ve fiyat bilgilerini göstermektedir.")
st.dataframe(df)

# ========== YENİ EKLENENLER ==========
st.subheader("Yeni Eklenen Firmalar")
for firma in ek_firmalar:
    info = ek_firmalar[firma]
    st.markdown(f"**{firma}** - {info['sektor']} - {info['atik']} ({info['miktar']} kg, {info['fiyat']} TL/kg)")

# ========== OPTİMİZASYON (PUlP) ==========
from pulp import LpProblem, LpVariable, lpSum, LpMinimize, LpStatus, value

def optimize_waste_allocation_pulp(firma_bilgileri, atik_turu, toplam_miktar):
    # Sadece seçili atık türü ve pozitif miktarı olan firmaları bul
    uygun_firmalar = {firma: info for firma, info in firma_bilgileri.items() if info["atik"] == atik_turu and info["miktar"] > 0}
    if not uygun_firmalar:
        return None, 0, []
    problem = LpProblem("Atik_Optimizasyonu", LpMinimize)
    # Karar değişkenleri
    x = {firma: LpVariable(f"x_{firma}", lowBound=0, upBound=uygun_firmalar[firma]["miktar"]) for firma in uygun_firmalar}
    # Amaç fonksiyon: toplam maliyeti minimize et
    problem += lpSum([x[firma] * uygun_firmalar[firma]["fiyat"] for firma in uygun_firmalar])
    # Talep kısıtı
    problem += lpSum([x[firma] for firma in uygun_firmalar]) == toplam_miktar
    status = problem.solve()
    if LpStatus[status] != "Optimal":
        return None, 0, []
    # Sonuçları hazırla
    sonuclar = []
    for firma in uygun_firmalar:
        miktar_alinan = x[firma].varValue if x[firma].varValue else 0
        if miktar_alinan > 0:
            sonuclar.append({"Gonderen": firma, "Alici": "Siz", "AtikTuru": atik_turu, "Miktar": miktar_alinan, "Birim Fiyat": uygun_firmalar[firma]["fiyat"]})
    toplam_maliyet = value(problem.objective)
    return sonuclar, toplam_maliyet, uygun_firmalar

# ========== MODEL ÇAĞRISI & ŞEBEKE ÇİZİMİ ==========
try:
    alici_koordinati = tuple(map(float, koordinatlar.split(",")))
except:
    alici_koordinati = (0.0, 0.0)

if secim == "Ürün almak istiyorum" and uygulama_butonu:
    results, total_cost, uygun_firmalar = optimize_waste_allocation_pulp(firma_bilgileri, atik_turu, miktar)
    if results is None or len(results) == 0:
        st.error("Optimizasyon modeli çözülemedi! (Uygun firma yok ya da toplam miktar sağlanamıyor.)")
    else:
        st.success(f"Toplam Taşıma Maliyeti: {total_cost:.2f} TL")
        # Detaylı çözüm:
        detaylar = ""
        for row in results:
            detaylar += f"{row['Gonderen']} firmasından {row['Miktar']} kg alınacak. Birim fiyat: {row['Birim Fiyat']} TL/kg\n"
        st.info(f"Optimal çözüm:\n{detaylar}")

        st.header("Şebeke Grafiği")
        grafik = nx.DiGraph()
        grafik.add_node("Siz", pos=(alici_koordinati[1], alici_koordinati[0]))
        for row in results:
            src = row["Gonderen"]
            grafik.add_node(src, pos=(firma_koordinatlari[src][1], firma_koordinatlari[src][0]))
            grafik.add_edge(src, "Siz", mesafe=f"{row['Miktar']:.2f} kg", renk="green")
        pos = nx.get_node_attributes(grafik, 'pos')
        kenar_renkleri = [grafik[u][v]['renk'] for u, v in grafik.edges()]
        etiketler = {(u, v): grafik[u][v]['mesafe'] for u, v in grafik.edges()}
        plt.figure(figsize=(6,6))
        nx.draw(grafik, pos, with_labels=True, node_color="lightblue", node_size=2500, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(grafik, pos, edge_labels=etiketler, font_size=8)
        nx.draw_networkx_edges(grafik, pos, edge_color=kenar_renkleri, width=2)
        plt.title("Optimal Taşıma Şebekesi")
        plt.axis('off')
        st.pyplot(plt)

# ======== QR KODU HER ZAMAN ========
qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
qr = qrcode.make(qr_link)
qr_buffer = io.BytesIO()
qr.save(qr_buffer)
st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_container_width=True)
