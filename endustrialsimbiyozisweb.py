import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
import json
import pandas as pd

# Matris dosyasını yükleme (uzaklık, süre ve maliyet matrisleri JSON dosyasından alınacak)
with open("matrices.json", "r") as dosya:
    matrisler = json.load(dosya)

uzaklik_matrisi = pd.DataFrame(matrisler["distance_matrix"])
sure_matrisi = pd.DataFrame(matrisler["time_matrix"])
maliyet_matrisi = pd.DataFrame(matrisler["cost_matrix"])

# Streamlit URL (Yerli ağ için kendi IP adresinizi yazın)
streamlit_url = "http://192.168.1.10:8501"

# Optimizasyon modeli oluşturma fonksiyonu
def optimizasyon_modeli_olustur(optimizasyon_amaci, alici_talebi, satici_verileri):
    # Optimizasyon problemi oluşturuluyor
    problem = pulp.LpProblem("EndustriyelSimbiyoz", pulp.LpMinimize)

    # Karar değişkenleri (Her satıcının ne kadar miktar sağlayacağı)
    satici_degiskenleri = {satici: pulp.LpVariable(f"Satıcı_{satici}", 0, satici_verileri[satici]['kapasite'], pulp.LpContinuous)
                           for satici in satici_verileri}

    # Amaç fonksiyonu (Optimizasyon amacı)
    if optimizasyon_amaci == "Yol minimizasyonu":
        problem += pulp.lpSum(satici_degiskenleri[satici] * satici_verileri[satici]['uzaklik'] for satici in satici_verileri), "ToplamUzaklik"
    elif optimizasyon_amaci == "Maliyet minimizasyonu":
        problem += pulp.lpSum(satici_degiskenleri[satici] * satici_verileri[satici]['maliyet'] for satici in satici_verileri), "ToplamMaliyet"
    elif optimizasyon_amaci == "Süre minimizasyonu":
        problem += pulp.lpSum(satici_degiskenleri[satici] * satici_verileri[satici]['sure'] for satici in satici_verileri), "ToplamSure"

    # Talep kısıtı (Alici talebi toplamda karşılanmalı)
    problem += pulp.lpSum(satici_degiskenleri[satici] for satici in satici_verileri) == alici_talebi, "TalepKisiti"

    # Optimizasyon problemi çözülüyor
    problem.solve()

    return problem, satici_degiskenleri

