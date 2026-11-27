"""Genera los gráficos SVG del perfil de GitHub con datos reales de la API.

Uso:   GITHUB_TOKEN=... python scripts/generar.py
Salida: carpeta assets/

Cada gráfico se genera en dos temas:
  nombre.svg        tema oscuro
  nombre-claro.svg  tema claro (el README elige uno u otro con <picture>)

Secciones (estilo app de música):
  artista.svg        encabezado del perfil
  acerca.svg         tarjeta "Acerca de" con descripción y cifras
  playlist.svg       encabezado de la playlist de proyectos
  pista-*.svg        una fila por proyecto
  discografia.svg    título de la sección de áreas
  album-*.svg        un álbum por área de trabajo
  creditos.svg       stack técnico
  actividad.svg      mapa de calor de contribuciones del último año
  resumen.svg        "Un año en GitHub": cifras, racha y lenguajes
  barra.svg          barra de reproducción
  contacto-*.svg     iconos de contacto
  boton-*.svg        botones Seguir y Compartir
"""
import base64
import json
import math
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from datetime import date
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
    ("Precision-Truck-Parts---Help-Desk", "Precision HelpDesk", "Mesa de ayuda e inventario de TI",
     "Bases de datos", "React, Node.js, MySQL", "piloto", "ticket", ("#1D4ED8", "#0B1E4A")),
    ("IP-Scanner", "IP Inspector", "Escáner de red y puertos con interfaz gráfica",
     "Redes", "Python, CustomTkinter", "release", "radar", ("#0F766E", "#062925")),
    ("Cerberus", "Cerberus", "HR & Biometric System: nómina y asistencia",
     "Bases de datos", "VB.NET, MySQL, SQL Server", "activo", "monitor", ("#7C3AED", "#24104A")),
    ("Microsoft-Office-Installer", "Office Installer", "Instala Office LTSC con un solo comando",
     "Soporte técnico", "PowerShell, HTML", "release", "descarga", ("#B91C1C", "#3A0A0A")),
    ("Adobe-Genuine-Service-AGS-Alert", "Adobe AGS Alert", "Desactiva Adobe Genuine Service de forma reversible",
     "Mantenimiento", "PowerShell", "activo", "llave-cifrado", ("#B45309", "#3B1D05")),
]

# Tecnologías que se muestran en la sección de créditos (sin C#, Docker, VB.NET ni ZKTeco)
TECNOLOGIAS = [
    ("java", "Java"), ("nodejs", "Node.js"), ("python", "Python"), ("c", "C"),
    ("powershell", "PowerShell"), ("react", "React"), ("ts", "TypeScript"), ("html", "HTML/CSS"),
    ("css", "CSS"), ("mysql", "MySQL"), ("mssql", "SQL Server"), ("linux", "Linux"),
    ("windows", "Windows Server"), ("git", "Git"),
]

COLORES_LENGUAJE = {
    "JavaScript": "#F1E05A", "TypeScript": "#3178C6", "Python": "#3572A5",
    "PowerShell": "#5391FE", "Batch": "#C1F12E", "PHP": "#7A86B8",
    "HTML": "#E34C26", "CSS": "#8F5FD0", "Rust": "#DEA584", "Dart": "#00B4AB",
    "R": "#198CE7", "Shell": "#89E051", "Visual Basic .NET": "#945DB7",
    "Prolog": "#C0475F", "Dockerfile": "#4A9FE0",
}

# ================================================================ temas
# Colores de cada tema. Las mosaicos de iconos son siempre blancos para que
# los logos oscuros (MySQL, GitHub...) se vean en cualquier fondo.
TEMAS = {
    "oscuro": {
        "bg": "#121212", "panel": "#1E1E1E", "fg": "#FFFFFF", "sub": "#B3B3B3", "txt2": "#E0E0E0",
        "verde": "#1ED760", "linea": "#2A2A2A", "gris": "#7A7A7A", "borde": "#2A2A2A",
        "pastilla": "#000000", "pastilla_op": ".35", "pastilla_borde": "#FFFFFF",
        "art1": "#0F5132", "art2": "#121212", "luz": "#1ED760",
        "ac1": "#14532D", "ac2": "#0C2D48", "ac_txt": "#F0F0F0",
        "acv": "#000000", "acv_op": ".45", "sombra": "#000000", "play": "#000000",
        "barra_bg": "#000000", "barra_borde": "#282828", "barra_pista": "#4D4D4D", "barra_avance": "#FFFFFF",
        "pl1": "#1F3B2A", "pl2": "#121212",
        "act": ["#2A2A2A", "#0E4429", "#006D32", "#26A641", "#39D353"],
    },
    "claro": {
        "bg": "#FFFFFF", "panel": "#F3F4F6", "fg": "#111827", "sub": "#4B5563", "txt2": "#1F2937",
        "verde": "#15803D", "linea": "#E5E7EB", "gris": "#6B7280", "borde": "#E5E7EB",
        "pastilla": "#111827", "pastilla_op": ".06", "pastilla_borde": "#111827",
        "art1": "#BBF7D0", "art2": "#FFFFFF", "luz": "#22C55E",
        "ac1": "#DCFCE7", "ac2": "#DBEAFE", "ac_txt": "#111827",
        "acv": "#FFFFFF", "acv_op": "0", "sombra": "#94A3B8", "play": "#FFFFFF",
        "barra_bg": "#F3F4F6", "barra_borde": "#E5E7EB", "barra_pista": "#D1D5DB", "barra_avance": "#111827",
        "pl1": "#D1FAE5", "pl2": "#FFFFFF",
        "act": ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"],
    },
}
C = dict(TEMAS["oscuro"])  # tema activo; se cambia con aplicar_tema()
MOSAICO = "#FFFFFF"
MOSAICO_BORDE = "#D1D5DB"
SANS = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"


