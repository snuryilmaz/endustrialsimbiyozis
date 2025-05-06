import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import qrcode
from PIL import Image
import json
import random
import pandas as pd

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


# Kullanıcı Bilgileri Girişi
st.title("Endüstriyel Simbiyoz Optimizasyon Aracı")

st.header("Kullanıcı Bilgileri")
name = st.text_input("Adınız Soyadınız")
company_name = st.text_input("Şirket İsmi")
sector = st.selectbox(
    "Şirket Sektörü",
    ["Demir-Çelik", "Plastik Enjeksiyon", "Makine İmalatı"]
)

# Atık Bilgileri Seçimi
waste_options = {
    "Demir-Çelik": ["Demir Talaşı", "Çelik Artığı"],
    "Plastik Enjeksiyon": ["PT", "HDPE", "PVC"],
    "Makine İmalatı": ["Metal Talaşı", "Yağlı Atık"]
}

waste = st.selectbox("Atık Türü", waste_options.get(sector, []))

if st.button("Bilgileri Kaydet"):
    st.success(f"Bilgiler Kaydedildi: {name}, {company_name}, {sector}, {waste}")

# Rastgele Uzaklık Matrisi
st.header("Uzaklık Matrisi")
try:
    with open("database.json", "r") as f:
        data = json.load(f)
    st.write("Mevcut Uzaklık Matrisi:")
    st.dataframe(pd.DataFrame(data["distance_matrix"]))
except FileNotFoundError:
    st.warning("Uzaklık matrisi bulunamadı. Yeni bir rastgele matris oluşturuluyor...")

    # 8 firma için rastgele uzaklık matrisi oluştur
    firms = [f"Firma {i+1}" for i in range(8)]
    distance_matrix = {
        firm: {other: random.randint(10, 100) if firm != other else 0 for other in firms}
        for firm in firms
    }

    # Database'e kaydet
    with open("database.json", "w") as f:
        json.dump({"distance_matrix": distance_matrix}, f)

    st.write("Yeni Uzaklık Matrisi:")
    st.dataframe(pd.DataFrame(distance_matrix))

# Streamlit Sidebar
st.sidebar.header("Optimizasyon Seçenekleri")
objective_type = st.sidebar.selectbox(
    "Optimizasyon amacını seçin",
    ["Yol minimizasyonu", "Maliyet minimizasyonu", "Süre minimizasyonu"]
)

st.sidebar.header("Alıcı Bilgileri")
buyer_demand = st.sidebar.number_input("Alıcı talebi (birim)", min_value=1, step=1)

st.sidebar.header("Satıcı Bilgileri")
supplier_count = st.sidebar.number_input("Satıcı sayısı", min_value=1, max_value=10, step=1)

supplier_data = {}
for i in range(1, supplier_count + 1):
    st.sidebar.subheader(f"Satıcı {i}")
    capacity = st.sidebar.number_input(f"Satıcı {i} kapasitesi", min_value=1, step=1)
    distance = st.sidebar.number_input(f"Satıcı {i} mesafesi", min_value=1.0, step=1.0)
    cost = st.sidebar.number_input(f"Satıcı {i} maliyeti", min_value=1.0, step=1.0)
    time = st.sidebar.number_input(f"Satıcı {i} süresi", min_value=1.0, step=1.0)
    supplier_data[i] = {"capacity": capacity, "distance": distance, "cost": cost, "time": time}

if st.button("Optimizasyonu Çalıştır"):
    # Run optimization
    prob, supplier_vars = create_optimization_model(objective_type, buyer_demand, supplier_data)

    # Display results
    if pulp.LpStatus[prob.status] == "Optimal":
        st.success("Optimal atama sağlandı!")
        for supplier in supplier_vars:
            st.write(f"Satıcı {supplier}: {supplier_vars[supplier].varValue} birim")
        draw_network_graph(supplier_data, buyer_demand, supplier_vars, objective_type)
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

st.image("qrcode.png", caption="Bu QR kodu tarayarak siteye erişin!")
st.write(f"Erişim için URL: {streamlit_url}")
