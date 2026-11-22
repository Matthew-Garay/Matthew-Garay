"""Genera los SVG del perfil de GitHub con datos reales de la API.

Uso:  GITHUB_TOKEN=... python scripts/generar.py
Salida: carpeta assets/
"""
import json
import os
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USUARIO = "Matthew-Garay"
SALIDA = Path(__file__).resolve().parent.parent / "assets"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

# ---------------------------------------------------------------- estilo
BG = "#012456"          # azul de PowerShell
FG = "#EEEDF0"
CMD = "#F9F1A5"         # comandos
PARAM = "#9DA5B4"       # parámetros y etiquetas
STR = "#61D6D6"         # valores
OK = "#16C60C"          # Running
WARN = "#F9F1A5"
BORDE = "#2B4F86"
BARRA = "#E8E8E8"
MONO = "'Cascadia Mono','Cascadia Code',Consolas,'SF Mono',Menlo,'DejaVu Sans Mono',monospace"
ANCHO_CHAR = 0.61       # ancho aproximado de un carácter monoespaciado (em)
# Las cifras solo se muestran cuando ya suman; aparecen solas al crecer.
MIN_ESTRELLAS = 5
MIN_DESCARGAS = 25

COLORES_LENGUAJE = {
    "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Python": "#3572A5",
    "PowerShell": "#5391FE", "Batchfile": "#C1F12E", "PHP": "#7A86B8",
    "HTML": "#E34C26", "CSS": "#663399", "Rust": "#DEA584", "Dart": "#00B4AB",
    "R": "#198CE7", "Shell": "#89E051", "Visual Basic .NET": "#945DB7",
    "Prolog": "#C0475F", "Dockerfile": "#4A9FE0", "Cisco Packet Tracer": "#1BA0D7",
}

PROYECTOS = [
    ("Precision-Truck-Parts---Help-Desk", "Precision HelpDesk",
     "Mesa de ayuda e inventario de TI para una empresa real: tickets, insumos, reportes PDF y métricas en tiempo real.",
     "sistema en empresa"),
    ("IP-Scanner", "IP Inspector",
     "Escáner de red y puertos con interfaz gráfica: encuentra dispositivos y revisa sus puertos abiertos.", None),
    ("Microsoft-Office-Installer", "Office Installer",
     "Instala Office LTSC 2016 a 2024 con un solo comando, con interfaz gráfica o consola.", None),
    ("MG-Toolkit", "MG Toolkit",
     "Limpieza, optimización y reparación de Windows 10 y 11 desde un solo archivo.", None),
    ("Adobe-Genuine-Service-AGS-Alert", "AGS Alert Off",
     "Quita las alertas de Adobe Genuine Service en Acrobat y se puede revertir en cualquier momento.", None),
    ("resiliente-chat", "Resiliente Chat",
     "Chat grupal en tiempo real con WebSockets cifrados, historial de mensajes y Docker.", "funcional"),
    ("qr-studio", "QR Studio",
     "Generador de códigos QR con logo, patrones, colores y degradados. Funciona sin conexión.", None),
    ("Redtech", "RedTech",
     "Red corporativa en Packet Tracer: topología, VLANs, subneteo VLSM y documentación técnica.", "proyecto de redes"),
]

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


# ---------------------------------------------------------------- API
def api(ruta, datos=None):
    url = ruta if ruta.startswith("http") else f"https://api.github.com{ruta}"
    cuerpo = json.dumps(datos).encode() if datos else None
    req = urllib.request.Request(url, data=cuerpo, method="POST" if datos else "GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "perfil-generador")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def datos_repos():
    repos = api(f"/users/{USUARIO}/repos?per_page=100&type=owner")
    return [r for r in repos if not r["fork"] and r["name"] != USUARIO]


def descargas(repo):
    try:
        rels = api(f"/repos/{USUARIO}/{repo}/releases?per_page=100")
    except Exception:
        return 0, None
    total = sum(a["download_count"] for r in rels for a in r.get("assets", []))
    return total, (rels[0]["tag_name"] if rels else None)


def commits_ultimo_anio():
    if not TOKEN:
        return None
    q = {"query": "query($u:String!){user(login:$u){contributionsCollection{totalCommitContributions restrictedContributionsCount}}}",
         "variables": {"u": USUARIO}}
    try:
        c = api("https://api.github.com/graphql", q)["data"]["user"]["contributionsCollection"]
        return c["totalCommitContributions"] + c["restrictedContributionsCount"]
    except Exception:
        return None


# ---------------------------------------------------------------- utilidades SVG
def t(x, y, texto, color=FG, size=15, peso=400, extra=""):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" font-weight="{peso}" '
            f'font-family="{MONO}" xml:space="preserve" {extra}>{escape(texto)}</text>')


