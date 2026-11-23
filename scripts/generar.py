"""Genera los gráficos SVG del perfil de GitHub con datos reales de la API.

Uso:   GITHUB_TOKEN=... python scripts/generar.py
Salida: carpeta assets/

Secciones:
  perfil.svg         consola de PowerShell que describe el perfil (animada)
  servicios.svg      Get-Service con las cuatro áreas de trabajo y el stack
  reproductor.svg    proyecto destacado con ficha técnica
  playlist.svg       encabezado de la playlist de proyectos
  pista-*.svg        una fila por proyecto
  resumen.svg        "Tu año en código": contribuciones, racha y lenguajes
"""
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import date, datetime, timezone
from html import escape
from pathlib import Path

USUARIO = "Matthew-Garay"
SALIDA = Path(__file__).resolve().parent.parent / "assets"
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

# ================================================================ datos fijos
AREAS = {
    "Mantenimiento": "#F59B23",
    "Soporte técnico": "#4CB3FF",
    "Programación": "#1ED760",
    "Bases de datos": "#B49BFF",
    "Redes": "#2DD4BF",
    "Seguridad": "#FF6B8B",
}

# repo, título, descripción corta, área, tecnologías, estado, icono, colores de portada
PISTAS = [
    ("Precision-Truck-Parts---Help-Desk", "Precision HelpDesk", "Mesa de ayuda e inventario de TI en empresa",
     "Bases de datos", "React, Node.js, MySQL", "piloto", "ticket", ("#1D4ED8", "#0B1E4A")),
    ("IP-Scanner", "IP Inspector", "Escáner de red y puertos con interfaz gráfica",
     "Redes", "Python, CustomTkinter", "release", "radar", ("#0F766E", "#062925")),
    ("MG-Toolkit", "MG Toolkit", "Limpieza, reparación y diagnóstico de Windows",
     "Mantenimiento", "Batch, DISM, SFC", "release", "llave", ("#C2410C", "#3B1405")),
    ("Microsoft-Office-Installer", "Office Installer", "Instala Office LTSC con un solo comando",
     "Soporte técnico", "PowerShell, HTML", "release", "descarga", ("#B91C1C", "#3A0A0A")),
    ("Adobe-Genuine-Service-AGS-Alert", "AGS Alert Off", "Desactiva alertas de Adobe de forma reversible",
     "Soporte técnico", "PowerShell", "release", "campana", ("#7C3AED", "#24104A")),
    ("Directo-a-Obra", "Directo a Obra", "Tienda en línea de materiales de construcción",
     "Bases de datos", "PHP, MySQL, PHPMailer", "académico", "carrito", ("#A16207", "#33200A")),
    ("resiliente-chat", "Resiliente Chat", "Chat grupal en tiempo real con cifrado TLS",
     "Programación", "Node.js, WSS, Docker", "funcional", "chat", ("#0369A1", "#06223A")),
    ("qr-studio", "QR Studio", "Generador de códigos QR personalizables",
     "Programación", "JavaScript, Canvas", "demo", "qr", ("#15803D", "#062A14")),
    ("Redtech", "RedTech", "Diseño de red corporativa con VLANs y VLSM",
     "Redes", "Cisco Packet Tracer", "académico", "red", ("#0E7490", "#06242C")),
    ("CifradoAsimetrico", "Cifrado RSA", "Cifrado asimétrico en el navegador",
     "Seguridad", "Web Crypto API, Tailwind", "demo", "llave-cifrado", ("#BE185D", "#3A0A1E")),
    ("remote-support-app", "Remote Support App", "Escritorio remoto P2P para soporte",
     "Soporte técnico", "Rust, Flutter, WebRTC", "en desarrollo", "monitor", ("#4338CA", "#15123F")),
]

COLORES_LENGUAJE = {
    "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Python": "#3572A5",
    "PowerShell": "#5391FE", "Batch": "#C1F12E", "PHP": "#7A86B8",
    "HTML": "#E34C26", "CSS": "#8F5FD0", "Rust": "#DEA584", "Dart": "#00B4AB",
    "R": "#198CE7", "Shell": "#89E051", "Visual Basic .NET": "#945DB7",
    "Prolog": "#C0475F", "Dockerfile": "#4A9FE0",
}

# ================================================================ estilos
# consola
PS_BG, PS_FG, PS_CMD, PS_PARAM, PS_STR, PS_OK = "#012456", "#EEEDF0", "#F9F1A5", "#9DA5B4", "#61D6D6", "#16C60C"
PS_BORDE, PS_BARRA = "#2B4F86", "#E8E8E8"
MONO = "'Cascadia Mono','Cascadia Code',Consolas,'SF Mono',Menlo,'DejaVu Sans Mono',monospace"
ANCHO_MONO = 0.61
# reproductor
R_BG, R_PANEL, R_FG, R_SUB, R_VERDE, R_LINEA = "#121212", "#1E1E1E", "#FFFFFF", "#B3B3B3", "#1ED760", "#2A2A2A"
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"


# ================================================================ API
def api(ruta, datos=None):
    url = ruta if ruta.startswith("http") else f"https://api.github.com{ruta}"
    cuerpo = json.dumps(datos).encode() if datos else None
    req = urllib.request.Request(url, data=cuerpo, method="POST" if datos else "GET")
    req.add_header("Accept", "application/vnd.github+json")
    req.add_header("User-Agent", "perfil-generador")
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")
    for intento in range(4):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except (urllib.error.URLError, ConnectionError, TimeoutError):
            if intento == 3:
                raise
            time.sleep(2 * (intento + 1))


def graphql(query, **variables):
    return api("https://api.github.com/graphql", {"query": query, "variables": variables})["data"]


