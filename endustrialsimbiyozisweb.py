import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
import math
import os  # <-- BU ÖNEMLİ EXCEL İÇİN!!!

# Excel dosyasını başta bir kere kontrol et ve oluştur
excel_path = "kayitlar.xlsx"
if "excel_data" not in st.session_state:
    if os.path.exists(excel_path):
        # Eğer dosya varsa, oku ve belleğe al
        st.session_state["excel_data"] = pd.read_excel(excel_path)
    else:
        # Eğer dosya yoksa, boş bir DataFrame oluştur ve belleğe al
        st.session_state["excel_data"] = pd.DataFrame(
            columns=["Islem Tipi", "Firma Adı", "Sektör", "Atık Türü", "Miktar", "Fiyat", "Kullanıcı Adı"]
        )

# -------------------------------------------------------------------------
def get_new_coordinates(existing_coords, num_new_firms):
    """
    Yeni firmalar için çember düzeninde koordinatlar oluşturur.
    existing_coords: Mevcut firma koordinatlarının listesi [(lat, lon), ...]
    num_new_firms: Eklenmesi gereken yeni firma sayısı
    """
    # Çemberin merkezini ve yarıçapını belirle
    center_lat = sum([coord[0] for coord in existing_coords]) / len(existing_coords)
    center_lon = sum([coord[1] for coord in existing_coords]) / len(existing_coords)
    radius = 0.03  # Çemberin yarıçapı (isteğe göre büyütülebilir)

    # Yeni firmaları çember boyunca eşit aralıklarla yerleştir
    angle_step = 2 * math.pi / num_new_firms  # Her yeni firma için açı aralığı
    new_coords = []
    for i in range(num_new_firms):
        angle = i * angle_step
        new_lat = center_lat + radius * math.sin(angle)
        new_lon = center_lon + radius * math.cos(angle)
        new_coords.append((new_lat, new_lon))
    return new_coords

# ------------------ OPTİMİZASYON FONKSİYONU ------------------
def optimize_waste_allocation(firmalar, atik_turu, talep_miktari):
    uygunlar = []
    for f_adi, f_bilgi in firmalar.items():
        if f_bilgi["atik"] == atik_turu and f_bilgi["miktar"] > 0:
            uygunlar.append({
                "Firma": f_adi,
                "Fiyat": f_bilgi["fiyat"],
                "Miktar": f_bilgi["miktar"]
            })
    uygunlar.sort(key=lambda x: x["Fiyat"])

    kalan = talep_miktari
    toplam_maliyet = 0
    toplam_alinan = 0
    eslesmeler = []
    for u in uygunlar:
        alinacak = min(u["Miktar"], kalan)
        if alinacak <= 0:
            continue
        toplam_maliyet += alinacak * u["Fiyat"]
        toplam_alinan += alinacak
        eslesmeler.append({
            "Gonderen": u["Firma"],
            "Alici": "Siz",
            "Miktar": alinacak,
            "Fiyat (TL/kg)": u["Fiyat"],
            "Tutar": alinacak * u["Fiyat"]
        })
        kalan -= alinacak
        if kalan <= 0:
            break

    if toplam_alinan == 0:
        return None, 0, 0

    return eslesmeler, toplam_maliyet, toplam_alinan

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
# Başlık
st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")

# Tanıtım Yazısı
st.subheader("Endüstriyel Simbiyoz Nedir?")
st.write("""
Endüstriyel simbiyoz, bir üretim sürecinde açığa çıkan atık veya yan ürünlerin başka bir üretim sürecinde girdi olarak kullanılmasıdır.
Bu yaklaşım, kaynakların daha verimli kullanılmasını sağlayarak çevresel faydalar sunar ve ekonomik tasarruflar yaratır.
Arayüzümüz firmaların atık ürünlerini en uygun maliyetle paylaşabileceği bir platform sunar.
Bu araç Karadeniz Teknik Üniversitesi Endüstri Mühendisliği Öğrencileri 
Aylin Özmen, Halime Genç,Sema Nur Yılmaz ve Zeynep Kiki tarafından 2024/2025 Bahar dönemi lisans bitirme projesi kapsamında hazırlanmıştır.
""")

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
if "yeni_firmalar" not in st.session_state:
    st.session_state["yeni_firmalar"] = []
if "firma_koordinatlari" not in st.session_state:
    st.session_state["firma_koordinatlari"] = firma_koordinatlari.copy()

