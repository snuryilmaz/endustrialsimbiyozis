import streamlit as st
import pandas as pd
import os
import datetime
import networkx as nx
import matplotlib.pyplot as plt
import qrcode
import io
import pulp

EXCEL_LOG = "firma_log.xlsx"

# --- LOG KAYIT FONKSİYONLARI ---
def loga_islem_ekle(islem, firma_dict, kullanici="Anonim"):
    # Loga yeni bir işlem satırı ekle
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    kayit = {**firma_dict}
    kayit.update({
        "Tarih": now,
        "İşlem": islem,
        "Kullanıcı": kullanici
    })
    if os.path.exists(EXCEL_LOG):
        df = pd.read_excel(EXCEL_LOG)
        df = pd.concat([df, pd.DataFrame([kayit])], ignore_index=True)
    else:
        df = pd.DataFrame([kayit])
    df.to_excel(EXCEL_LOG, index=False)

def logdan_guncel_firmalari_al():
    # Logdan güncel (eklenmiş ve silinmemiş) firmaların listesini çıkar
    if not os.path.exists(EXCEL_LOG):
        return []
    df = pd.read_excel(EXCEL_LOG)
    # Sadece en son işlemi "ekle" olan firmalar günceldir
    df = df.sort_values("Tarih")
    firmalar = {}
    for _, row in df.iterrows():
        ad = row["Firma Adı"]
        if row["İşlem"] == "ekle":
            firmalar[ad] = dict(row)
        elif row["İşlem"] == "sil":
            firmalar.pop(ad, None)
    return list(firmalar.values())

# --- OPTİMİZASYON ---
def optimize_waste_allocation(firma_listesi, atik_turu, talep_miktari):
    atik_turu_norm = atik_turu.strip().lower()
    tedarikciler = [
        f for f in firma_listesi
        if str(f["Atık Türü"]).strip().lower() == atik_turu_norm and f["Miktar"] > 0
    ]
    if not tedarikciler:
        return None, 0, 0

    problem = pulp.LpProblem("AtikOptimizasyon", pulp.LpMinimize)
    karar_degiskenleri = {
        f["Firma Adı"]: pulp.LpVariable(f"alis_{f['Firma Adı']}", lowBound=0, upBound=f["Miktar"], cat="Continuous")
        for f in tedarikciler
    }
    problem += pulp.lpSum([karar_degiskenleri[f["Firma Adı"]] * f["Fiyat"] for f in tedarikciler])
    problem += pulp.lpSum([karar_degiskenleri[f["Firma Adı"]] for f in tedarikciler]) <= talep_miktari
    problem.solve()

    sonuc = []
    toplam_maliyet = 0
    toplam_alinan = 0
    for f in tedarikciler:
        miktar = karar_degiskenleri[f["Firma Adı"]].varValue if karar_degiskenleri[f["Firma Adı"]].varValue else 0
        if miktar > 0:
            sonuc.append({
                "Gonderen": f["Firma Adı"],
                "Alici": "Siz",
                "Miktar": miktar,
                "Fiyat (TL/kg)": f["Fiyat"],
                "Tutar": miktar * f["Fiyat"]
            })
            toplam_maliyet += miktar * f["Fiyat"]
            toplam_alinan += miktar

    return sonuc, toplam_maliyet, toplam_alinan