def cargar_datos():
    repos = [r for r in api(f"/users/{USUARIO}/repos?per_page=100&type=owner")
             if not r["fork"] and r["name"] != USUARIO]
    nombres = {r["name"]: r for r in repos}

    # commits y última versión por repo
    for nombre in nombres:
        d = graphql("""query($o:String!,$n:String!){repository(owner:$o,name:$n){
            defaultBranchRef{target{... on Commit{history{totalCount}}}}
            releases(first:1,orderBy:{field:CREATED_AT,direction:DESC}){nodes{tagName}}}}""",
                    o=USUARIO, n=nombre)["repository"]
        ref = d["defaultBranchRef"]
        nombres[nombre]["_commits"] = ref["target"]["history"]["totalCount"] if ref else 0
        rel = d["releases"]["nodes"]
        nombres[nombre]["_version"] = rel[0]["tagName"] if rel else None

    # lenguajes por bytes
    bytes_lenguaje = Counter()
    for nombre in nombres:
        for lang, b in api(f"/repos/{USUARIO}/{nombre}/languages").items():
            bytes_lenguaje["Batch" if lang == "Batchfile" else lang] += b

    # calendario de contribuciones
    c = graphql("""query($u:String!){user(login:$u){contributionsCollection{
        totalCommitContributions restrictedContributionsCount
        contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}""",
                u=USUARIO)["user"]["contributionsCollection"]
    dias = [(date.fromisoformat(d["date"]), d["contributionCount"])
            for w in c["contributionCalendar"]["weeks"] for d in w["contributionDays"]]
    return {
        "repos": nombres,
        "lenguajes": bytes_lenguaje.most_common(),
        "commits_anio": c["totalCommitContributions"] + c["restrictedContributionsCount"],
        "contribuciones": c["contributionCalendar"]["totalContributions"],
        "semanas": [sum(d["contributionCount"] for d in w["contributionDays"])
                    for w in c["contributionCalendar"]["weeks"]],
        "dias": dias,
    }


# ================================================================ SVG básico
def txt(x, y, s, color, size, peso=400, fuente=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" font-weight="{peso}" '
            f'font-family="{fuente}" xml:space="preserve" {extra}>{escape(str(s))}</text>')


def mono(x, y, partes, size=15, extra=""):
    s = "".join(f'<tspan fill="{c}">{escape(p)}</tspan>' for p, c in partes)
    return f'<text x="{x}" y="{y}" font-size="{size}" font-family="{MONO}" xml:space="preserve" {extra}>{s}</text>'


def svg(w, h, contenido, etiqueta, estilo="", defs=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(etiqueta)}"><style>{estilo}</style><defs>{defs}</defs>{contenido}</svg>')


def envolver(texto, max_chars):
    lineas, actual = [], ""
    for p in texto.split():
        if actual and len(actual) + 1 + len(p) > max_chars:
            lineas.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}".strip()
    return lineas + ([actual] if actual else [])


def fecha_corta(d):
    return f"{d.day} {MESES[d.month - 1]} {d.year}"


# ================================================================ consola
def ventana(w, h, titulo, contenido, estilo=""):
    cx = w - 120
    barra = (f'<rect width="{w}" height="36" fill="{PS_BARRA}"/>'
             f'<g transform="translate(14 10)"><rect width="16" height="16" rx="2" fill="{PS_BG}"/>'
             f'<path d="M4 4l5 4-5 4M9 12h4" stroke="{PS_FG}" stroke-width="1.8" fill="none"/></g>'
             + txt(40, 23, titulo, "#1B1B1B", 13, fuente="'Segoe UI',system-ui,sans-serif")
             + f'<g stroke="#333" stroke-width="1.2" fill="none"><path d="M{cx} 18h10"/>'
               f'<rect x="{cx + 40}" y="13" width="10" height="10"/>'
               f'<path d="M{cx + 82} 13l10 10M{cx + 92} 13l-10 10"/></g>')
    cuerpo = (f'<g clip-path="url(#v)"><rect width="{w}" height="{h}" fill="{PS_BG}"/>{barra}{contenido}</g>'
              f'<rect x=".5" y=".5" width="{w - 1}" height="{h - 1}" rx="10" fill="none" stroke="{PS_BORDE}"/>')
    return svg(w, h, cuerpo, titulo, estilo, f'<clipPath id="v"><rect width="{w}" height="{h}" rx="10"/></clipPath>')


PROMPT = "PS C:\\Users\\matthew> "


def svg_perfil():
    W, size, lh, x0 = 880, 16, 27, 26
    cw = size * ANCHO_MONO
    filas = [
        ("Nombre", "Matthew Garay", PS_FG),
        ("Rol", "Soporte técnico, mantenimiento y desarrollo de software", PS_STR),
        ("Mantenimiento", "Diagnóstico, reparación y actualización de equipos", PS_STR),
        ("Soporte", "Mesa de ayuda, Windows, impresoras y redes LAN", PS_STR),
        ("Programación", "Aplicaciones web con React, Node.js y APIs REST", PS_STR),
        ("BasesDeDatos", "Diseño y administración de MySQL y SQL Server", PS_STR),
        ("Automatización", "Scripts de TI en PowerShell, Batch y Python", PS_STR),
        ("Contacto", "linkedin.com/in/matthewgarayperez", PS_STR),
    ]
    cmd = "Get-Perfil"
    y = 74
    partes = [mono(x0, y, [(PROMPT, PS_FG), (cmd, PS_CMD)], size)]
    ancho_cmd = len(cmd) * cw + 4
    partes.append(f'<rect class="tapa" x="{x0 + len(PROMPT) * cw - 1:.1f}" y="{y - size}" '
                  f'width="{ancho_cmd:.1f}" height="{size + 7}" fill="{PS_BG}"/>')
    y += lh * 1.6
    for i, (k, v, c) in enumerate(filas):
        partes.append(mono(x0, y, [(f"{k:<15}", PS_PARAM), (": ", PS_PARAM), (v, c)], size,
                           f'class="sal" style="animation-delay:{1.45 + i * 0.08:.2f}s"'))
        y += lh
    y += lh * 0.6
    partes.append(mono(x0, y, [(PROMPT, PS_FG)], size, 'class="sal" style="animation-delay:2.2s"'))
    partes.append(f'<rect class="cursor" x="{x0 + len(PROMPT) * cw + 2:.1f}" y="{y - size + 2}" '
                  f'width="{cw:.1f}" height="{size + 3}" fill="{PS_FG}"/>')
    estilo = f"""
.tapa{{transform:translateX({ancho_cmd + 2:.0f}px);animation:teclear 1s steps({len(cmd)}) .35s both}}
@keyframes teclear{{from{{transform:translateX(0)}}to{{transform:translateX({ancho_cmd + 2:.0f}px)}}}}
.sal{{animation:ver .01s linear both}}
@keyframes ver{{from{{opacity:0}}to{{opacity:1}}}}
.cursor{{animation:ver .01s linear 2.2s both,parpadeo 1.1s steps(1) 2.2s infinite}}
@keyframes parpadeo{{50%{{opacity:0}}}}
@media (prefers-reduced-motion:reduce){{.tapa,.sal,.cursor{{animation:none}}.tapa{{display:none}}}}"""
    return ventana(W, int(y + 30), "Windows PowerShell", "".join(partes), estilo)


