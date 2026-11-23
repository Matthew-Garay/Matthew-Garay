<p align="center">
  <img src="assets/artista.svg" width="100%" alt="Matthew Garay, técnico de soporte y desarrollador. Áreas: mantenimiento, soporte técnico, programación y bases de datos."/>
</p>

<p align="center">
  <img src="assets/acerca.svg" width="100%" alt="Acerca de. Matthew Garay trabaja en el área de TI de RFV Truck Parts and Accessories desde septiembre de 2026, donde atiende reportes de usuarios, da mantenimiento a computadoras e impresoras y revisa la red local. Repara equipos desde 2021 y escribe sus propias herramientas de soporte: MG Toolkit, Office Installer e IP Inspector. En su residencia profesional desarrolló Precision HelpDesk, un sistema de tickets e inventario de TI hecho con React, Node.js y MySQL."/>
</p>

<p align="center">
  <img src="assets/playlist.svg" width="100%" alt="Playlist de proyectos"/>
</p>

<details>
<summary><img src="assets/pista-01.svg" width="96%" alt="1. Precision HelpDesk"/></summary>

Lo desarrolló durante su residencia en RFV Truck Parts. Ahí los reportes de fallas llegaban por mensajes y hojas de cálculo, y no había un inventario confiable de los equipos de cada área.

Con el sistema, cada empleado levanta su ticket con fotos de la falla, pide insumos y consulta manuales. El área de TI asigna y sigue los tickets, lleva el inventario de hardware y software y saca reportes en PDF. Los avisos llegan al momento con Socket.IO y también por correo.

El frontend está hecho con React, Vite y Tailwind, y la API con Node.js y Express sobre MySQL. Para que dos personas no descuenten el mismo artículo del inventario a la vez, cada operación bloquea el registro con `SELECT … FOR UPDATE`. En las pruebas, comprimir las fotos con Sharp redujo su peso más de 90 % y la caché bajó la carga del dashboard de 85 ms a 3 ms.

Hoy está en prueba piloto, incluida una sucursal. Pasará a producción cuando la empresa tenga un servidor propio para alojarlo.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/Precision-Truck-Parts---Help-Desk)

</details>

<details>
<summary><img src="assets/pista-02.svg" width="96%" alt="2. IP Inspector"/></summary>

Aplicación de escritorio para Windows que muestra qué dispositivos hay en una red local y qué puertos tienen abiertos. Matthew la usa para revisar redes sin instalar herramientas pesadas.

Encuentra los equipos por ARP, ICMP y TCP, y trata de identificar qué es cada uno (computadora, impresora, cámara, router, teléfono) con lo que el propio aparato anuncia en la red, el fabricante de su tarjeta de red y los puertos que responde. Trae perfiles de escaneo rápido, completo y para cámaras, además de ping, traceroute, DNS y WHOIS.

Está escrita en Python con CustomTkinter.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/IP-Scanner). Descarga: [última versión](https://github.com/Matthew-Garay/IP-Scanner/releases/latest).

</details>

<details>
<summary><img src="assets/pista-03.svg" width="96%" alt="3. MG Toolkit"/></summary>

Un solo archivo `.bat` con el mantenimiento que Matthew hace en cada computadora: borrar temporales, reparar Windows con DISM, SFC y CHKDSK, buscar virus con Defender, crear un punto de restauración, respaldar archivos y controladores, e instalar programas con winget.

Se puede correr completo en automático o paso por paso. Al final entrega un informe con una calificación de 0 a 100 y lo que falta corregir. Solo usa herramientas que ya trae Windows y funciona de Windows 7 a 11.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/MG-Toolkit). Descarga: [última versión](https://github.com/Matthew-Garay/MG-Toolkit/releases/latest).

</details>

<details>
<summary><img src="assets/pista-04.svg" width="96%" alt="4. Office Installer"/></summary>

Script de PowerShell para instalar Office LTSC 2024, 2021, 2019 o 2016 con un solo comando. Tiene una versión con ventanas y otra de consola, y no necesita nada extra para funcionar. Surgió de tener que instalar Office equipo por equipo.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/Microsoft-Office-Installer). Sitio: [matthew-garay.github.io/Microsoft-Office-Installer](https://matthew-garay.github.io/Microsoft-Office-Installer/).

</details>

<details>
<summary><img src="assets/pista-05.svg" width="96%" alt="5. AGS Alert Off"/></summary>

Script de PowerShell que detiene y deshabilita Adobe Genuine Service, el servicio que muestra avisos repetidos en Acrobat. Deja una tarea programada que lo mantiene apagado y guarda un registro de cada acción. Con `-Uninstall` el servicio vuelve a quedar como estaba.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/Adobe-Genuine-Service-AGS-Alert). Descarga: [última versión](https://github.com/Matthew-Garay/Adobe-Genuine-Service-AGS-Alert/releases/latest).

</details>

<details>
<summary><img src="assets/pista-06.svg" width="96%" alt="6. Directo a Obra"/></summary>

Tienda en línea de materiales de construcción, hecha como proyecto de la carrera. Tiene catálogo con filtros por categoría y precio, carrito de compras y envío de la factura al correo del cliente con PHPMailer. Está hecha en PHP con MySQL y Bootstrap.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/Directo-a-Obra)

</details>

<details>
<summary><img src="assets/pista-07.svg" width="96%" alt="7. Resiliente Chat"/></summary>

Chat grupal en el navegador. Los mensajes viajan por WebSockets cifrados con TLS y, al entrar, cada persona ve los últimos 50 mensajes. El servidor es Node.js con Express y se puede levantar con Docker.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/resiliente-chat)

</details>

<details>
<summary><img src="assets/pista-08.svg" width="96%" alt="8. QR Studio"/></summary>