firma_bilgileri = st.session_state["firma_bilgileri"]
firma_koordinatlari = st.session_state["firma_koordinatlari"]
varsayilan_firma_isimleri = list(varsayilan_firmalar.keys())

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
        
        # Dinamik olarak alıcı koordinatını hesapla
        max_lon = max([koor[1] for koor in firma_koordinatlari.values()])
        min_lon = min([koor[1] for koor in firma_koordinatlari.values()])
        mean_lat = sum([koor[0] for koor in firma_koordinatlari.values()]) / len(firma_koordinatlari)
        alici_koordinati = (mean_lat, (max_lon + min_lon) / 2)  # Yeni dinamik hesaplama
        
        # Koordinatı kullanıcıya sadece bilgi olarak göster
        st.info(f"Alıcı noktası otomatik olarak {alici_koordinati[0]:.5f}, {alici_koordinati[1]:.5f} koordinatında bulundu.")
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
            if yeni_id not in firma_bilgileri:
                # Mevcut koordinatları listele
                mevcut_koordinatlar = list(firma_koordinatlari.values())
                
                # Yeni firma için benzersiz koordinat al
                yeni_koordinatlar = get_new_coordinates(mevcut_koordinatlar, num_new_firms=1)
                gps = yeni_koordinatlar[0]  # İlk yeni koordinatı al
                firma_koordinatlari[yeni_id] = gps

                #Firma bilgi güncellemesi
                firma_bilgileri[yeni_id] = {
                    "sektor": sektor_sec,
                    "atik": atik_turu,
                    "fiyat": fiyat,
                    "miktar": miktar
                }
                st.session_state["yeni_firmalar"].append(yeni_id)
                # EXCEL KAYDI:
                st.session_state["excel_data"] = pd.concat(
                    [st.session_state["excel_data"], pd.DataFrame([{
                        "Islem Tipi": "Satıcı Kaydı",
                        "Firma Adı": firma_adi,
                        "Sektör": sektor_sec,
                        "Atık Türü": atik_turu,
                        "Miktar": miktar,
                        "Fiyat": fiyat,
                        "Kullanıcı Adı": "-"
                    }])],
                    ignore_index=True)
                st.session_state["excel_data"].to_excel(excel_path, index=False)
                st.success(f"{yeni_id} başarıyla eklendi!")
            else:
                st.warning(f"{yeni_id} zaten sistemde mevcut.")

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
sonuc, toplam_maliyet, toplam_alinan = None, 0, 0
alici_koordinati = None

if secim == "Ürün almak istiyorum":
    # Alıcı koordinatı ve uygulama butonu yukarıda tanımlı
    if 'uygulama_butonu' in locals() and uygulama_butonu:
        sonuc, toplam_maliyet, toplam_alinan = optimize_waste_allocation(firma_bilgileri, atik_turu, miktar)
        if sonuc is None or toplam_alinan == 0:
            st.error("Talebiniz karşılanamadı, uygun ürün bulunamadı!")
        else:
            eksik = miktar - toplam_alinan
            if eksik > 0:
                st.warning(f"Talebinizin {eksik} kg'lık kısmı karşılanamadı! Sadece {toplam_alinan} kg karşılandı.")
            else:
                st.success(f"Tüm talebiniz karşılandı! {toplam_alinan} kg ürün teslim edilecek.")
            # EXCEL'E KAYIT EKLE
            excel_path = "kayitlar.xlsx"
            if not os.path.exists(excel_path):
                df_init = pd.DataFrame(columns=["Islem Tipi", "Firma Adı", "Sektör", "Atık Türü", "Miktar", "Fiyat", "Kullanıcı Adı"])
                df_init.to_excel(excel_path, index=False)
            df_excel = pd.read_excel(excel_path)
            for row in sonuc:
                yeni_satir = {
                    "Islem Tipi": "Satın Alma",
                    "Firma Adı": row["Gonderen"],
                    "Sektör": firma_bilgileri[row["Gonderen"]]["sektor"],
                    "Atık Türü": firma_bilgileri[row["Gonderen"]]["atik"],
                    "Miktar": row["Miktar"],
                    "Fiyat": row["Fiyat (TL/kg)"],
                    "Kullanıcı Adı": ad_soyad
                }
                df_excel = pd.concat([df_excel, pd.DataFrame([yeni_satir])], ignore_index=True)
            df_excel.to_excel(excel_path, index=False)

            st.success(f"Toplam Taşıma Maliyeti: {toplam_maliyet:.2f} TL")

            # Sonuç Tablosu
            st.write("**Satın Alım Dağılımı:**")
            st.dataframe(pd.DataFrame(sonuc))

