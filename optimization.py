# optimizasyon.py

import pulp

def optimize_waste_allocation_from_dict(firma_bilgileri, tasima_maliyeti):
    firmalar = list(firma_bilgileri.keys())
    atik_turleri = list(set([v["atik"] for v in firma_bilgileri.values()]))

    # Üretim miktarı ve fiyatları
    uretim = {(f, firma_bilgileri[f]["atik"]): firma_bilgileri[f]["miktar"] for f in firmalar}
    fiyatlar = {f: firma_bilgileri[f]["fiyat"] for f in firmalar}

    # Model
    model = pulp.LpProblem("Atik_Tasima_Optimizasyonu", pulp.LpMinimize)

    # Karar değişkenleri: x[i][j][k] -> i firmasından j firmasına k atık türünde taşınan miktar
    x = pulp.LpVariable.dicts("x",
        ((i, j, k) for i in firmalar for j in firmalar for k in atik_turleri if i != j),
        lowBound=0,
        cat="Continuous"
    )

    # Amaç fonksiyonu: Toplam taşıma maliyetini minimize et
    model += pulp.lpSum(
        x[i, j, k] * tasima_maliyeti.get((i, j), 9999)
        for (i, j, k) in x
    )

    # Üretim (arz) kısıtı: Bir firmanın gönderebileceği atık kendi miktarını aşamaz
    for i in firmalar:
        for k in atik_turleri:
            model += pulp.lpSum(x[i, j, k] for j in firmalar if i != j and (i, j, k) in x) <= \
                     uretim.get((i, k), 0)

    # Talep kısıtı örneği (opsiyonel, basit haliyle)
    # Burada her firmanın aldığı toplam atık >= 0 gibi, spesifik talep yoksa es geçilebilir

    # Çöz
    model.solve()

    # Sonuçları listele
    results_list = []
    for (i, j, k), var in x.items():
        if var.varValue and var.varValue > 0:
            results_list.append({"Gonderen": i, "Alici": j, "AtikTuru": k, "Miktar": var.varValue})

    total_cost = pulp.value(model.objective)
    return results_list, total_cost, pulp.LpStatus[model.status]