def tspans(x, y, partes, size=15, extra=""):
    """partes: lista de (texto, color)."""
    s = "".join(f'<tspan fill="{c}">{escape(p)}</tspan>' for p, c in partes)
    return f'<text x="{x}" y="{y}" font-size="{size}" font-family="{MONO}" xml:space="preserve" {extra}>{s}</text>'


def envolver(texto, max_chars):
    lineas, actual = [], ""
    for palabra in texto.split():
        if len(actual) + len(palabra) + (1 if actual else 0) > max_chars:
            lineas.append(actual)
            actual = palabra
        else:
            actual = f"{actual} {palabra}" if actual else palabra
    if actual:
        lineas.append(actual)
    return lineas


def ventana(ancho, alto, titulo, contenido, css=""):
    """Ventana estilo consola de Windows con barra de título clara."""
    controles_x = ancho - 120
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" viewBox="0 0 {ancho} {alto}" role="img" aria-label="{escape(titulo)}">
<style>{css}</style>
<defs><clipPath id="v"><rect width="{ancho}" height="{alto}" rx="10"/></clipPath></defs>
<g clip-path="url(#v)">
<rect width="{ancho}" height="{alto}" fill="{BG}"/>
<rect width="{ancho}" height="36" fill="{BARRA}"/>
<g transform="translate(14 10)"><rect width="16" height="16" rx="2" fill="{BG}"/><path d="M4 4l5 4-5 4" stroke="{FG}" stroke-width="1.8" fill="none"/><path d="M9 12h4" stroke="{FG}" stroke-width="1.8"/></g>
{t(40, 23, titulo, "#1B1B1B", 13, 400, 'font-family="Segoe UI,system-ui,sans-serif"').replace(f'font-family="{MONO}" ', '')}
<g stroke="#333" stroke-width="1.2" fill="none">
<path d="M{controles_x} 18h10"/>
<rect x="{controles_x + 40}" y="13" width="10" height="10"/>
<path d="M{controles_x + 82} 13l10 10M{controles_x + 92} 13l-10 10"/>
</g>
{contenido}
</g>
<rect x=".5" y=".5" width="{ancho - 1}" height="{alto - 1}" rx="10" fill="none" stroke="{BORDE}"/>
</svg>'''


def prompt(ruta="C:\\Users\\matthew"):
    return f"PS {ruta}> "


# ---------------------------------------------------------------- hero
def svg_hero():
    W, size, lh = 880, 16, 27
    x0, y = 26, 74
    p = prompt()
    cmd = "Get-Perfil"
    cw = size * ANCHO_CHAR
    xc = x0 + len(p) * cw
    filas = [
        ("Nombre     ", "Matthew Garay"),
        ("Rol        ", "Soporte técnico y programación"),
        ("Hago       ", "Mesa de ayuda, redes y mantenimiento de equipos"),
        ("Construyo  ", "Aplicaciones web con React, Node.js y MySQL"),
        ("Automatizo ", "Tareas de TI con PowerShell, Batch y Python"),
        ("Contacto   ", "linkedin.com/in/matthewgarayperez"),
    ]
    partes = [tspans(x0, y, [(p, FG), (cmd, CMD)], size)]
    ancho_cmd = len(cmd) * cw + 4
    partes.append(f'<rect class="tapa" x="{xc - 1}" y="{y - size}" width="{ancho_cmd}" height="{size + 7}" fill="{BG}"/>')
    y += lh * 1.6
    for i, (k, v) in enumerate(filas):
        partes.append(tspans(x0, y, [(k, PARAM), (": ", PARAM), (v, STR if i else FG)], size,
                             f'class="sal" style="animation-delay:{1.45 + i * 0.09:.2f}s"'))
        y += lh
    y += lh * 0.6
    partes.append(tspans(x0, y, [(p, FG)], size, 'class="sal" style="animation-delay:2.15s"'))
    partes.append(f'<rect class="cursor" x="{x0 + len(p) * cw + 2}" y="{y - size + 2}" width="{cw}" height="{size + 3}" fill="{FG}"/>')
    alto = int(y + 30)
    css = f'''
