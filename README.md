# Pruebas

Borrador de guía para presentar el primer diseño de una casa a un cliente, con la imagen de TAUKAR Espacios.

- `index.html`: página completa. Dos opciones: A en L y B con patio interno.
- `taukar-espacios.png` y `arbol.png`: logo y árbol tomados del documento de especificaciones.
- Las notas en color madera son instrucciones para armar la página real; se ocultan con el botón de arriba y se borran antes de enviarla.

Se ve en https://handeress.github.io/Pruebas/ cuando GitHub Pages está activo (Settings → Pages → Deploy from a branch → main / root).

## PDF

`herramientas/generar_pdf.py` arma el PDF de 12 hojas (formato de las especificaciones de TAUKAR Espacios) a partir de `index.html`. Ver las notas al inicio del archivo.

## Terreno, casas e implantación (lote 10, Suesca)

- `terreno/sitio.json`: grilla de alturas cada 2 m digitalizada del plano de la parcelación (curvas cada 2 m, aproximada), lindero del lote 10, vía vehicular y vía peatonal. El terreno se ve sin color, en gris con curvas de nivel.
- `casas/A.json` y `casas/B.json`: mallas 3D de cada opción, su planta esquemática y su ubicación en el lote. Las arma `herramientas/casas.py` (A sale de `herramientas/fuentes/casa_L_geo.json`, el 3D de la casa en L; B se levanta en el script desde la variación con patio).
- Implantación: cerca de la esquina 14, con 10 m (`RETIRO`) a los linderos 14-13 y 14-17, medidos al borde de cubiertas y terrazas. El frente mira hacia donde baja el terreno (`sitio.frente`).
- El mismo script dibuja el plano del lote (general y detalle de la esquina 14) dentro de `index.html`, entre `<!--LOTE-->` y `<!--/LOTE-->`.

## Revisión de actividades (app Presupuestos)

- `revision-actividades/index.html`: lista de chequeo de las 175 actividades iniciales de la app Presupuestos, con casilla de aprobación y observación por actividad. Guarda en el celular y el botón de abajo copia el resultado para pegarlo en el chat.
- Se ve en https://handeress.github.io/Pruebas/revision-actividades/
