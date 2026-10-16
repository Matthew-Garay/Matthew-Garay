# Guía de Instalación Local

Esta guía te ayuda a configurar el proyecto en tu entorno local.

## Requisitos previos

- Git
- Navegador web moderno
- (Si aplica) Servidor web local (XAMPP, WAMP, Laragon, etc.)

## Instalación

1. Clona el repositorio:
   ```bash
   git clone https://github.com/Matthew-Garay/Matthew-Garay.git
   cd Matthew-Garay
   ```
2. Instala las dependencias (si aplica):
   ```bash
   # Ejemplo para proyectos con composer
   composer install
   ```
3. Configura las variables de entorno:
   ```bash
   cp .env.example .env
   # Edita .env con tus valores reales
   ```
4. Inicia el servidor local y abre el proyecto en tu navegador.

## Verificación

Después de completar la instalación, deberías poder ver el proyecto funcionando en `http://localhost/`.

## Solución de problemas

Si encuentras problemas, abre un issue con la etiqueta `bug` y describe los pasos seguidos y el mensaje de error.
