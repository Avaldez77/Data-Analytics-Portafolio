import pandas as pd

metrics = ["Lines", "Qty (pcs)", "Weight (Kg)", "CBM (M3)"]
methods = ["Air", "Ocean"]
subsidiaries = ["SEDA", "SEM", "SAMCOL", "SECH", "SEASA", "SEPR"]

data_dict = {
    sub: {method: {metric: 0 for metric in metrics} for method in methods}
    for sub in subsidiaries
}

data_dict_dg = {
    sub: {"Air": {metric: 0 for metric in metrics}}
    for sub in subsidiaries
}

country_to_sub = {
    "AR": "SEDA",
    "MX": "SEM",
    "CO": "SAMCOL",
    "CL": "SECH",
    "BR": "SEASA",
    "PR": "SEPR"
}

file_path = r"C:\Users\a.chacon\Downloads\outbound\C600-EXP-Reporte_de_Pedidos_12_meses.csv"
df = pd.read_csv(file_path, dtype=str)

required_cols = ["Ship-To Country", "Ship Type", "DG Y/N", "DO", "Delivery Qty", "Gross Weight", "Vol."]
missing = [c for c in required_cols if c not in df.columns]
if missing:
    raise ValueError(f"Faltan columnas en el CSV: {missing}")

def to_num(s):
    return pd.to_numeric(
        s.astype(str).str.replace(",", "", regex=False),
        errors="coerce"
    ).fillna(0)

df["Delivery Qty"] = to_num(df["Delivery Qty"])
df["Gross Weight"] = to_num(df["Gross Weight"])
df["Vol."] = to_num(df["Vol."])

df_all = df.copy()
df_all["Ship-To Country"] = df_all["Ship-To Country"].astype(str).str.strip().str.upper()
df_all["DG Y/N"] = df_all["DG Y/N"].astype(str).str.strip().str.upper()
df_all["Ship Type"] = df_all["Ship Type"].astype(str).str.strip()

df_all["Subsidiary"] = df_all["Ship-To Country"].map(country_to_sub)
df_sub = df_all.dropna(subset=["Subsidiary"]).copy()
df_sub["Ship Type"] = df_sub["Ship Type"].str.title()

df_gc = df_sub[df_sub["DG Y/N"] == "NO"].copy()

group_gc = df_gc.groupby(["Subsidiary", "Ship Type"]).agg(
    Lines=("DO", "count"),
    Qty_pcs=("Delivery Qty", "sum"),
    Weight_Kg=("Gross Weight", "sum"),
    CBM_M3=("Vol.", "sum")
).reset_index()

for _, row in group_gc.iterrows():
    sub = row["Subsidiary"]
    method = row["Ship Type"]
    if sub in data_dict and method in data_dict[sub]:
        data_dict[sub][method]["Lines"] = row["Lines"]
        data_dict[sub][method]["Qty (pcs)"] = row["Qty_pcs"]
        data_dict[sub][method]["Weight (Kg)"] = row["Weight_Kg"]
        data_dict[sub][method]["CBM (M3)"] = row["CBM_M3"]

final_rows_gc = []
for sub in data_dict:
    for method in data_dict[sub]:
        for metric, value in data_dict[sub][method].items():
            final_rows_gc.append([sub, method, metric, value])

final_df_gc = pd.DataFrame(final_rows_gc, columns=["Subsidiary", "Type", "Category", "Total"])

df_dg = df_sub[(df_sub["DG Y/N"] == "YES") & (df_sub["Ship Type"] == "Air")].copy()

group_dg = df_dg.groupby(["Subsidiary", "Ship Type"]).agg(
    Lines=("DO", "count"),
    Qty_pcs=("Delivery Qty", "sum"),
    Weight_Kg=("Gross Weight", "sum"),
    CBM_M3=("Vol.", "sum")
).reset_index()

for _, row in group_dg.iterrows():
    sub = row["Subsidiary"]
    if sub in data_dict_dg:
        data_dict_dg[sub]["Air"]["Lines"] = row["Lines"]
        data_dict_dg[sub]["Air"]["Qty (pcs)"] = row["Qty_pcs"]
        data_dict_dg[sub]["Air"]["Weight (Kg)"] = row["Weight_Kg"]
        data_dict_dg[sub]["Air"]["CBM (M3)"] = row["CBM_M3"]

