import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import qrcode
import io
import math
import os  # <-- BU ÖNEMLİ EXCEL İÇİN!!!
import random
from datetime import date, timedelta

# Excel dosyasını başta bir kere kontrol et ve oluştur
excel_path = "kayitlar.xlsx"
if "excel_data" not in st.session_state:
    if os.path.exists(excel_path):
        st.session_state["excel_data"] = pd.read_excel(excel_path)
    else:
        st.session_state["excel_data"] = pd.DataFrame(
            columns=["Islem Tipi", "Firma Adı", "Sektör", "Atık Türü", "Miktar", "Fiyat", "Kullanıcı Adı"]
        )

# Türkçe ay isimleri (tarih formatlamak için)
TURKISH_MONTHS = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"
]

def format_tarih(d: date):
    ay_adi = TURKISH_MONTHS[d.month - 1]
    return f"{d.day} {ay_adi} {d.year}"

# -------------------------------------------------------------------------
def get_new_coordinates(existing_coords, num_new_firms):
    center_lat = sum([coord[0] for coord in existing_coords]) / len(existing_coords)
    center_lon = sum([coord[1] for coord in existing_coords]) / len(existing_coords)
    radius = 0.03
    angle_step = 2 * math.pi / num_new_firms
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
        if f_bilgi.get("atik") == atik_turu and f_bilgi.get("miktar", 0) > 0:
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
    /* Soft krem arka plan ve hafif opak uygulama kartı */
    body {
        background-color: #faf7f0;
        background-attachment: fixed;
    }
    .stApp {
        background-color: rgba(255,255,255,0.92);
        padding-top: 40px;
    }
    .logo-container {
        position: fixed;
        top: 30px;
        right: 24px;
        z-index: 9999;
        background-color: white;
        padding: 8px;
        border-radius: 16px;
        box-shadow: 0 0 10px rgba(0,0,0,0.12);
    }
    .logo-container img { height: 90px; }
    h1,h2,h3,h4,h5,h6 { color: #1f5a3b !important; }

    /* SIDEBAR STYLING */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #eef8f1 0%, #e6f3ea 100%);
        border-right: 1px solid rgba(31,90,59,0.06);
        padding: 18px 16px;
    }
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .css-1aumxhk {
        color: #0f4b3f !important;
    }

    /* ALTERNATIF B: Outline / ters buton (hafif) */
    [data-testid="stSidebar"] .stButton>button,
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        color: #1f5a3b !important;
        border: 1.6px solid #1f8f5a !important;
        padding: 6px 10px !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stButton>button:hover,
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(31,143,90,0.08) !important;
    }

    /* Input alanları daha okunaklı */
    [data-testid="stSidebar"] .stTextInput>div>div>input,
    [data-testid="stSidebar"] .stNumberInput>div>div>input,
    [data-testid="stSidebar"] .stSelectbox>div>div>div {
        background-color: rgba(255,255,255,0.95) !important;
        border-radius: 6px;
        color: #0f3b2d;
        padding: 6px 8px;
    }

    /* Daha ince increment/dectement butonları görünümü (genel) */
    [data-testid="stSidebar"] .stNumberInput button {
        width: 28px !important;
        height: 28px !important;
        line-height: 28px !important;
    }

    /* Küçük responsive düzeltmeler */
    @media (max-width: 640px) {
        [data-testid="stSidebar"] {
            padding: 12px 10px;
        }
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

# -------------------- SABİDE + FORMLAR ----------------------
# Sabit veriler (aynı zamanda state yönetimi)
varsayilan_firmalar = {
    "Firma 1": {"sektor": "Demir-Çelik", "atik": "Metal Talaşı", "fiyat": 5, "miktar": 100, "lead_time_days": random.randint(0, 15)},
    "Firma 2": {"sektor": "Demir-Çelik", "atik": "Çelik Parçaları", "fiyat": 4, "miktar": 200, "lead_time_days": random.randint(0, 15)},
    "Firma 3": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 15, "miktar": 150, "lead_time_days": random.randint(0, 15)},
    "Firma 4": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 10, "miktar": 300, "lead_time_days": random.randint(0, 15)},
    "Firma 5": {"sektor": "Plastik Enjeksiyon", "atik": "HDPE", "fiyat": 12, "miktar": 250, "lead_time_days": random.randint(0, 15)},
    "Firma 6": {"sektor": "Makine İmalat", "atik": "Elektronik Atıklar", "fiyat": 20, "miktar": 100, "lead_time_days": random.randint(0, 15)},
    "Firma 7": {"sektor": "Makine İmalat", "atik": "Makine Parçaları", "fiyat": 18, "miktar": 200, "lead_time_days": random.randint(0, 15)},
    "Firma 8": {"sektor": "Plastik Enjeksiyon", "atik": "PT", "fiyat": 8, "miktar": 400, "lead_time_days": random.randint(0, 15)},
    "Firma 9": {"sektor": "Gıda", "atik": "Yemek Artıkları", "fiyat": 2, "miktar": 250, "lead_time_days": random.randint(0, 15)},
    "Firma 10": {"sektor": "Kağıt & Ambalaj", "atik": "Karton", "fiyat": 1.2, "miktar": 650, "lead_time_days": random.randint(0, 15)},
}