def aplicar_tema(nombre):
    C.clear()
    C.update(TEMAS[nombre])


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

    # calendario de contribuciones (matriz: una lista de 7 días por semana)
    c = graphql("""query($u:String!){user(login:$u){contributionsCollection{
        totalCommitContributions restrictedContributionsCount
        contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}""",
                u=USUARIO)["user"]["contributionsCollection"]
    matriz = [[(date.fromisoformat(d["date"]), d["contributionCount"]) for d in w["contributionDays"]]
              for w in c["contributionCalendar"]["weeks"]]
    return {
        "repos": nombres,
        "lenguajes": bytes_lenguaje.most_common(),
        "commits_anio": c["totalCommitContributions"] + c["restrictedContributionsCount"],
        "contribuciones": c["contributionCalendar"]["totalContributions"],
        "matriz": matriz,
        "semanas": [sum(v for _, v in sem) for sem in matriz],
        "dias": [x for sem in matriz for x in sem],
    }


# ================================================================ SVG básico
def txt(x, y, s, color, size, peso=400, fuente=SANS, extra=""):
    return (f'<text x="{x:.1f}" y="{y:.1f}" fill="{color}" font-size="{size}" font-weight="{peso}" '
            f'font-family="{fuente}" xml:space="preserve" {extra}>{escape(str(s))}</text>')


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


def recortar(s, n):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


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
    "codigo": '<path d="M38 32L20 50l18 18M62 32l18 18-18 18M55 26L45 74"/>',
    "base": ('<ellipse cx="50" cy="28" rx="24" ry="8"/><path d="M26 28v44c0 4 11 8 24 8s24-4 24-8V28"/>'
             '<path d="M26 50c0 4 11 8 24 8s24-4 24-8"/>'),
    "soporte": ('<path d="M26 56v-8a24 24 0 0 1 48 0v8"/><rect x="20" y="54" width="12" height="18" rx="4"/>'
                '<rect x="68" y="54" width="12" height="18" rx="4"/><path d="M74 72c0 6-8 8-18 8"/>'),
}


