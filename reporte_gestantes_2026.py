"""Reporte anual 2026 de gestantes (visitas domiciliarias) en Excel.

Replica mes a mes la lógica de views/c1/seguimiento_vd_ges.py (gestantes_join_df)
y genera un libro con resumen, indicadores por EESS, distribución y detalle nominal.

Uso:  python reporte_gestantes_2026.py
"""
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from utils.functions_data import gestantes_unicas_visitados
from utils.helpers import mes_short, mes_compname, validar_vd_gestante

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
CS_URL = os.getenv("CS_URL")

YEAR = "2026"
OUTPUT = os.path.join(BASE_DIR, f"reporte_gestantes_{YEAR}.xlsx")
# Desde mayo 2026 la etapa se registra sin distinguir adulta/adolescente
ETAPAS_POSITIVAS = ["Visita Domiciliaria (Adolescente)", "Visita Domiciliaria (Adulta)", "Visita Domiciliaria"]


def load_data():
    carga_df = pd.read_parquet(f"https://{CS_URL}/GESTANTE_VISITAS_DOMICILIARIAS_DATA.parquet", engine="pyarrow")
    vd_df = pd.read_parquet(f"https://{CS_URL}/GESTANTES_VISITAS_DOMICILIARIAS_DATA.parquet", engine="pyarrow")
    padron_df = pd.read_parquet(f"https://{CS_URL}/PADRON_TRUJILLO.parquet", engine="pyarrow")

    vd_df["Año"] = vd_df["Año"].astype(str)
    carga_df["Mes"] = carga_df["Mes"].astype(int)
    carga_df["Establecimiento de Salud"] = carga_df["Establecimiento de Salud"].fillna("Sin Asignar")
    return carga_df, vd_df, padron_df


def prepare_padron(padron_df, fecha_actual):
    prioridad = {"DNI": 1, "CUI": 2, "CNV": 3}
    padron_df = padron_df.copy()
    padron_df["Prioridad"] = padron_df["Tipo de Documento"].map(prioridad)
    padron_df = padron_df.sort_values(by=["Documento", "Prioridad"])
    padron_df = padron_df.drop_duplicates(subset="Documento", keep="first").drop(columns=["Prioridad"])
    padron_df["EDAD_MESES"] = padron_df["FECHA DE NACIMIENTO"].apply(
        lambda x: (fecha_actual.year - x.year) * 12 + (fecha_actual.month - x.month)
    )
    padron_df = padron_df[[
        "NUMERO DE DOCUMENTO  DE LA MADRE", "Documento", "DATOS NIÑO PADRON", "FECHA DE NACIMIENTO",
        "DIRECCION PADRON", "EESS", "EDAD_MESES",
    ]]
    return padron_df[padron_df["EDAD_MESES"] <= 12]