turikler = {
    "Demir-Çelik": ["Metal Talaşı", "Çelik Parçaları"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalat": ["Makine Parçaları", "Elektronik Atıklar"],
    "Gıda": ["Meyve-Sebze Posası", "Yemek Artıkları"],
    "Yem ve Mama Üretim": [],
    "Kağıt & Ambalaj": ["Karton", "Endüstriyel Kağıt Atığı"]
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
    "Firma 9": (41.0400, 39.7500),
    "Firma 10": (41.0450, 39.7550),
}

# STATE initialization
if "firma_bilgileri" not in st.session_state:
    st.session_state["firma_bilgileri"] = {k: v.copy() for k, v in varsayilan_firmalar.items()}
if "yeni_firmalar" not in st.session_state:
    st.session_state["yeni_firmalar"] = []
if "firma_koordinatlari" not in st.session_state:
    st.session_state["firma_koordinatlari"] = firma_koordinatlari.copy()

firma_bilgileri = st.session_state["firma_bilgileri"]
firma_koordinatlari = st.session_state["firma_koordinatlari"]
varsayilan_firma_isimleri = list(varsayilan_firmalar.keys())

# SIDEBAR: seçim ve formlar
with st.sidebar:
    st.title("🌾 Kullanıcı Seçimi")
    secim = st.radio("⚙️ Ne yapmak istiyorsunuz?", ["Ürün almak istiyorum", "Satıcı kaydı yapmak istiyorum"], index=0)

    if secim == "Ürün almak istiyorum":
        # Alıcı formu - tek submit (daha iyi UX)
        with st.form("alici_form"):
            ad_soyad = st.text_input("Ad Soyad", placeholder="Adınızı ve soyadınızı girin", help="İsim soyisim görünecektir.")
            sirket_adi = st.text_input("Şirket Adı", placeholder="Şirketinizi girin (opsiyonel)")
            sektor = st.selectbox("Şirketin Sektörü", list(turikler.keys()))
            atik_options = turikler.get(sektor, [])
            if atik_options:
                atik_turu = st.selectbox("Atık Türü", atik_options, help="İhtiyacınız olan atık türünü seçin.")
            else:
                st.info("Seçtiğiniz sektör atık üretmiyor veya alım için uygun atık türü yok.")
                atik_turu = None

            miktar = st.number_input("Alınacak Miktar (kg)", min_value=1, max_value=100000, value=100, step=1, help="Talep edilen miktarı kg cinsinden girin.")
            # Dinamik alıcı koordinatı (bilgi amaçlı)
            max_lon = max([koor[1] for koor in firma_koordinatlari.values()])
            min_lon = min([koor[1] for koor in firma_koordinatlari.values()])
            mean_lat = sum([koor[0] for koor in firma_koordinatlari.values()]) / len(firma_koordinatlari)
            alici_koordinati = (mean_lat, (max_lon + min_lon) / 2)

            uygulama_butonu = st.form_submit_button("Uygulamayı Çalıştır")

    else:
        # Satıcı kayıt formu
        with st.form("satici_form"):
            firma_adi = st.text_input("Firma Adı", placeholder="Örn. ABC San. A.Ş.", help="Kayıtlı firma adı benzersiz olmalıdır.")
            sektor_sec = st.selectbox("Sektör", list(turikler.keys()))
            atik_secenekleri = turikler.get(sektor_sec, [])
            if atik_secenekleri:
                atik_turu = st.selectbox("Satmak istediğiniz Atık Ürün", atik_secenekleri, help="Satmak istediğiniz atık türünü seçin.")
            else:
                st.info("Bu sektör atık üretmiyor. Satıcı kaydı atık bildirimi gerektirmez.")
                atik_turu = None

            miktar = st.number_input("Satmak istediğiniz ürün miktarı (kg)", min_value=1, value=100, step=1)
            fiyat = st.number_input("Ürünü ne kadara satmak istiyorsunuz? (TL/kg)", min_value=0.0, value=1.0, step=0.1, format="%.2f", help="TL/kg cinsinden fiyat girin.")
            with st.expander("Gelişmiş: Temin süresi (varsayılan 15 gün)"):
                temin_suresi = st.number_input("Bu ürünü kaç günde temin edebilirsiniz? (gün)", min_value=0, value=15, step=1)
                st.write("Bu bilgi alıcılar için tahmini teslim süresi sağlar.")
            kaydet_buton = st.form_submit_button("KAYDIMI TAMAMLA")

# -------------------- BAŞLIK ve İÇERİK ----------------------
st.title("Kaizen Connect: Sanayide Atığı Değere Dönüştüren Dijital Platform")
st.subheader("🏭 Endüstriyel Simbiyoz Nedir?")
st.write("""
🍃 Endüstriyel simbiyoz, bir üretim sürecinde açığa çıkan atık veya yan ürünlerin başka bir üretim sürecinde girdi olarak kullanılmasıdır.
Bu yaklaşım, kaynakların daha verimli kullanılmasını sağlayarak çevresel faydalar sunar ve ekonomik tasarruflar yaratır.✨
""")

st.markdown("""
### Vizyonumuz

Sanayide atığın değer kazandığı, işletmelerin birlikte büyüdüğü bir gelecek kurmak istiyoruz.  
Bizim için sürdürülebilirlik sadece bir hedef değil — yeni bir iş yapma biçimi.  
Kaynakların paylaşıldığı, çevrenin korunduğu ve herkesin kazandığı bir endüstriyel simbiyoz ağı oluşturmayı hayal ediyoruz.

🌱 **Misyonumuz**

Farklı sektörlerdeki firmaları bir araya getirip, birinin atığını diğerinin hammaddesine dönüştürüyoruz.  
Veri odaklı analizlerle doğru eşleşmeleri yapıyor, israfı azaltırken verimliliği artırıyoruz.  
Kısacası, biz endüstriyel simbiyozu sadece anlatmıyoruz; gerçeğe dönüştürüyoruz. 🌍🔄
""")

# Görsel - çerçeveli veya basit
st.markdown(
    """
    <div style="display:flex;justify-content:center;margin:18px auto;">
        <img src="https://raw.githubusercontent.com/snuryilmaz/endustrialsimbiyozis/main/endustrialsymbiozis.png" 
             alt="Örnek Endüstriyel Simbiyoz Ağı" style="border:6px solid #1f5a3b;border-radius:8px;max-width:100%;height:auto;">
    </div>
    """,
    unsafe_allow_html=True
)

# -------------------- FORM SONUÇ İŞLEMLERİ ----------------------
# Satıcı kayıt submit işlemi
if 'kaydet_buton' in locals() and kaydet_buton:
    if firma_adi:
        yeni_id = firma_adi.strip()
        if yeni_id not in firma_bilgileri:
            mevcut_koordinatlar = list(firma_koordinatlari.values())
            yeni_koordinatlar = get_new_coordinates(mevcut_koordinatlar, num_new_firms=1)
            gps = yeni_koordinatlar[0]
            firma_koordinatlari[yeni_id] = gps
            firma_bilgileri[yeni_id] = {
                "sektor": sektor_sec,
                "atik": atik_turu,
                "fiyat": fiyat,
                "miktar": miktar,
                "lead_time_days": int(temin_suresi) if 'temin_suresi' in locals() else 15
            }
            st.session_state["yeni_firmalar"].append(yeni_id)
            # EXCEL KAYDI
            st.session_state["excel_data"] = pd.concat(
                [st.session_state["excel_data"], pd.DataFrame([{
                    "Islem Tipi": "Satıcı Kaydı",
                    "Firma Adı": firma_adi,
                    "Sektör": sektor_sec,
                    "Atık Türü": atik_turu if atik_turu is not None else "-",
                    "Miktar": miktar,
                    "Fiyat": fiyat,
                    "Kullanıcı Adı": "-"
                }])],
                ignore_index=True)
            st.session_state["excel_data"].to_excel(excel_path, index=False)
            st.success(f"{yeni_id} başarıyla eklendi!")
            teslim_tarihi = date.today() + timedelta(days=int(firma_bilgileri[yeni_id].get("lead_time_days", 15)))
            st.info(f"Kaydınız alındı. Tahmini temin: {format_tarih(teslim_tarihi)}.")
        else:
            st.warning(f"{yeni_id} zaten sistemde mevcut.")
    else:
        st.error("Firma adı boş bırakılamaz.")

# Alıcı uygulaması submit işlemi
sonuc, toplam_maliyet, toplam_alinan = None, 0, 0
if 'uygulama_butonu' in locals() and uygulama_butonu:
    if atik_turu is None:
        st.error("Seçtiğiniz sektör için geçerli atık türü yok; işlem yapılamıyor.")
    else:
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
                    "Kullanıcı Adı": ad_soyad if ad_soyad else "-"
                }
                df_excel = pd.concat([df_excel, pd.DataFrame([yeni_satir])], ignore_index=True)
            df_excel.to_excel(excel_path, index=False)
            st.success(f"Toplam Taşıma Maliyeti: {toplam_maliyet:.2f} TL")
            st.write("**Satın Alım Dağılımı:**")
            st.dataframe(pd.DataFrame(sonuc))