.tapa{{transform:translateX({ancho_cmd + 2}px);animation:teclear 1s steps({len(cmd)}) .35s both}}
@keyframes teclear{{from{{transform:translateX(0)}}to{{transform:translateX({ancho_cmd + 2}px)}}}}
.sal{{animation:ver .01s linear both}}
@keyframes ver{{from{{opacity:0}}to{{opacity:1}}}}
.cursor{{animation:ver .01s linear 2.15s both,parpadeo 1.1s steps(1) 2.15s infinite}}
@keyframes parpadeo{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.tapa,.sal,.cursor{{animation:none}}.tapa{{display:none}}}}'''
    return ventana(W, alto, "Windows PowerShell", "\n".join(partes), css)


# ---------------------------------------------------------------- servicios
def svg_servicios():
    W, size, lh = 880, 14.5, 24
    x0, y = 26, 70
    servicios = [
        ("Soporte", "Mantenimiento preventivo y correctivo de hardware"),
        ("Soporte", "Diagnóstico y reparación de PC y laptops"),
        ("Soporte", "Instalación y configuración de Windows y software"),
        ("Soporte", "Impresoras láser y térmicas"),
        ("Redes", "Cableado, VLAN y subneteo VLSM"),
        ("MesaAyuda", "Atención a usuarios y seguimiento de tickets"),
        ("Web", "Aplicaciones web con React y Node.js"),
        ("API", "APIs REST con JWT y permisos por rol"),
        ("Datos", "Diseño de bases de datos MySQL"),
        ("Automatiza", "Scripts de automatización en PowerShell y Batch"),
        ("Escritorio", "Aplicaciones de escritorio en Python"),
    ]
    partes = [tspans(x0, y, [(prompt("C:\\WINDOWS\\system32"), FG), ("Get-Service", CMD), (" -Name ", PARAM), ("Matthew*", STR)], size)]
    y += lh * 1.5
    partes.append(t(x0, y, f"{'Status':<10}{'Name':<13}DisplayName", FG, size))
    y += lh
    partes.append(t(x0, y, f"{'------':<10}{'----':<13}-----------", FG, size))
    for nombre, desc in servicios:
        y += lh
        partes.append(tspans(x0, y, [(f"{'Running':<10}", OK), (f"{nombre:<13}", FG), (desc, STR)], size))
    return ventana(W, int(y + 30), "Administrador: Windows PowerShell", "\n".join(partes))


# ---------------------------------------------------------------- barra de proyectos
def svg_comando(texto_cmd, args=""):
    W, H = 880, 46
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(texto_cmd)}">
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDE}"/>
{tspans(26, 29, [(prompt(), FG), (texto_cmd, CMD), (args, PARAM)], 15)}
</svg>'''


# ---------------------------------------------------------------- tarjetas
def fecha_corta(iso):
    d = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


