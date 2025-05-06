import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
import json
import pandas as pd
from geopy.distance import geodesic  # Gerçek mesafe hesaplama için

# Matris dosyasını yükleme (uzaklık, süre ve maliyet matrisleri JSON dosyasından alınır)
with open("matrices.json", "r") as dosya:
    matrisler = json.load(dosya)

# Firmaların ve alıcının GPS koordinatları (örnek veriler)
firma_koordinatlari = {
    "Firma 1": (41.0105, 39.7266),
    "Firma 2": (40.9900, 39.7200),
    "Firma 3": (41.0200, 39.7400)
}

# Kullanıcı konumu (örnek: ARSİN OSB merkezi)
kullanici_koordinati = (41.0000, 39.7000)

# Mesafe hesaplama fonksiyonu
def mesafe_hesapla(konum1, konum2):
    return geodesic(konum1, konum2).kilometers

# Uzaklık matrisini güncelleme
for firma, koordinat in firma_koordinatlari.items():
    mesafe = mesafe_hesapla(kullanici_koordinati, koordinat)
    matrisler["distance_matrix"]["Buyer"][firma] = mesafe
    matrisler["distance_matrix"][firma]["Buyer"] = mesafe

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
