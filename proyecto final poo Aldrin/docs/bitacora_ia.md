# Bitácora de uso de IA – Sistema de Pedidos Llajta

**Estudiante:** Gonzales Lovera Aldrin Gabriel
**Herramienta usada:** Claude (Anthropic), chat web/app.

## 2. Registro de usos

### Entrada 1 – Generación del código del modelo

| Fecha | 17/11/2026 |
| Semana |3|
| Herramienta | Claude |
| Tipo de uso | Generación de código |
| Consulta textual | "Con base en este diagrama v2 y en las reglas de negocio del documento que te pasé anteriormente, necesito que hagas lo siguiente: 1. Implementación en Python: Escribe el código completo respetando estrictamente los nombres exactos de clases, atributos protegidos, tipos de datos y firmas de métodos del diagrama…" (se adjuntó el diagrama v2 y el enunciado) |
| Qué acepté | Estructura de clases y jerarquías (`Producto`, `Pedido`, `MetodoPago`), propiedades con validación, estados del pedido, cargos, pagos, compensación por retraso, `Restaurante`. |
| Qué modifiqué y por qué | ✏️ ______________________________ |
| Archivo o clase | `modelo/productos.py`, `modelo/pedidos.py`, `modelo/pagos.py`, `modelo/clientes.py`, `modelo/variante.py`, `modelo/utilidades.py`, `restaurante.py` |
| ¿Lo explico sin ayuda? (Sí / Parcial / No) | ✏️ ____ |

Notas verificables: la IA agregó métodos que no estaban en el diagrama (`contar_productos()`, `contiene()`, `unidades_gratis()`, `calcular_descuentos()`, `calcular_compensacion()`, `calcular_total_a_pagar()`, `ocupa_mesa()`, `permitido_en_delivery()`); deben figurar en el diagrama v2. Los parámetros de las seis variantes quedaron en `modelo/variante.py`; la variante activa por defecto es la A hasta que se configure la propia.

### Entrada 2 – Pruebas y menú de consola

| Fecha | 17/11/2026 |
| Semana |3|
| Herramienta | Claude |
| Tipo de uso | Generación de código |
| Consulta textual | "Crea un bloque de pruebas (o archivo main.py) que ejecute paso a paso todos los casos de uso y escenarios de error que están en el documento, imprimiendo en consola los resultados, totales, comprobantes y el reporte final…" |
| Qué acepté | `pruebas.py` con verificaciones `assert` (caso de referencia, combo dentro de combo, errores de validación, estados, pagos, retraso, variantes) y `main.py` con el menú de consola. |
| Archivo o clase | `pruebas.py`, `main.py` |
| ¿Lo explico sin ayuda? |Si|

## 3. Declaración

Marca solo lo que sea verdad:

- [x] No usé IA en la semana 1 (modelado en aula, diagrama v1).
- [x] No usé IA en la semana 2 (jerarquía `Producto` y `Combo`, escrita en VS Code).
- [X] Usé IA en las semanas 3 y 4 solo como se permite, y lo registré en esta bitácora.
- [x] No usaré IA durante la defensa.
- [x] Este registro incluye todos mis usos de IA en el proyecto y puedo explicar el código que entrego.


