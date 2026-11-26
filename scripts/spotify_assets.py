"""Genera los SVG del README con estilo Spotify en assets/spotify/.

Ejecutar desde la raíz del repo:  python scripts/spotify_assets.py
Los degradados van dentro de la imagen, así que se ven igual en modo claro y oscuro.
"""
import os
from xml.sax.saxutils import escape

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
SALIDA = os.path.join(RAIZ, "assets", "spotify")
VERDE = "#1DB954"
FUENTE = "Segoe UI, Helvetica, Arial, sans-serif"


def escribir(nombre, ancho, alto, cuerpo, defs=""):
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{ancho}" height="{alto}" '
        f'viewBox="0 0 {ancho} {alto}" role="img">\n'
        f"<defs>{defs}</defs>\n{cuerpo}\n</svg>\n"
    )
    os.makedirs(SALIDA, exist_ok=True)
    with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8") as f:
        f.write(svg)


def hero():
    defs = (
        f'<linearGradient id="fondo" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{VERDE}" stop-opacity=".7"/>'
        f'<stop offset=".55" stop-color="#1B3A26"/>'
        f'<stop offset="1" stop-color="#121212"/></linearGradient>'
        f'<linearGradient id="avatar" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{VERDE}"/><stop offset="1" stop-color="#0B5E2A"/></linearGradient>'
    )
    cuerpo = f"""
<rect width="880" height="340" rx="16" fill="url(#fondo)"/>
<circle cx="130" cy="170" r="84" fill="url(#avatar)"/>
<text x="130" y="190" text-anchor="middle" font-family="{FUENTE}" font-size="56" font-weight="800" fill="#FFFFFF">MG</text>
<circle cx="200" cy="108" r="19" fill="{VERDE}" stroke="#FFFFFF" stroke-width="3"/>
<path d="M191 108l6 6 12-13" fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round"/>
<text x="254" y="96" font-family="{FUENTE}" font-size="13" font-weight="700" letter-spacing="3" fill="{VERDE}">PERFIL VERIFICADO</text>
<text x="254" y="166" font-family="{FUENTE}" font-size="60" font-weight="800" fill="#FFFFFF">Matthew Garay</text>
<text x="254" y="204" font-family="{FUENTE}" font-size="22" fill="#F0F0F0">Software Developer &amp; IT Systems Specialist</text>
<text x="254" y="240" font-family="{FUENTE}" font-size="16" fill="#D9D9D9">Desde 2021 en producción • Sistemas &amp; Desarrollo Web</text>
<text x="254" y="266" font-family="{FUENTE}" font-size="15" fill="#BDBDBD">Tecámac, Estado de México • Abierto a proyectos</text>
"""
    escribir("hero.svg", 880, 340, cuerpo, defs)


def banner(nombre, titulo, subtitulo):
    defs = (
        f'<linearGradient id="fondo" x1="0" y1="0" x2="1" y2="0">'
        f'<stop offset="0" stop-color="{VERDE}" stop-opacity=".5"/>'
        f'<stop offset="1" stop-color="#121212" stop-opacity=".92"/></linearGradient>'
    )
    cuerpo = f"""
<rect width="880" height="120" rx="14" fill="url(#fondo)"/>
<text x="32" y="60" font-family="{FUENTE}" font-size="32" font-weight="800" fill="#FFFFFF">{escape(titulo)}</text>
<text x="32" y="93" font-family="{FUENTE}" font-size="16" fill="#E0E0E0">{escape(subtitulo)}</text>
"""
    escribir(nombre, 880, 120, cuerpo, defs)


def reproductor():
    cuerpo = f"""
<circle cx="50" cy="48" r="28" fill="{VERDE}"/>
<path d="M44 34v28l23-14z" fill="#000000"/>
<text x="98" y="40" font-family="{FUENTE}" font-size="16" font-weight="700" fill="#FFFFFF">Reproduciendo: Proyectos de Matthew Garay</text>
<text x="98" y="64" font-family="{FUENTE}" font-size="13" fill="#BDBDBD">14 repositorios públicos • Tecámac, México</text>
<rect x="98" y="76" width="620" height="4" rx="2" fill="#4D4D4D"/>
<rect x="98" y="76" width="372" height="4" rx="2" fill="{VERDE}"/>
<circle cx="470" cy="78" r="6" fill="#FFFFFF"/>
"""
    escribir("reproductor.svg", 780, 96, cuerpo)


if __name__ == "__main__":
    hero()
    banner("acerca.svg", "Acerca de", "Biografía del artista")
    banner("playlist.svg", "Playlist pública", "Proyectos destacados • 5 pistas")
    banner("discografia.svg", "Discografía", "Lanzamientos populares • Álbumes • Sencillos y EP")
    banner("creditos.svg", "Créditos", "Producción, stack técnico y herramientas")
    banner("github.svg", "Un año en GitHub", "Actividad del artista")
    banner("contacto.svg", "En gira", "Redes del artista")
    reproductor()
    print("listo:", SALIDA)