def portada(x, y, tam, icono, colores, uid, radio=4):
    c1, c2 = colores
    escala = tam / 100
    return (f'<defs><linearGradient id="g{uid}" x1="0" y1="0" x2="1" y2="1">'
            f'<stop offset="0" stop-color="{c1}"/><stop offset="1" stop-color="{c2}"/></linearGradient></defs>'
            f'<rect x="{x}" y="{y}" width="{tam}" height="{tam}" rx="{radio}" fill="url(#g{uid})"/>'
            f'<g transform="translate({x} {y}) scale({escala})" fill="none" stroke="#fff" '
            f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{ICONOS[icono]}</g>')


# ================================================================ playlist
COLS = {"num": 40, "img": 60, "titulo": 124, "area": 440, "tec": 600, "fin": 852}


def svg_playlist(total_commits, n_proyectos):
    W, H = 880, 230
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="url(#pl)"/>']
    # mosaico de portadas
    for i, pista in enumerate(PISTAS[:4]):
        x, y = 32 + (i % 2) * 80, 28 + (i // 2) * 80
        p.append(portada(x, y, 80, pista[6], pista[7], f"m{i}", 0))
    p.append(txt(214, 52, "Playlist pública", C["fg"], 13, 600))
    p.append(txt(210, 108, "Proyectos", C["fg"], 54, 800, extra='letter-spacing="-1.5"'))
    p.append(txt(214, 144, "Soporte, mantenimiento, redes, programación y bases de datos.", C["sub"], 14.5))
    p.append(txt(214, 172, f"Creada por Matthew Garay  •  {n_proyectos} proyectos  •  {total_commits} commits  •  "
                           f"Actualizada {fecha_corta(date.today())}", C["fg"], 13, 500))
    yc = 214
    p.append(txt(COLS["num"], yc, "#", C["sub"], 13, extra='text-anchor="end"'))
    p.append(txt(COLS["titulo"], yc, "Título", C["sub"], 13))
    p.append(txt(COLS["area"], yc, "Área", C["sub"], 13))
    p.append(txt(COLS["tec"], yc, "Tecnologías", C["sub"], 13))
    p.append(txt(COLS["fin"], yc, "Estado", C["sub"], 13, extra='text-anchor="end"'))
    p.append(f'<line x1="24" x2="{W - 24}" y1="{H - 4}" y2="{H - 4}" stroke="{C["linea"]}"/>')
    defs = (f'<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["pl1"]}"/>'
            f'<stop offset="1" stop-color="{C["pl2"]}"/></linearGradient>')
    return svg(W, H, "".join(p), "Playlist de proyectos", defs=defs)


def svg_pista(i, pista, repo):
    W, H = 880, 64
    nombre_repo, titulo, desc, area, tec, estado, icono, colores = pista
    p = [f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>']
    sonando = i == 1
    if sonando:
        for k, (x, retraso) in enumerate([(28, 0), (33.5, .35), (39, .7)]):
            p.append(f'<rect class="eq" style="animation-delay:{retraso}s" x="{x}" y="26" width="3.5" '
                     f'height="16" rx="1" fill="{C["verde"]}"/>')
    else:
        p.append(txt(COLS["num"], 38, i, C["sub"], 15, extra='text-anchor="end"'))
    p.append(portada(COLS["img"], 8, 48, icono, colores, f"p{i}"))
    p.append(txt(COLS["titulo"], 29, titulo, C["verde"] if sonando else C["fg"], 16, 600))
    p.append(txt(COLS["titulo"], 49, recortar(desc, 46), C["sub"], 13))
    p.append(f'<circle cx="{COLS["area"] + 4}" cy="{34}" r="4" fill="{AREAS[area]}"/>')
    p.append(txt(COLS["area"] + 14, 38.5, area, C["sub"], 13.5))
    p.append(txt(COLS["tec"], 38.5, recortar(tec, 26), C["sub"], 13.5))
    if estado == "release":
        estado = repo.get("_version") or "release"
    color = {"en desarrollo": "#F59B23", "académico": C["sub"]}.get(estado, C["verde"])
    p.append(txt(COLS["fin"], 31, estado, color, 13, 600, extra='text-anchor="end"'))
    estrellas = repo.get("stargazers_count", 0)
    p.append(txt(COLS["fin"], 50, f"♥ {estrellas}  •  {repo.get('_commits', 0)} commits", C["sub"], 12,
                 extra='text-anchor="end"'))
    estilo = ("" if not sonando else
              ".eq{transform-box:fill-box;transform-origin:center bottom;animation:eq 1.1s ease-in-out infinite}"
              "@keyframes eq{0%,100%{transform:scaleY(.35)}50%{transform:scaleY(1)}}"
              "@media (prefers-reduced-motion:reduce){.eq{animation:none}}")
    return svg(W, H, "".join(p), f"{i}. {titulo}: {desc}", estilo)


# ================================================================ actividad (mapa de calor)
def svg_actividad(d):
    W = 880
    matriz = d["matriz"]
    paso = (W - 64) / len(matriz)
    cel = paso - 3
    x0, y0 = 32, 110
    ly = y0 + 7 * paso + 22
    H = int(ly + 36)
    maxv = max((v for sem in matriz for _, v in sem), default=0) or 1
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{C["bg"]}"/>',
         txt(32, 50, "Actividad", C["fg"], 24, 800, extra='letter-spacing="-.5"'),
         txt(32, 76, f"{d['contribuciones']} contribuciones en los últimos 12 meses", C["sub"], 14)]
    vistos = set()
    for col, sem in enumerate(matriz):
        f0 = sem[0][0]
        if f0.month not in vistos and f0.day <= 7:
            vistos.add(f0.month)
            p.append(txt(x0 + col * paso, y0 - 12, MESES[f0.month - 1], C["sub"], 11.5))
        for fila, (_, v) in enumerate(sem):
            nivel = 0 if v == 0 else min(4, max(1, math.ceil(v * 4 / maxv)))
            p.append(f'<rect x="{x0 + col * paso:.1f}" y="{y0 + fila * paso:.1f}" width="{cel:.1f}" '
                     f'height="{cel:.1f}" rx="3" fill="{C["act"][nivel]}"/>')
    lx = W - 230
    p.append(txt(lx, ly + 10, "Menos", C["sub"], 11.5))
    for k in range(5):
        p.append(f'<rect x="{lx + 46 + k * 16}" y="{ly}" width="12" height="12" rx="3" fill="{C["act"][k]}"/>')
    p.append(txt(lx + 46 + 5 * 16 + 4, ly + 10, "Más", C["sub"], 11.5))
    return svg(W, H, "".join(p), f"Actividad: {d['contribuciones']} contribuciones en el último año")


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
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{C["bg"]}"/>',
         f'<rect width="{W}" height="{H}" rx="12" fill="url(#rs)"/>']
    p.append(txt(32, 58, "Un año en GitHub", C["fg"], 36, 800, extra='letter-spacing="-1"'))
    p.append(txt(32, 84, "Contribuciones en GitHub durante los últimos 12 meses", C["sub"], 14.5))

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
                      f'height="{2 * h:.1f}" rx="{min(2.5, (paso - 2.5) / 2):.1f}" fill="{C["verde"]}" opacity="{op}"/>')
    p.append("".join(barras))
    vistos = set()
    for i in range(len(semanas)):
        dia = d["dias"][min(i * 7, len(d["dias"]) - 1)][0]
        if dia.month not in vistos and dia.day <= 7:
            vistos.add(dia.month)
            p.append(txt(x0 + i * paso, centro + alto + 24, MESES[dia.month - 1], C["sub"], 11.5))

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
        p.append(txt(x, y, n, C["fg"], 34, 800, extra='letter-spacing="-1"'))
        p.append(txt(x, y + 24, etiqueta, C["sub"], 13))

    # lenguajes
    y = 392
    p.append(f'<line x1="32" x2="{W - 32}" y1="{y - 22}" y2="{y - 22}" stroke="{C["linea"]}"/>')
    p.append(txt(32, y + 6, "Lenguajes más usados", C["fg"], 16, 700))
    total = sum(b for _, b in d["lenguajes"]) or 1
    top = d["lenguajes"][:5]
    col_w = (W - 64) / 5
    for i, (lang, b) in enumerate(top):
        x = 32 + i * col_w
        pct = b * 100 / total
        p.append(txt(x, y + 44, f"{i + 1}", C["sub"], 22, 800))
        p.append(txt(x + 26, y + 44, lang, C["fg"], 15, 600))
        p.append(f'<rect x="{x}" y="{y + 60}" width="{col_w - 24:.1f}" height="4" rx="2" fill="{C["linea"]}"/>')
        p.append(f'<rect x="{x}" y="{y + 60}" width="{(col_w - 24) * b / top[0][1]:.1f}" '
                 f'height="4" rx="2" fill="{COLORES_LENGUAJE.get(lang, C["verde"])}"/>')
        p.append(txt(x, y + 84, f"{pct:.0f} % del código", C["sub"], 12))
    p.append(txt(W - 32, H - 18, f"{len(d['repos'])} repositorios públicos  •  actualizado el {fecha_corta(date.today())}",
                 C["gris"], 11.5, extra='text-anchor="end"'))
    defs = (f'<radialGradient id="rs" cx="0.85" cy="0" r="0.9"><stop offset="0" stop-color="{C["verde"]}" stop-opacity=".22"/>'
            f'<stop offset="1" stop-color="{C["verde"]}" stop-opacity="0"/></radialGradient>')
    return svg(W, H, "".join(p), f"Un año en GitHub: {d['commits_anio']} commits, racha de {mayor} días", defs=defs)


