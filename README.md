# Endüstriyel Simbiyozis

Bu proje, KTÜ Endüstri Mühendisliği öğrencileri tarafından Trabzon/Arsin OSB'de endüstriyel simbiyoz kapsamında Alıcı ve Satıcı firmaları eşleştirici bir arayüz oluşturmak için tasarlanmıştır. 

## Gereksinimler

Projeyi çalıştırmadan önce aşağıdaki paketlerin yüklü olduğundan emin olun:

```bash
pip install streamlit pulp networkx matplotlib pillow qrcode
```

## Kullanım

Streamlit uygulamasını çalıştırmak için aşağıdaki komutu kullanabilirsiniz:

```bash
streamlit run app.py
```

## Koddan Örnek

Aşağıda optimizasyon modeli oluşturma fonksiyonuna dair bir örnek verilmiştir:

```python
import streamlit as st
import pulp
import networkx as nx
import matplotlib.pyplot as plt
import qrcode
from PIL import Image

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

    return prob
```

## Lisans

Bu proje [MIT Lisansı](https://opensource.org/licenses/MIT) ile lisanslanmıştır.
