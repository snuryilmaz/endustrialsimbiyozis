import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
from geopy.distance import geodesic
import pandas as pd
import qrcode
import io

# Başlık
st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")

# Tanıtım Yazısı
st.subheader("Endüstriyel Simbiyoz Nedir?")
st.write("""
Endüstriyel simbiyoz, bir üretim sürecinde açığa çıkan atık veya yan ürünlerin başka bir üretim sürecinde girdi olarak kullanılmasıdır. 
Bu yaklaşım, kaynakların daha verimli kullanılmasını sağlayarak çevresel faydalar sunar ve ekonomik tasarruflar yaratır. 
Bu araç, firmaların atık ürünlerini en uygun maliyetle paylaşabileceği bir platform sunar.
""")

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

# Firma Bilgileri Tablosu
firma_bilgileri_tablo = {
    "Firma Adı": ["Firma 1", "Firma 2", "Firma 3", "Firma 4", "Firma 5", "Firma 6", "Firma 7", "Firma 8"],
    "Sektör": ["Demir-Çelik", "Demir-Çelik", "Makine İmalat", "Plastik Enjeksiyon", "Plastik Enjeksiyon", 
               "Makine İmalat", "Makine İmalat", "Plastik Enjeksiyon"],
    "Ürün": ["Metal Talaşı", "Çelik Parçaları", "Makine Parçaları", "PT", "HDPE", 
             "Elektronik Atıklar", "Makine Parçaları", "PT"],
    "Miktar (kg)": [100, 200, 150, 300, 250, 100, 200, 400],
    "Fiyat (TL/kg)": [5, 4, 15, 10, 12, 20, 18, 8]
}

df = pd.DataFrame(firma_bilgileri_tablo)

st.subheader("Firma Bilgileri")
st.write("Aşağıdaki tablo, sistemde kayıtlı firmaların sektör, ürün, miktar ve fiyat bilgilerini göstermektedir.")
st.dataframe(df)

with st.sidebar:
    # Kullanıcı bilgileri
    st.header("Kullanıcı Bilgileri")
    ad_soyad = st.text_input("Ad Soyad")
    sirket_adi = st.text_input("Şirket Adı")
    sektor = st.selectbox("Şirketin Sektörü", ["Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalat"])

    # Dinamik Atık Türü Seçimi
    atik_turleri = {
        "Demir-Çelik": ["Metal Talaşı", "Çelik Parçaları"],
        "Plastik Enjeksiyon": ["PT", "HDPE"],
        "Makine İmalat": ["Makine Parçaları", "Elektronik Atıklar"]
    }
    atik_turu = st.selectbox("Atık Türü", atik_turleri[sektor])
    miktar = st.number_input("Alınacak Miktar (kg)", min_value=1, max_value=1000)
    koordinatlar = st.text_input("Kullanıcı GPS Koordinatları (enlem, boylam)", "41.0000,39.7000")

    # "Uygulamayı Çalıştır" butonu
    uygulama_butonu = st.button("Uygulamayı Çalıştır")

# Koordinatları al
try:
    alici_koordinati = tuple(map(float, koordinatlar.split(",")))
except ValueError:
    st.error("Geçerli bir koordinat giriniz (örnek: 41.0000,39.7000)")

if uygulama_butonu:
    # Uygun firmaları filtrele
    uygun_firmalar = {
        firma: bilgi for firma, bilgi in firma_bilgileri.items()
        if bilgi["sektor"] == sektor and bilgi["atik"] == atik_turu
    }

    if not uygun_firmalar:
        st.error("Seçilen sektöre ve atık türüne uygun firma bulunamadı!")
    else:
        # Optimizasyon modeli
        problem = pulp.LpProblem("AtikOptimizasyon", pulp.LpMaximize)
        karar_degiskenleri = {firma: pulp.LpVariable(firma, 0, uygun_firmalar[firma]["miktar"], pulp.LpContinuous) for firma in uygun_firmalar}

        # Amaç fonksiyonu: Fiyatları minimize et, alınacak miktarı maksimize et
        problem += pulp.lpSum(karar_degiskenleri[firma] * uygun_firmalar[firma]["fiyat"] for firma in uygun_firmalar)

        # Talep kısıtı
        problem += pulp.lpSum(karar_degiskenleri[firma] for firma in uygun_firmalar) <= miktar

        # Optimizasyonu çöz
        problem.solve()

        # Optimizasyon sonuçlarını hesapla
        toplam_alinan = sum(karar_degiskenleri[firma].varValue for firma in uygun_firmalar)
        eksik_miktar = miktar - toplam_alinan

        st.header("Optimizasyon Sonuçları")
        for firma in uygun_firmalar:
            alinan_miktar = karar_degiskenleri[firma].varValue
            if alinan_miktar > 0:
                st.write(f"{firma}: {alinan_miktar:.2f} kg, Fiyat: {uygun_firmalar[firma]['fiyat']} TL/kg")

        if eksik_miktar > 0:
            st.warning(f"Talebinizin {eksik_miktar:.2f} kg'ı karşılanamadı.")
        else:
            st.success("Tüm talebiniz başarıyla karşılandı!")

        # QR Kod Ekleme
        qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
        qr = qrcode.make(qr_link)
        qr_buffer = io.BytesIO()
        qr.save(qr_buffer)
        st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_column_width=True)
