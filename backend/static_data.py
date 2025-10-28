import random

varsayilan_firmalar = {
    "Firma 1": {"sektor": "Demir-Çelik", "atik": "Metal Talaşı", "fiyat": 5, "miktar": 100, "lead_time_days": random.randint(0, 15)},
    # ... diğer firmalar ...
}

turikler = {
    "Demir-Çelik": ["Metal Talaşı", "Çelik Parçaları"],
    # ... diğer sektörler ...
}

firma_koordinatlari = {
    "Firma 1": (41.0105, 39.7266),
    # ... diğer koordinatlar ...
}