# ================================================================ página de artista
# Cambia a True cuando subas una foto real a tu perfil de GitHub.
USAR_FOTO = False

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
        "Despliegue automatizado con PowerShell",
        "Instalación y configuración de equipos de cómputo",
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
    ("Redes y conectividad", "red", ("#0F766E", "#062925"), [
        "Cableado estructurado y conectores RJ45",
        "Redes LAN y segmentación con VLAN",
        "Subneteo VLSM por áreas",
        "Diseño de topologías en Cisco Packet Tracer",
        "Configuración básica de switches",
        "Diagnóstico de conectividad y latencia",
    ]),
    ("Seguridad informática", "llave-cifrado", ("#BE123C", "#3B0A1B"), [
        "Escaneo de puertos y hosts activos",
        "Desactivación de servicios innecesarios",
        "Control de acceso y permisos por rol",
        "Respaldos automatizados",
        "Auditoría de software y licencias",
        "Actualizaciones y parches de seguridad",
    ]),
]

AREAS_ARTISTA = [("Mantenimiento", "#F59B23"), ("Soporte técnico", "#4CB3FF"),
                 ("Programación", "#1ED760"), ("Bases de datos", "#B49BFF")]


def foto_base64():
    if not USAR_FOTO:
        return None
    try:
        req = urllib.request.Request(f"https://github.com/{USUARIO}.png?size=360",
                                     headers={"User-Agent": "perfil-generador"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return base64.b64encode(r.read()).decode()
    except Exception:
        return None


def svg_artista(d):
    W, H = 880, 290
    cx, cy, r = 130, 150, 92
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="url(#art)"/>',
         f'<rect width="{W}" height="{H}" rx="12" fill="url(#luz)"/>',
         f'<circle cx="{cx}" cy="{cy + 6}" r="{r}" fill="{C["sombra"]}" opacity=".35"/>']
    foto = foto_base64()
    if foto:
        p.append(f'<image href="data:image/png;base64,{foto}" x="{cx - r}" y="{cy - r}" width="{2 * r}" '
                 f'height="{2 * r}" clip-path="url(#av)" preserveAspectRatio="xMidYMid slice"/>')
    else:
        p.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="url(#mono)"/>')
        p.append(txt(cx, cy + 22, "MG", "#FFFFFF", 64, 800, extra='text-anchor="middle" letter-spacing="-2"'))
    x = 262
    p.append(txt(x, 92, "Software Developer & IT Systems Specialist", C["sub"], 14, 600))
    p.append(txt(x - 4, 176, "Matthew Garay", C["fg"], 70, 800, extra='letter-spacing="-2.5"'))
    p.append(f'<circle cx="{x + 5}" cy="212" r="5" fill="{C["verde"]}"/>')
    p.append(txt(x + 18, 217, "Abierto a proyectos", C["fg"], 16, 600))
    ax = x
    for nombre, color in AREAS_ARTISTA:
        ancho = len(nombre) * 13 * 0.56 + 34
        p.append(f'<rect x="{ax}" y="238" width="{ancho:.0f}" height="30" rx="15" fill="{C["pastilla"]}" '
                 f'fill-opacity="{C["pastilla_op"]}" stroke="{C["pastilla_borde"]}" stroke-opacity=".18"/>')
        p.append(f'<circle cx="{ax + 15}" cy="253" r="4.5" fill="{color}"/>')
        p.append(txt(ax + 26, 257.5, nombre, C["fg"], 13, 600))
        ax += ancho + 8
    defs = (f'<linearGradient id="art" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["art1"]}"/>'
            f'<stop offset=".75" stop-color="{C["art2"]}"/></linearGradient>'
            f'<radialGradient id="luz" cx=".15" cy=".1" r=".7"><stop offset="0" stop-color="{C["luz"]}" stop-opacity=".28"/>'
            f'<stop offset="1" stop-color="{C["luz"]}" stop-opacity="0"/></radialGradient>'
            f'<linearGradient id="mono" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#1ED760"/>'
            f'<stop offset="1" stop-color="#0B4F2B"/></linearGradient>'
            f'<clipPath id="av"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>')
    return svg(W, H, "".join(p), "Matthew Garay: soporte técnico, mantenimiento, programación y bases de datos", defs=defs)


BIO = [
    "Perfil híbrido en TI que combina el desarrollo de software, con una sólida base en soluciones web, "
    "y el soporte técnico. Tengo dominio en la gestión de bases de datos para análisis, así como en el "
    "mantenimiento integral de hardware y software.",
    "Me distingo por un enfoque resolutivo y paciente para encontrar la raíz de cada problema, y me apasiona "
    "simplificar la tecnología para que sea una herramienta de valor.",
    "Especialidad principal: Desarrollo web y soporte técnico de TI.",
    "Enfoque: encontrar la causa raíz y dejar la solución documentada.",
]


def svg_acerca(d, n_proyectos, n_areas):
    W = 880
    cx0, cy0, cw = 32, 74, W - 64
    cifras = [(str(d["commits_anio"]), "commits en el último año"),
              (str(n_proyectos), "repositorios públicos"),
              (str(n_areas), "áreas de trabajo")]
    lineas = [envolver(par, 92) for par in BIO]
    alto_bio = sum(len(l) * 24 for l in lineas) + (len(lineas) - 1) * 12
    ch = 28 + 100 + alto_bio + 30
    H = int(cy0 + ch + 32)
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{C["bg"]}"/>',
         txt(32, 50, "Acerca de", C["fg"], 24, 800, extra='letter-spacing="-.5"'),
         f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="10" fill="url(#ac)"/>',
         f'<g clip-path="url(#acc)" opacity=".5">'
         f'<circle cx="{cx0 + cw - 90}" cy="{cy0 + 40}" r="120" fill="#F59B23" opacity=".35"/>'
         f'<circle cx="{cx0 + cw - 10}" cy="{cy0 + 130}" r="110" fill="#4CB3FF" opacity=".35"/>'
         f'<circle cx="{cx0 + cw - 40}" cy="{cy0 + ch - 20}" r="90" fill="#B49BFF" opacity=".3"/></g>',
         f'<rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="10" fill="url(#acv)"/>']
    x, y = cx0 + 28, cy0 + 28
    for i, (n, etiqueta) in enumerate(cifras):
        xi = x + i * 210
        p.append(txt(xi, y + 44, n, C["fg"], 44, 800, extra='letter-spacing="-1.5"'))
        p.append(txt(xi, y + 70, etiqueta, C["txt2"], 14))
    y += 100
    for lin in lineas:
        for l in lin:
            y += 24
            p.append(txt(x, y, l, C["ac_txt"], 15))
        y += 12
    defs = (f'<linearGradient id="ac" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["ac1"]}"/>'
            f'<stop offset="1" stop-color="{C["ac2"]}"/></linearGradient>'
            f'<linearGradient id="acv" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["acv"]}" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="{C["acv"]}" stop-opacity="{C["acv_op"]}"/></linearGradient>'
            f'<clipPath id="acc"><rect x="{cx0}" y="{cy0}" width="{cw}" height="{ch}" rx="10"/></clipPath>')
    return svg(W, H, "".join(p), "Acerca de Matthew Garay. " + " ".join(BIO), defs=defs)