def build_month(mes_num, carga_df, vd_df, padron_df):
    """Devuelve (gestantes_join_df, kpis, tabla_eess) para un mes, igual que el dashboard."""
    mes = mes_short(mes_num)
    carga_filt_df = carga_df[(carga_df["Año"] == YEAR) & (carga_df["Mes"] == mes_num)]
    actvd = vd_df[(vd_df["Año"] == YEAR) & (vd_df["Mes"] == mes)]
    vd_movil_df = actvd[actvd["Dispositivo Intervención"] == "MOVIL"]
    vd_web_df = actvd[actvd["Dispositivo Intervención"] == "WEB"]

    num_carga = carga_filt_df.shape[0]
    num_vd_prog = carga_filt_df["Total de visitas completas para la edad"].sum()

    gest_unicas = gestantes_unicas_visitados(actvd, "Número de Documento", "ALL GESTANTE W DUPLICADOS")
    num_gest_vd = gest_unicas.shape[0]
    gest_unicas.columns = ["Doc_gestante", "Actor Social Ultimo Mes", "Etapa", "Número Visitas"]
    gest_unicas = gest_unicas[["Doc_gestante", "Etapa", "Número Visitas"]]

    gest_dff = pd.merge(carga_filt_df, padron_df, left_on="Número de Documento",
                        right_on="NUMERO DE DOCUMENTO  DE LA MADRE", how="left")
    gest_dff["Estado Gestante"] = gest_dff["Total de VD presenciales Válidas"].apply(validar_vd_gestante)

    carpeta = os.path.join(BASE_DIR, "data", "puerperas", mes)
    archivos = [f for f in os.listdir(carpeta) if f.endswith(".parquet")] if os.path.isdir(carpeta) else []
    if archivos:
        puerp = pd.concat([pd.read_parquet(os.path.join(carpeta, a)) for a in archivos], ignore_index=True)
        puerp = puerp.drop_duplicates(subset="Número de Documento", keep="first").set_index("Número de Documento")
        en_puerp = gest_dff["Número de Documento"].isin(puerp.index)
        gest_dff.loc[en_puerp, "EDAD_MESES"] = gest_dff.loc[en_puerp, "Número de Documento"].map(puerp["EDAD_MESES"])
        gest_dff.loc[en_puerp, "FECHA DE NACIMIENTO"] = gest_dff.loc[en_puerp, "Número de Documento"].map(puerp["FECHA DE NACIMIENTO"])

    gest_dff["ESTADO_NACIMIENTO"] = gest_dff["FECHA DE NACIMIENTO"].apply(lambda f: "GESTANTE" if pd.isna(f) else "PUERPERA")
    gest_dff = gest_dff.rename(columns={"FECHA DE NACIMIENTO": "Fecha Nacimiento Hijo", "EDAD_MESES": "Edad en Meses Hijo"})
    join = pd.merge(gest_dff, gest_unicas, left_on="Número de Documento", right_on="Doc_gestante", how="left")
    join["Etapa"] = join["Etapa"].fillna("No Visitadas")

    # El cruce con el padrón duplica madres con más de un hijo: los conteos se hacen por gestante única
    unicas = join.drop_duplicates(subset="Número de Documento")
    completas = (unicas["Estado Gestante"] == "Visita Completa").sum()
    con_cel = unicas["Celular de la Madre"].notna().sum()
    kpis = {
        "Mes": mes_compname(mes_num),
        "Gestantes Cargadas": num_carga,
        "Gestantes Visitadas": num_gest_vd,
        "Gestantes Sin Visita": num_carga - num_gest_vd,
        "VD Programadas": num_vd_prog,
        "Visitas Totales": actvd.shape[0],
        "Visitas Móvil": vd_movil_df.shape[0],
        "Visitas Web": vd_web_df.shape[0],
        "% VD Georreferenciadas": vd_movil_df.shape[0] / num_vd_prog if num_vd_prog else 0,
        "Meta VD (75%)": round(num_vd_prog * 0.75),
        "% Registro Telefónico": con_cel / num_carga if num_carga else 0,
        "Gestantes VD Completa": completas,
        "% Oportunos y Completos": completas / num_carga if num_carga else 0,
        "Gestantes con VD Efectiva": unicas["Etapa"].isin(ETAPAS_POSITIVAS).sum(),
        "Puérperas": (unicas["ESTADO_NACIMIENTO"] == "PUERPERA").sum(),
    }

    # Tabla por EESS (mismo cálculo que gestantes_tabla_df del dashboard)
    tabla = join.drop_duplicates(subset="Número de Documento").groupby("Establecimiento de Salud").agg(
        **{"Gestantes Programadas": ("Número de Documento", "count"),
           "Visitas Programadas": ("Total de visitas completas para la edad", "sum")}
    ).reset_index()
    tabla["Establecimiento de Salud"] = tabla["Establecimiento de Salud"].str[11:]
    geo = vd_movil_df.groupby("Establecimiento de Salud").size().rename("Visitas Realizadas GEO")
    web = vd_web_df.groupby("Establecimiento de Salud").size().rename("Visitas Realizadas WEB")
    tabla = tabla.merge(geo, on="Establecimiento de Salud", how="left").merge(web, on="Establecimiento de Salud", how="left")
    tabla[["Visitas Realizadas GEO", "Visitas Realizadas WEB"]] = tabla[["Visitas Realizadas GEO", "Visitas Realizadas WEB"]].fillna(0).astype(int)
    tabla["Visitas Realizadas"] = tabla["Visitas Realizadas GEO"] + tabla["Visitas Realizadas WEB"]
    tabla = tabla.sort_values("Gestantes Programadas", ascending=False)
    tabla.insert(0, "Mes", mes_compname(mes_num))

    join = join.drop(columns=["Mes"])
    join.insert(0, "Mes", mes_compname(mes_num))
    join.insert(0, "N° Mes", mes_num)
    return join, kpis, tabla


