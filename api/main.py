"""FastAPI backend — expone el pipeline TIC como endpoints JSON."""

import sys
from pathlib import Path
from typing import Any

import pandas as pd
from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

sys.path.insert(0, str(Path(__file__).parent.parent))

from pipeline import extract, transform, analyze
import main as pipeline_orchestrator

app = FastAPI(title="TIC Dashboard API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://estructura-five.vercel.app",  # ← agrega esto
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)

_cache: dict[str, pd.DataFrame] = {}


def _load_pipeline() -> None:
    raw_tickets = extract.load_tickets()
    raw_indicators = extract.load_indicators()
    raw_software_edu = extract.load_software_education()
    raw_software_op = extract.load_software_operational()
    raw_development = extract.load_development_activities()

    _cache["tickets"] = transform.transform_tickets(raw_tickets)
    _cache["indicators"] = transform.transform_indicators(raw_indicators)
    _cache["software_edu"] = transform.transform_software_education(raw_software_edu)
    _cache["software_op"] = transform.transform_software_operational(raw_software_op)
    _cache["development"] = transform.transform_development(raw_development)


def _data() -> dict[str, pd.DataFrame]:
    if not _cache:
        _load_pipeline()
    return _cache


def _serialize(dataframe: pd.DataFrame) -> list[dict[str, Any]]:
    df = dataframe.copy()
    for column in df.select_dtypes(include=["datetime64[ns]", "datetimetz"]).columns:
        df[column] = df[column].dt.strftime("%Y-%m-%d").where(df[column].notna(), None)
    return df.where(pd.notna(df), None).to_dict(orient="records")


# ── PIPELINE ──────────────────────────────────────────────────────────────────

@app.post("/api/pipeline/ejecutar")
def ejecutar_pipeline(background_tasks: BackgroundTasks):
    def run_and_refresh():
        pipeline_orchestrator.run()
        _cache.clear()
        _load_pipeline()

    background_tasks.add_task(run_and_refresh)
    return {"mensaje": "Pipeline iniciado en segundo plano"}


@app.get("/api/pipeline/descargar")
def descargar_reporte():
    reporte = Path(__file__).parent.parent / "reporte_infraestructura_TIC.xlsx"
    return FileResponse(
        path=str(reporte),
        filename="reporte_infraestructura_TIC.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


# ── RESUMEN ───────────────────────────────────────────────────────────────────

@app.get("/api/resumen-ejecutivo")
def resumen_ejecutivo():
    data = _data()
    result = analyze.resumen_ejecutivo(data["tickets"], data["indicators"], data["development"])
    return _serialize(result)


# ── TICKETS ───────────────────────────────────────────────────────────────────

@app.get("/api/tickets/por-estado")
def tickets_por_estado():
    return _serialize(analyze.tickets_por_estado(_data()["tickets"]))


@app.get("/api/tickets/por-topico")
def tickets_por_topico():
    return _serialize(analyze.tickets_por_topico(_data()["tickets"]))


@app.get("/api/tickets/por-empleado")
def tickets_por_empleado():
    return _serialize(analyze.tickets_por_empleado(_data()["tickets"]))


@app.get("/api/tickets/tendencia-mensual")
def tendencia_mensual_tickets():
    return _serialize(analyze.tendencia_mensual_tickets(_data()["tickets"]))


@app.get("/api/tickets/topicos-criticos")
def topicos_criticos():
    return _serialize(analyze.topicos_criticos(_data()["tickets"]))


# ── INDICADORES ───────────────────────────────────────────────────────────────

@app.get("/api/indicadores/resumen")
def resumen_indicadores():
    return _serialize(analyze.resumen_indicadores(_data()["indicators"]))


@app.get("/api/indicadores/en-riesgo")
def indicadores_en_riesgo():
    return _serialize(analyze.indicadores_en_riesgo(_data()["indicators"]))


@app.get("/api/indicadores/tendencia")
def tendencia_indicadores():
    return _serialize(analyze.tendencia_indicadores(_data()["indicators"]))


# ── SOFTWARE ──────────────────────────────────────────────────────────────────

@app.get("/api/software/licencias-por-vencer")
def licencias_por_vencer():
    return _serialize(analyze.licencias_por_vencer(_data()["software_edu"]))


@app.get("/api/software/inventario-por-campus")
def inventario_por_campus():
    return _serialize(analyze.inventario_por_campus(_data()["software_edu"]))


@app.get("/api/software/inventario-por-tipo")
def inventario_por_tipo():
    return _serialize(analyze.inventario_por_tipo_licencia(_data()["software_edu"]))


# ── DESARROLLO ────────────────────────────────────────────────────────────────

@app.get("/api/desarrollo/actividades-por-estado")
def actividades_por_estado():
    return _serialize(analyze.actividades_por_estado(_data()["development"]))


@app.get("/api/desarrollo/cuellos-de-botella")
def cuellos_de_botella():
    return _serialize(analyze.cuellos_de_botella(_data()["development"]))


@app.get("/api/desarrollo/ciclo-por-asignado")
def ciclo_por_asignado():
    return _serialize(analyze.ciclo_por_asignado(_data()["development"]))


@app.get("/api/desarrollo/tendencia-mensual")
def tendencia_mensual_desarrollo():
    return _serialize(analyze.tendencia_mensual_desarrollo(_data()["development"]))
