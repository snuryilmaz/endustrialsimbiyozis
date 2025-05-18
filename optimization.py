import pulp

def optimize_waste_allocation(firma_bilgileri, atik_turu, talep_miktari):
    atik_turu_norm = atik_turu.strip().lower()
    tedarikciler = [
        f for f, v in firma_bilgileri.items()
        if str(v["atik"]).strip().lower() == atik_turu_norm and v["miktar"] > 0
    ]

    if not tedarikciler:
        return None, 0, 0

    problem = pulp.LpProblem("AtikOptimizasyon", pulp.LpMinimize)
    karar_degiskenleri = {
        f: pulp.LpVariable(f"alis_{f}", lowBound=0, upBound=firma_bilgileri[f]["miktar"], cat="Continuous")
        for f in tedarikciler
    }

    problem += pulp.lpSum([karar_degiskenleri[f] * firma_bilgileri[f]["fiyat"] for f in tedarikciler])
    problem += pulp.lpSum([karar_degiskenleri[f] for f in tedarikciler]) <= talep_miktari
    problem.solve()

    sonuc = []
    toplam_maliyet = 0
    toplam_alinan = 0
    for f in tedarikciler:
        miktar = karar_degiskenleri[f].varValue if karar_degiskenleri[f].varValue else 0
        if miktar > 0:
            sonuc.append({
                "Gonderen": f,
                "Alici": "Siz",
                "Miktar": miktar,
                "Fiyat (TL/kg)": firma_bilgileri[f]["fiyat"],
                "Tutar": miktar * firma_bilgileri[f]["fiyat"]
            })
            toplam_maliyet += miktar * firma_bilgileri[f]["fiyat"]
            toplam_alinan += miktar

    return sonuc, toplam_maliyet, toplam_alinan