def svg_album(titulo, icono, colores, pistas, uid, anio=2026):
    W, H = 430, 382
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{C["panel"]}"/>',
         f'<rect width="{W}" height="140" rx="12" fill="url(#ab{uid})" opacity=".55"/>']
    p.append(portada(22, 22, 100, icono, colores, f"al{uid}", 6))
    p.append(txt(140, 48, f"Álbum  •  {anio}", C["fg"], 12.5, 600))
    lineas = envolver(titulo, 20)
    for i, linea in enumerate(lineas):
        p.append(txt(138, 80 + i * 26, linea, C["fg"], 24, 800, extra='letter-spacing="-.6"'))
    p.append(txt(140, 80 + len(lineas) * 26 + 4, f"Matthew Garay  •  {len(pistas)} canciones", C["sub"], 12.5))
    y = 166
    for i, pista in enumerate(pistas, 1):
        p.append(txt(36, y, i, C["sub"], 13.5, extra='text-anchor="end"'))
        p.append(txt(54, y, pista, C["fg"], 13.5))
        y += 34
    defs = (f'<linearGradient id="ab{uid}" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{colores[0]}"/>'
            f'<stop offset="1" stop-color="{C["panel"]}"/></linearGradient>')
    return svg(W, H, "".join(p), f"{titulo}: " + ", ".join(pistas), defs=defs)