# Şebeke grafiği çizim fonksiyonu
def sebeke_grafigi_ciz(satici_verileri, alici_talebi, satici_degiskenleri, optimizasyon_amaci, optimal_satici):
    # Şebeke grafiği için yönlü bir grafik oluşturuluyor
    grafik = nx.DiGraph()

    # Optimizasyon amacına göre veri anahtarları
    optimizasyon_harita = {
        "Yol minimizasyonu": "uzaklik",
        "Maliyet minimizasyonu": "maliyet",
        "Süre minimizasyonu": "sure"
    }

    # Düğümler ekleniyor (Alıcı ve Satıcılar)
    grafik.add_node("Siz", rol="alici")  # Alıcıyı temsil eden düğüm
    for satici in satici_verileri:
        grafik.add_node(f"Firma {satici}", rol="satici")  # Satıcıları temsil eden düğümler

    # Kenarlar ekleniyor (Satıcıdan alıcıya olan bağlantılar)
    for satici in satici_verileri:
        renk = "green" if satici == optimal_satici else "gray"  # Optimal eşleşme yeşil renkle gösterilecek
        grafik.add_edge(f"Firma {satici}", "Siz",
                        agirlik=satici_verileri[satici][optimizasyon_harita[optimizasyon_amaci]],
                        miktar=satici_degiskenleri[satici].varValue,
                        renk=renk)

    # Grafiği çizmek için düzenleme
    konum = nx.spring_layout(grafik)
    kenar_etiketleri = {(u, v): f"{veri['miktar']} birim" for u, v, veri in grafik.edges(data=True)}
    kenar_renkleri = [veri["renk"] for _, _, veri in grafik.edges(data=True)]

    # Grafiği çizdir
    nx.draw(grafik, konum, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(grafik, konum, edge_labels=kenar_etiketleri)
    nx.draw_networkx_edges(grafik, konum, edge_color=kenar_renkleri, width=2)
    plt.title("Optimal Eşleşme Şebekesi")
    st.pyplot(plt)

# Streamlit arayüzü başlığı
st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")

# Kullanıcı bilgileri için sol şerit
st.sidebar.header("Kullanıcı Bilgileri")
ad_soyad = st.sidebar.text_input("Adınız Soyadınız", "")
sirket_adi = st.sidebar.text_input("Şirket İsmi", "")
sektor = st.sidebar.selectbox(
    "Şirket Sektörü",
    ["", "Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalatı"],  # Boş seçenek varsayılan
    index=0
)

# Atık bilgileri seçimi
atik_secenekleri = {
    "Demir-Çelik": ["Demir Talaşı", "Çelik Artığı"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalatı": ["Metal Talaşı", "Yağlı Atık"]
}
atik = st.sidebar.selectbox("Almak İstediğiniz Atık", atik_secenekleri.get(sektor, []))

# Optimizasyon amacı ve talep
st.sidebar.header("Optimizasyon Seçenekleri")
optimizasyon_amaci = st.sidebar.selectbox(
    "Optimizasyon amacını seçin",
    ["Yol minimizasyonu", "Maliyet minimizasyonu", "Süre minimizasyonu"]
)
alici_talebi = st.sidebar.number_input("Alıcı talebi (birim)", min_value=1, step=1)

# Satıcı verileri (Sektör ve atık bilgisine göre filtreleme)
satici_verileri = {
    "Firma 1": {"sektor": "Plastik Enjeksiyon", "atik": "HDPE", "kapasite": 100, "uzaklik": 50, "maliyet": 15, "sure": 5},
    "Firma 2": {"sektor": "Demir-Çelik", "atik": "Demir Talaşı", "kapasite": 200, "uzaklik": 30, "maliyet": 10, "sure": 3},
    "Firma 3": {"sektor": "Makine İmalatı", "atik": "Metal Talaşı", "kapasite": 150, "uzaklik": 70, "maliyet": 20, "sure": 7},
    # Diğer firmalar...
}

# Seçilen sektöre ve atığa uygun firmaları filtreleme
filtrelenmis_firmalar = {
    firma: veri for firma, veri in satici_verileri.items() if veri["sektor"] == sektor and veri["atik"] == atik
}

# Optimizasyon butonu
if st.sidebar.button("Optimizasyonu Çalıştır"):
    # Optimizasyon modeli oluştur ve çalıştır
    problem, satici_degiskenleri = optimizasyon_modeli_olustur(optimizasyon_amaci, alici_talebi, filtrelenmis_firmalar)

    # Optimizasyon sonuçları
    if pulp.LpStatus[problem.status] == "Optimal":
        st.success("Optimal eşleşme sağlandı!")
        optimal_satici = max(satici_degiskenleri, key=lambda x: satici_degiskenleri[x].varValue or 0)
        sebeke_grafigi_ciz(filtrelenmis_firmalar, alici_talebi, satici_degiskenleri, optimizasyon_amaci, optimal_satici)

        # Toplam değerler
        toplam_maliyet = sum(filtrelenmis_firmalar[satici]["maliyet"] * (satici_degiskenleri[satici].varValue or 0) for satici in filtrelenmis_firmalar)
        toplam_sure = sum(filtrelenmis_firmalar[satici]["sure"] * (satici_degiskenleri[satici].varValue or 0) for satici in filtrelenmis_firmalar)
        st.subheader("Toplam Değerler")
        st.write(f"Toplam Maliyet: {toplam_maliyet} $")
        st.write(f"Toplam Süre: {toplam_sure} saat")
        st.write(f"Toplam Taşınacak Miktar: {alici_talebi} birim")
    else:
        st.error("Optimum çözüm bulunamadı.")

# QR kod oluştur ve göster
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(streamlit_url)
qr.make(fit=True)
img = qr.make_image(fill_color="black", back_color="white")
img.save("qrcode.png")

st.image("qrcode.png", caption="Bu QR kodu tarayarak siteye erişin!", use_column_width=True)
st.write(f"Erişim için URL: {streamlit_url}")
