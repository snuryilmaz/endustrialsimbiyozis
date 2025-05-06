import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
import json
import pandas as pd

# Matris dosyasını yükleme
with open("matrices.json", "r") as f:
    matrices = json.load(f)

distance_matrix = pd.DataFrame(matrices["distance_matrix"])
time_matrix = pd.DataFrame(matrices["time_matrix"])
cost_matrix = pd.DataFrame(matrices["cost_matrix"])

# Streamlit URL (Yerel ağ için IP adresinizi yazın)
streamlit_url = "http://192.168.1.10:8501"  # Kendi IP adresinizi yazın

def create_optimization_model(objective_type, buyer_demand, supplier_data):
    # Create the optimization problem
    prob = pulp.LpProblem("IndustrialSymbiosis", pulp.LpMinimize)

    # Decision variables
    supplier_vars = {i: pulp.LpVariable(f"Supplier_{i}", 0, supplier_data[i]['capacity'], pulp.LpContinuous)
                     for i in supplier_data}

    # Objective function
    if objective_type == "Yol minimizasyonu":
        prob += pulp.lpSum(supplier_vars[i] * supplier_data[i]['distance'] for i in supplier_data), "TotalDistance"
    elif objective_type == "Maliyet minimizasyonu":
        prob += pulp.lpSum(supplier_vars[i] * supplier_data[i]['cost'] for i in supplier_data), "TotalCost"
    elif objective_type == "Süre minimizasyonu":
        prob += pulp.lpSum(supplier_vars[i] * supplier_data[i]['time'] for i in supplier_data), "TotalTime"

    # Constraints
    prob += pulp.lpSum(supplier_vars[i] for i in supplier_data) == buyer_demand, "DemandConstraint"

    # Solve the problem
    prob.solve()

    return prob, supplier_vars


def draw_network_graph(supplier_data, buyer_demand, supplier_vars, objective_type):
    G = nx.DiGraph()

    # Mapping 'objective_type' to corresponding keys in 'supplier_data'
    objective_mapping = {
        "Yol minimizasyonu": "distance",
        "Maliyet minimizasyonu": "cost",
        "Süre minimizasyonu": "time"
    }

    # Add nodes for suppliers and buyer
    for supplier in supplier_data:
        G.add_node(f"Supplier_{supplier}", role='supplier')
    G.add_node("Buyer", role='buyer')

    # Add edges with weights
    for supplier in supplier_data:
        G.add_edge(f"Supplier_{supplier}", "Buyer",
                   weight=supplier_data[supplier][objective_mapping[objective_type]],
                   quantity=supplier_vars[supplier].varValue)

    pos = nx.spring_layout(G)
    edge_labels = {(u, v): f"{data['quantity']} units" for u, v, data in G.edges(data=True)}

    # Draw the graph
    nx.draw(G, pos, with_labels=True, node_color="lightblue", node_size=3000, font_size=10, font_weight="bold")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
    plt.title("Optimal Assignment Network")
    st.pyplot(plt)


# Streamlit UI
st.title("Endüstriyel Simbiyoz ARSİN OSB Optimizasyon Aracı")

# Sol Şeride Kullanıcı Girdileri
st.sidebar.header("Kullanıcı Bilgileri")
name = st.sidebar.text_input("Adınız Soyadınız", "")
company_name = st.sidebar.text_input("Şirket İsmi", "")
sector = st.sidebar.selectbox(
    "Şirket Sektörü",
    ["", "Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalatı"],  # Boş seçenek varsayılan
    index=0
)

# Atık Bilgileri Seçimi
waste_options = {
    "Demir-Çelik": ["Demir Talaşı", "Çelik Artığı"],
    "Plastik Enjeksiyon": ["PT", "HDPE"],
    "Makine İmalatı": ["Metal Talaşı", "Yağlı Atık"]
}
waste = st.sidebar.selectbox("Almak İstediğiniz Atık", waste_options.get(sector, []))

# Optimizasyon Amacı ve Talep
st.sidebar.header("Optimizasyon Seçenekleri")
objective_type = st.sidebar.selectbox(
    "Optimizasyon amacını seçin",
    ["Yol minimizasyonu", "Maliyet minimizasyonu", "Süre minimizasyonu"]
)
buyer_demand = st.sidebar.number_input("Alıcı talebi (birim)", min_value=1, step=1)

# Firma Verileri (Sektöre Göre Filtreleme)
firm_data = {
    "Firma 1": {"sector": "Plastik Enjeksiyon", "waste": "HDPE", "capacity": 100, "distance": 50, "cost": 15, "time": 5},
    "Firma 2": {"sector": "Demir-Çelik", "waste": "Demir Talaşı", "capacity": 200, "distance": 30, "cost": 10, "time": 3},
    "Firma 3": {"sector": "Makine İmalatı", "waste": "Metal Talaşı", "capacity": 150, "distance": 70, "cost": 20, "time": 7},
    # Diğer firmalar...
}

filtered_firms = {
    firm: data for firm, data in firm_data.items() if data["sector"] == sector and data["waste"] == waste
}

if st.sidebar.button("Optimizasyonu Çalıştır"):
    # Optimizasyon Modeli
    prob, supplier_vars = create_optimization_model(objective_type, buyer_demand, filtered_firms)

    # Sonuçlar
    if pulp.LpStatus[prob.status] == "Optimal":
        st.success("Optimal eşleşme sağlandı!")
        for supplier in supplier_vars:
            st.write(f"{supplier}: {supplier_vars[supplier].varValue} birim")
        draw_network_graph(filtered_firms, buyer_demand, supplier_vars, objective_type)
    else:
        st.error("Optimum çözüm bulunamadı.")

# QR Kodu Oluştur ve Göster
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