def svg_seccion(titulo, subtitulo=""):
    W, H = 880, 70
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{C["bg"]}"/>',
         txt(32, 44, titulo, C["fg"], 24, 800, extra='letter-spacing="-.5"')]
    if subtitulo:
        p.append(txt(W - 32, 44, subtitulo, C["sub"], 13.5, extra='text-anchor="end"'))
    return svg(W, H, "".join(p), titulo)


# ================================================================ tecnologías y créditos
_ICONOS_CACHE = {}


def icono_datauri(nombre):
    """Descarga el icono de skillicons y lo devuelve como data URI (para incrustarlo en el SVG)."""
    if nombre not in _ICONOS_CACHE:
        try:
            req = urllib.request.Request(f"https://skillicons.dev/icons?i={nombre}",
                                         headers={"User-Agent": "perfil-generador"})
            with urllib.request.urlopen(req, timeout=30) as r:
                datos = r.read()
            _ICONOS_CACHE[nombre] = "data:image/svg+xml;base64," + base64.b64encode(datos).decode("ascii")
        except (urllib.error.URLError, TimeoutError):
            _ICONOS_CACHE[nombre] = None
    return _ICONOS_CACHE[nombre]


def cuadros_tecnologias(items, y0, cols=9, tam=80, sep=14):
    """Mosaicos blancos del mismo tamaño: logo arriba y nombre abajo (siempre legibles en ambos temas)."""
    W = 880
    ancho = cols * tam + (cols - 1) * sep
    x0 = (W - ancho) / 2
    p = []
    for idx, (clave, etiqueta) in enumerate(items):
        x = x0 + (idx % cols) * (tam + sep)
        y = y0 + (idx // cols) * (tam + sep)
        p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{tam}" height="{tam}" rx="14" fill="{MOSAICO}" '
                 f'stroke="{MOSAICO_BORDE}"/>')
        uri = icono_datauri(clave) if clave and clave != "mssql" else None
        if clave == "mssql":
            # skillicons no tiene SQL Server: icono propio (base de datos, color de SQL Server)
            ix, iy = x + (tam - 40) / 2, y + 8
            p.append(f'<rect x="{ix:.1f}" y="{iy:.1f}" width="40" height="40" rx="8" fill="#CC2927"/>'
                     f'<g transform="translate({ix:.1f} {iy:.1f}) scale(.4)" fill="none" stroke="#fff" '
                     f'stroke-width="5" stroke-linecap="round" stroke-linejoin="round">{ICONOS["base"]}</g>')
            p.append(txt(x + tam / 2, y + 68, etiqueta, "#111827", 10.5, 600, extra='text-anchor="middle"'))
        elif uri:
            p.append(f'<image href="{uri}" x="{x + (tam - 40) / 2:.1f}" y="{y + 8:.1f}" width="40" height="40"/>')
            p.append(txt(x + tam / 2, y + 68, etiqueta, "#111827", 10.5, 600, extra='text-anchor="middle"'))
        else:
            p.append(txt(x + tam / 2, y + 46, etiqueta, "#111827", 13, 700, extra='text-anchor="middle"'))
    filas = (len(items) + cols - 1) // cols
    return "".join(p), filas * tam + (filas - 1) * sep


