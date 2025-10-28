import random

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
