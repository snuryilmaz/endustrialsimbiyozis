import pulp

def optimize_waste_allocation(firma_bilgileri, talep_urun, talep_miktar):
    # Sadece seçilen ürünü satan firmalar
    uygun_firmalar = {f: info for f, info in firma_bilgileri.items() if info['atik'] == talep_urun and info['miktar'] > 0}
    if not uygun_firmalar or talep_miktar <= 0:
        return None, None, []

    # Değişkenler: Her uygun firma için alınacak miktar
    x = pulp.LpVariable.dicts("alinan", uygun_firmalar.keys(), lowBound=0, cat="Continuous")

    # Model
    model = pulp.LpProblem("AlimOptimizasyonu", pulp.LpMinimize)
    # Amaç fonksiyonu: toplam maliyet
    model += pulp.lpSum(x[f] * uygun_firmalar[f]['fiyat'] for f in uygun_firmalar)

    # Talep kısıtı: toplam alınan miktar >= istenen miktar
    model += pulp.lpSum(x[f] for f in uygun_firmalar) == talep_miktar

    # Her firmadan en fazla mevcut miktar alınabilir
    for f in uygun_firmalar:
        model += x[f] <= uygun_firmalar[f]['miktar']

    status = model.solve(pulp.PULP_CBC_CMD(msg=0))

    if pulp.LpStatus[model.status] != "Optimal":
        return None, None, []

    # Sonuçları çıkar
    results = []
    for f in uygun_firmalar:
        miktar = x[f].varValue
        if miktar and miktar > 0:
            results.append({
                "Firma": f,
                "AlinanMiktar": miktar,
                "BirimFiyat": uygun_firmalar[f]['fiyat'],
                "Tutar": miktar * uygun_firmalar[f]['fiyat']
            })
    toplam_maliyet = sum(r["Tutar"] for r in results)
    return results, toplam_maliyet, uygun_firmalar
