"""
Descarga las ediciones anónimas de la Wikipedia en inglés (artículos) de un periodo fijo
usando la API `list=recentchanges` y las guarda en data/ediciones_wikipedia.csv.gz.

Se ejecuta una sola vez: el notebook lee el CSV resultante y lo reproduce como flujo.
La API solo conserva ~30 días de cambios recientes, por eso guardamos el CSV en el repositorio.

Nota: Wikimedia limita las peticiones (HTTP 429) desde algunas IPs de servidores en la nube.
Desde una conexión doméstica funciona sin problemas (≈250 peticiones, unos 5-10 minutos).
"""
import json, time, gzip, os, sys
import requests
import pandas as pd

API_URL = "https://en.wikipedia.org/w/api.php"
HEADERS = {"User-Agent": "ProyectoFlujosDatosUC3M/1.0 (proyecto academico; https://github.com/javiacey16/proyecto-series-temporales)"}
INICIO = "2026-10-08T00:00:00Z"     # incluido
FIN    = "2026-10-18T00:00:00Z"     # excluido -> 10 días completos
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "ediciones_wikipedia.csv.gz")


def pedir(params, intentos=8):
    for i in range(intentos):
        try:
            r = requests.get(API_URL, headers=HEADERS, params=params, timeout=60)
            if r.status_code == 200:
                return r.json()
            espera = r.headers.get("Retry-After", "")
            espera = int(espera) if espera.isdigit() else 5 * (i + 1)
            print(f"  código {r.status_code}, espero {espera}s", flush=True)
        except (requests.RequestException, ValueError) as e:
            espera = 5 * (i + 1)
            print(f"  error {type(e).__name__}, espero {espera}s", flush=True)
        time.sleep(espera)
    raise RuntimeError("La API no responde")


def descargar():
    params = {"action": "query", "list": "recentchanges", "format": "json", "formatversion": 2,
              "rcprop": "title|ids|sizes|flags|user|comment|tags|timestamp",
              "rctype": "edit|new", "rcnamespace": 0, "rcshow": "anon|!bot", "rclimit": 500,
              "rcdir": "newer", "rcstart": INICIO, "rcend": FIN}
    filas, n = [], 0
    while True:
        datos = pedir(params)
        filas += datos.get("query", {}).get("recentchanges", [])
        n += 1
        if n % 20 == 0:
            print(f"  {n} peticiones, {len(filas)} ediciones, hasta {filas[-1]['timestamp']}", flush=True)
        if "continue" not in datos:
            break
        params.update(datos["continue"])
        time.sleep(1.0)
    return filas


def a_tabla(filas):
    d = pd.DataFrame(filas)
    d = d.drop_duplicates("revid")
    out = pd.DataFrame({
        "revid": d["revid"].astype("int64"),
        "timestamp": d["timestamp"],
        "title": d["title"].fillna(""),
        "comment": d.get("comment", pd.Series("", index=d.index)).fillna(""),
        "user_es_ip": ~d["user"].fillna("").str.startswith("~"),
        "minor": d.get("minor", False).fillna(False).astype(bool),
        "new": (d["type"] == "new"),
        "oldlen": d["oldlen"].fillna(0).astype(int),
        "newlen": d["newlen"].fillna(0).astype(int),
        "revertida": d["tags"].map(lambda t: "mw-reverted" in t if isinstance(t, list) else False),
    })
    return out.sort_values(["timestamp", "revid"]).reset_index(drop=True)


if __name__ == "__main__":
    os.makedirs(os.path.dirname(SALIDA), exist_ok=True)
    t0 = time.time()
    filas = descargar()
    tabla = a_tabla(filas)
    tabla.to_csv(SALIDA, index=False, compression="gzip")
    print(f"{len(tabla)} ediciones guardadas en {SALIDA} ({time.time() - t0:.0f}s)")
