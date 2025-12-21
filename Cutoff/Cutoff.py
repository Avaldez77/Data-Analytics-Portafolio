import pandas as pd
import numpy as np
import pyodbc
import time
from datetime import datetime
from tqdm import tqdm

# =========================
# FUNCIÓN LIMPIAR COLUMNAS
# =========================
def limpiar(columna):
    return (
        columna.astype(str)
        .str.strip()
        .str.extract(r"(\d+)")
        .astype(float)
    )

# =========================
# CONEXIÓN SQL SERVER (SANITIZED)
# =========================
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=<SQL_SERVER_HOST_OR_IP>;'
    'DATABASE=<SQL_DATABASE_NAME>;'
    'Trusted_Connection=yes;'
)

query = """
SELECT * FROM <BUYERSCODE_TABLE>
"""

buyers = pd.read_sql(query, conn)
conn.close()

# =========================
# DICCIONARIOS
# =========================
subscutoffdic = {
    "Prime Auto": "11:01",
    "Prime Hub": "18:01",
    "Prime Non-Channel": "10:31",
    "Channel": "13:01",
    "Affiliates": "15:01",
}

countrydic = {
    "VE": "11:01"
}

countrypersondic = {
    "UY": "person1",
    "AN": "person2",
    "AW": "person2",
    "BB": "person2",
    "BZ": "person9",
    "CW": "person2",
    "GD": "person2",
    "GY": "person2",
    "JM": "person2",
    "LC": "person2",
    "PR": "person2",
    "TT": "person2",
    "VC": "person2",
    "PA": "person3",
    "VE": "person3",
    "HN": "person4",
    "PY": "person5",
    "DO": "person5",
    "BO": "person6",
    "EC": "person6",
    "CR": "person7",
    "NI": "person7",
    "GT": "person8",
    "SV": "person8",
    "MX": "person10",
    "CO": "person11",
    "BR": "person12",
    "CL": "person12",
    "AR": "person13",
    "PE": "person13",
    "CH": "person14",
}

# =========================
# RENOMBRE (AJUSTE PEDIDO)
# =========================
df_source_export =50090  # si ya lo tienes cargado con ese nombre, esta línea lo "traduce"

# =========================
# PROCESO DOPERFORMANCE
# =========================
# Antes: DOperformance =50090.iloc[:, [5, 6, 8, 26, 39, 67]]
df_ops_kpi = df_source_export.iloc[:, [5, 6, 8, 26, 39, 67]]
df_ops_kpi = df_ops_kpi.rename(columns={"SoldTo code": "CODE"})

# =========================
# PROCESO BUYER
# =========================
buyer = buyers.iloc[:, [0, 2, 3]].copy()
buyer["CODE"] = limpiar(buyer["CODE"])
df_ops_kpi["CODE"] = limpiar(df_ops_kpi["CODE"])

# =========================
# MERGE DATAFRAMES
# =========================
dfprueba = pd.merge(df_ops_kpi, buyer, on="CODE", how="outer")
dfprueba = dfprueba.rename(columns={"DO Created by": "createdby"})

# =========================
# FILTROS
# =========================
dfprueba = dfprueba[dfprueba["SO Type"] == "YN01"]
dfprueba = dfprueba[dfprueba["Week"] >= 47]

# =========================
# RENOMBRAR COLUMNAS
# =========================
dfprueba = dfprueba.rename(columns={
    "COUNTRY": "country",
    "GROUP": "group"
})

# =========================
# MAPEAR VALORES
# =========================
country = dfprueba["country"].map(countrydic)

# =========================
# ACTUALIZAR CUTOFF
# =========================
dfprueba["cutoff"] = dfprueba["group"].map(subscutoffdic)
dfprueba["cutoff"].update(dfprueba["country"].map(subscutoffdic))

# =========================
# REEMPLAZAR BOT / CRT
# =========================
def reemplazar_bot_por_creador(df, countrypersondic):
    for index, row in df.iterrows():
        createdby = str(row.get("createdby", "")).upper()
        country = str(row.get("country", "")).upper()

        if ("BOT" in createdby or "CRT" in createdby) and country in countrypersondic:
            df.at[index, "createdby"] = countrypersondic[country]
    return df

dfprueba = reemplazar_bot_por_creador(dfprueba, countrypersondic)