def svg_servicios():
    W, size, lh, x0 = 880, 14.5, 24, 26
    servicios = [
        ("Mantenimiento", "Diagnóstico de fallas de hardware y software"),
        ("Mantenimiento", "Limpieza interna y mantenimiento preventivo"),
        ("Mantenimiento", "Cambio de componentes: RAM, SSD y discos"),
        ("Soporte", "Mesa de ayuda y atención a usuarios"),
        ("Soporte", "Instalación de Windows, Office y controladores"),
        ("Soporte", "Impresoras láser y térmicas, redes LAN y VLAN"),
        ("Programacion", "Aplicaciones web con React, Vite y Tailwind"),
        ("Programacion", "APIs REST con Node.js, Express, JWT y roles"),
        ("Programacion", "Automatización con PowerShell, Batch y Python"),
        ("BasesDeDatos", "Modelado entidad-relación y normalización (3FN)"),
        ("BasesDeDatos", "MySQL y SQL Server: consultas y transacciones"),
        ("BasesDeDatos", "Reportes y análisis de datos con Power BI"),
    ]
    stack = [
        ("Lenguajes", "JavaScript, TypeScript, Python, PHP, SQL, PowerShell, Batch, Bash, VB.NET, Rust, R"),
        ("Frameworks", "React, Vite, Tailwind CSS, Bootstrap, Node.js, Express, Socket.IO, Flutter"),
        ("BasesDeDatos", "MySQL, SQL Server"),
        ("Sistemas", "Windows 10/11, Windows Server, Ubuntu, Kali Linux, Arch Linux"),
        ("Infraestructura", "Redes Cisco, Packet Tracer, VMware, VirtualBox, Docker, AWS"),
        ("Herramientas", "Git, GitHub, VS Code, Visual Studio, Postman, Power BI, Excel"),
        ("Metodologias", "Scrum, Kanban, ITIL v4"),
    ]
    y = 70
    p = [mono(x0, y, [("PS C:\\WINDOWS\\system32> ", PS_FG), ("Get-Service", PS_CMD),
                      (" -Name ", PS_PARAM), ("Matthew*", PS_STR)], size)]
    y += lh * 1.5
    p.append(mono(x0, y, [(f"{'Status':<10}{'Name':<15}DisplayName", PS_FG)], size))
    y += lh
    p.append(mono(x0, y, [(f"{'------':<10}{'----':<15}-----------", PS_FG)], size))
    previo = None
    for nombre, desc in servicios:
        y += lh + (8 if previo and previo != nombre else 0)
        p.append(mono(x0, y, [(f"{'Running':<10}", PS_OK), (f"{nombre:<15}", PS_FG), (desc, PS_STR)], size))
        previo = nombre
    y += lh * 1.8
    p.append(mono(x0, y, [(PROMPT, PS_FG), ("Get-Stack", PS_CMD), (" | ", PS_FG), ("Format-List", PS_CMD)], size))
    y += lh * 1.5
    etiqueta = 16
    max_chars = int((W - 2 * x0) / (size * ANCHO_MONO)) - etiqueta - 2
    for k, v in stack:
        for i, linea in enumerate(envolver(v, max_chars)):
            izq = f"{k:<{etiqueta}}: " if i == 0 else " " * (etiqueta + 2)
            p.append(mono(x0, y, [(izq, PS_PARAM), (linea, PS_STR)], size))
            y += lh
    return ventana(W, int(y + 14), "Administrador: Windows PowerShell", "".join(p))


# ================================================================ portadas
ICONOS = {
    "ticket": '<path d="M22 32h56v10a8 8 0 0 0 0 16v10H22V58a8 8 0 0 0 0-16z"/><path d="M38 50l8 8 16-16"/>',
    "radar": '<circle cx="50" cy="50" r="28"/><circle cx="50" cy="50" r="16"/><path d="M50 50L70 30"/><circle cx="62" cy="58" r="3" fill="#fff"/>',
    "llave": '<path d="M62 24a14 14 0 0 0-14 18L26 64a6 6 0 0 0 8 8l22-22a14 14 0 0 0 18-14l-9 9-8-2-2-8z"/>',
    "descarga": '<path d="M50 22v36M36 46l14 14 14-14M26 64v12h48V64"/>',
    "campana": '<path d="M34 64V48a16 16 0 0 1 32 0v16l6 6H28zM44 74a6 6 0 0 0 12 0"/><path d="M24 24l52 52"/>',
    "carrito": '<path d="M22 28h10l8 32h32l6-22H36"/><circle cx="44" cy="72" r="4"/><circle cx="66" cy="72" r="4"/>',
    "chat": '<path d="M24 30h38v26H40l-10 8v-8h-6z"/><path d="M68 42h8v24h-6v8l-10-8H44v-4"/>',
    "qr": ('<rect x="26" y="26" width="18" height="18"/><rect x="56" y="26" width="18" height="18"/>'
           '<rect x="26" y="56" width="18" height="18"/><path d="M56 56h6v6h-6zM68 62h6v12h-12v-6"/>'),
    "red": ('<circle cx="50" cy="28" r="7"/><circle cx="28" cy="68" r="7"/><circle cx="72" cy="68" r="7"/>'
            '<circle cx="50" cy="56" r="5"/><path d="M50 35v16M45 59l-12 6M55 59l12 6"/>'),
    "llave-cifrado": '<rect x="30" y="46" width="40" height="30" rx="4"/><path d="M38 46v-8a12 12 0 0 1 24 0v8M50 58v8"/>',
    "monitor": '<rect x="22" y="26" width="56" height="38" rx="3"/><path d="M40 76h20M50 64v12"/><path d="M44 36l14 8-6 2 4 7-3 1-4-7-5 4z" fill="#fff"/>',
}


