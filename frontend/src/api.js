const BASE = (import.meta.env.VITE_API_URL || "") + "/api";

async function get(path) {
  const response = await fetch(BASE + path);
  if (!response.ok) throw new Error(`Error ${response.status}: ${path}`);
  return response.json();
}

export const api = {
  resumenEjecutivo: () => get("/resumen-ejecutivo"),

  tickets: {
    porEstado: () => get("/tickets/por-estado"),
    porTopico: () => get("/tickets/por-topico"),
    porEmpleado: () => get("/tickets/por-empleado"),
    tendenciaMensual: () => get("/tickets/tendencia-mensual"),
    topicosCriticos: () => get("/tickets/topicos-criticos"),
  },

  indicadores: {
    resumen: () => get("/indicadores/resumen"),
    enRiesgo: () => get("/indicadores/en-riesgo"),
    tendencia: () => get("/indicadores/tendencia"),
  },

  software: {
    licenciasPorVencer: () => get("/software/licencias-por-vencer"),
    inventarioPorCampus: () => get("/software/inventario-por-campus"),
    inventarioPorTipo: () => get("/software/inventario-por-tipo"),
  },

  desarrollo: {
    actividadesPorEstado: () => get("/desarrollo/actividades-por-estado"),
    cuellosDeBotella: () => get("/desarrollo/cuellos-de-botella"),
    cicloPorAsignado: () => get("/desarrollo/ciclo-por-asignado"),
    tendenciaMensual: () => get("/desarrollo/tendencia-mensual"),
  },

  ejecutarPipeline: () =>
    fetch(BASE + "/pipeline/ejecutar", { method: "POST" }).then((r) => r.json()),
};