# -------------------- ŞEBEKE GRAFİĞİ ----------------------

# Şebeke grafiği yalnızca alım işlemi tamamlandıysa gösterilecek
if secim == "Ürün almak istiyorum" and uygulama_butonu and sonuc and toplam_alinan > 0:
    st.header("Şebeke Grafiği")

    # Şebeke grafiği için yönlü bir grafik oluştur
    grafik = nx.DiGraph()

    # Alıcı koordinatını belirle
    if alici_koordinati is not None:
        grafik.add_node("Siz", pos=(alici_koordinati[1], alici_koordinati[0]))
    else:
        # Varsayılan konum
        grafik.add_node("Siz", pos=(39.72, 41.01))

    # Düğüm renklerini, boyutlarını ve kenar kalınlıklarını tutacak listeler
    node_colors = []
    node_sizes = []
    edge_widths = []

    # Gönderici düğümleri ve kenarları ekle
    for row in sonuc:
        src = row["Gonderen"]
        dst = row["Alici"]
        miktar_flow = row["Miktar"]

        if src in firma_koordinatlari:
            # Gönderici düğümünü ekle
            grafik.add_node(src, pos=(firma_koordinatlari[src][1], firma_koordinatlari[src][0]))
            # Gönderici ile alıcı arasına kenar ekle
            grafik.add_edge(src, "Siz", weight=miktar_flow, label=f"{miktar_flow:.0f} kg")

            # Kenar kalınlığını miktara göre ayarla
            edge_widths.append(1 + miktar_flow / 50)

    # Sektöre göre renk haritası
    sector_colors = {
        "Demir-Çelik": "red",
        "Makine İmalat": "orange",
        "Plastik Enjeksiyon": "purple"
    }

    # Düğüm renklerini ve boyutlarını ayarla
    for node in grafik.nodes:
        if node == "Siz":
            node_colors.append("green")  # Alıcı düğümü yeşil
            node_sizes.append(3000)      # Alıcı düğümü daha büyük
        else:
            sektor = firma_bilgileri[node]["sektor"] if node in firma_bilgileri else "Bilinmiyor"
            node_colors.append(sector_colors.get(sektor, "blue"))  # Sektöre göre renk
            node_sizes.append(2000)  # Gönderici düğümleri daha küçük

    # Düğüm ve kenarları çiz
    pos = nx.get_node_attributes(grafik, 'pos')
    # Eksik pozisyonlar için varsayılan koordinat atanması
    missing_nodes = [node for node in grafik.nodes if node not in pos]
    for node in missing_nodes:
        st.warning(f"{node} düğümü için koordinat bulunamadı. Varsayılan (0, 0) koordinatı atanıyor.")
        pos[node] = (0, 0)  # Varsayılan koordinat (0, 0)
    edge_labels = nx.get_edge_attributes(grafik, 'label')

    nx.draw(
        grafik,
        pos,
        with_labels=True,
        node_color=node_colors,
        node_size=node_sizes,
        font_size=10,
        font_weight="bold",
        edge_color="gray",
        width=edge_widths
    )
    nx.draw_networkx_edge_labels(grafik, pos, edge_labels=edge_labels, font_size=10)
    plt.title("Optimal Taşıma Şebekesi")
    plt.axis('off')
    st.pyplot(plt)
    plt.clf()

# GRAFİK SONRASI EXCEL İNDİRME BUTONU
st.info("Aşağıdaki butona tıklayarak tüm işlem geçmişinizi Excel dosyası olarak indirebilirsiniz.")
if os.path.exists(excel_path):
    with open(excel_path, "rb") as file:
        st.download_button(
            label="🗂️ İşlem Kayıtlarını Excel Olarak İndir",
            data=file,
            file_name="kayitlar.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="download-excel"
        )

st.image(
    "https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/osbkonumlandirma.png",
    caption="Çalışılan 8 OSB firmasının konumları",
    use_container_width=True
)
st.image(
    "https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/endustrialsymbiozis.jpg",
    caption="Örnek Endüstriyel Simbiyoz Ağı",
    use_container_width=True
)

# -------------------- QR KODU HER ZAMAN GÖSTER ----------------------
qr_link = "https://endustrialsimbiyozis-snuryilmazktu.streamlit.app/"
qr = qrcode.make(qr_link)
qr_buffer = io.BytesIO()
qr.save(qr_buffer)
st.image(qr_buffer, caption=f"Platforma Hızlı Erişim için QR Kod ({qr_link})", use_container_width=True)