# ----------------------------------------------------------------------------- Excel
NAVY, TEAL, TEAL_LIGHT, GREY, WHITE = "#1F3B57", "#1A8C8C", "#E3F2F1", "#F4F6F8", "#FFFFFF"
SERIES = ["#1A8C8C", "#E07A5F", "#3D5A80", "#F2CC8F", "#81B29A", "#9C6ADE"]


def make_formats(wb):
    f = {}
    f["title"] = wb.add_format({"bold": True, "font_size": 20, "font_color": NAVY})
    f["subtitle"] = wb.add_format({"italic": True, "font_size": 10, "font_color": "#6B7785"})
    f["section"] = wb.add_format({"bold": True, "font_size": 13, "font_color": WHITE, "bg_color": NAVY, "indent": 1, "valign": "vcenter"})
    f["header"] = wb.add_format({"bold": True, "font_color": WHITE, "bg_color": TEAL, "border": 1, "border_color": WHITE,
                                 "align": "center", "valign": "vcenter", "text_wrap": True})
    base = {"border": 1, "border_color": "#D5DBE1", "valign": "vcenter"}
    f["text"] = wb.add_format(base)
    f["int"] = wb.add_format({**base, "num_format": "#,##0", "align": "center"})
    f["pct"] = wb.add_format({**base, "num_format": "0.0%", "align": "center"})
    f["total_text"] = wb.add_format({**base, "bold": True, "bg_color": TEAL_LIGHT})
    f["total_int"] = wb.add_format({**base, "bold": True, "bg_color": TEAL_LIGHT, "num_format": "#,##0", "align": "center"})
    f["total_pct"] = wb.add_format({**base, "bold": True, "bg_color": TEAL_LIGHT, "num_format": "0.0%", "align": "center"})
    f["card_label"] = wb.add_format({"font_size": 9, "font_color": "#6B7785", "bg_color": GREY, "align": "center",
                                     "valign": "bottom", "text_wrap": True, "top": 5, "top_color": TEAL})
    f["card_value"] = wb.add_format({"bold": True, "font_size": 22, "font_color": NAVY, "bg_color": GREY, "align": "center",
                                     "valign": "vcenter", "num_format": "#,##0"})
    f["card_pct"] = wb.add_format({"bold": True, "font_size": 22, "font_color": NAVY, "bg_color": GREY, "align": "center",
                                   "valign": "vcenter", "num_format": "0.0%"})
    f["note"] = wb.add_format({"font_size": 9, "italic": True, "font_color": "#6B7785", "text_wrap": True, "valign": "top"})
    return f


def write_table(ws, f, row, col, df, fmts, total=None):
    """Escribe df con encabezado; fmts: formato por columna ('text'|'int'|'pct'). Devuelve última fila."""
    ws.set_row(row, 32)
    for j, c in enumerate(df.columns):
        ws.write(row, col + j, c, f["header"])
    for i, rec in enumerate(df.itertuples(index=False), start=1):
        for j, v in enumerate(rec):
            ws.write(row + i, col + j, v, f[fmts[j]])
    last = row + len(df)
    if total is not None:
        last += 1
        for j, v in enumerate(total):
            ws.write(last, col + j, v, f["total_" + fmts[j]])
    return last


