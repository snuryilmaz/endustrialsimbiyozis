import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
from optimization import optimize_waste_allocation

# --------- SABİT VERİLER ----------
turikler = {
    "Demir-Çelik": ["Metal Talaşı", "Çelik Parçaları"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalat": ["Makine Parçaları", "Elektronik Atıklar"]
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

if "firma_bilgileri" not in st.session_state:
    st.session_state["firma_bilgileri"] = default_firmalar.copy()
if "yeni_firmalar" not in st.session_state:
    st.session_state["yeni_firmalar"] = []

firma_bilgileri = st.session_state["firma_bilgileri"]

# --------- ARAYÜZ/STİL ----------
st.markdown(
    """
    <style>
    body {background-image: url('https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/arsinosb.jpg');background-size: cover;background-repeat: no-repeat;}
    .stApp {background-color: rgba(255,255,255,0.6);}
    .logo-container {position: fixed;top: 15px;right: 15px;z-index: 9999;background-color: white;padding: 10px;border-radius: 12px;box-shadow: 0 0 10px rgba(0,0,0,0.2);}
    .logo-container img {height: 100px;}
    h1, h2, h3, h4, h5, h6 {color: #2e7d32 !important;}
    </style>
    """, unsafe_allow_html=True
)
st.markdown(
    """<div class="logo-container">
        <img src="https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/streamlitLogo.png" alt="Logo">
    </div>""",
    unsafe_allow_html=True
)

st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")
st.subheader("Endüstriyel Simbiyoz Nedir?")
st.write("Endüstriyel simbiyoz, bir üretim sürecinde açığa çıkan atık veya yan ürünlerin başka bir üretim sürecinde girdi olarak kullanılmasıdır. Bu araç, firmaların atık ürünlerini en uygun maliyetle paylaşabileceği bir platform sunar.")

# --------- SIDEBAR KULLANICI ---------
with st.sidebar:
    st.title("Kullanıcı Seçimi")
    secim = st.radio("Ne yapmak istiyorsunuz?", ["Ürün almak istiyorum", "Satıcı kaydı yapmak istiyorum"], index=0)

    if secim == "Ürün almak istiyorum":
        st.header("Alıcı Bilgileri")
        ad_soyad = st.text_input("Ad Soyad")
        sirket_adi = st.text_input("Şirket Adı")
        sektor = st.selectbox("Şirketin Sektörü", list(turikler.keys()))
        atik_turu = st.selectbox("Atık Türü", turikler[sektor])
        miktar = st.number_input("Alınacak Miktar (kg)", min_value=1, max_value=1000)
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
            st.session_state["firma_bilgileri"][yeni_id] = {
                "sektor": sektor_sec,
                "atik": atik_turu,
                "fiyat": fiyat,
                "miktar": miktar
            }
            st.session_state["yeni_firmalar"].append(yeni_id)
            st.success(f"{yeni_id} başarıyla eklendi!")
    st.header("Firma Silme")
    silinecek = st.selectbox("Silinecek Firma", [""] + list(firma_bilgileri.keys()))
    if st.button("Firmayı Sil") and silinecek:
        st.session_state["firma_bilgileri"].pop(silinecek, None)
        if silinecek in st.session_state["yeni_firmalar"]:
            st.session_state["yeni_firmalar"].remove(silinecek)
        st.warning(f"{silinecek} silindi!")
        st.experimental_rerun()

# --------- TABLO ----------
firma_bilgileri_tablo = {
    "Firma Adı": list(firma_bilgileri.keys()),
    "Sektör": [v["sektor"] for v in firma_bilgileri.values()],
    "Ürün": [v["atik"] for v in firma_bilgileri.values()],
    "Miktar (kg)": [v["miktar"] for v in firma_bilgileri.values()],
    "Fiyat (TL/kg)": [v["fiyat"] for v in firma_bilgileri.values()]
}
df = pd.DataFrame(firma_bilgileri_tablo)
st.subheader("Firma Bilgileri")
st.dataframe(df)

st.subheader("Yeni Eklenen Firmalar")
for firma in st.session_state["yeni_firmalar"]:
    if firma in firma_bilgileri:
        sektor = firma_bilgileri[firma]['sektor']
        atik = firma_bilgileri[firma]['atik']
        miktar = firma_bilgileri[firma]['miktar']
        fiyat = firma_bilgileri[firma]['fiyat']
        st.markdown(f"**{firma}** - {sektor} - {atik} ({miktar} kg, {fiyat} TL/kg)")

# --------- MODEL VE ŞEBEKE ---------
if secim == "Ürün almak istiyorum" and uygulama_butonu:
    results, toplam_maliyet, uygun_firmalar = optimize_waste_allocation(firma_bilgileri, atik_turu, miktar)
    if not results:
        st.error("Talebinizi karşılayacak firma yok veya miktar uygun değil!")
    else:
        st.success(f"Toplam Taşıma Maliyeti: {toplam_maliyet:.2f} TL")
        st.header("Şebeke Grafiği")
        g = nx.DiGraph()
        g.add_node("Siz")
        for row in results:
            firma = row["Firma"]
            g.add_node(firma)
            g.add_edge(firma, "Siz", label=f"{row['AlinanMiktar']:.0f} kg\n{row['BirimFiyat']} TL/kg")
        pos = nx.spring_layout(g)
        plt.figure(figsize=(6, 4))
        nx.draw(g, pos, with_labels=True, node_color=["#95d5b2" if n=="Siz" else "#ffd6a5" for n in g.nodes()], node_size=2500, font_size=12)
        nx.draw_networkx_edge_labels(g, pos, edge_labels={(u, v): d["label"] for u, v, d in g.edges(data=True)}, font_size=10)
        plt.axis('off')
        st.pyplot(plt)

        # Özet
        st.markdown("### Eşleşme Sonucu")
        for row in results:
            st.markdown(f"- {row['Firma']}'dan **{row['AlinanMiktar']:.0f} kg** alınacak. ({row['BirimFiyat']} TL/kg → {row['Tutar']:.0f} TL)")
        st.markdown(f"**Toplam maliyet:** {toplam_maliyet:.0f} TL")

# --------- QR KODU HER ZAMAN GÖSTER ---------
qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
qr = qrcode.make(qr_link)
qr_buffer = io.BytesIO()
qr.save(qr_buffer)
st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_container_width=True)
