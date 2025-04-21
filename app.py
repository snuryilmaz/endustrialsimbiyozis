import streamlit as st
from utils.data_loader import load_database, get_suppliers_and_buyer
from utils.graph_utils import draw_network_graph
from optimization import create_optimization_model

# Load database
database = load_database("database.json")
suppliers, buyer = get_suppliers_and_buyer(database)

# Streamlit UI
st.title("Endüstriyel Simbiyoz Optimizasyon Aracı")
st.sidebar.header("Optimizasyon Seçenekleri")
objective_type = st.sidebar.selectbox(
    "Optimizasyon amacını seçin",
    ["distance", "cost", "time"]
)

if st.button("Optimizasyonu Çalıştır"):
    # Run optimization
    prob, assignments = create_optimization_model(objective_type, buyer, suppliers)

    # Display results
    if prob.status == 1:  # Optimal
        st.success("Optimal atama sağlandı!")
        for supplier_id, quantity in assignments.items():
            st.write(f"Firma {supplier_id}: {quantity} birim")
        draw_network_graph(suppliers, buyer, assignments, objective_type)
    else:
        st.error("Optimum çözüm bulunamadı.")