import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import json
import pandas as pd

# Matris dosyasını yükleme
with open("matrices.json", "r") as f:
    matrices = json.load(f)

distance_matrix = pd.DataFrame(matrices["distance_matrix"])
time_matrix = pd.DataFrame(matrices["time_matrix"])
cost_matrix = pd.DataFrame(matrices["cost_matrix"])

# Firma bilgileri ve sektör eşlemesi
firm_data = {
    "Firma 1": {"sector": "Plastik Enjeksiyon", "waste": "HDPE", "amount": 100, "price": 15},
    "Firma 2": {"sector": "Demir-Çelik", "waste": "Demir Talaşı", "amount": 200, "price": 10},
    "Firma 3": {"sector": "Makine İmalatı", "waste": "Metal Talaşı", "amount": 150, "price": 20},
    "Firma 4": {"sector": "Demir-Çelik", "waste": "Çelik Artığı", "amount": 180, "price": 12},
    "Firma 5": {"sector": "Plastik Enjeksiyon", "waste": "PT", "amount": 120, "price": 18},
    "Firma 6": {"sector": "Makine İmalatı", "waste": "Yağlı Atık", "amount": 140, "price": 25},
    "Firma 7": {"sector": "Makine İmalatı", "waste": "Metal Talaşı", "amount": 130, "price": 22},
    "Firma 8": {"sector": "Plastik Enjeksiyon", "waste": "HDPE", "amount": 110, "price": 19},
}

# Sol Şeride Kullanıcı Girdileri
st.sidebar.header("Kullanıcı Bilgileri")
name = st.sidebar.text_input("Adınız Soyadınız")
company_name = st.sidebar.text_input("Şirket İsmi")
sector = st.sidebar.selectbox(
    "Şirket Sektörü",
    ["Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalatı"]
)

waste_options = {
    "Demir-Çelik": ["Demir Talaşı", "Çelik Artığı"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalatı": ["Metal Talaşı", "Yağlı Atık"]
}
waste = st.sidebar.selectbox("Almak İstediğiniz Atık", waste_options.get(sector, []))

# Atığa Göre Firma Verilerini Filtreleme
filtered_firms = {
    firm: data for firm, data in firm_data.items() if data["sector"] == sector and data["waste"] == waste
}

st.header("Satıcı Firmalar")
if filtered_firms:
    for firm, data in filtered_firms.items():
        st.subheader(f"{firm} - {data['sector']}")
        st.write(f"Atık: {data['waste']}")
        st.write(f"Miktar: {data['amount']} birim")
        st.write(f"Fiyat: {data['price']} $/birim")
        if st.button(f"{firm} Ürünü Al"):
            selected_firm = firm
else:
    st.warning("Seçtiğiniz atığı satan firma bulunamadı.")

# Şebeke Grafiği ve Optimizasyon
if "selected_firm" in locals():
    st.header("Şebeke Grafiği")
    
    # Şebeke Grafiği Çizimi
    G = nx.DiGraph()
    G.add_node("Buyer", role="buyer")
    G.add_node(selected_firm, role="supplier")

    distance = distance_matrix.loc["Buyer", selected_firm]
    time = time_matrix.loc["Buyer", selected_firm]
    cost = cost_matrix.loc["Buyer", selected_firm] * filtered_firms[selected_firm]["amount"]

    G.add_edge(selected_firm, "Buyer", distance=distance, time=time, cost=cost)

    pos = nx.spring_layout(G)
    edge_labels = {(u, v): f"Mesafe: {data['distance']} km\nMaliyet: {data['cost']} $\nSüre: {data['time']} saat"
                   for u, v, data in G.edges(data=True)}

    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Şebeke Grafiği")
    st.pyplot(plt)

    # Toplam Değerler
    st.subheader("Toplam Değerler")
    st.write(f"Toplam Mesafe: {distance} km")
    st.write(f"Toplam Süre: {time} saat")
    st.write(f"Toplam Maliyet: {cost} $")
    st.write(f"Eşleşen Firma: {selected_firm}")