# -------------------- FİRMA TABLOSU ----------------------
firma_bilgileri_tablo = {
    "Firma Adı": list(firma_bilgileri.keys()),
    "Sektör": [v["sektor"] for v in firma_bilgileri.values()],
    "Ürün": [v.get("atik", "") for v in firma_bilgileri.values()],
    "Miktar (kg)": [v["miktar"] for v in firma_bilgileri.values()],
    "Fiyat (TL/kg)": [v["fiyat"] for v in firma_bilgileri.values()],
    "Temin Süresi (gün)": [v.get("lead_time_days", "") for v in firma_bilgileri.values()]
}
df = pd.DataFrame(firma_bilgileri_tablo)
st.subheader("Firma Bilgileri")
st.write("Aşağıdaki tablo, sistemde kayıtlı firmaların sektör, ürün, miktar, fiyat ve temin süresi bilgilerini göstermektedir.")
st.dataframe(df)

# -------------------- ŞEBEKE GRAFİĞİ ----------------------
if secim == "Ürün almak istiyorum" and 'uygulama_butonu' in locals() and uygulama_butonu and sonuc and toplam_alinan > 0:
    st.subheader("Satıcı Bilgilendirmeleri")
    remaining = miktar
    for row in sonuc:
        src = row["Gonderen"]
        allocated = row["Miktar"]
        if allocated <= 0:
            continue
        firma = firma_bilgileri.get(src, {})
        firma_stok = firma.get("miktar", 0)
        lead = firma.get("lead_time_days", None)
        remaining_after = max(0, remaining - allocated)
        temel = f"{src} — Elimizde {firma_stok} kg hazır; bu sipariş için {allocated} kg göndereceğiz."
        if remaining_after == 0:
            st.success(temel + " En kısa zamanda teslimat gerçekleşecektir.")
        else:
            if allocated == firma_stok:
                st.warning(temel + f" Kalan talep: {remaining_after} kg diğer firmalardan temin edilecek.")
            else:
                if lead is not None:
                    tahmini = date.today() + timedelta(days=lead)
                    st.info(temel + f" Kalan {remaining_after} kg için temin süresi: {lead} gün (tahmini: {format_tarih(tahmini)}).")
                else:
                    st.info(temel + f" Kalan {remaining_after} kg için temin süresi bildirilmemiş.")
        remaining = remaining_after

    st.header("Şebeke Grafiği")
    grafik = nx.DiGraph()
    grafik.add_node("Siz", pos=(39.72, 41.01))
    node_colors = []
    node_sizes = []
    edge_widths = []
    for row in sonuc:
        src = row["Gonderen"]
        miktar_flow = row["Miktar"]
        if src in firma_koordinatlari:
            grafik.add_node(src, pos=(firma_koordinatlari[src][1], firma_koordinatlari[src][0]))
            grafik.add_edge(src, "Siz", weight=miktar_flow, label=f"{miktar_flow:.0f} kg")
            edge_widths.append(0.5)
    sector_colors = {
        "Demir-Çelik": "#7EC8E3",
        "Makine İmalat": "#FFD580",
        "Plastik Enjeksiyon": "#D3D3D3",
        "Gıda": "#C8E6C9",
        "Yem ve Mama Üretim": "#FFE0B2",
        "Kağıt & Ambalaj": "#FFF9C4"
    }
    for node in grafik.nodes:
        if node == "Siz":
            node_colors.append("red")
            node_sizes.append(3000)
        else:
            sektor = firma_bilgileri[node]["sektor"] if node in firma_bilgileri else "Bilinmiyor"
            node_colors.append(sector_colors.get(sektor, "blue"))
            node_sizes.append(2000)
    pos = nx.get_node_attributes(grafik, 'pos')
    missing_nodes = [node for node in grafik.nodes if node not in pos]
    for node in missing_nodes:
        st.warning(f"{node} düğümü için koordinat bulunamadı. Varsayılan (0, 0) atanıyor.")
        pos[node] = (0, 0)
    edge_labels = nx.get_edge_attributes(grafik, 'label')
    nx.draw(grafik, pos, with_labels=True, node_color=node_colors, node_size=node_sizes, font_size=10, font_weight="bold", edge_color="gray", width=edge_widths)
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
# Not: "Çalışılan 8 OSB firmasının konumları" görseli kaldırıldı.
# QR kodu bölümü yorum satırı halinde duruyor (isteğe bağlı ekleyebilirsiniz).
