# Pruebas

Borrador de guía para presentar el primer diseño de una casa a un cliente, con la imagen de TAUKAR Espacios.

- `index.html`: página completa en un solo archivo. Los tres modelos 3D (opciones A, B y C) son de relleno.
- `taukar-espacios.png` y `arbol.png`: logo y árbol tomados del documento de especificaciones.
- Las notas en color madera son instrucciones para armar la página real; se ocultan con el botón de arriba y se borran antes de enviarla.

Se ve en https://handeress.github.io/Pruebas/ cuando GitHub Pages está activo (Settings → Pages → Deploy from a branch → main / root).

## PDF

`herramientas/generar_pdf.py` arma el PDF de 12 hojas (formato de las especificaciones de TAUKAR Espacios) a partir de `index.html`. Ver las notas al inicio del archivo.

## Terreno real (lote 10, Suesca)

`terreno/sitio.json` y `terreno/satelite.jpg` montan el 3D de las tres opciones sobre el terreno real: grilla de alturas cada 2 m digitalizada del plano de la parcelación (curvas cada 2 m, aproximada), foto satelital de Google Earth, lindero del lote 10, vía vehicular y vía peatonal. La casa va en el centro del lote mirando hacia abajo de la pendiente, apoyada en pedestales; el centro y el frente se cambian en `sitio.centro` y `sitio.frente`. Si los archivos no cargan, se ve el terreno plano de antes.
