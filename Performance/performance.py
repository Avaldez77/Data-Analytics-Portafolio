# %%
# PROJECT_X – ETL Tracking Info → CSV → SQL Server  (SANITIZED)

# =========================
# IMPORTS
# =========================
import pandas as pd
import os
import pyodbc
import time
import numpy as np
from tqdm import tqdm
from datetime import datetime
from dateutil.relativedelta import relativedelta
import openpyxl
import difflib
from itertools import combinations


# =========================
# RUTAS EXCEL (SANITIZED)
# =========================
rutas = [
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_JAN-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_FEB-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_MAR-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_APR-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_MAY-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_JUN-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_JUL-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_AUG-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_SEP-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_OCT-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_NOV-2025.XLSX",
    r"\\10.10.10.10\Corp_Share\svc\OPS\Automation_CoE\EDI\PROJECT_X\tracking Info_DEC-2025.XLSX",
]

meses = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]


# =========================
# DICCIONARIO PERSONAS (NO SE ELIMINA, SOLO SE SANITIZA)
# =========================
# Deja países tal cual. Cambia solo nombres/correos/IDs reales a person1, person2...
personas = {
    "person1": {"country": "Panama",      "role": "Owner"},
    "person2": {"country": "Costa Rica",  "role": "Backup"},
    "person3": {"country": "Guatemala",   "role": "Reviewer"},
    "person4": {"country": "Ecuador",     "role": "Approver"},
    "person5": {"country": "Uruguay",     "role": "Stakeholder"},
    "person6": {"country": "Paraguay",    "role": "Stakeholder"},
}


# =========================
# CARGA EXCELS
# =========================
for i in range(len(rutas)):
    mes = meses[i]
    ruta_archivo = rutas[i]
    nombre_variable = f"{mes}2025"

    if os.path.exists(ruta_archivo):
        try:
            df = pd.read_excel(ruta_archivo, engine="openpyxl")
            globals()[nombre_variable] = df
            print(f"{mes} cargado OK")
        except Exception as e:
            print(f"{mes} ERROR: {e}")
    else:
        print(f"{mes} NO encontrado")


# =========================
# FILTRADO DE COLUMNAS
# =========================
cols = """
"""
listacols = cols.split("\n")

dataframes = [
    JAN2025, FEB2025, MAR2025, APR2025, MAY2025, JUN2025,
    JUL2025, AUG2025, SEP2025, OCT2025, NOV2025, DEC2025
]

for i in range(len(dataframes)):
    dataframes[i] = dataframes[i][
        [c for c in dataframes[i].columns if c in listacols]
    ]


# =========================
# ORDENAR COLUMNAS
# =========================
for m in meses:
    globals()[f"{m}2025"] = globals()[f"{m}2025"][sorted(globals()[f"{m}2025"].columns)]


# =========================
# CONCATENAR
# =========================
Lista_df = [
    MAR2025, APR2025, MAY2025, JUN2025,
    JUL2025, AUG2025, SEP2025, OCT2025, NOV2025, DEC2025
]

REPORT_TRK_50090 = pd.concat(Lista_df, ignore_index=True)
REPORT_TRK_50090 = REPORT_TRK_50090.dropna(how="all", axis=1)

REPORT_TRK_50090["Document Date"] = pd.to_datetime(REPORT_TRK_50090["Document Date"])
REPORT_TRK_50090["Week"] = REPORT_TRK_50090["Document Date"].dt.isocalendar().week


# =========================
# EXPORT CSV
# =========================
csv_path = r"C:\Users\generic.user\Documents\PROJECT_X\REPORT_TRK_50090.csv"
REPORT_TRK_50090.to_csv(csv_path, index=False)


# =========================
# VALIDAR COLUMNAS CLAVE
# =========================
dfs = {
    "MAR2025": MAR2025,
    "APR2025": APR2025,
    "MAY2025": MAY2025,
    "JUN2025": JUN2025,
    "JUL2025": JUL2025,
    "AUG2025": AUG2025,
    "SEP2025": SEP2025,
    "OCT2025": OCT2025,
    "NOV2025": NOV2025
}

cols_a_validar = ["2nd GI Date", "ePOD Date", "ePOD Entry Date"]

for nombre, df in dfs.items():
    faltantes = [c for c in cols_a_validar if c not in df.columns]
    if faltantes:
        print(f"❌ {nombre} sin columnas {faltantes}")
    else:
        print(f"✅ {nombre} OK")


# =========================
# CARGAR CSV PARA SQL
# =========================
tabla_sql = "REPORT_TRK_50090"
week_col = "Week"

df = pd.read_csv(csv_path)
df.columns = df.columns.str.strip().str.replace("\u200b", "")

cols_bloqueadas = [
    "2nd GI Date", "ePOD Date", "ePOD Entry Date",
    "Consolidation No.", "Packing Material", "Vehicle No."
]

df = df[[c for c in df.columns if c in listacols and c not in cols_bloqueadas]]

if week_col not in df.columns:
    raise ValueError(f"Columna {week_col} no existe")

df[week_col] = df[week_col].astype(int)

semana_actual = datetime.today().isocalendar().week
rango_semanas = [(semana_actual - i) % 52 or 52 for i in range(10)]
df_rango = df[df[week_col].isin(rango_semanas)].copy()
df_rango = df_rango.replace({np.nan: None})


# =========================
# CONEXIÓN SQL SERVER (SANITIZED)
# =========================
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=10.10.20.20;'
    'DATABASE=CORP_ANALYTICS;'
    'Trusted_Connection=yes;'
)
cursor = conn.cursor()

cursor.execute(f"""
SELECT COUNT(*)
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_NAME = '{tabla_sql}'
""")

existe_tabla = cursor.fetchone()[0] > 0


# =========================
# CREAR TABLA SI NO EXISTE
# =========================
if not existe_tabla:
    tipo_sql = {
        'int64': 'BIGINT',
        'float64': 'FLOAT',
        'object': 'VARCHAR(255)',
        'bool': 'BIT',
        'datetime64[ns]': 'DATETIME',
        'UInt32': 'INT'
    }

    columnas_sql = []
    for col in df.columns:
        tipo = tipo_sql.get(str(df[col].dtype), 'VARCHAR(255)')
        columnas_sql.append(f"[{col}] {tipo}")

    create_stmt = f"CREATE TABLE {tabla_sql} ({', '.join(columnas_sql)})"
    cursor.execute(create_stmt)
    conn.commit()


# =========================
# INSERT MASIVO
# =========================
df_insertar = df_rango.copy()

cursor.fast_executemany = True
cols_sql = ", ".join([f"[{c}]" for c in df_insertar.columns])
placeholders = ", ".join(["?"] * len(df_insertar.columns))
insert_stmt = f"INSERT INTO {tabla_sql} ({cols_sql}) VALUES ({placeholders})"

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

with open("log_carga_report_trk_50090.txt", "a", encoding="utf-8") as f:
    f.write(log_msg)

cursor.close()
conn.close()