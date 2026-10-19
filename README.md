# Proyecto de Flujos de Datos · Wikipedia

**Aprendizaje Automático en Series Temporales y Flujos de Datos** · Máster en IA Aplicada (UC3M), curso 2026/27

Sistema que, para cada edición anónima de la Wikipedia en inglés, estima el riesgo de que acabe revertida, aprendiendo en flujo con [River](https://riverml.xyz), y que vigila la aparición de *data drift* y *concept drift*.

## Contenido

| Fichero | Qué es |
|---|---|
| `proyecto_flujos_wikipedia.ipynb` | Notebook principal (introducción, estado del arte, desarrollo, conclusiones) |
| `data/ediciones_wikipedia.csv.gz` | 122.679 ediciones anónimas del 8 al 17 de octubre de 2026 (UTC) con su etiqueta `revertida` |
| `descargar_datos.py` | Script que genera el CSV a partir de la API `list=recentchanges` de Wikipedia |

## Cómo ejecutarlo

```bash
pip install river pandas numpy matplotlib scipy
jupyter notebook proyecto_flujos_wikipedia.ipynb
```

En Google Colab basta con abrir el notebook: instala River y descarga el CSV del repositorio si no está en local. La ejecución completa tarda unos 6–8 minutos.

> El CSV se incluye porque la API de Wikipedia solo conserva unos 30 días de historial: así el trabajo es reproducible.