final_rows_dg = []
for sub in data_dict_dg:
    for metric, value in data_dict_dg[sub]["Air"].items():
        final_rows_dg.append([sub, "Air", metric, value])

final_df_dg = pd.DataFrame(final_rows_dg, columns=["Subsidiary", "Type", "Category", "Total"])

categories_disty = ["Lines", "Qty (pcs)", "Weight", "CBM"]

def normalize_ship_type(x: str) -> str:
    x = str(x).strip().upper()
    if x == "AIR":
        return "Air"
    if x in ["TRUCK", "LOCAL DELIVERY", "LOCAL", "DELIVERY", "GROUND"]:
        return "Truck"
    if x in ["OCEAN", "VESSEL", "SEA", "SHIP"]:
        return "Vessel"
    return x.title()

code_to_name = {
    "CR": "Costa Rica",
    "GT": "Guatemala",
    "PA": "Panama",
    "EC": "Ecuador",
    "HN": "Honduras",
    "SV": "El Salvador",
    "DO": "Dominica",
    "VE": "Venezuela",
    "UY": "Uruguay",
    "PY": "Paraguay",
    "CB": "Caribbean",
    "NI": "Nicaragua",
    "BO": "Bolivia",
}

template_p3 = [
    ("CR","Truck"), ("CR","Air"),
    ("GT","Truck"), ("GT","Truck"),
    ("PA","Air"),
    ("EC","Vessel"), ("EC","Air"),
    ("HN","Air"),
    ("SV","Truck"), ("SV","Air"),
    ("DO","Air"),
    ("VE","Air"),
    ("UY","Air"),
    ("PY","Air"),
    ("CB","Air"),
    ("NI","Air"),
    ("BO","Air"),
]

template_p4 = [
    ("CR","Air"), ("CR","Truck"),
    ("GT","Air"),
    ("GT","Truck"), ("GT","Truck"),
    ("PA","Truck"),
    ("EC","Air"), ("EC","Vessel"),
    ("HN","Air"),
    ("SV","Air"), ("SV","Truck"),
    ("DO","Air"),
    ("VE","Air"),
    ("UY","Air"),
    ("PY","Air"),
    ("CB","Air"),
    ("NI","Air"),
    ("BO","Air"),
]

base = df_all.copy()
base["ShipMethod"] = base["Ship Type"].apply(normalize_ship_type)

def build_disty_from_template(df_src: pd.DataFrame, template: list[tuple[str, str]]) -> pd.DataFrame:
    grp = df_src.groupby(["Ship-To Country", "ShipMethod"]).agg(
        Lines=("DO", "count"),
        Qty_pcs=("Delivery Qty", "sum"),
        Weight=("Gross Weight", "sum"),
        CBM=("Vol.", "sum")
    ).reset_index()

    lookup = {}
    for _, r in grp.iterrows():
        lookup[(r["Ship-To Country"], r["ShipMethod"])] = {
            "Lines": float(r["Lines"]),
            "Qty (pcs)": float(r["Qty_pcs"]),
            "Weight": float(r["Weight"]),
            "CBM": float(r["CBM"]),
        }

    rows = []
    for cc, method in template:
        sub_name = "Disty"
        type_value = f"{code_to_name.get(cc, cc)} {method}"
        vals = lookup.get((cc, method), {"Lines": 0, "Qty (pcs)": 0, "Weight": 0, "CBM": 0})
        for cat in categories_disty:
            rows.append([sub_name, type_value, cat, vals[cat]])

    return pd.DataFrame(rows, columns=["Subsidiary", "Type", "Category", "Total"])

sheet3 = build_disty_from_template(base[base["DG Y/N"] == "NO"], template_p3)
sheet4 = build_disty_from_template(base[base["DG Y/N"] == "YES"], template_p4)

output_path = r"C:\Users\a.chacon\Downloads\outbound\Result.xlsx"

with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    final_df_gc.to_excel(writer, sheet_name="gc subsidiary", index=False, header=True)
    final_df_dg.to_excel(writer, sheet_name="dg subsidiary", index=False, header=True)
    sheet3.to_excel(writer, sheet_name="Pestaña 3", index=False, header=True)
    sheet4.to_excel(writer, sheet_name="Pestaña 4", index=False, header=True)

print(f"Archivo generado en: {output_path}")