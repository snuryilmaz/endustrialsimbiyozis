import pandas as pd
import pulp

def optimize_waste_allocation(excel_path):
    # Excel dosyasını oku
    df_S = pd.read_excel(excel_path, sheet_name="Uretim_Miktari")
    df_D = pd.read_excel(excel_path, sheet_name="Talep_Miktari")
    df_T = pd.read_excel(excel_path, sheet_name="Tasima_Maliyeti")

    firmalar = sorted(set(df_S["Firma"]) | set(df_D["Firma"]))
    atik_turleri = sorted(set(df_S["AtikTuru"]) | set(df_D["AtikTuru"]))

    uretim = {(r["Firma"], r["AtikTuru"]): r["UretimMiktari"] for _, r in df_S.iterrows()}
    talep = {(r["Firma"], r["AtikTuru"]): r["TalepMiktari"] for _, r in df_D.iterrows()}
    maliyet = {(r["Gonderen"], r["Alici"]): r["Maliyet"] for _, r in df_T.iterrows()}

    # Uyum matrisi
    Cijk = {}
    for i in firmalar:
        for j in firmalar:
            for k in atik_turleri:
                if i != j:
                    Cijk[(i, j, k)] = int(uretim.get((i, k), 0) > 0 and talep.get((j, k), 0) > 0)
                else:
                    Cijk[(i, j, k)] = 0

    uretim_toplam = df_S.groupby("AtikTuru")["UretimMiktari"].sum()
    talep_toplam = df_D.groupby("AtikTuru")["TalepMiktari"].sum()
    Qk = {k: min(uretim_toplam.get(k, 0), talep_toplam.get(k, 0)) for k in atik_turleri}

    # Model oluştur
    model = pulp.LpProblem("Endustriyel_Simbiyoz", pulp.LpMinimize)

    # Karar değişkenleri
    x = pulp.LpVariable.dicts("x",
        ((i, j, k) for i in firmalar for j in firmalar for k in atik_turleri),
        lowBound=0, cat="Continuous")

    # Amaç fonksiyonu
    model += pulp.lpSum(
        maliyet.get((i, j), 0) * x[i, j, k]
        for i in firmalar for j in firmalar for k in atik_turleri if i != j
    )

    # Üretim kısıtı
    for i in firmalar:
        for k in atik_turleri:
            model += pulp.lpSum(x[i, j, k] for j in firmalar if j != i) <= uretim.get((i, k), 0)

    # Talep kısıtı
    for j in firmalar:
        for k in atik_turleri:
            model += pulp.lpSum(x[i, j, k] for i in firmalar if i != j) <= talep.get((j, k), 0)

    # Kendi kendine akış olmasın
    for f in firmalar:
        for k in atik_turleri:
            model += x[f, f, k] == 0

    # Uyum kısıtı (compatible ise izin ver)
    for i in firmalar:
        for j in firmalar:
            for k in atik_turleri:
                model += x[i, j, k] <= Cijk[(i, j, k)] * 1e5

    # Denge kısıtı
    for k in atik_turleri:
        model += pulp.lpSum(x[i, j, k] for i in firmalar for j in firmalar if i != j) == Qk[k]

    # Minimum gönderim (ör: 100 kg ve uyumluysa)
    min_threshold = 100
    for i in firmalar:
        for j in firmalar:
            for k in atik_turleri:
                model += x[i, j, k] >= min_threshold * Cijk[(i, j, k)]

    # CBC ile çöz (varsayılan)
    model.solve()

    # Sonuçlar
    if pulp.LpStatus[model.status] == "Optimal":
        results_list = []
        for i in firmalar:
            for j in firmalar:
                for k in atik_turleri:
                    val = x[i, j, k].varValue
                    if val is not None and val > 0:
                        results_list.append({"Gonderen": i, "Alici": j, "AtikTuru": k, "Miktar": val})
        return results_list, pulp.value(model.objective)
    else:
        return None, None