def portada(x, y, tam, icono, colores, uid, radio=4):
    c1, c2 = colores
    escala = tam / 100
    return (f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<rect x="{x}" y="{y}" width="{tam}" height="{tam}" rx="{radio}" fill="url(#g{uid})"/>'
            f'<g transform="translate({x} {y}) scale({escala})" fill="none" stroke="#fff" '
            f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{ICONOS[icono]}</g>')


# ================================================================ reproductor
def svg_reproductor(repo):
    W, H = 880, 632
    pista = PISTAS[0]
    c1, _ = pista[7]
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{R_BG}"/>',
         f'<rect width="{W}" height="300" rx="12" fill="url(#cab)"/>']
    p.append(portada(32, 36, 200, pista[6], pista[7], "rep", 6))
    p.append(txt(262, 72, "Sonando ahora: proyecto destacado", R_FG, 13, 600))
    p.append(txt(258, 128, "Precision HelpDesk", R_FG, 50, 800, extra='letter-spacing="-1"'))
    p.append(txt(262, 164, "Mesa de ayuda y gestión de activos de TI para RFV Truck Parts", R_SUB, 15.5))
    meta = f"Matthew Garay  •  2026  •  {repo['_commits']} commits  •  proyecto de titulación"
    p.append(txt(262, 192, meta, R_FG, 13.5, 500))
    # controles
    p.append(f'<circle cx="290" cy="245" r="26" fill="{R_VERDE}"/><path d="M282 232v26l21-13z" fill="#000"/>')
    p.append(f'<g fill="none" stroke="{R_SUB}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M343 236a9 9 0 0 1 14 0 9 9 0 0 1 14 0c0 9-14 18-14 18s-14-9-14-18z"/>'
             f'<path d="M392 245h2M402 245h2M412 245h2" stroke-width="3"/></g>')
    # ciclo de vida
    fases = ["Análisis", "Diseño", "Desarrollo", "Pruebas", "Piloto", "Producción"]
    actual = 4
    bx, bw, by = 450, 370, 245
    paso = bw / (len(fases) - 1)
    p.append(f'<rect x="{bx}" y="{by - 2}" width="{bw}" height="4" rx="2" fill="#535353"/>')
    p.append(f'<rect x="{bx}" y="{by - 2}" width="{paso * actual:.1f}" height="4" rx="2" fill="{R_FG}"/>')
    p.append(f'<circle cx="{bx + paso * actual:.1f}" cy="{by}" r="7" fill="{R_FG}"/>')
    for i, f in enumerate(fases):
        p.append(txt(bx + paso * i, by + 24, f, R_FG if i == actual else R_SUB, 11.5,
                     700 if i == actual else 400, extra='text-anchor="middle"'))
    p.append(txt(bx, by - 14, "Estado del proyecto", R_SUB, 11.5))

    # ficha técnica
    y0 = 330
    columnas = [
        ("Problema", "Los reportes de fallas llegaban por mensajes y hojas de cálculo, sin seguimiento ni un inventario confiable de equipos."),
        ("Solución", "Plataforma web con tickets, inventario de activos, solicitud de insumos, manuales y métricas en tiempo real."),
        ("Seguridad", "JWT sin estado, contraseñas con bcrypt, permisos por rol, rate limiting y pruebas contra inyección SQL."),
    ]
    cw = (W - 64 - 2 * 20) / 3
    for i, (t, d) in enumerate(columnas):
        x = 32 + i * (cw + 20)
        p.append(txt(x, y0, t, R_FG, 16, 700))
        for j, linea in enumerate(envolver(d, 38)):
            p.append(txt(x, y0 + 26 + j * 20, linea, R_SUB, 13.5))

    # arquitectura
    y1 = 450
    p.append(txt(32, y1, "Arquitectura", R_FG, 16, 700))
    cajas = [("React + Vite", "SPA responsiva"), ("API REST", "Node.js · Express"), ("MySQL", "InnoDB · 3FN")]
    bwc, bhc, gap = 170, 52, 46
    for i, (a, b) in enumerate(cajas):
        x = 32 + i * (bwc + gap)
        p.append(f'<rect x="{x}" y="{y1 + 16}" width="{bwc}" height="{bhc}" rx="8" fill="{R_PANEL}" stroke="#333"/>')
        p.append(txt(x + 14, y1 + 38, a, R_FG, 14, 600))
        p.append(txt(x + 14, y1 + 57, b, R_SUB, 12))
        if i:
            ax = x - gap
            p.append(f'<path d="M{ax + 6} {y1 + 42}h{gap - 14}m-6 -5l6 5-6 5" stroke="{R_VERDE}" '
                     f'stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    extras = ["Socket.IO: alertas de SLA", "Nodemailer: correos", "Sharp: compresión", "Reportes PDF"]
    ex = 32 + 3 * (bwc + gap) - 10
    for i, e in enumerate(extras):
        p.append(f'<circle cx="{ex + 4}" cy="{y1 + 24 + i * 16}" r="3" fill="{R_VERDE}"/>')
        p.append(txt(ex + 14, y1 + 28 + i * 16, e, R_SUB, 12))

    # resultados
    y2 = 582
    metricas = [("-90 %", "peso de imágenes"), ("85 → 3 ms", "dashboard con caché"),
                ("< 2 s", "PDF de 1000 tickets"), ("50 req/s", "carga estable")]
    mw = (W - 64) / 4
    p.append(f'<line x1="32" x2="{W - 32}" y1="{y2 - 26}" y2="{y2 - 26}" stroke="{R_LINEA}"/>')
    for i, (n, d) in enumerate(metricas):
        x = 32 + i * mw
        p.append(txt(x, y2 + 4, n, R_VERDE, 22, 800))
        p.append(txt(x, y2 + 26, d, R_SUB, 12.5))
    defs = (f'<linearGradient id="cab" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{c1}"/>'
            f'<stop offset="1" stop-color="{R_BG}"/></linearGradient>')
    return svg(W, H, "".join(p), "Proyecto destacado: Precision HelpDesk", defs=defs)


# ================================================================ playlist
COLS = {"num": 40, "img": 60, "titulo": 124, "area": 440, "tec": 600, "fin": 852}


def svg_playlist(total_commits):
    W, H = 880, 230
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="url(#pl)"/>']
    # mosaico de portadas
    for i, pista in enumerate(PISTAS[:4]):
        x, y = 32 + (i % 2) * 80, 28 + (i // 2) * 80
        p.append(portada(x, y, 80, pista[6], pista[7], f"m{i}", 0))
    p.append(txt(214, 52, "Playlist pública", R_FG, 13, 600))
    p.append(txt(210, 108, "Proyectos", R_FG, 54, 800, extra='letter-spacing="-1.5"'))
    p.append(txt(214, 144, "Soporte, mantenimiento, redes, programación y bases de datos.", R_SUB, 14.5))
    p.append(txt(214, 172, f"Matthew Garay  •  {len(PISTAS)} proyectos  •  {total_commits} commits", R_FG, 13.5, 500))
    yc = 214
    p.append(txt(COLS["num"], yc, "#", R_SUB, 13, extra='text-anchor="end"'))
    p.append(txt(COLS["titulo"], yc, "Título", R_SUB, 13))
    p.append(txt(COLS["area"], yc, "Área", R_SUB, 13))
    p.append(txt(COLS["tec"], yc, "Tecnologías", R_SUB, 13))
    p.append(txt(COLS["fin"], yc, "Estado", R_SUB, 13, extra='text-anchor="end"'))
    p.append(f'<line x1="24" x2="{W - 24}" y1="{H - 4}" y2="{H - 4}" stroke="{R_LINEA}"/>')
    defs = (f'<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1F3B2A"/>'
            f'<stop offset="1" stop-color="{R_BG}"/></linearGradient>')
    return svg(W, H, "".join(p), "Playlist de proyectos", defs=defs)


def recortar(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def svg_pista(i, pista, repo):
    W, H = 880, 64
    nombre_repo, titulo, desc, area, tec, estado, icono, colores = pista
    p = [f'<rect width="{W}" height="{H}" fill="{R_BG}"/>']
    p.append(txt(COLS["num"], 38, i, R_SUB, 15, extra='text-anchor="end"'))
    p.append(portada(COLS["img"], 8, 48, icono, colores, f"p{i}"))
    p.append(txt(COLS["titulo"], 29, titulo, R_FG, 16, 600))
    p.append(txt(COLS["titulo"], 49, recortar(desc, 46), R_SUB, 13))
    p.append(f'<circle cx="{COLS["area"] + 4}" cy="{34}" r="4" fill="{AREAS[area]}"/>')
    p.append(txt(COLS["area"] + 14, 38.5, area, R_SUB, 13.5))
    p.append(txt(COLS["tec"], 38.5, recortar(tec, 26), R_SUB, 13.5))
    if estado == "release":
        estado = repo.get("_version") or "release"
    color = {"en desarrollo": "#F59B23", "académico": R_SUB}.get(estado, R_VERDE)
    p.append(txt(COLS["fin"], 31, estado, color, 13, 600, extra='text-anchor="end"'))
    p.append(txt(COLS["fin"], 50, f"{repo.get('_commits', 0)} commits", R_SUB, 12, extra='text-anchor="end"'))
    return svg(W, H, "".join(p), f"{i}. {titulo}: {desc}")


# ================================================================ resumen anual
def rachas(dias):
    mayor = actual = 0
    for _, n in dias:
        actual = actual + 1 if n else 0
        mayor = max(mayor, actual)
    hoy = 0
    cola = dias[:-1] if dias and not dias[-1][1] else dias   # hoy sin contribuir no rompe la racha
    for _, n in reversed(cola):
        if not n:
            break
        hoy += 1
    return mayor, hoy


def svg_resumen(d):
    W, H = 880, 520
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{R_BG}"/>',
         f'<rect width="{W}" height="{H}" rx="12" fill="url(#rs)"/>']
    p.append(txt(32, 58, "Tu año en código", R_FG, 36, 800, extra='letter-spacing="-1"'))
    p.append(txt(32, 84, "Contribuciones en GitHub durante los últimos 12 meses", R_SUB, 14.5))

    # forma de onda semanal
    semanas = d["semanas"]
    maxv = max(semanas) or 1
    x0, ancho, centro, alto = 32, W - 64, 176, 66
    paso = ancho / len(semanas)
    barras = []
    for i, v in enumerate(semanas):
        h = max(2, alto * (v / maxv) ** 0.6)
        op = 1 if v else 0.35
        barras.append(f'<rect x="{x0 + i * paso + 1:.1f}" y="{centro - h:.1f}" width="{paso - 2.5:.1f}" '
                      f'height="{2 * h:.1f}" rx="{min(2.5, (paso - 2.5) / 2):.1f}" fill="{R_VERDE}" opacity="{op}"/>')
    p.append("".join(barras))
    # meses
    inicio = d["dias"][0][0]
    vistos = set()
    for i in range(len(semanas)):
        dia = d["dias"][min(i * 7, len(d["dias"]) - 1)][0]
        if dia.month not in vistos and dia.day <= 7:
            vistos.add(dia.month)
            p.append(txt(x0 + i * paso, centro + alto + 24, MESES[dia.month - 1], R_SUB, 11.5))
    _ = inicio

    # cifras
    mayor, actual = rachas(d["dias"])
    por_dia = Counter()
    for f, n in d["dias"]:
        por_dia[f.weekday()] += n
    dia_fav = DIAS[por_dia.most_common(1)[0][0]] if por_dia else "-"
    cifras = [(d["commits_anio"], "commits"), (d["contribuciones"], "contribuciones"),
              (f"{mayor} días", "racha más larga"), (dia_fav.capitalize(), "día más productivo")]
    y = 318
    cw = (W - 64) / 4
    for i, (n, etiqueta) in enumerate(cifras):
        x = 32 + i * cw
        p.append(txt(x, y, n, R_FG, 34, 800, extra='letter-spacing="-1"'))
        p.append(txt(x, y + 24, etiqueta, R_SUB, 13))

    # lenguajes
    y = 392
    p.append(f'<line x1="32" x2="{W - 32}" y1="{y - 22}" y2="{y - 22}" stroke="{R_LINEA}"/>')
    p.append(txt(32, y + 6, "Tus lenguajes más usados", R_FG, 16, 700))
    total = sum(b for _, b in d["lenguajes"]) or 1
    top = d["lenguajes"][:5]
    col_w = (W - 64) / 5
    for i, (lang, b) in enumerate(top):
        x = 32 + i * col_w
        pct = b * 100 / total
        p.append(txt(x, y + 44, f"{i + 1}", R_SUB, 22, 800))
        p.append(txt(x + 26, y + 44, lang, R_FG, 15, 600))
        p.append(f'<rect x="{x}" y="{y + 60}" width="{col_w - 24:.1f}" height="4" rx="2" fill="#333"/>')
        p.append(f'<rect x="{x}" y="{y + 60}" width="{(col_w - 24) * b / top[0][1]:.1f}" '
                 f'height="4" rx="2" fill="{COLORES_LENGUAJE.get(lang, R_VERDE)}"/>')
        p.append(txt(x, y + 84, f"{pct:.0f} % del código", R_SUB, 12))
    p.append(txt(W - 32, H - 18, f"{len(d['repos'])} repositorios públicos  •  actualizado el {fecha_corta(date.today())}",
                 "#7A7A7A", 11.5, extra='text-anchor="end"'))
    defs = ('<radialGradient id="rs" cx="0.85" cy="0" r="0.9"><stop offset="0" stop-color="#1ED760" stop-opacity=".22"/>'
            '<stop offset="1" stop-color="#1ED760" stop-opacity="0"/></radialGradient>')
    return svg(W, H, "".join(p), f"Tu año en código: {d['commits_anio']} commits, racha de {mayor} días", defs=defs)


# ================================================================ página de artista
# Cambia a True cuando subas una foto real a tu perfil de GitHub.
USAR_FOTO = False

ICONOS.update({
    "codigo": '<path d="M38 32L20 50l18 18M62 32l18 18-18 18M55 26L45 74"/>',
    "base": ('<ellipse cx="50" cy="28" rx="24" ry="8"/><path d="M26 28v44c0 4 11 8 24 8s24-4 24-8V28"/>'
             '<path d="M26 50c0 4 11 8 24 8s24-4 24-8"/>'),
    "soporte": ('<path d="M26 56v-8a24 24 0 0 1 48 0v8"/><rect x="20" y="54" width="12" height="18" rx="4"/>'
                '<rect x="68" y="54" width="12" height="18" rx="4"/><path d="M74 72c0 6-8 8-18 8"/>'),
})

ALBUMES = [
    ("Mantenimiento y reparación", "llave", ("#EA580C", "#431407"), [
        "Diagnóstico de fallas de hardware y software",
        "Limpieza interna y mantenimiento preventivo",
        "Cambio de componentes: RAM, SSD y discos",
        "Formateo, respaldo y recuperación de datos",
        "Optimización y reparación de Windows",
    ]),
    ("Soporte técnico", "soporte", ("#2563EB", "#0B1E4A"), [
        "Mesa de ayuda y atención a usuarios",
        "Instalación de Windows, Office y controladores",
        "Impresoras láser y térmicas",
        "Redes LAN: cableado, VLAN y subneteo VLSM",
        "Despliegue automatizado con PowerShell",
    ]),
    ("Programación", "codigo", ("#16A34A", "#052E16"), [
        "Aplicaciones web con React, Vite y Tailwind",
        "APIs REST con Node.js y Express",
        "Autenticación JWT y permisos por rol",
        "Tiempo real con Socket.IO y WebSockets",
        "Aplicaciones de escritorio en Python",
    ]),
    ("Bases de datos", "base", ("#7C3AED", "#2E1065"), [
        "Modelado entidad-relación",
        "Normalización hasta tercera forma normal",
        "MySQL y SQL Server",
        "Transacciones y control de concurrencia",
        "Reportes y análisis con Power BI",
    ]),
]


def foto_base64():
    if not USAR_FOTO:
        return None
    try:
        req = urllib.request.Request(f"https://github.com/{USUARIO}.png?size=360",
                                     headers={"User-Agent": "perfil-generador"})
        with urllib.request.urlopen(req, timeout=30) as r:
            import base64
            return base64.b64encode(r.read()).decode()
    except Exception:
        return None


def svg_artista(d):
    W, H = 880, 372
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="url(#art)"/>',
         f'<rect width="{W}" height="{H}" rx="12" fill="url(#luz)"/>']
    cx, cy, r = 130, 160, 92
    foto = foto_base64()
    p.append(f'<circle cx="{cx}" cy="{cy + 6}" r="{r}" fill="#000" opacity=".35"/>')
    if foto:
        p.append(f'<image href="data:image/png;base64,{foto}" x="{cx - r}" y="{cy - r}" width="{2 * r}" '
                 f'height="{2 * r}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#mono)"/>')
        p.append(txt(cx, cy + 22, "MG", R_FG, 64, 800, extra='text-anchor="middle" letter-spacing="-2"'))
    x = 262
    p.append(f'<circle cx="{x + 9}" cy="82" r="9" fill="#3D91F4"/><path d="M{x + 5} 82l3 3 6-6" stroke="#fff" '
             f'stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    p.append(txt(x + 26, 87, "Perfil profesional de TI", R_FG, 14, 600))
    p.append(txt(x - 4, 168, "Matthew Garay", R_FG, 70, 800, extra='letter-spacing="-2.5"'))
    p.append(txt(x, 204, f"{d['commits_anio']} commits en el último año  •  {len(d['repos'])} repositorios públicos",
                 R_FG, 15.5, 500))
    # áreas
    ax = x
    for nombre, color in [("Mantenimiento", "#F59B23"), ("Soporte técnico", "#4CB3FF"),
                          ("Programación", "#1ED760"), ("Bases de datos", "#B49BFF")]:
        ancho = len(nombre) * 13 * 0.56 + 34
        p.append(f'<rect x="{ax}" y="226" width="{ancho:.0f}" height="30" rx="15" fill="#000" fill-opacity=".35" '
                 f'stroke="#fff" stroke-opacity=".18"/>')
        p.append(f'<circle cx="{ax + 15}" cy="241" r="4.5" fill="{color}"/>')
        p.append(txt(ax + 26, 245.5, nombre, R_FG, 13, 600))
        ax += ancho + 8
    # controles
    y = 316
    p.append(f'<circle cx="68" cy="{y}" r="28" fill="{R_VERDE}"/><path d="M60 {y - 13}v26l21-13z" fill="#000"/>')
    p.append(f'<rect x="116" y="{y - 16}" width="84" height="32" rx="16" fill="none" stroke="#fff" stroke-opacity=".6"/>')
    p.append(txt(158, y + 5, "Seguir", R_FG, 13.5, 700, extra='text-anchor="middle"'))
    p.append(f'<g fill="{R_SUB}"><circle cx="226" cy="{y}" r="2.5"/><circle cx="236" cy="{y}" r="2.5"/>'
             f'<circle cx="246" cy="{y}" r="2.5"/></g>')
    p.append(txt(W - 32, y + 5, "Tecámac, Estado de México", R_SUB, 13.5, extra='text-anchor="end"'))
    defs = (f'<linearGradient id="art" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0F5132"/>'
            f'<stop offset=".75" stop-color="{R_BG}"/></linearGradient>'
            f'<radialGradient id="luz" cx=".15" cy=".1" r=".7"><stop offset="0" stop-color="#1ED760" stop-opacity=".28"/>'
            f'<stop offset="1" stop-color="#1ED760" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="mono" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1ED760"/>'
            f'<stop offset="1" stop-color="#0B4F2B"/></linearGradient>'
            f'<clipPath id="av"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    return svg(W, H, "".join(p), "Matthew Garay: soporte técnico, mantenimiento, programación y bases de datos", defs=defs)


def svg_acerca():
    W = 880
    consola = svg_perfil()
    import re
    m = re.search(r'height="(\d+)" viewBox="0 0 880 (\d+)"', consola)
    alto_c = int(m.group(2))
    ancho_i = W - 64
    alto_i = alto_c * ancho_i / 880
    interior = consola.replace('<svg xmlns="http://www.w3.org/2000/svg" width="880"',
                               f'<svg x="32" y="76" width="{ancho_i}"', 1)
    interior = interior.replace(f'height="{alto_c}" viewBox', f'height="{alto_i:.0f}" viewBox', 1)
    H = int(76 + alto_i + 32)
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{R_BG}"/>',
         txt(32, 50, "Acerca de", R_FG, 24, 800, extra='letter-spacing="-.5"'), interior]
    return svg(W, H, "".join(p), "Acerca de Matthew Garay")


def svg_album(titulo, icono, colores, pistas, uid):
    W, H = 430, 334
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{R_PANEL}"/>',
         f'<rect width="{W}" height="140" rx="12" fill="url(#ab{uid})" opacity=".55"/>']
    p.append(portada(22, 22, 100, icono, colores, f"al{uid}", 6))
    p.append(txt(140, 48, "Álbum", R_FG, 12.5, 600))
    lineas = envolver(titulo, 20)
    for i, linea in enumerate(lineas):
        p.append(txt(138, 80 + i * 26, linea, R_FG, 24, 800, extra='letter-spacing="-.6"'))
    p.append(txt(140, 80 + len(lineas) * 26 + 4, f"Matthew Garay  •  {len(pistas)} canciones", R_SUB, 12.5))
    y = 166
    for i, pista in enumerate(pistas, 1):
        p.append(txt(36, y, i, R_SUB, 13.5, extra='text-anchor="end"'))
        p.append(txt(54, y, pista, R_FG, 13.5))
        y += 34
    defs = (f'<linearGradient id="ab{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{colores[0]}"/>'
            f'<stop offset="1" stop-color="{R_PANEL}"/></linearGradient>')
    return svg(W, H, "".join(p), f"{titulo}: " + ", ".join(pistas), defs=defs)


def svg_seccion(titulo, subtitulo=""):
    W, H = 880, 70
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{R_BG}"/>',
         txt(32, 44, titulo, R_FG, 24, 800, extra='letter-spacing="-.5"')]
    if subtitulo:
        p.append(txt(W - 32, 44, subtitulo, R_SUB, 13.5, extra='text-anchor="end"'))
    return svg(W, H, "".join(p), titulo)