def sheet_resumen(wb, f, kpis_df, gen_date):
    ws = wb.add_worksheet("Resumen")
    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 14)
    ws.set_column("C:P", 14)
    ws.write("B2", f"Reporte Anual de Gestantes {YEAR} — Visitas Domiciliarias", f["title"])
    meses = f"{kpis_df['Mes'].iloc[0]} – {kpis_df['Mes'].iloc[-1]}"
    ws.write("B3", f"Periodo: {meses} {YEAR}   ·   Generado: {gen_date:%d/%m/%Y %H:%M}", f["subtitle"])

    tot = kpis_df.sum(numeric_only=True)
    vd_prog = tot["VD Programadas"]
    cards = [
        ("Gestantes cargadas\n(suma mensual)", tot["Gestantes Cargadas"], "card_value"),
        ("Visitas realizadas", tot["Visitas Totales"], "card_value"),
        ("VD programadas", vd_prog, "card_value"),
        ("% VD georreferenciadas", tot["Visitas Móvil"] / vd_prog if vd_prog else 0, "card_pct"),
        ("% Oportunos y completos", tot["Gestantes VD Completa"] / tot["Gestantes Cargadas"], "card_pct"),
        ("% Registro telefónico", (kpis_df["% Registro Telefónico"] * kpis_df["Gestantes Cargadas"]).sum() / tot["Gestantes Cargadas"], "card_pct"),
    ]
    for i, (label, value, fmt) in enumerate(cards):
        c = 1 + i * 2
        ws.set_row(4, 30)
        ws.set_row(5, 38)
        ws.merge_range(4, c, 4, c + 1, label, f["card_label"])
        ws.merge_range(5, c, 5, c + 1, value, f[fmt])

    ws.set_row(7, 22)
    ws.merge_range(7, 1, 7, 15, "Indicadores mensuales", f["section"])
    cols = list(kpis_df.columns)
    fmts = ["text"] + ["pct" if c.startswith("%") else "int" for c in cols[1:]]
    total = ["TOTAL"]
    for c in cols[1:]:
        if c == "% VD Georreferenciadas":
            total.append(tot["Visitas Móvil"] / vd_prog if vd_prog else 0)
        elif c == "% Registro Telefónico":
            total.append(cards[5][1])
        elif c == "% Oportunos y Completos":
            total.append(cards[4][1])
        else:
            total.append(tot[c])
    first = 8
    last = write_table(ws, f, first, 1, kpis_df, fmts, total)
    ws.set_row(first, 45)
    n = len(kpis_df)
    for c in ("% VD Georreferenciadas", "% Oportunos y Completos", "% Registro Telefónico"):
        j = 1 + cols.index(c)
        ws.conditional_format(first + 1, j, first + n, j, {"type": "data_bar", "bar_color": "#7CC4C4", "bar_solid": True, "min_type": "num", "min_value": 0})

    # Gráficos
    cat = ["Resumen", first + 1, 1, first + n, 1]
    ref = lambda name: ["Resumen", first + 1, 1 + cols.index(name), first + n, 1 + cols.index(name)]
    chart_row = last + 3

    ch1 = wb.add_chart({"type": "column"})
    for k, name in enumerate(["Gestantes Cargadas", "Gestantes Visitadas", "Gestantes VD Completa"]):
        ch1.add_series({"name": name, "categories": cat, "values": ref(name), "fill": {"color": SERIES[k]},
                        "data_labels": {"value": True, "font": {"size": 8}}, "gap": 80})
    ch1.set_title({"name": "Gestantes por mes", "name_font": {"size": 12, "color": NAVY}})
    ch1.set_legend({"position": "bottom"})
    ch1.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E5E8EB"}}})
    ch1.set_size({"width": 620, "height": 330})
    ch1.set_chartarea({"border": {"none": True}})
    ws.insert_chart(chart_row, 1, ch1)

    ch2 = wb.add_chart({"type": "line"})
    for k, name in enumerate(["% VD Georreferenciadas", "% Oportunos y Completos", "% Registro Telefónico"]):
        ch2.add_series({"name": name, "categories": cat, "values": ref(name),
                        "line": {"color": SERIES[k], "width": 2.5},
                        "marker": {"type": "circle", "size": 6, "fill": {"color": SERIES[k]}, "border": {"color": SERIES[k]}},
                        "data_labels": {"value": True, "position": "above", "num_format": "0%", "font": {"size": 8}}})
    ch2.set_title({"name": "Indicadores (%) por mes", "name_font": {"size": 12, "color": NAVY}})
    ch2.set_legend({"position": "bottom"})
    ch2.set_y_axis({"num_format": "0%", "min": 0, "major_gridlines": {"visible": True, "line": {"color": "#E5E8EB"}}})
    ch2.set_size({"width": 620, "height": 330})
    ch2.set_chartarea({"border": {"none": True}})
    ws.insert_chart(chart_row, 9, ch2)

    ch3 = wb.add_chart({"type": "column", "subtype": "stacked"})
    for k, name in enumerate(["Visitas Móvil", "Visitas Web"]):
        ch3.add_series({"name": name, "categories": cat, "values": ref(name), "fill": {"color": SERIES[k + 2]}, "gap": 60})
    line = wb.add_chart({"type": "line"})
    line.add_series({"name": "VD Programadas", "categories": cat, "values": ref("VD Programadas"),
                     "line": {"color": SERIES[1], "width": 2, "dash_type": "dash"}, "marker": {"type": "none"}})
    ch3.combine(line)
    ch3.set_title({"name": "Visitas realizadas vs programadas", "name_font": {"size": 12, "color": NAVY}})
    ch3.set_legend({"position": "bottom"})
    ch3.set_y_axis({"major_gridlines": {"visible": True, "line": {"color": "#E5E8EB"}}})
    ch3.set_size({"width": 620, "height": 330})
    ch3.set_chartarea({"border": {"none": True}})
    ws.insert_chart(chart_row + 18, 1, ch3)

    note_row = chart_row + 18
    ws.merge_range(note_row, 9, note_row + 10, 15,
                   "Notas:\n"
                   "• % VD Georreferenciadas = visitas móvil / VD programadas (meta 75%).\n"
                   "• % Oportunos y completos = gestantes con 2+ VD presenciales válidas / gestantes cargadas.\n"
                   "• Gestantes Visitadas = gestantes únicas con al menos una intervención en el mes.\n"
                   "• VD Efectiva = última etapa 'Visita Domiciliaria' (no incluye No Encontrado/Rechazado).\n"
                   "• El total anual de gestantes es la suma de las cargas mensuales (una gestante puede repetirse entre meses).\n"
                   f"• El mes en curso ({kpis_df['Mes'].iloc[-1]}) tiene datos parciales.",
                   f["note"])
    ws.freeze_panes(first + 1, 2)


