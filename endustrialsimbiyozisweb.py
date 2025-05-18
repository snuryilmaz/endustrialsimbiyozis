import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
import pulp

# -------------------- BAŞLIK VE TANITIM ----------------------
st.markdown("""
    <style>
    .green-title {
        color: #185C37;
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 0.3em;
    }
    .green-subheader {
        color: #185C37;
        font-size: 1.5em !important;
        font-weight: bold !important;
        margin-bottom: 0.2em !important;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="green-title">Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı</div>', unsafe_allow_html=True)
st.markdown('<div class="green-subheader">Endüstriyel Simbiyoz Nedir?</div>', unsafe_allow_html=True)
st.write("""
Endüstriyel simbiyoz, bir üretim sürecinde açığa çıkan atık veya yan ürünlerin başka bir üretim sürecinde girdi olarak kullanılmasıdır. 
Bu yaklaşım, kaynakların daha verimli kullanılmasını sağlayarak çevresel faydalar sunar ve ekonomik tasarruflar yaratır. 
Arayüzümüz firmaların atık ürünlerini en uygun maliyetle paylaşabileceği bir platform sunar. 
Bu araç Karadeniz Teknik Üniversitesi Endüstri Mühendisliği Öğrencileri Aylin Özmen, Halime Genç,Sema Nur Yılmaz ve Zeynep Kiki tarafından 2024/2025 Bahar dönemi lisans bitirme projesi kapsamında hazırlanmıştır. 
""")

# -------------------- OPTİMİZASYON FONKSİYONU ----------------------
def optimize_waste_allocation(firma_bilgileri, atik_turu, talep_miktari):
    atik_turu_norm = atik_turu.strip().lower()
    tedarikciler = [
        f for f, v in firma_bilgileri.items()
        if str(v["atik"]).strip().lower() == atik_turu_norm and v["miktar"] > 0
    ]
    if not tedarikciler:
        return None, 0, 0

    problem = pulp.LpProblem("AtikOptimizasyon", pulp.LpMinimize)
    karar_degiskenleri = {
        f: pulp.LpVariable(f"alis_{f}", lowBound=0, upBound=firma_bilgileri[f]["miktar"], cat="Continuous")
        for f in tedarikciler
    }

    problem += pulp.lpSum([karar_degiskenleri[f] * firma_bilgileri[f]["fiyat"] for f in tedarikciler])
    problem += pulp.lpSum([karar_degiskenleri[f] for f in tedarikciler]) <= talep_miktari
    problem.solve()

    sonuc = []
    toplam_maliyet = 0
    toplam_alinan = 0
    for f in tedarikciler:
        miktar = karar_degiskenleri[f].varValue if karar_degiskenleri[f].varValue else 0
        if miktar > 0:
            sonuc.append({
                "Gonderen": f,
                "Alici": "Siz",
                "Miktar": miktar,
                "Fiyat (TL/kg)": firma_bilgileri[f]["fiyat"],
                "Tutar": miktar * firma_bilgileri[f]["fiyat"]
            })
            toplam_maliyet += miktar * firma_bilgileri[f]["fiyat"]
            toplam_alinan += miktar

    return sonuc, toplam_maliyet, toplam_alinan

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

# -------------------- SABİT VERİLER ----------------------
varsayilan_firmalar = {
    "Firma 1": {"sektor": "Demir-Çelik", "atik": "Metal Talaşı", "fiyat": 5, "miktar": 100},
    "Firma 2": {"sektor": "Demir-Çelik", "atik": "Çelik Parçaları", "fiyat": 4, "miktar": 200},
    "Firma 3": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 15, "miktar": 150},
    "Firma 4": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 10, "miktar": 300},
    "Firma 5": {"sektor": "Plastik Enjeksiyon", "atik": "HDPE", "fiyat": 12, "miktar": 250},
    "Firma 6": {"sektor": "Makine İmalat", "atik": "Elektronik Atıklar", "fiyat": 20, "miktar": 100},
    "Firma 7": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 18, "miktar": 200},
    "Firma 8": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 8, "miktar": 400},
}
varsayilan_firma_isimleri = list(varsayilan_firmalar.keys())

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

# -------------------- STATE YÖNETİMİ ----------------------
if "firma_bilgileri" not in st.session_state:
    st.session_state["firma_bilgileri"] = varsayilan_firmalar.copy()
if "firma_koordinatlari" not in st.session_state:
    st.session_state["firma_koordinatlari"] = firma_koordinatlari.copy()

firma_bilgileri = st.session_state["firma_bilgileri"]
firma_koordinatlari = st.session_state["firma_koordinatlari"]

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
        miktar = st.number_input("Alınacak Miktar (kg)", min_value=1, max_value=10000, value=100)
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
        if kaydet_buton and firma_adi:
            yeni_id = firma_adi.strip()
            if yeni_id not in firma_bilgileri and yeni_id != "":
                gps = (41.01 + 0.001 * (len(firma_bilgileri)-len(varsayilan_firma_isimleri)), 39.72 + 0.001 * (len(firma_bilgileri)-len(varsayilan_firma_isimleri)))
                firma_koordinatlari[yeni_id] = gps
                firma_bilgileri[yeni_id] = {
                    "sektor": sektor_sec,
                    "atik": atik_turu,
                    "fiyat": fiyat,
                    "miktar": miktar
                }
                st.success(f"{yeni_id} başarıyla eklendi!")

    # Firma silme bölümü (sadece yeni eklenenler)
    st.subheader("Firma Silme")
    yeni_firmalar = [f for f in firma_bilgileri if f not in varsayilan_firma_isimleri]
    if yeni_firmalar:
        silinecek_firma = st.selectbox("Silinecek Firma", yeni_firmalar)
        if st.button("Firmayı Sil"):
            firma_bilgileri.pop(silinecek_firma, None)
            firma_koordinatlari.pop(silinecek_firma, None)
            st.success(f"{silinecek_firma} başarıyla silindi!")
    else:
        st.info("Silinebilecek ek firma yok.")

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

# -------------------- MODEL & ŞEBEKE ----------------------
try:
    alici_koordinati = tuple(map(float, koordinatlar.split(",")))
except:
    alici_koordinati = (0.0, 0.0)

if secim == "Ürün almak istiyorum" and uygulama_butonu:
    sonuc, toplam_maliyet, toplam_alinan = optimize_waste_allocation(firma_bilgileri, atik_turu, miktar)
    if sonuc is None or toplam_alinan == 0:
        st.error("Talebiniz karşılanamadı, uygun ürün bulunamadı!")
    else:
        eksik = miktar - toplam_alinan
        if eksik > 0:
            st.warning(f"Talebinizin {eksik} kg'lık kısmı karşılanamadı! Sadece {toplam_alinan} kg karşılandı.")
        else:
            st.success(f"Tüm talebiniz karşılandı! {toplam_alinan} kg ürün teslim edilecek.")

        st.success(f"Toplam Taşıma Maliyeti: {toplam_maliyet:.2f} TL")

        # Sonuç Tablosu
        if sonuc:
            st.write("**Satın Alım Dağılımı:**")
            st.dataframe(pd.DataFrame(sonuc))

        # Şebeke Grafiği
        st.header("Şebeke Grafiği")
        grafik = nx.DiGraph()
        grafik.add_node("Siz", pos=(alici_koordinati[1], alici_koordinati[0]))
        for row in sonuc:
            src = row["Gonderen"]
            dst = row["Alici"]
            miktar_flow = row["Miktar"]
            if src in firma_koordinatlari:
                grafik.add_node(src, pos=(firma_koordinatlari[src][1], firma_koordinatlari[src][0]))
                grafik.add_edge(src, "Siz", weight=miktar_flow, label=f"{miktar_flow:.0f} kg")
        pos = nx.get_node_attributes(grafik, 'pos')
        edge_labels = nx.get_edge_attributes(grafik, 'label')
        nx.draw(grafik, pos, with_labels=True, node_color="lightblue", node_size=2500, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(grafik, pos, edge_labels=edge_labels, font_size=10)
        plt.title("Optimal Taşıma Şebekesi")
        plt.axis('off')
        st.pyplot(plt)
        plt.clf()

# -------------------- QR KODU HER ZAMAN GÖSTER ----------------------
qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
qr = qrcode.make(qr_link)
qr_buffer = io.BytesIO()
qr.save(qr_buffer)
st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_container_width=True)