def svg_creditos():
    W = 880
    grupos = [
        ("Lenguajes", "JavaScript, TypeScript, Python, PHP, SQL, PowerShell, Batch, Bash, VB.NET, Rust, Dart, R"),
        ("Frameworks y librerías", "React, Vite, Tailwind CSS, Bootstrap, Node.js, Express, Socket.IO, Flutter, CustomTkinter"),
        ("Bases de datos", "MySQL, SQL Server"),
        ("Sistemas operativos", "Windows 10/11, Windows Server, Ubuntu, Kali Linux, Arch Linux"),
        ("Infraestructura y redes", "Cisco (VLAN, VLSM, enrutamiento), Packet Tracer, VMware, VirtualBox, Docker, AWS"),
        ("Herramientas", "Git, GitHub, VS Code, Visual Studio, Postman, Power BI, Excel, Microsoft Office"),
        ("Metodologías", "Scrum, Kanban, ITIL v4"),
        ("Hardware", "Diagnóstico, reemplazo de componentes, impresoras láser y térmicas, cableado estructurado"),
    ]
    col_w = (W - 64 - 32) / 2
    p = [txt(32, 50, "Créditos", R_FG, 24, 800, extra='letter-spacing="-.5"')]
    alturas = [0, 0]
    for i, (rol, valor) in enumerate(grupos):
        c = i % 2
        x = 32 + c * (col_w + 32)
        y = 92 + alturas[c]  # primera fila justo debajo del título
        p.append(txt(x, y, rol, R_FG, 15, 700))
        lineas = envolver(valor, 54)
        for j, l in enumerate(lineas):
            p.append(txt(x, y + 22 + j * 19, l, R_SUB, 13.5))
        alturas[c] += 22 + len(lineas) * 19 + 22
    H = int(92 + max(alturas) + 6)
    return svg(W, H, f'<rect width="{W}" height="{H}" rx="12" fill="{R_BG}"/>' + "".join(p), "Créditos: stack técnico")