def sheet_eess(wb, f, tabla_all, meses):
    ws = wb.add_worksheet("Por EESS")
    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 46)
    ws.set_column("C:Z", 11)
    ws.write("B2", "Indicadores por Establecimiento de Salud", f["title"])

    # Matriz % GEO por EESS x mes
    t = tabla_all.copy()
    piv_geo = t.pivot_table(index="Establecimiento de Salud", columns="Mes", values="Visitas Realizadas GEO", aggfunc="sum")
    piv_prog = t.pivot_table(index="Establecimiento de Salud", columns="Mes", values="Visitas Programadas", aggfunc="sum")
    piv_ges = t.pivot_table(index="Establecimiento de Salud", columns="Mes", values="Gestantes Programadas", aggfunc="sum")
    piv_geo, piv_prog, piv_ges = (p.reindex(columns=meses) for p in (piv_geo, piv_prog, piv_ges))
    order = piv_ges.sum(axis=1).sort_values(ascending=False).index
    pct = (piv_geo / piv_prog).reindex(order)

    row = 3
    ws.set_row(row, 22)
    ws.merge_range(row, 1, row, 1 + len(meses) + 1, "% VD georreferenciadas (Visitas móvil / VD programadas)", f["section"])
    row += 1
    ws.set_row(row, 28)
    ws.write(row, 1, "Establecimiento de Salud", f["header"])
    for j, m in enumerate(meses):
        ws.write(row, 2 + j, m, f["header"])
    ws.write(row, 2 + len(meses), "Año", f["header"])
    for i, eess in enumerate(order, start=1):
        ws.write(row + i, 1, eess, f["text"])
        for j, m in enumerate(meses):
            v = pct.loc[eess, m]
            ws.write(row + i, 2 + j, None if pd.isna(v) else v, f["pct"])
        anual = piv_geo.loc[eess].sum() / piv_prog.loc[eess].sum() if piv_prog.loc[eess].sum() else 0
        ws.write(row + i, 2 + len(meses), anual, f["total_pct"])
    ws.conditional_format(row + 1, 2, row + len(order), 2 + len(meses), {
        "type": "3_color_scale", "min_color": "#F4A6A6", "mid_color": "#FCE7A8", "max_color": "#8CD3B0",
        "min_type": "num", "min_value": 0, "mid_type": "num", "mid_value": 0.5, "max_type": "num", "max_value": 0.75})
    row += len(order) + 3

    # Gestantes cargadas por EESS x mes
    ws.set_row(row, 22)
    ws.merge_range(row, 1, row, 1 + len(meses) + 1, "Gestantes cargadas por mes", f["section"])
    row += 1
    ws.set_row(row, 28)
    ws.write(row, 1, "Establecimiento de Salud", f["header"])
    for j, m in enumerate(meses):
        ws.write(row, 2 + j, m, f["header"])
    ws.write(row, 2 + len(meses), "Total", f["header"])
    ges = piv_ges.reindex(order).fillna(0).astype(int)
    for i, eess in enumerate(order, start=1):
        ws.write(row + i, 1, eess, f["text"])
        for j, m in enumerate(meses):
            ws.write(row + i, 2 + j, ges.loc[eess, m], f["int"])
        ws.write(row + i, 2 + len(meses), ges.loc[eess].sum(), f["total_int"])
    tr = row + len(order) + 1
    ws.write(tr, 1, "TOTAL", f["total_text"])
    for j, m in enumerate(meses):
        ws.write(tr, 2 + j, ges[m].sum(), f["total_int"])
    ws.write(tr, 2 + len(meses), ges.values.sum(), f["total_int"])
    ws.conditional_format(row + 1, 2, row + len(order), 1 + len(meses), {"type": "2_color_scale", "min_color": "#FFFFFF", "max_color": "#7CC4C4"})
    row = tr + 3

    # Detalle mensual (tabla del dashboard)
    ws.set_row(row, 22)
    ws.merge_range(row, 1, row, 9, "Detalle mensual por EESS", f["section"])
    row += 1
    det = tabla_all[["Establecimiento de Salud", "Mes", "Gestantes Programadas", "Visitas Programadas",
                     "Visitas Realizadas GEO", "Visitas Realizadas WEB", "Visitas Realizadas"]].copy()
    det["% Actual GEO"] = (det["Visitas Realizadas GEO"] / det["Visitas Programadas"]).fillna(0)
    det_fmts = ["text", "text", "int", "int", "int", "int", "int", "pct"]
    ws.set_row(row, 45)
    for j, c in enumerate(det.columns):
        ws.write(row, 1 + j, c, f["header"])
    r = row
    for mes, g in det.groupby("Mes", sort=False):
        for rec in g.itertuples(index=False):
            r += 1
            for j, v in enumerate(rec):
                ws.write(r, 1 + j, v, f[det_fmts[j]])
        r += 1
        s = g.sum(numeric_only=True)
        ws.write(r, 1, f"TOTAL {mes.upper()}", f["total_text"])
        ws.write(r, 2, mes, f["total_text"])
        for j, c in enumerate(det.columns[2:], start=3):
            val = (s["Visitas Realizadas GEO"] / s["Visitas Programadas"] if s["Visitas Programadas"] else 0) if c == "% Actual GEO" else s[c]
            ws.write(r, j, val, f["total_pct" if c.startswith("%") else "total_int"])
    ws.conditional_format(row + 1, 8, r, 8, {"type": "data_bar", "bar_color": "#7CC4C4", "bar_solid": True, "min_type": "num", "min_value": 0, "max_type": "num", "max_value": 1})


