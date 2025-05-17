# pyomo_model.py

import pandas as pd
import pyomo.environ as pe
from pyomo.opt import SolverFactory, TerminationCondition, SolverStatus

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

    model = pe.ConcreteModel()
    model.F = pe.Set(initialize=firmalar)
    model.K = pe.Set(initialize=atik_turleri)

    model.production = pe.Param(model.F, model.K, initialize=lambda m, f, k: uretim.get((f, k), 0))
    model.demand = pe.Param(model.F, model.K, initialize=lambda m, f, k: talep.get((f, k), 0))
    model.cost = pe.Param(model.F, model.F, model.K, initialize=lambda m, i, j, k: maliyet.get((i, j), 0))
    model.compatibility = pe.Param(model.F, model.F, model.K, initialize=lambda m, i, j, k: Cijk.get((i, j, k), 0))
    model.Qk = pe.Param(model.K, initialize=Qk)
    model.x = pe.Var(model.F, model.F, model.K, domain=pe.NonNegativeReals)

    def obj_rule(m):
        return sum(m.cost[i, j, k] * m.x[i, j, k] for i in m.F for j in m.F for k in m.K if i != j)
    model.obj = pe.Objective(rule=obj_rule, sense=pe.minimize)

    def prod_rule(m, i, k):
        return sum(m.x[i, j, k] for j in m.F if j != i) <= m.production[i, k]
    model.prod_con = pe.Constraint(model.F, model.K, rule=prod_rule)

    def dem_rule(m, j, k):
        return sum(m.x[i, j, k] for i in m.F if i != j) <= m.demand[j, k]
    model.dem_con = pe.Constraint(model.F, model.K, rule=dem_rule)

    def no_self_rule(m, f, k):
        return m.x[f, f, k] == 0
    model.self_con = pe.Constraint(model.F, model.K, rule=no_self_rule)

    def comp_rule(m, i, j, k):
        return m.x[i, j, k] <= m.compatibility[i, j, k] * 1e5
    model.compat_con = pe.Constraint(model.F, model.F, model.K, rule=comp_rule)

    def balance_rule(m, k):
        return sum(m.x[i, j, k] for i in m.F for j in m.F if i != j) == m.Qk[k]
    model.balance_con = pe.Constraint(model.K, rule=balance_rule)

    min_threshold = 100
    def min_shipment_rule(m, i, j, k):
        return m.x[i, j, k] >= min_threshold * m.compatibility[i, j, k]
    model.min_shipment_con = pe.Constraint(model.F, model.F, model.K, rule=min_shipment_rule)

    solver = SolverFactory("gurobi")
    results = solver.solve(model, tee=True)

    if (results.solver.status == SolverStatus.ok) and \
       (results.solver.termination_condition == TerminationCondition.optimal):
        results_list = []
        for i in model.F:
            for j in model.F:
                for k in model.K:
                    val = pe.value(model.x[i, j, k])
                    if val and val > 0:
                        results_list.append({"Gonderen": i, "Alici": j, "AtikTuru": k, "Miktar": val})
        return results_list, pe.value(model.obj)
    else:
        print("Çözüm bulunamadı veya model optimal değil!")
        print("Status:", results.solver.status)
        print("Termination:", results.solver.termination_condition)
        return None, None