def svg_barra(repo):
    W, H = 880, 88
    pista = PISTAS[0]
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="#000"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="#282828"/>']
    p.append(portada(18, 16, 56, pista[6], pista[7], "bar", 4))
    p.append(txt(88, 40, pista[1], R_FG, 14, 600))
    p.append(txt(88, 60, "Matthew Garay", R_SUB, 12.5))
    p.append(f'<path d="M252 33a6 6 0 0 1 9 0 6 6 0 0 1 9 0c0 6-9 12-9 12s-9-6-9-12z" fill="{R_VERDE}"/>')
    cx = W / 2
    g = (f'<g stroke="{R_SUB}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
         f'<path d="M{cx - 100} 26h5l12 12h7M{cx - 100} 38h5l12-12h7M{cx - 80} 22l4 4-4 4M{cx - 80} 34l4 4-4 4"/>'
         f'<path d="M{cx - 44} 25v14M{cx - 30} 25l-11 7 11 7z" fill="{R_SUB}"/>'
         f'<path d="M{cx + 44} 25v14M{cx + 30} 25l11 7-11 7z" fill="{R_SUB}"/>'
         f'<path d="M{cx + 74} 30v-2a4 4 0 0 1 4-4h14l-3-3M{cx + 96} 34v2a4 4 0 0 1-4 4H{cx + 78}l3 3"/></g>')
    p.append(g)
    p.append(f'<circle cx="{cx}" cy="32" r="16" fill="#fff"/><path d="M{cx - 5} 25v14M{cx + 5} 25v14" '
             f'stroke="#000" stroke-width="3.2" stroke-linecap="round"/>')
    bx, bw = cx - 200, 400
    avance = 0.8
    p.append(txt(bx - 12, 68, "Piloto", R_SUB, 11, extra='text-anchor="end"'))
    p.append(f'<rect x="{bx}" y="62" width="{bw}" height="4" rx="2" fill="#4D4D4D"/>')
    p.append(f'<rect x="{bx}" y="62" width="{bw * avance}" height="4" rx="2" fill="#fff"/>')
    p.append(txt(bx + bw + 12, 68, "Producción", R_SUB, 11))
    p.append(txt(W - 24, 50, f"{repo.get('_commits', 0)} commits", R_SUB, 12, extra='text-anchor="end"'))
    return svg(W, H, "".join(p), "Reproduciendo: Precision HelpDesk")