def sheet_distribucion(wb, f, join_all, meses):
    ws = wb.add_worksheet("Etapa y Estado")
    ws.hide_gridlines(2)
    ws.set_column("A:A", 2)
    ws.set_column("B:B", 36)
    ws.set_column("C:L", 11)
    ws.write("B2", "Distribución de gestantes por etapa de visita y estado", f["title"])

    def block(row, title, col, chart_title, anchor):
        piv = join_all.drop_duplicates(subset=["Mes", "Número de Documento"]).pivot_table(index=col, columns="Mes", values="Número de Documento", aggfunc="count").reindex(columns=meses).fillna(0).astype(int)
        piv["Total"] = piv.sum(axis=1)
        piv = piv.sort_values("Total", ascending=False)
        ws.set_row(row, 22)
        ws.merge_range(row, 1, row, 2 + len(meses), title, f["section"])
        df = piv.reset_index()
        total = ["TOTAL"] + [int(df[c].sum()) for c in df.columns[1:]]
        last = write_table(ws, f, row + 1, 1, df, ["text"] + ["int"] * (len(df.columns) - 1), total)
        ch = wb.add_chart({"type": "column", "subtype": "percent_stacked"})
        for k in range(len(piv)):
            ch.add_series({"name": ["Etapa y Estado", row + 2 + k, 1],
                           "categories": ["Etapa y Estado", row + 1, 2, row + 1, 1 + len(meses)],
                           "values": ["Etapa y Estado", row + 2 + k, 2, row + 2 + k, 1 + len(meses)],
                           "fill": {"color": SERIES[k % len(SERIES)]}, "gap": 50})
        ch.set_title({"name": chart_title, "name_font": {"size": 12, "color": NAVY}})
        ch.set_legend({"position": "bottom"})
        ch.set_y_axis({"num_format": "0%"})
        ch.set_size({"width": 560, "height": 300})
        ch.set_chartarea({"border": {"none": True}})
        ws.insert_chart(anchor, 2 + len(meses) + 2, ch)
        return last

    last = block(3, "Gestantes por etapa de visita", "Etapa", "Etapa de visita por mes", 3)
    last = block(max(last + 3, 20), "Gestantes vs puérperas", "ESTADO_NACIMIENTO", "Estado por mes", max(last + 3, 20))
    last = block(max(last + 3, 37), "Estado de visita (2+ VD válidas = completa)", "Estado Gestante", "Estado de visita por mes", max(last + 3, 37))
    block(max(last + 3, 54), "Tipo de documento", "Tipo de Documento", "Tipo de documento por mes", max(last + 3, 54))