def svg_tarjeta(nombre, desc, lenguaje, estrellas, bajadas, version, etiqueta, actualizado):
    W, H = 430, 168
    partes = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="10" fill="{BG}" stroke="{BORDE}"/>']
    partes.append(t(22, 38, nombre, FG, 17, 700))
    tag = etiqueta or (f"release {version}" if version else None)
    if tag:
        tw = len(tag) * 12 * ANCHO_CHAR + 18
        color = WARN if tag == "en desarrollo" else OK
        partes.append(f'<rect x="{W - 22 - tw}" y="22" width="{tw:.0f}" height="22" rx="11" fill="none" stroke="{color}"/>')
        partes.append(t(W - 22 - tw + 9, 37, tag, color, 12))
    y = 68
    for linea in envolver(desc, 46)[:3]:
        partes.append(t(22, y, linea, "#C9D1DC", 13.5))
        y += 21
    my = H - 22
    x = 22
    color = COLORES_LENGUAJE.get(lenguaje, PARAM)
    partes.append(f'<circle cx="{x + 5}" cy="{my - 4}" r="5" fill="{color}"/>')
    partes.append(t(x + 16, my, lenguaje, PARAM, 12.5))
    x += 16 + len(lenguaje) * 12.5 * ANCHO_CHAR + 18
    if estrellas >= MIN_ESTRELLAS:
        partes.append(t(x, my, f"★ {estrellas}", PARAM, 12.5))
        x += (len(str(estrellas)) + 2) * 12.5 * ANCHO_CHAR + 16
    if bajadas >= MIN_DESCARGAS:
        txt = f"⬇ {bajadas:,} descargas".replace(",", " ")
        partes.append(t(x, my, txt, PARAM, 12.5))
    partes.append(t(W - 22, my, fecha_corta(actualizado), PARAM, 12.5, 400, 'text-anchor="end"'))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="{escape(nombre)}: {escape(desc)}">
{chr(10).join(partes)}
</svg>'''


# ---------------------------------------------------------------- stack + estadísticas
def svg_stack(stats, lenguajes):
    W, size, lh = 880, 14.5, 24
    x0, y = 26, 70
    cw = size * ANCHO_CHAR
    grupos = [
        ("Lenguajes", "JavaScript, TypeScript, Python, PHP, PowerShell, Batch, Bash, SQL, Rust, Dart, R, VB.NET"),
        ("Frameworks", "React, Vite, Tailwind CSS, Bootstrap, Node.js, Express, Socket.IO, Flutter"),
        ("BasesDatos", "MySQL, SQL Server"),
        ("Sistemas", "Windows 10/11, Windows Server, Ubuntu, Kali Linux, Arch Linux"),
        ("Infra", "Redes Cisco, Packet Tracer, VMware, VirtualBox, Docker, AWS"),
        ("Herramientas", "Git, GitHub, VS Code, Visual Studio, Postman, Power BI, Excel"),
        ("Metodologias", "Scrum, Kanban, ITIL v4"),
    ]
    etiqueta = 14
    max_chars = int((W - x0 * 2) / cw) - etiqueta - 2
    partes = [tspans(x0, y, [(prompt(), FG), ("Get-Stack", CMD), (" | ", FG), ("Format-List", CMD)], size)]
    y += lh * 1.5
    for k, v in grupos:
        for i, linea in enumerate(envolver(v, max_chars)):
            izq = f"{k:<{etiqueta}}: " if i == 0 else " " * (etiqueta + 2)
            partes.append(tspans(x0, y, [(izq, PARAM), (linea, STR)], size))
            y += lh
    y += lh * 0.7
    partes.append(tspans(x0, y, [(prompt(), FG), ("Get-Estadisticas", CMD), (" -Fuente ", PARAM), ("github.com", STR)], size))
    y += lh * 1.5
    filas = [("Repositorios", f'{stats["repos"]} públicos')]
    if stats["commits"] is not None:
        filas.append(("Commits", f'{stats["commits"]} en el último año'))
    if stats["estrellas"] >= MIN_ESTRELLAS * 4:
        filas.append(("Estrellas", stats["estrellas"]))
    if stats["descargas"] >= MIN_DESCARGAS * 4:
        filas.append(("Descargas", stats["descargas"]))
    filas.append(("Actualizado", fecha_corta(datetime.now(timezone.utc).isoformat())))
    for k, v in filas:
        partes.append(tspans(x0, y, [(f"{k:<{etiqueta}}: ", PARAM), (str(v), FG)], size))
        y += lh
    partes.append(tspans(x0, y, [(f"{'Lenguajes':<{etiqueta}}: ", PARAM)], size))
    # barra de lenguajes por bytes de código
    bx, bw, bh = x0 + (etiqueta + 2) * cw, W - x0 - (x0 + (etiqueta + 2) * cw), 12
    total = sum(b for _, b in lenguajes) or 1
    cx = bx
    barra = [f'<clipPath id="b"><rect x="{bx:.1f}" y="{y - 11}" width="{bw:.1f}" height="{bh}" rx="6"/></clipPath><g clip-path="url(#b)">']
    for nombre, b in lenguajes:
        ancho = bw * b / total
        barra.append(f'<rect x="{cx:.1f}" y="{y - 11}" width="{ancho + .5:.1f}" height="{bh}" fill="{COLORES_LENGUAJE.get(nombre, PARAM)}"/>')
        cx += ancho
    barra.append("</g>")
    partes.append("".join(barra))
    y += lh
    lx = bx
    for nombre, b in lenguajes:
        etiqueta_l = f"{nombre} {b * 100 / total:.0f}%"
        largo = 14 + len(etiqueta_l) * 12.5 * ANCHO_CHAR + 20
        if lx + largo > W - x0:
            y += 20
            lx = bx
        partes.append(f'<circle cx="{lx + 5:.1f}" cy="{y - 4}" r="4.5" fill="{COLORES_LENGUAJE.get(nombre, PARAM)}"/>')
        partes.append(t(round(lx + 14, 1), y, etiqueta_l, PARAM, 12.5))
        lx += largo
    return ventana(W, int(y + 30), "Windows PowerShell", "\n".join(partes))


# ---------------------------------------------------------------- main
def main():
    SALIDA.mkdir(exist_ok=True)
    repos = {r["name"]: r for r in datos_repos()}

    total_bajadas = 0
    bajadas_por_repo = {}
    for nombre in repos:
        n, v = descargas(nombre)
        bajadas_por_repo[nombre] = (n, v)
        total_bajadas += n

    for repo, nombre, desc, etiqueta in PROYECTOS:
        r = repos.get(repo)
        if not r:
            print(f"aviso: {repo} no es público, se omite")
            continue
        lenguaje = (r.get("language") or "Cisco Packet Tracer")
        if lenguaje == "Batchfile":
            lenguaje = "Batch"
            COLORES_LENGUAJE["Batch"] = COLORES_LENGUAJE["Batchfile"]
        n, v = bajadas_por_repo.get(repo, (0, None))
        svg = svg_tarjeta(nombre, desc, lenguaje, r["stargazers_count"], n, v, etiqueta, r["pushed_at"])
        (SALIDA / f"proyecto-{repo.lower().strip('-')}.svg").write_text(svg, encoding="utf-8")

    bytes_lenguaje = {}
    for nombre in repos:
        for lang, b in api(f"/repos/{USUARIO}/{nombre}/languages").items():
            bytes_lenguaje[lang] = bytes_lenguaje.get(lang, 0) + b
    top = sorted(bytes_lenguaje.items(), key=lambda kv: -kv[1])[:6]
    top = [("Batch" if k == "Batchfile" else k, v) for k, v in top]
    COLORES_LENGUAJE["Batch"] = COLORES_LENGUAJE["Batchfile"]

    stats = {
        "repos": len(repos),
        "estrellas": sum(r["stargazers_count"] for r in repos.values()),
        "descargas": total_bajadas,
        "commits": commits_ultimo_anio(),
    }
    (SALIDA / "perfil.svg").write_text(svg_hero(), encoding="utf-8")
    (SALIDA / "servicios.svg").write_text(svg_servicios(), encoding="utf-8")
    (SALIDA / "proyectos.svg").write_text(svg_comando("Get-Proyectos", " -Destacados"), encoding="utf-8")
    (SALIDA / "stack.svg").write_text(svg_stack(stats, top), encoding="utf-8")
    print("listo:", stats, datetime.now(timezone.utc).isoformat(timespec="minutes"))


if __name__ == "__main__":
    main()
