import pulp

def create_optimization_model(objective_type, buyer, suppliers):
    prob = pulp.LpProblem("IndustrialSymbiosis", pulp.LpMinimize)

    # Decision variables
    supplier_vars = {s['id']: pulp.LpVariable(f"Supplier_{s['id']}", 0, s['capacity'], pulp.LpContinuous)
                     for s in suppliers}

    # Objective function
    prob += pulp.lpSum(supplier_vars[s['id']] * s[objective_type] for s in suppliers)

    # Constraints
    prob += pulp.lpSum(supplier_vars[s['id']] for s in suppliers) == buyer['demand'], "DemandConstraint"

    # Solve
    prob.solve()

    assignments = {s['id']: supplier_vars[s['id']].varValue for s in suppliers}
    return prob, assignments