import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import pandas as pd
import qrcode
import io
import uuid  # benzersiz ID üretimi için
from optimization import optimize_waste_allocation

# -------------------- STİL ----------------------
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

st.markdown(
    """
    <div class="logo-container">
        <img src="https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/streamlitLogo.png" alt="Logo">
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------- SABİT VERİLER (BAŞLANGIÇ) ----------------------
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

# -------------------- SESSION'DA KALICI FİRMALAR ----------------------
if "firma_bilgileri" not in st.session_state:
    st.session_state["firma_bilgileri"] = default_firmalar.copy()
if "yeni_firmalar" not in st.session_state:
    st.session_state["yeni_firmalar"] = []

firma_bilgileri = st.session_state["firma_bilgileri"]

# -------------------- SIDEBAR ----------------------
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
            gps = (41.01 + 0.001 * len(st.session_state["yeni_firmalar"]), 39.72 + 0.001 * len(st.session_state["yeni_firmalar"]))
            firma_koordinatlari[yeni_id] = gps
            st.session_state["firma_bilgileri"][yeni_id] = {
                "sektor": sektor_sec,
                "atik": atik_turu,
                "fiyat": fiyat,
                "miktar": miktar
            }
            st.session_state["yeni_firmalar"].append(yeni_id)
            st.success(f"{yeni_id} başarıyla eklendi!")

    # Firma Silme
    st.header("Firma Silme")
    silinecek = st.selectbox("Silinecek Firma", [""] + list(firma_bilgileri.keys()))
    if st.button("Firmayı Sil") and silinecek:
        st.session_state["firma_bilgileri"].pop(silinecek, None)
        if silinecek in st.session_state["yeni_firmalar"]:
            st.session_state["yeni_firmalar"].remove(silinecek)
        firma_koordinatlari.pop(silinecek, None)
        st.warning(f"{silinecek} silindi!")
        st.experimental_rerun()

# -------------------- FİRMA TABLOSU ----------------------
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

# Yeni eklenen firmalar için gösterim
st.subheader("Yeni Eklenen Firmalar")
for firma in st.session_state["yeni_firmalar"]:
    col1, col2 = st.columns([5, 1])
    if firma in firma_bilgileri:
        sektor = firma_bilgileri[firma]['sektor']
        atik = firma_bilgileri[firma]['atik']
        miktar = firma_bilgileri[firma]['miktar']
        fiyat = firma_bilgileri[firma]['fiyat']
        with col1:
            st.markdown(f"**{firma}** - {sektor} - {atik} ({miktar} kg, {fiyat} TL/kg)")

# -------------------- MODEL ----------------------

try:
    alici_koordinati = tuple(map(float, koordinatlar.split(",")))
except:
    alici_koordinati = (0.0, 0.0)

if secim == "Ürün almak istiyorum" and uygulama_butonu:
    results, total_cost = optimize_waste_allocation(firma_bilgileri)
    if results is None:
        st.error("Optimizasyon modeli çözülemedi!")
    else:
        st.success(f"Toplam Taşıma Maliyeti: {total_cost:.2f} TL")

        st.header("Şebeke Grafiği")
        grafik = nx.DiGraph()
        grafik.add_node("Siz", pos=(alici_koordinati[1], alici_koordinati[0]))
        for row in results:
            src = row["Gonderen"]
            dst = row["Alici"]
            miktar_flow = row["Miktar"]
            grafik.add_node(src, pos=(firma_koordinatlari.get(src, (0, 0))[1], firma_koordinatlari.get(src, (0, 0))[0]))
            grafik.add_node(dst, pos=(firma_koordinatlari.get(dst, (0, 0))[1], firma_koordinatlari.get(dst, (0, 0))[0]))
            renk = "green" if miktar_flow > 0 else "gray"
            grafik.add_edge(src, dst, mesafe=f"{miktar_flow:.2f} kg", renk=renk)

        pos = nx.get_node_attributes(grafik, 'pos')
        kenar_renkleri = [grafik[u][v]['renk'] for u, v in grafik.edges()]
        etiketler = {(u, v): grafik[u][v]['mesafe'] for u, v in grafik.edges()}

        nx.draw(grafik, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(grafik, pos, edge_labels=etiketler, font_size=8)
        nx.draw_networkx_edges(grafik, pos, edge_color=kenar_renkleri, width=2)
        plt.title("Optimal Taşıma Şebekesi")
        st.pyplot(plt)

# -------------------- QR KODU HER ZAMAN GÖSTER ----------------------
qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
qr = qrcode.make(qr_link)
qr_buffer = io.BytesIO()
qr.save(qr_buffer)
st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_container_width=True)