def svg_creditos():
    W = 880
    grupos = [
        ("Producido por", "Matthew Garay"),
        ("Backend y bases de datos", "Node.js, Express, PHP, Python, Java, C, VB.NET, MySQL, SQL Server"),
        ("Frontend y UI", "React, TypeScript, JavaScript, Tailwind CSS, Vite, HTML/CSS, Bootstrap, Flutter"),
        ("Infraestructura, redes y soporte TI", "Windows, Windows Server, Linux, PowerShell, Batch, Git, "
         "AWS, Cisco Packet Tracer, redes LAN y VLAN"),
        ("Herramientas", "Git, GitHub, VS Code, Visual Studio, Postman, Power BI, Excel"),
    ]
    col_w = (W - 64 - 32) / 2
    p = [txt(32, 50, "Créditos", C["fg"], 24, 800, extra='letter-spacing="-.5"')]
    alturas = [0, 0]
    for i, (rol, valor) in enumerate(grupos):
        c = i % 2
        x = 32 + c * (col_w + 32)
        y = 92 + alturas[c]
        p.append(txt(x, y, rol, C["fg"], 15, 700))
        lineas = envolver(valor, 54)
        for j, l in enumerate(lineas):
            p.append(txt(x, y + 22 + j * 19, l, C["sub"], 13.5))
        alturas[c] += 22 + len(lineas) * 19 + 22
    y_logos = 92 + max(alturas) + 18
    p.append(txt(32, y_logos, "Tecnologías", C["fg"], 15, 700))
    bloque, alto = cuadros_tecnologias(TECNOLOGIAS, y_logos + 16)
    p.append(bloque)
    H = int(y_logos + 16 + alto + 20)
    return svg(W, H, f'<rect width="{W}" height="{H}" rx="12" fill="{C["bg"]}"/>' + "".join(p),
               "Créditos: stack técnico y tecnologías")


def svg_contacto(clave, etiqueta):
    """Mosaico blanco de 72 px con solo el icono (sin texto)."""
    tam = 72
    uri = icono_datauri(clave)
    p = [f'<rect x=".5" y=".5" width="{tam - 1}" height="{tam - 1}" rx="16" fill="{MOSAICO}" stroke="{MOSAICO_BORDE}"/>']
    if uri:
        p.append(f'<image href="{uri}" x="16" y="16" width="40" height="40"/>')
    else:
        p.append(txt(tam / 2, tam / 2 + 6, etiqueta[0], "#111827", 22, 800, extra='text-anchor="middle"'))
    return svg(tam, tam, "".join(p), etiqueta)


def svg_boton(texto, relleno, color_txt, borde):
    W, H = 150, 44
    p = [f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="22" fill="{relleno}" stroke="{borde}"/>',
         txt(W / 2, 28, texto, color_txt, 15, 700, extra='text-anchor="middle"')]
    return svg(W, H, "".join(p), texto)


