# Genera el PDF "Casa_Suesca_primer_diseno_revN.pdf" (12 hojas de 720 x 540 pt) a partir de index.html.
# Abre la página con Chrome sin ventana, captura el 3D de cada opción, toma plantas, croquis y datos,
# arma las hojas con el formato de las especificaciones de TAUKAR Espacios y las imprime a PDF.
# Requiere: python3, playwright y Google Chrome. Ajustar las rutas /home/claude/... al sitio donde se clone el repo.
# Uso: python3 herramientas/generar_pdf.py   (deja slides.html y el PDF en la carpeta de trabajo /home/claude/pdfgen)
import asyncio, base64, json, html
from playwright.async_api import async_playwright
ARGS=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader","--ignore-gpu-blocklist","--no-sandbox"]
def b64(path, mime):
    return "data:%s;base64,%s"%(mime, base64.b64encode(open(path,'rb').read()).decode())
FD="/usr/share/fonts/truetype/google-fonts/"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=ARGS)
        pg = await b.new_page(viewport={"width":900,"height":1000}, device_scale_factor=2)
        await pg.goto("file:///home/claude/pruebas/index.html", wait_until="load")
        await pg.wait_for_timeout(800)
        await pg.evaluate("""()=>{window.__modelo.E.auto=false;document.body.classList.add('sin-guia');
          document.querySelector('.controles').style.visibility='hidden';document.getElementById('pista').style.display='none';
          const c=document.getElementById('modelo');c.style.height='640px';c.style.maxHeight='640px';window.dispatchEvent(new Event('resize'));}""")
        data={}
        OPC=await pg.evaluate("OPC")
        for op in "ABC":
            await pg.evaluate(f"document.querySelector('.selector button[data-op=\"{op}\"]').click()")
            await pg.evaluate("(()=>{const m=window.__modelo;m.meta.dist=15.5;m.E.dist=15.5;m.pide();})()")
            await pg.wait_for_timeout(600)
            cv=await pg.query_selector("#modelo"); await cv.scroll_into_view_if_needed(); await pg.wait_for_timeout(200)
            await cv.screenshot(path=f"p_{op}.png")
            plano=await pg.evaluate("document.getElementById('plano').innerHTML")
            await pg.evaluate("(()=>{document.getElementById('bArriba').click();const m=window.__modelo;m.meta.dist=17;m.pide();})()"); await pg.wait_for_timeout(2600)
            await cv.screenshot(path=f"t_{op}.png")
            await pg.evaluate("document.getElementById('bArriba').click();document.getElementById('bCubierta').click()"); await pg.wait_for_timeout(2600)
            data[op]={"plano":plano}
        bloques=await pg.evaluate("document.getElementById('bloques').innerHTML")
        det=await pg.evaluate("document.querySelector('#determinantes .croquis').innerHTML")
        bio=await pg.evaluate("document.querySelector('#bioclimatica .croquis').innerHTML")
        pres=await pg.evaluate("Array.from(document.querySelectorAll('#presentacion > p:not(.guia)')).map(e=>e.textContent)")
        prog=await pg.evaluate("Array.from(document.querySelectorAll('.programa li')).map(e=>e.textContent)")
        detp=await pg.evaluate("document.querySelector('#determinantes > p:not(.guia)').textContent")
        biop=await pg.evaluate("document.querySelector('#bioclimatica > p:not(.guia)').textContent")
        fecha=await pg.evaluate("document.querySelector('.ficha li').textContent")
        await pg.close()

        FONDO={"A":"#E3EACF","B":"#E9E6D2","C":"#DFE3E1"}; AC={"A":"#424D22","B":"#7B7C52","C":"#595959"}
        logo=b64("/home/claude/pruebas/taukar-espacios.png","image/png"); arbol=b64("/home/claude/pruebas/arbol.png","image/png")
        def cab(t,sub=""):
            return f'''<img class="arb" src="{arbol}"><div class="cab"><div class="l1"><span class="sq"><i></i><i></i></span><b>CASA EN SUESCA</b></div><div class="l2"><i></i><span>PRIMER DISEÑO</span></div></div>
<div class="tit"><div class="t">{t}</div><div class="st">{sub}</div></div>'''
        S=[]
        # 1 portada
        S.append(f'''<section class="s portada"><div class="panel"></div><img class="arbg" src="{arbol}">
<div class="pt"><h1>CASA EN<br>SUESCA</h1><p class="pd">Primer diseño:</p><ol><li>Determinantes de la implantación</li><li>Opciones de diseño</li><li>Sostenibilidad y bioclimática</li></ol><p class="fe">{fecha}</p></div>
<div class="con">proyectos@arqteka.com<br>Cra 13 N. 93 – 53<br>Cel 3159762675</div><img class="lg" src="{logo}"></section>''')
        # 2 presentación + programa
        S.append(f'''<section class="s">{cab("Presentación","Programa del proyecto")}<div class="cuerpo dos">
<div><h3>Presentación</h3>{"".join("<p>"+html.escape(x)+"</p>" for x in pres)}</div>
<div><h3>Programa del proyecto</h3><ul class="prog">{"".join("<li>"+html.escape(x)+"</li>" for x in prog)}</ul></div></div></section>''')
        # 3 determinantes
        S.append(f'''<section class="s">{cab("Determinantes de la implantación","Comunes a las tres opciones")}<div class="cuerpo"><p class="intro">{html.escape(detp)}</p><div class="croq c2">{det}</div></div></section>''')
        # 4 bloques
        S.append(f'''<section class="s">{cab("Determinantes aplicados","Vista de bloques, opción en L")}<div class="cuerpo blo"><div class="bl">{bloques}</div>
<ul class="ley"><li><i style="background:#ABAC8A"></i>Social</li><li><i style="background:#C9D6A8"></i>Privado</li><li><i style="background:#CFCFCF"></i>Servicios</li><li><i style="background:#E3C79D"></i>Terraza</li></ul></div></section>''')
        # 5-10 opciones
        for op in "ABC":
            d=OPC[op]; n=d["nombre"]
            filas="".join(f'<tr><td class="n">{i+1}</td><td>{html.escape(e[0])}</td><td class="r">{e[1]} m²</td></tr>' for i,e in enumerate(d["esp"]))
            filas+=f'<tr class="tot"><td></td><td>Área total</td><td class="r">{d["total"]} m²</td></tr><tr class="inv"><td></td><td>Presupuesto aproximado</td><td class="r">$ 000000</td></tr><tr class="inv"><td></td><td>Valor del m²</td><td class="r">$ 000000</td></tr>'
            S.append(f'''<section class="s" style="--f:{FONDO[op]};--a:{AC[op]}">{cab("Opción "+op+", "+n[0].lower()+n[1:],"Volumen y áreas")}<div class="cuerpo op">
<div class="izq"><p class="lema">{html.escape(d["texto"])}</p><img class="m3d" src="{b64(f"p_{op}.png","image/png")}"></div>
<div class="der"><table class="ar">{filas}</table></div></div></section>''')
            S.append(f'''<section class="s" style="--f:{FONDO[op]};--a:{AC[op]}">{cab("Opción "+op+", "+n[0].lower()+n[1:],"Planta")}<div class="cuerpo op pl">
<div class="izq"><div class="plano">{data[op]["plano"]}</div></div>
<div class="der"><img class="m3d" src="{b64(f"t_{op}.png","image/png")}"><p class="vive">{html.escape(d["vive"])}</p><p class="nota">Los números de la planta son los de la tabla de áreas.</p></div></div></section>''')
        # 11 comparativo
        rows=[("Área total",lambda x:x["total"]+" m²"),("Frente",lambda x:x["frente"]+" m"),("Presupuesto aproximado",lambda x:"$ 000000"),("Valor del m²",lambda x:"$ 000000"),("Lo mejor",lambda x:html.escape(x["mejor"])),("Sacrifica",lambda x:html.escape(x["sacrifica"]))]
        th="".join(f'<th style="background:{FONDO[k]}"><b>{k}</b><span>{OPC[k]["nombre"]}</span></th>' for k in "ABC")
        tb="".join("<tr><th>"+r[0]+"</th>"+"".join(f'<td style="background:{FONDO[k]}66">{r[1](OPC[k])}</td>' for k in "ABC")+"</tr>" for r in rows)
        S.append(f'''<section class="s">{cab("Las tres, lado a lado","Comparativo")}<div class="cuerpo"><table class="cmp"><thead><tr><th></th>{th}</tr></thead><tbody>{tb}</tbody></table></div></section>''')
        # 12 bioclimática
        S.append(f'''<section class="s">{cab("Sostenibilidad y bioclimática","Comunes a las tres opciones")}<div class="cuerpo"><p class="intro">{html.escape(biop)}</p><div class="croq c3">{bio}</div></div></section>''')

        css=f'''
@font-face{{font-family:P;font-weight:300;src:url("file://{FD}Poppins-Light.ttf")}}
@font-face{{font-family:P;font-weight:400;src:url("file://{FD}Poppins-Regular.ttf")}}
@font-face{{font-family:P;font-weight:500;src:url("file://{FD}Poppins-Medium.ttf")}}
@page{{size:720pt 540pt;margin:0}}
*{{box-sizing:border-box}} html,body{{margin:0}}
body{{font-family:P,sans-serif;font-weight:300;color:#595959;font-size:11pt;line-height:1.5;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
.s{{width:720pt;height:540pt;position:relative;overflow:hidden;page-break-after:always;background:linear-gradient(100deg,#E3EACF 0%,#F3F6E8 42%,#fff 68%)}}
.arb{{position:absolute;right:6pt;bottom:0;height:500pt;opacity:.16;mix-blend-mode:multiply}}
.cab{{position:absolute;left:4pt;top:6pt;width:352pt;height:62pt;background:rgba(255,255,255,.78);padding:9pt 0 0 6pt}}
.cab .l1{{display:flex;align-items:center;gap:5pt}} .cab .sq i{{display:block;width:8pt;height:8pt;background:#ABAC8A;margin-bottom:3pt}} .cab .sq i:last-child{{margin:0}}
.cab b{{font-weight:400;font-size:16pt;letter-spacing:.22em;color:#595959}}
.cab .l2{{display:flex;align-items:center;gap:14pt;margin-top:7pt}} .cab .l2 i{{width:58pt;height:8pt;background:#ABAC8A}} .cab .l2 span{{font-size:8.5pt;letter-spacing:.5em;color:#ABAC8A;font-weight:400}}
.tit{{position:absolute;right:30pt;top:22pt;text-align:right}} .tit .t{{display:inline-block;font-size:12.5pt;border-bottom:2pt solid #ABAC8A;padding:0 4pt 3pt 22pt;color:#595959}} .tit .st{{font-size:10.5pt;margin-top:4pt;padding-right:4pt}}
.cuerpo{{position:absolute;left:36pt;right:36pt;top:92pt;bottom:26pt}}
h3{{margin:0 0 8pt;font-weight:400;font-size:11pt;letter-spacing:.24em;text-transform:uppercase;color:#424D22}}
p{{margin:0 0 9pt}}
.dos{{display:grid;grid-template-columns:1.15fr 1fr;gap:34pt;background:rgba(255,255,255,.82);padding:22pt 26pt}}
.prog{{margin:0;padding:0;list-style:none;border-top:.75pt solid #D5D8C4}} .prog li{{padding:7pt 0 7pt 16pt;border-bottom:.75pt solid #D5D8C4;position:relative}} .prog li::before{{content:"";position:absolute;left:0;top:13pt;width:7pt;height:6pt;background:#ABAC8A}}
.intro{{max-width:520pt;margin-bottom:10pt}}
.croq{{display:grid;gap:10pt 22pt;background:rgba(255,255,255,.82);padding:14pt 18pt}} .c2{{grid-template-columns:1fr 1fr}} .c3{{grid-template-columns:1fr 1fr 1fr}}
.croq article{{display:grid;grid-template-columns:104pt 1fr;gap:12pt;align-items:center;padding:6pt 0}} .c3 article{{grid-template-columns:1fr;gap:4pt;align-items:start}}
.croq svg{{width:104pt;height:auto}} .c3 svg{{width:120pt}}
.croq h3{{font-size:8.5pt;letter-spacing:.16em;margin:0 0 3pt;font-weight:500}} .croq p{{margin:0;font-size:9.5pt;line-height:1.4}}
.blo .bl{{width:500pt;margin:-8pt auto 0}} .blo svg{{width:100%;height:auto}} .blo text,.plano text{{font-family:P,sans-serif}}
.ley{{position:absolute;right:8pt;bottom:8pt;margin:0;padding:10pt 14pt;list-style:none;background:rgba(255,255,255,.85);font-size:9.5pt}} .ley li{{margin:3pt 0}} .ley i{{display:inline-block;width:16pt;height:9pt;margin-right:7pt;border:.5pt solid #999}}
.op{{display:grid;grid-template-columns:390pt 1fr;gap:20pt}} .op.pl{{grid-template-columns:360pt 1fr}}
.izq{{background:var(--f);padding:12pt}} .lema{{font-size:10pt;line-height:1.4;margin:0 0 8pt}} .m3d{{display:block;width:100%}}
.op.pl .izq{{display:flex;align-items:center;justify-content:center}} .plano{{width:100%}} .plano svg{{width:100%;height:auto;max-height:392pt}}
.der{{background:rgba(255,255,255,.85);padding:12pt 14pt}} .vive{{margin-top:10pt;font-size:10pt}} .nota{{font-size:8.5pt;color:#8E8F73}}
table{{border-collapse:collapse;width:100%}} .ar td{{padding:5.2pt 0;border-bottom:.6pt solid #D5D8C4;font-size:10pt}} .ar .n{{width:16pt;color:var(--a);font-weight:500}} .ar .r{{text-align:right;white-space:nowrap}}
.ar .tot td{{font-weight:500;color:var(--a);border-bottom:1.5pt solid var(--a)}}
.cmp{{background:rgba(255,255,255,.85)}} .cmp th,.cmp td{{text-align:left;vertical-align:top;padding:9pt 12pt;border-bottom:.6pt solid #D5D8C4;font-weight:300;font-size:10.5pt}}
.cmp thead th b{{display:block;font-weight:400;font-size:17pt;letter-spacing:.1em;color:#595959}} .cmp thead th span{{font-size:8.5pt;letter-spacing:.2em;text-transform:uppercase;color:#7B7C52;font-weight:400}}
.cmp tbody th{{width:150pt;font-size:8.5pt;letter-spacing:.14em;text-transform:uppercase;color:#8E8F73;font-weight:500}}
.portada{{background:#fff}} .portada .panel{{position:absolute;left:0;top:0;width:440pt;height:404pt;background:linear-gradient(95deg,#E3EACF,#F1F5E4 60%,#F8FAF2)}}
.arbg{{position:absolute;right:0;top:20pt;height:520pt;mix-blend-mode:multiply}}
.pt{{position:absolute;right:288pt;top:136pt;text-align:right}} .pt h1{{margin:0;font-weight:400;font-size:19pt;letter-spacing:.34em;line-height:1.55;color:#424D22}}
.pt .pd{{margin:24pt 0 8pt;font-size:11pt}} .pt ol{{margin:0;padding:0;list-style-position:inside;font-size:10.5pt;line-height:1.5}} .pt .fe{{margin-top:16pt;font-size:9.5pt;letter-spacing:.1em}}
.con{{position:absolute;left:0;width:212pt;top:440pt;text-align:right;font-size:9.5pt;letter-spacing:.22em;line-height:1.55}}
.lg{{position:absolute;left:230pt;top:416pt;width:372pt}}
'''
        doc=f'<!DOCTYPE html><html lang="es"><head><meta charset="utf-8"><style>{css}</style></head><body>{"".join(S)}</body></html>'
        open("slides.html","w",encoding="utf-8").write(doc)
        pg=await b.new_page()
        await pg.goto("file:///home/claude/pdfgen/slides.html", wait_until="load"); await pg.wait_for_timeout(500)
        await pg.pdf(path="Casa_Suesca_primer_diseno_rev1.pdf", width="10in", height="7.5in", print_background=True, prefer_css_page_size=True)
        await b.close()
asyncio.run(main())
