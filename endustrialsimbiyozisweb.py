import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import json
from geopy.distance import geodesic
import qrcode
from PIL import Image

# Matris dosyasını yükleme
with open("matrices.json", "r") as dosya:
    matrisler = json.load(dosya)

# Kullanıcı arayüzü başlığı
st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")

# Kullanıcı bilgileri
with st.sidebar:
    st.header("Kullanıcı Bilgileri")
    ad_soyad = st.text_input("Ad Soyad")
    sirket_adi = st.text_input("Şirket Adı")
    sektor = st.selectbox("Şirketin Sektörü", ["Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalat"])
    alici_koordinati = st.text_input("Kullanıcı GPS Koordinatları (enlem,boylam)", "41.0000,39.7000")

    # Alıcı koordinatlarını dönüştür
    try:
        alici_koordinati = tuple(map(float, alici_koordinati.split(",")))
    except ValueError:
        st.error("Geçerli bir koordinat giriniz (örnek: 41.0000,39.7000)")

# Firmaların GPS koordinatları
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

# Mesafeleri hesapla
def mesafe_hesapla(alici_koordinati, firma_koordinatlari):
    mesafeler = {}
    for firma, koordinat in firma_koordinatlari.items():
        mesafe = geodesic(alici_koordinati, koordinat).kilometers
        mesafeler[firma] = mesafe
    return mesafeler

mesafeler = mesafe_hesapla(alici_koordinati, firma_koordinatlari)

# Optimizasyon modeli
problem = pulp.LpProblem("EndustriyelSimbiyoz", pulp.LpMinimize)
karar_degiskenleri = {firma: pulp.LpVariable(f"{firma}", 0, 1, pulp.LpBinary) for firma in firma_koordinatlari}
problem += pulp.lpSum(karar_degiskenleri[firma] * mesafe for firma, mesafe in mesafeler.items()), "ToplamMesafe"

# Optimizasyonu çöz
problem.solve()

# Şebeke grafiği çizimi
st.header("Şebeke Grafiği")
grafik = nx.DiGraph()

# Düğümler ekleniyor
grafik.add_node("Siz", pos=(alici_koordinati[1], alici_koordinati[0]), rol="alici")
for firma, koordinat in firma_koordinatlari.items():
    grafik.add_node(firma, pos=(koordinat[1], koordinat[0]), rol="satici")

# Kenarlar ekleniyor
optimal_firma = None
for firma, mesafe in mesafeler.items():
    renk = "green" if pulp.value(karar_degiskenleri[firma]) == 1 else "gray"
    grafik.add_edge(firma, "Siz", mesafe=f"{mesafe:.2f} km", renk=renk)
    if renk == "green":
        optimal_firma = firma

# Grafiği çizmek için düzenleme
pos = nx.get_node_attributes(grafik, 'pos')
kenar_renkleri = [grafik[u][v]["renk"] for u, v in grafik.edges()]
etiketler = {(u, v): grafik[u][v]["mesafe"] for u, v in grafik.edges()}

nx.draw(grafik, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold")
nx.draw_networkx_edge_labels(grafik, pos, edge_labels=etiketler, font_size=8)
nx.draw_networkx_edges(grafik, pos, edge_color=kenar_renkleri, width=2)
plt.title("Optimal Eşleşme Şebekesi")
st.pyplot(plt)

# Optimizasyon sonuçları
st.header("Optimizasyon Sonuçları")
if optimal_firma:
    st.write(f"Optimal Eşleşme Sağlanan Firma: {optimal_firma}")
st.write(f"Toplam Mesafe: {pulp.value(problem.objective):.2f} km")