# ================================================================ main
def main():
    SALIDA.mkdir(exist_ok=True)
    for viejo in SALIDA.glob("*.svg"):
        viejo.unlink()
    d = cargar_datos()
    repos = d["repos"]
    (SALIDA / "artista.svg").write_text(svg_artista(d), encoding="utf-8")
    (SALIDA / "acerca.svg").write_text(svg_acerca(), encoding="utf-8")
    (SALIDA / "discografia.svg").write_text(svg_seccion("Discografía", "4 álbumes, uno por área de trabajo"), encoding="utf-8")
    for i, (titulo, icono, colores, pistas) in enumerate(ALBUMES, 1):
        (SALIDA / f"album-{i}.svg").write_text(svg_album(titulo, icono, colores, pistas, i), encoding="utf-8")
    (SALIDA / "creditos.svg").write_text(svg_creditos(), encoding="utf-8")
    (SALIDA / "barra.svg").write_text(svg_barra(repos[PISTAS[0][0]]), encoding="utf-8")
    (SALIDA / "reproductor.svg").write_text(svg_reproductor(repos[PISTAS[0][0]]), encoding="utf-8")
    total = sum(repos.get(pista[0], {}).get("_commits", 0) for pista in PISTAS)
    (SALIDA / "playlist.svg").write_text(svg_playlist(total), encoding="utf-8")
    for i, pista in enumerate(PISTAS, 1):
        (SALIDA / f"pista-{i:02d}.svg").write_text(svg_pista(i, pista, repos.get(pista[0], {})), encoding="utf-8")
    (SALIDA / "resumen.svg").write_text(svg_resumen(d), encoding="utf-8")
    print("listo:", d["commits_anio"], "commits,", d["contribuciones"], "contribuciones,", len(repos), "repos")


if __name__ == "__main__":
    main()