def sheet_detalle(wb, f, join_all):
    ws = wb.add_worksheet("Detalle Nominal")
    df = join_all.drop(columns=["Doc_gestante", "update"], errors="ignore").copy()
    for c in df.columns:
        if isinstance(df[c].dtype, pd.DatetimeTZDtype):
            df[c] = df[c].dt.tz_localize(None)
    df = df.astype(object).where(df.notna(), None)
    date_fmt = wb.add_format({"num_format": "dd/mm/yyyy"})
    ws.add_table(0, 0, len(df), len(df.columns) - 1, {
        "data": df.values.tolist(),
        "columns": [{"header": c, "format": date_fmt if pd.api.types.is_datetime64_any_dtype(join_all[c]) else None} for c in df.columns],
        "style": "Table Style Medium 2",
        "name": "DetalleGestantes",
    })
    for j, c in enumerate(df.columns):
        sample = df[c].dropna().astype(str).head(200)
        width = min(max([len(c)] + [len(s) for s in sample]) + 2, 45)
        ws.set_column(j, j, width)
    ws.set_row(0, 30)
    ws.freeze_panes(1, 4)


def main():
    gen_date = datetime.now()
    carga_df, vd_df, padron_df = load_data()
    padron_df = prepare_padron(padron_df, gen_date)
    meses_num = sorted(carga_df.loc[carga_df["Año"] == YEAR, "Mes"].unique())

    joins, kpis, tablas = [], [], []
    for m in meses_num:
        j, k, t = build_month(m, carga_df, vd_df, padron_df)
        joins.append(j); kpis.append(k); tablas.append(t)
        print(f"{k['Mes']}: {k['Gestantes Cargadas']} gestantes, {k['Visitas Totales']} visitas")

    join_all = pd.concat(joins, ignore_index=True)
    kpis_df = pd.DataFrame(kpis)
    tabla_all = pd.concat(tablas, ignore_index=True)
    meses = [mes_compname(m) for m in meses_num]

    with pd.ExcelWriter(OUTPUT, engine="xlsxwriter") as writer:
        wb = writer.book
        f = make_formats(wb)
        sheet_resumen(wb, f, kpis_df, gen_date)
        sheet_eess(wb, f, tabla_all, meses)
        sheet_distribucion(wb, f, join_all, meses)
        sheet_detalle(wb, f, join_all)
    print(f"Reporte generado: {OUTPUT}")


if __name__ == "__main__":
    main()
