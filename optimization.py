# optimization.py

import pulp

def optimize_waste_allocation(firma_bilgileri, atik_turu, talep_miktari):
    # Sadece seçilen atık türündeki tedarikçileri bul
    tedarikciler = [f for f, v in firma_bilgileri.items() if v["atik"] == atik_turu and v["miktar"] > 0]
    if not tedarikciler:
        return None, 0, []

    problem = pulp.LpProblem("AtikOptimizasyon", pulp.LpMinimize)
    karar_degiskenleri = {f: pulp.LpVariable(f"alis_{f}", lowBound=0, upBound=firma_bilgileri[f]["miktar"], cat="Continuous") for f in tedarikciler}

    # Amaç fonksiyonu: Toplam maliyeti minimize et
    problem += pulp.lpSum([karar_degiskenleri[f] * firma_bilgileri[f]["fiyat"] for f in tedarikciler])

    # Toplam alınan miktar, talep edilen miktarı aşamaz!
    problem += pulp.lpSum([karar_degiskenleri[f] for f in tedarikciler]) <= talep_miktari

    # Çözüm
    problem.solve()

    # Sonuçları işle
    sonuc = []
    toplam_maliyet = 0
    toplam_alinan = 0
    for f in tedarikciler:
        miktar = karar_degiskenleri[f].varValue if karar_degiskenleri[f].varValue else 0
        if miktar > 0:
            sonuc.append({
                "Gonderen": f,
                "Alici": "Siz",
                "AtikTuru": atik_turu,
                "Miktar": miktar,
                "BirimFiyat": firma_bilgileri[f]["fiyat"],
                "Maliyet": miktar * firma_bilgileri[f]["fiyat"]
            })
            toplam_maliyet += miktar * firma_bilgileri[f]["fiyat"]
            toplam_alinan += miktar

    return sonuc, toplam_maliyet, toplam_alinan
