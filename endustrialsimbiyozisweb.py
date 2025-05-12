import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic

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

# Firmaların sektör ve atık bilgileri
firma_bilgileri = {
    "Firma 1": {"sektor": "Demir-Çelik", "atik": "Metal Talaşı", "fiyat": 5, "miktar": 100},
    "Firma 2": {"sektor": "Demir-Çelik", "atik": "Çelik Parçaları", "fiyat": 4, "miktar": 200},
    "Firma 3": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 15, "miktar": 150},
    "Firma 4": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 10, "miktar": 300},
    "Firma 5": {"sektor": "Plastik Enjeksiyon", "atik": "HDPE", "fiyat": 12, "miktar": 250},
    "Firma 6": {"sektor": "Makine İmalat", "atik": "Elektronik Atıklar", "fiyat": 20, "miktar": 100},
    "Firma 7": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 18, "miktar": 200},
    "Firma 8": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 8, "miktar": 400},
}

# Kullanıcı bilgileri
with st.sidebar:
    st.header("Kullanıcı Bilgileri")
    ad_soyad = st.text_input("Ad Soyad")
    sirket_adi = st.text_input("Şirket Adı")
    sektor = st.selectbox("Şirketin Sektörü", ["Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalat"])
    atik_turu = st.selectbox("Atık Türü", ["Metal Talaşı", "Çelik Parçaları", "PT", "HDPE", "Makine Parçaları", "Elektronik Atıklar"])
    miktar = st.number_input("Alınacak Miktar (kg)", min_value=1, max_value=1000)
    koordinatlar = st.text_input("Kullanıcı GPS Koordinatları (enlem, boylam)", "41.0000,39.7000")

# Koordinatları al
try:
    alici_koordinati = tuple(map(float, koordinatlar.split(",")))
except ValueError:
    st.error("Geçerli bir koordinat giriniz (örnek: 41.0000,39.7000)")

# "Uygulamayı Çalıştır" butonu
if st.button("Uygulamayı Çalıştır"):
    # Uygun firmaları filtrele
    uygun_firmalar = {
        firma: bilgi for firma, bilgi in firma_bilgileri.items()
        if bilgi["sektor"] == sektor and bilgi["atik"] == atik_turu
    }

    # Firmalarla mesafeleri hesapla
    mesafeler = {
        firma: geodesic(alici_koordinati, firma_koordinatlari[firma]).kilometers
        for firma in uygun_firmalar
    }

    # Optimizasyon modeli
    problem = pulp.LpProblem("AtikOptimizasyon", pulp.LpMinimize)
    karar_degiskenleri = {firma: pulp.LpVariable(firma, 0, 1, pulp.LpBinary) for firma in uygun_firmalar}

    # Amaç fonksiyonu: Mesafe ve maliyeti minimize et
    problem += pulp.lpSum(
        karar_degiskenleri[firma] * (mesafeler[firma] + uygun_firmalar[firma]["fiyat"])
        for firma in uygun_firmalar
    )

    # Talep kısıtı
    problem += pulp.lpSum(
        karar_degiskenleri[firma] * uygun_firmalar[firma]["miktar"] for firma in uygun_firmalar
    ) >= miktar

    # Optimizasyonu çöz
    problem.solve()

    # Şebeke grafiği
    st.header("Şebeke Grafiği")
    grafik = nx.DiGraph()
    grafik.add_node("Siz", pos=(alici_koordinati[1], alici_koordinati[0]))

    optimal_firmalar = []
    for firma in uygun_firmalar:
        grafik.add_node(firma, pos=(firma_koordinatlari[firma][1], firma_koordinatlari[firma][0]))
        renk = "green" if karar_degiskenleri[firma].varValue == 1 else "gray"
        grafik.add_edge(firma, "Siz", mesafe=f"{mesafeler[firma]:.2f} km", renk=renk)

        if karar_degiskenleri[firma].varValue == 1:
            optimal_firmalar.append(firma)

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
    toplam_maliyet = pulp.value(problem.objective)
    st.write(f"Toplam Maliyet: {toplam_maliyet:.2f} TL")
    st.write("Optimal Eşleşme Sağlanan Firmalar:")
    for firma in optimal_firmalar:
        st.write(f"{firma} - Mesafe: {mesafeler[firma]:.2f} km, Fiyat: {uygun_firmalar[firma]['fiyat']} TL/kg")