# ================================================================ barra de reproducción
def svg_barra(n_proyectos, total_commits):
    W, H = 880, 88
    p = [f'<rect width="{W}" height="{H}" rx="12" fill="{C["barra_bg"]}"/>',
         f'<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="12" fill="none" stroke="{C["barra_borde"]}"/>']
    for i, (_, icono, colores, _) in enumerate(ALBUMES[:4]):
        p.append(portada(18 + (i % 2) * 28, 16 + (i // 2) * 28, 28, icono, colores, f"bar{i}", 0))
    p.append(txt(88, 40, "Proyectos", C["fg"], 14, 600))
    p.append(txt(88, 60, "Matthew Garay", C["sub"], 12.5))
    p.append(f'<path d="M190 33a6 6 0 0 1 9 0 6 6 0 0 1 9 0c0 6-9 12-9 12s-9-6-9-12z" fill="{C["verde"]}"/>')
    cx = W / 2
    p.append(f'<g stroke="{C["sub"]}" stroke-width="2" fill="none" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M{cx - 100} 26h5l12 12h7M{cx - 100} 38h5l12-12h7M{cx - 80} 22l4 4-4 4M{cx - 80} 34l4 4-4 4" stroke="{C["verde"]}"/>'
             f'<path d="M{cx - 44} 25v14M{cx - 30} 25l-11 7 11 7z" fill="{C["sub"]}"/>'
             f'<path d="M{cx + 44} 25v14M{cx + 30} 25l11 7-11 7z" fill="{C["sub"]}"/>'
             f'<path d="M{cx + 74} 30v-2a4 4 0 0 1 4-4h14l-3-3M{cx + 96} 34v2a4 4 0 0 1-4 4H{cx + 78}l3 3"/></g>')
    p.append(f'<circle cx="{cx}" cy="32" r="16" fill="{C["barra_avance"]}"/>'
             f'<path d="M{cx - 5} 25v14M{cx + 5} 25v14" stroke="{C["barra_bg"]}" stroke-width="3.2" stroke-linecap="round"/>')
    bx, bw = cx - 170, 340
    p.append(txt(bx - 12, 68, f"{n_proyectos} proyectos", C["sub"], 11, extra='text-anchor="end"'))
    p.append(f'<rect x="{bx}" y="62" width="{bw}" height="4" rx="2" fill="{C["barra_pista"]}"/>')
    p.append(f'<rect class="avance" x="{bx}" y="62" width="{bw}" height="4" rx="2" fill="{C["barra_avance"]}"/>')
    p.append(txt(bx + bw + 12, 68, f"{total_commits} commits", C["sub"], 11))
    vx = W - 150
    p.append(f'<g fill="none" stroke="{C["sub"]}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
             f'<path d="M{vx} 40h5l7 6V26l-7 6h-5z" fill="{C["sub"]}"/><path d="M{vx + 17} 31a5 5 0 0 1 0 6"/></g>')
    p.append(f'<rect x="{vx + 30}" y="34" width="96" height="4" rx="2" fill="{C["barra_pista"]}"/>')
    p.append(f'<rect x="{vx + 30}" y="34" width="70" height="4" rx="2" fill="{C["barra_avance"]}"/>')
    estilo = (".avance{transform-box:fill-box;transform-origin:left center;transform:scaleX(.62);"
              "animation:avanzar 45s linear infinite}"
              "@keyframes avanzar{from{transform:scaleX(.02)}to{transform:scaleX(1)}}"
              "@media (prefers-reduced-motion:reduce){.avance{animation:none}}")
    return svg(W, H, "".join(p), "Reproduciendo: Proyectos de Matthew Garay", estilo)


# ================================================================ main
def main():
    SALIDA.mkdir(exist_ok=True)
    for viejo in SALIDA.glob("*.svg"):
        viejo.unlink()
    d = cargar_datos()
    repos = d["repos"]
    total = sum(repos.get(pista[0], {}).get("_commits", 0) for pista in PISTAS)

    def escribir(nombre, generar):
        """Escribe la versión oscura (nombre.svg) y la clara (nombre-claro.svg)."""
        for tema, sufijo in (("oscuro", ""), ("claro", "-claro")):
            aplicar_tema(tema)
            (SALIDA / f"{nombre}{sufijo}.svg").write_text(generar(), encoding="utf-8")

    escribir("artista", lambda: svg_artista(d))
    escribir("acerca", lambda: svg_acerca(d, len(repos), len(ALBUMES)))
    escribir("playlist", lambda: svg_playlist(total, len(PISTAS)))
    for i, pista in enumerate(PISTAS, 1):
        escribir(f"pista-{i:02d}", lambda i=i, pista=pista: svg_pista(i, pista, repos.get(pista[0], {})))
    escribir("discografia", lambda: svg_seccion("Discografía", "Lanzamientos populares • Álbumes • Sencillos y EP"))
    for i, (titulo, icono, colores, pistas) in enumerate(ALBUMES, 1):
        escribir(f"album-{i}", lambda t=titulo, ic=icono, co=colores, pi=pistas, i=i: svg_album(t, ic, co, pi, i))
    escribir("creditos", svg_creditos)
    escribir("actividad", lambda: svg_actividad(d))
    escribir("resumen", lambda: svg_resumen(d))
    escribir("contacto", lambda: svg_seccion("Contacto", "Escríbeme o sígueme"))
    escribir("barra", lambda: svg_barra(len(PISTAS), total))

    # iconos de contacto y botones: mosaicos blancos, iguales en ambos temas
    aplicar_tema("oscuro")
    for clave, nombre in [("gmail", "correo"), ("linkedin", "linkedin"), ("github", "github")]:
        (SALIDA / f"contacto-{nombre}.svg").write_text(svg_contacto(clave, nombre.capitalize()), encoding="utf-8")
    (SALIDA / "boton-seguir.svg").write_text(svg_boton("Seguir", C["verde"], "#000000", C["verde"]), encoding="utf-8")
    (SALIDA / "boton-compartir.svg").write_text(svg_boton("Compartir", "#FFFFFF", "#111827", "#D1D5DB"), encoding="utf-8")
    print("listo:", d["commits_anio"], "commits,", d["contribuciones"], "contribuciones,", len(repos), "repos")


if __name__ == "__main__":
    main()