Generador de códigos QR que funciona por completo en el navegador, sin mandar datos a ningún servidor. Crea códigos para enlaces, redes WiFi, contactos, SMS, correos y WhatsApp, y permite cambiar colores, poner un logo y descargar en PNG, SVG o PDF. Está hecho en JavaScript.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/qr-studio). Pruébalo: [demo en línea](https://matthew-garay.github.io/qr-studio/).

</details>

<details>
<summary><img src="assets/pista-09.svg" width="96%" alt="9. RedTech"/></summary>

Diseño de la red de una empresa ficticia en Cisco Packet Tracer: topología, separación por VLANs, subneteo VLSM y documentación técnica. Proyecto de la carrera.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/Redtech)

</details>

<details>
<summary><img src="assets/pista-10.svg" width="96%" alt="10. Cifrado RSA"/></summary>

Página que explica y demuestra el cifrado con clave pública. Genera un par de claves RSA en el navegador con la Web Crypto API, cifra y descifra mensajes y permite exportar las claves. También explica el intercambio de claves Diffie-Hellman. Proyecto de la carrera.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/CifradoAsimetrico). Pruébalo: [demo en línea](https://matthew-garay.github.io/CifradoAsimetrico/).

</details>

<details>
<summary><img src="assets/pista-11.svg" width="96%" alt="11. Remote Support App"/></summary>

Aplicación de escritorio remoto para dar soporte, parecida a AnyDesk. Todavía está en desarrollo. El plan es una interfaz en Flutter, un núcleo en Rust que capture la pantalla y la envíe como video H.264, y conexión directa entre los dos equipos con WebRTC.

Código: [repositorio en GitHub](https://github.com/Matthew-Garay/remote-support-app)

</details>

<br/>

<p align="center">
  <img src="assets/discografia.svg" width="100%" alt="Discografía: cuatro álbumes, uno por área de trabajo"/>
</p>

<p align="center">
  <img src="assets/album-1.svg" width="49%" alt="Mantenimiento y reparación: diagnóstico de fallas de hardware y software, limpieza interna y mantenimiento preventivo, cambio de componentes (RAM, SSD y discos), formateo, respaldo y recuperación de datos, optimización y reparación de Windows."/>
  <img src="assets/album-2.svg" width="49%" alt="Soporte técnico: mesa de ayuda y atención a usuarios, instalación de Windows, Office y controladores, impresoras láser y térmicas, redes LAN (cableado, VLAN y subneteo VLSM), despliegue automatizado con PowerShell."/>
  <img src="assets/album-3.svg" width="49%" alt="Programación: aplicaciones web con React, Vite y Tailwind, APIs REST con Node.js y Express, autenticación JWT y permisos por rol, tiempo real con Socket.IO y WebSockets, aplicaciones de escritorio en Python."/>
  <img src="assets/album-4.svg" width="49%" alt="Bases de datos: modelado entidad-relación, normalización hasta tercera forma normal, MySQL y SQL Server, transacciones y control de concurrencia, reportes y análisis con Power BI."/>
</p>

<p align="center">
  <img src="assets/trayectoria.svg" width="100%" alt="Trayectoria: desde septiembre de 2026, soporte técnico de TI en RFV Truck Parts and Accessories; de marzo a julio de 2026, residencia profesional de 500 horas en la misma empresa; abril de 2025, servicio social en el TESCo; desde enero de 2021, reparación de equipo de cómputo por su cuenta."/>
</p>

<p align="center">
  <img src="assets/certificaciones.svg" width="100%" alt="Certificaciones: CCNA Introducción a Redes y CCNA Switching, Routing y Wireless Essentials, Introducción a la Ciberseguridad, Soporte y Seguridad de Red y Fundamentos de Análisis de Datos (Cisco Networking Academy); Fundamentos del Soporte Técnico (Google); Cloud Foundations (AWS Academy); Fundamentos de Power BI y Excel (Santander Open Academy)."/>
</p>

<p align="center">
  <img src="assets/creditos.svg" width="100%" alt="Créditos. Lenguajes: JavaScript, TypeScript, Python, PHP, SQL, PowerShell, Batch, Bash, VB.NET, Rust, Dart, R. Frameworks: React, Vite, Tailwind CSS, Bootstrap, Node.js, Express, Socket.IO, Flutter. Bases de datos: MySQL, SQL Server. Sistemas: Windows, Windows Server, Ubuntu, Kali, Arch. Infraestructura: Cisco, Packet Tracer, VMware, VirtualBox, Docker, AWS. Herramientas: Git, VS Code, Visual Studio, Postman, Power BI, Excel."/>
</p>

<p align="center">
  <img src="assets/resumen.svg" width="100%" alt="Un año en GitHub: commits, contribuciones, racha más larga, día más productivo y lenguajes más usados."/>
</p>

<p align="center">
  <a href="https://github.com/Matthew-Garay?tab=repositories"><img src="assets/barra.svg" width="100%" alt="Reproduciendo: Proyectos de Matthew Garay"/></a>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/matthewgarayperez/"><img src="https://img.shields.io/badge/LinkedIn-1ED760?style=for-the-badge&logo=linkedin&logoColor=black" alt="LinkedIn"/></a>
  <a href="mailto:1911.garay.perez@gmail.com"><img src="https://img.shields.io/badge/Correo-121212?style=for-the-badge&logo=gmail&logoColor=white" alt="Correo"/></a>
  <a href="https://github.com/Matthew-Garay?tab=repositories"><img src="https://img.shields.io/badge/Repositorios-121212?style=for-the-badge&logo=github&logoColor=white" alt="Repositorios"/></a>
</p>

<p align="center"><sub>Haz clic en un proyecto de la playlist para leer de qué trata.</sub></p>
