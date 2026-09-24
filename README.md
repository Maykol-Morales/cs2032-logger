# cs2032-logger

> Proyecto del curso **CS2032 – Cloud Computing** · UTEC

[![PyPI](https://img.shields.io/pypi/v/utec-logger)](https://pypi.org/project/utec-logger/)
[![CI](https://github.com/Maykol-Morales/cs2032-logger/actions/workflows/publish.yml/badge.svg)](https://github.com/Maykol-Morales/cs2032-logger/actions/workflows/publish.yml)

**utec-logger** es un logger para Python con salida en consola a color, archivos locales y envío opcional a **AWS CloudWatch Logs**.

📖 Documentación: https://utec-logger.github.io

## Características

- Consola con colores por nivel (`INFO`, `WARNING`, `ERROR`, `CRITICAL`)
- Archivos locales en `logs/log-<archivo>-<timestamp>.log`
- Envío opcional a CloudWatch Logs, activado solo con variables de entorno
- Indica el archivo y la línea desde donde se generó cada log
- Singleton: una única instancia en toda la aplicación
- Un fallo de CloudWatch nunca interrumpe tu aplicación

## Instalación

```bash
pip install utec-logger
```

Requiere Python 3.8+.

## Uso

```python
from utec_logger import logger

logger.info("Iniciando el sistema")
logger.warning("Uso de memoria alto")
logger.error("No se pudo conectar a la base de datos")
logger.critical("Servicio caído")
```

También puedes usar la clase y los niveles directamente:

```python
from utec_logger import Logger, Level

log = Logger()
log.log("Mensaje personalizado", level=Level.ERROR)
```

### Salida

Consola y archivo:

```
2025-05-03 12:30:01.123 | INFO | main.py:23 | Iniciando el sistema
```

CloudWatch (el timestamp va en el evento):

```
INFO | main.py:23 | Iniciando el sistema
```

## AWS CloudWatch (opcional)

El envío se activa cuando `CLOUD_WATCH_GROUP` y `CLOUD_WATCH_STREAM` están definidas. La conexión se hace en el primer log (no al importar) y el grupo y el stream se crean si no existen.

| Variable | Descripción |
|---|---|
| `CLOUD_WATCH_GROUP` | Grupo de logs |
| `CLOUD_WATCH_STREAM` | Stream de logs |
| `AWS_REGION` | Región de AWS |
| `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY` | Credenciales (opcional si usas un rol de IAM) |
| `AWS_SESSION_TOKEN` | Para credenciales temporales (por ejemplo, AWS Academy) |

Al conectarse, el logger muestra el estado en consola:

```
AWS Ready: 123456789012
CloudWatch Group: my-app-logs
CloudWatch Stream: dev-instance
CloudWatch Ready
```

## Desarrollo

```bash
pip install -e ".[test]"
pytest
```

Las pruebas usan [moto](https://github.com/getmoto/moto) para simular CloudWatch, sin tocar AWS.

## Publicación en PyPI

El workflow [`publish.yml`](.github/workflows/publish.yml) corre las pruebas en cada push y publica en PyPI al crear un **release** en GitHub, usando [Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (sin tokens en el repo):

1. Sube la versión en `pyproject.toml`.
2. Crea un release con el tag `v<versión>` (por ejemplo `v1.8`). El workflow verifica que coincidan.

## Proyectos relacionados

- [cs2032-logger-web](https://github.com/Maykol-Morales/cs2032-logger-web) — visor web de los archivos de log

## Créditos

Desarrollado con fines educativos para el curso de **Cloud Computing - UTEC**.

- **Geraldo Colchado**
    - *[gcolchado@utec.edu.pe](mailto:gcolchado@utec.edu.pe)*
    - Profesor de Cloud Computing

- **Maykol Morales**
    - *[maykol.morales@utec.edu.pe](mailto:maykol.morales@utec.edu.pe)*
    - ACL de Cloud Computing

- **Gino Daza**
    - *[gino.daza@utec.edu.pe](mailto:gino.daza@utec.edu.pe)*
    - Ex-Alumno de Cloud Computing

- **Ian Condori**
    - *[ian.condori@utec.edu.pe](mailto:ian.condori@utec.edu.pe)*
    - Ex-Alumno de Cloud Computing