# =========================
# CONVERTIR FECHAS
# =========================
dfprueba["D/O Creation Time (Local)"] = pd.to_datetime(dfprueba["D/O Creation Time (Local)"], errors="coerce")
dfprueba["cutoff"] = pd.to_datetime(dfprueba["cutoff"], errors="coerce")

print(dfprueba.head())

# =========================
# DETERMINAR STATUS
# =========================
dfprueba.loc[dfprueba["D/O Creation Time (Local)"] > dfprueba["cutoff"], "status"] = "Late"
dfprueba.loc[dfprueba["D/O Creation Time (Local)"] <= dfprueba["cutoff"], "status"] = "On time"

dfprueba.to_csv(
    r"<OUTPUT_FOLDER>\doperfomance.csv",
    index=False
)

# =========================
# VARIABLES SQL
# =========================
df = dfprueba
tabla_sql = "<DOPERFOMANCE_TABLE_NAME>"
week_col = "Week"

# =========================
# VALIDAR WEEK
# =========================
if week_col not in df.columns:
    raise ValueError(f"La columna '{week_col}' no fue encontrada")

df[week_col] = df[week_col].astype(int)

# =========================
# RANGO DE SEMANAS
# =========================
semana_actual = datetime.today().isocalendar().week
rango_semanas = [(semana_actual - i) % 52 or 52 for i in range(10)]
df_rango = df[df[week_col].isin(rango_semanas)].copy()
df_rango = df_rango.replace({np.nan: None})

# =========================
# CONEXIÓN SQL SERVER (SANITIZED)
# =========================
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=<SQL_SERVER_HOST_OR_IP>;'
    'DATABASE=<SQL_DATABASE_NAME>;'
    'Trusted_Connection=yes;'
)

cursor = conn.cursor()

# =========================
# VERIFICAR TABLA
# =========================
cursor.execute(f"""
    SELECT COUNT(*)
    FROM INFORMATION_SCHEMA.TABLES
    WHERE TABLE_NAME = '{tabla_sql}'
""")

existe_tabla = cursor.fetchone()[0] > 0

# =========================
# CREAR TABLA
# =========================
if not existe_tabla:
    print(f"Creando tabla '{tabla_sql}'...")

    tipo_sql = {
        "int64": "BIGINT",
        "float64": "FLOAT",
        "object": "VARCHAR(255)",
        "bool": "BIT",
        "datetime64[ns]": "DATETIME",
        "UInt32": "INT"
    }

    columnas_sql = []
    for col in df.columns:
        tipo = tipo_sql.get(str(df[col].dtype), "VARCHAR(255)")
        columnas_sql.append(f"[{col}] {tipo}")

    create_stmt = f"CREATE TABLE {tabla_sql} ({', '.join(columnas_sql)})"
    cursor.execute(create_stmt)
    conn.commit()

# =========================
# INSERTAR DATOS
# =========================
df_insertar = df_rango if existe_tabla else df.replace({np.nan: None})

cursor.fast_executemany = True
cols = ", ".join([f"[{c}]" for c in df_insertar.columns])
placeholders = ", ".join(["?"] * len(df_insertar.columns))
insert_stmt = f"INSERT INTO {tabla_sql} ({cols}) VALUES ({placeholders})"

start = time.time()
batch_size = 1000

for i in tqdm(range(0, len(df_insertar), batch_size), desc="Insertando datos"):
    batch = df_insertar.iloc[i:i + batch_size]
    cursor.executemany(insert_stmt, batch.values.tolist())
    conn.commit()

end = time.time()

# =========================
# LOG
# =========================
log_msg = (
    f"Carga completada: {len(df_insertar)} registros insertados\n"
    f"Tabla: {tabla_sql}\n"
    f"Semana actual: {semana_actual}\n"
    f"Semanas afectadas: {rango_semanas}\n"
    f"Tiempo total: {end - start:.2f} segundos\n"
    f"Fecha y hora: {datetime.now()}\n"
    f"{'-'*50}\n"
)

with open(r"<OUTPUT_FOLDER>\log_carga_DOPERFOMANCE.txt", "a", encoding="utf-8") as f:
    f.write(log_msg)

# =========================
# CIERRE
# =========================
cursor.close()
conn.close()
