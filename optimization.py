import pulp

def optimize_waste_allocation(firma_bilgileri):
    # Firma ve atık türleri kümeleri
    firmalar = list(firma_bilgileri.keys())
    atik_turleri = sorted(set(f["atik"] for f in firma_bilgileri.values()))

    # Üretim, talep, maliyet ve uygunluk
    uretim = {(f, k): firma_bilgileri[f]["miktar"] if firma_bilgileri[f]["atik"] == k else 0 for f in firmalar for k in atik_turleri}
    talep = {(f, k): firma_bilgileri[f]["miktar"] if firma_bilgileri[f]["atik"] == k else 0 for f in firmalar for k in atik_turleri}
    maliyet = {(i, j, k): abs(i.__hash__() - j.__hash__()) % 50 + 10 for i in firmalar for j in firmalar for k in atik_turleri if i != j}
    # Not: İsterseniz maliyeti geliştirebilirsin, burada örnek amaçlı basit bir fonksiyon var.

    # Model
    model = pulp.LpProblem("Atik_Tasima_Optimizasyonu", pulp.LpMinimize)
    x = pulp.LpVariable.dicts("x", ((i, j, k) for i in firmalar for j in firmalar for k in atik_turleri if i != j), lowBound=0, cat='Continuous')

    # Amaç fonksiyonu
    model += pulp.lpSum(maliyet[i, j, k] * x[(i, j, k)] for (i, j, k) in x), "Toplam_Tasima_Maliyeti"

    # Üretim kısıtı
    for i in firmalar:
        for k in atik_turleri:
            model += pulp.lpSum(x[(i, j, k)] for j in firmalar if i != j and (i, j, k) in x) <= uretim[(i, k)]

    # Talep kısıtı
    for j in firmalar:
        for k in atik_turleri:
            model += pulp.lpSum(x[(i, j, k)] for i in firmalar if i != j and (i, j, k) in x) <= talep[(j, k)]

    # Kendine gönderim yok
    # Zaten değişkenlerde i != j alındığı için gerek yok

    # Optimize et
    status = model.solve(pulp.PULP_CBC_CMD(msg=0))
    if status != pulp.LpStatusOptimal:
        return None, None

    results_list = []
    for (i, j, k) in x:
        miktar = x[(i, j, k)].varValue
        if miktar and miktar > 0:
            results_list.append({
                "Gonderen": i,
                "Alici": j,
                "AtikTuru": k,
                "Miktar": miktar
            })

    return results_list, pulp.value(model.objective)