# --- STİL VE BAŞLIK ---
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
Bu araç Karadeniz Teknik Üniversitesi Endüstri Mühendisliği Öğrencileri Aylin Özmen, Halime Genç,Sema Nur Yılmaz ve Zeynep Kiki 
tarafından 2024/2025 Bahar dönemi lisans bitirme projesi kapsamında hazırlanmıştır.
""")

# --- SABİT VERİLER (Varsayılan firmalar ilk kez eklenirse log'a yazılıyor) ---
varsayilan_firmalar = [
    {"Firma Adı": "Firma 1", "Sektör": "Demir-Çelik", "Atık Türü": "Metal Talaşı", "Miktar": 100, "Fiyat": 5, "Koordinat": "41.0105,39.7266"},
    {"Firma Adı": "Firma 2", "Sektör": "Demir-Çelik", "Atık Türü": "Çelik Parçaları", "Miktar": 200, "Fiyat": 4, "Koordinat": "40.9900,39.7200"},
    {"Firma Adı": "Firma 3", "Sektör": "Makine İmalat", "Atık Türü": "Makine Parçaları", "Miktar": 150, "Fiyat": 15, "Koordinat": "41.0200,39.7400"},
    {"Firma Adı": "Firma 4", "Sektör": "Plastik Enjeksiyon", "Atık Türü": "PT", "Miktar": 300, "Fiyat": 10, "Koordinat": "41.0005,39.7050"},
    {"Firma Adı": "Firma 5", "Sektör": "Plastik Enjeksiyon", "Atık Türü": "HDPE", "Miktar": 250, "Fiyat": 12, "Koordinat": "41.0150,39.7300"},
    {"Firma Adı": "Firma 6", "Sektör": "Makine İmalat", "Atık Türü": "Elektronik Atıklar", "Miktar": 100, "Fiyat": 20, "Koordinat": "41.0250,39.7350"},
    {"Firma Adı": "Firma 7", "Sektör": "Makine İmalat", "Atık Türü": "Makine Parçaları", "Miktar": 200, "Fiyat": 18, "Koordinat": "41.0300,39.7400"},
    {"Firma Adı": "Firma 8", "Sektör": "Plastik Enjeksiyon", "Atık Türü": "PT", "Miktar": 400, "Fiyat": 8, "Koordinat": "41.0350,39.7450"},
]
if not os.path.exists(EXCEL_LOG):
    for f in varsayilan_firmalar:
        loga_islem_ekle("ekle", f)

turikler = {
    "Demir-Çelik": ["Metal Talaşı", "Çelik Parçaları"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalat": ["Makine Parçaları", "Elektronik Atıklar"]
}

# --- ANA SAYFA KULLANICI ARAYÜZÜ ---
st.sidebar.title("Kullanıcı Seçimi")
secim = st.sidebar.radio(
    "Ne yapmak istiyorsunuz?",
    ["Ürün almak istiyorum", "Satıcı kaydı yapmak istiyorum"],
    index=0
)

firma_listesi = logdan_guncel_firmalari_al()

if secim == "Ürün almak istiyorum":
    st.sidebar.header("Alıcı Bilgileri")
    ad_soyad = st.sidebar.text_input("Ad Soyad")
    sirket_adi = st.sidebar.text_input("Şirket Adı")
    sektor = st.sidebar.selectbox("Şirketin Sektörü", list(turikler.keys()))
    atik_turu = st.sidebar.selectbox("Atık Türü", turikler[sektor])
    miktar = st.sidebar.number_input("Alınacak Miktar (kg)", min_value=1, max_value=10000, value=100)
    koordinatlar = st.sidebar.text_input("Kullanıcı GPS Koordinatları (enlem, boylam)", "41.0000,39.7000")
    uygulama_butonu = st.sidebar.button("Uygulamayı Çalıştır")

    # --- TABLO ---
    st.subheader("Firma Bilgileri")
    if firma_listesi:
        st.dataframe(pd.DataFrame(firma_listesi))
    else:
        st.warning("Kayıtlı firma yok.")

    # --- OPTİMİZASYON ---
    try:
        alici_koordinati = tuple(map(float, koordinatlar.split(",")))
    except:
        alici_koordinati = (0.0, 0.0)

    if uygulama_butonu:
        sonuc, toplam_maliyet, toplam_alinan = optimize_waste_allocation(firma_listesi, atik_turu, miktar)
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
            miktar_flow = row["Miktar"]
            firma = next((f for f in firma_listesi if f["Firma Adı"] == src), None)
            if firma and "Koordinat" in firma:
                lat, lon = map(float, str(firma["Koordinat"]).split(","))
                grafik.add_node(src, pos=(lon, lat))
                grafik.add_edge(src, "Siz", weight=miktar_flow, label=f"{miktar_flow:.0f} kg")
        pos = nx.get_node_attributes(grafik, 'pos')
        edge_labels = nx.get_edge_attributes(grafik, 'label')
        nx.draw(grafik, pos, with_labels=True, node_color="lightblue", node_size=2500, font_size=10, font_weight="bold")
        nx.draw_networkx_edge_labels(grafik, pos, edge_labels=edge_labels, font_size=10)
        plt.title("Optimal Taşıma Şebekesi")
        plt.axis('off')
        st.pyplot(plt)
        plt.clf()

elif secim == "Satıcı kaydı yapmak istiyorum":
    st.sidebar.header("Satıcı Kaydı")
    firma_adi = st.sidebar.text_input("Firma Adı")
    sektor_sec = st.sidebar.selectbox("Sektör", list(turikler.keys()))
    atik_secenekleri = turikler[sektor_sec]
    atik_turu = st.sidebar.selectbox("Satmak istediğiniz Atık Ürün", atik_secenekleri)
    miktar = st.sidebar.number_input("Satmak istediğiniz ürün miktarı (kg)", min_value=1)
    fiyat = st.sidebar.number_input("Ürünü ne kadara satmak istiyorsunuz? (TL/kg)", min_value=0.0)
    koordinat = st.sidebar.text_input("Firma GPS Koordinatları (enlem, boylam)", "41.0000,39.7000")
    kaydet_buton = st.sidebar.button("KAYDIMI TAMAMLA")
    if kaydet_buton and firma_adi:
        yeni_firma = {
            "Firma Adı": firma_adi.strip(),
            "Sektör": sektor_sec,
            "Atık Türü": atik_turu,
            "Miktar": miktar,
            "Fiyat": fiyat,
            "Koordinat": koordinat.strip()
        }
        # Aynı isimli firma zaten varsa eklenmez
        mevcut_firmalar = [f["Firma Adı"] for f in firma_listesi]
        if yeni_firma["Firma Adı"] not in mevcut_firmalar:
            loga_islem_ekle("ekle", yeni_firma)
            st.success(f"{firma_adi} başarıyla eklendi!")
        else:
            st.warning("Bu isimde bir firma zaten var!")

    # --- SİLME BÖLÜMÜ (Sadece eklenen firmalar silinebilir, varsayılanlar silinmez) ---
    varsayilan_isimler = [f["Firma Adı"] for f in varsayilan_firmalar]
    yeni_firmalar = [f for f in firma_listesi if f["Firma Adı"] not in varsayilan_isimler]
    st.sidebar.subheader("Firma Silme")
    if yeni_firmalar:
        silinecek_firma = st.sidebar.selectbox("Silinecek Firma", [f["Firma Adı"] for f in yeni_firmalar])
        if st.sidebar.button("Firmayı Sil"):
            silinen = next((f for f in yeni_firmalar if f["Firma Adı"] == silinecek_firma), None)
            if silinen:
                loga_islem_ekle("sil", silinen)
                st.success(f"{silinecek_firma} başarıyla silindi!")
    else:
        st.sidebar.info("Silinebilecek ek firma yok.")

# --- QR KODU HER ZAMAN GÖSTER ---
qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
qr = qrcode.make(qr_link)
qr_buffer = io.BytesIO()
qr.save(qr_buffer)
st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_container_width=True)
