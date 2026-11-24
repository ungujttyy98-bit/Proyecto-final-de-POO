# Sistema de Pedidos – Llajta

> Sistema de consola en Python para gestionar el menú, los clientes, los pedidos y los pagos de un restaurante de comida típica de Cochabamba.

## Descripción

Sabor Valluno atiende pedidos en el local, para llevar y por delivery. Antes tomaba los pedidos en una libreta: cobraba mal los combos, olvidaba el costo de los envases y no sabía cuánto cobrar por el envío a cada zona. Este sistema resuelve esos problemas aplicando los cuatro pilares de la Programación Orientada a Objetos a partir de un diagrama de clases propio (`docs/diagrama_v2.png`).


Proyecto Integrador de **Programación Orientada a Objetos**, individual.

Estudiante:Joel Alfred Colque Tito

## Características

- Menú con platos, bebidas (vaso o jarra) y **combos que pueden contener otros combos**.
- Disponibilidad de productos por día de la semana; un combo está disponible solo si todos sus productos lo están.
- Tres tipos de pedido con sus cargos: **local** (mesas 1–15), **para llevar** (envases) y **delivery** (envío por zona, envío gratis, pedido mínimo).
- Ciclo de vida del pedido: `REGISTRADO → EN_PREPARACION → LISTO → ENTREGADO`, con cancelación solo desde `REGISTRADO`.
- Pagos en **efectivo** (con cambio), **QR** (código de 10 dígitos) y **tarjeta** (3 % de comisión). El delivery no acepta tarjeta.
- Compensación automática por retraso en delivery: si la entrega pasa de 60 minutos, se devuelve el costo del envío.
- Comprobante de pago y reporte de ventas del día (por tipo de pedido y 3 productos más vendidos).
- Reglas parametrizadas para las seis variantes (A–F) en un solo archivo.

## Tecnologías

`Python 3` `módulo abc` `biblioteca estándar` `Git/GitHub`

No se usan frameworks ni librerías externas.

## Requisitos

- Python 3.8 o superior.
- Una terminal. No hay que instalar paquetes.

## Instalación

```bash
git https://github.com/ungujttyy98-bit/Proyecto-final-de-POO.git
cd <repositorio>
```

## Uso

Menú de consola interactivo (pide la variante al iniciar; por defecto A):

```bash
python3 main.py
```

Pruebas automáticas, con todos los casos de uso y escenarios de error:

```bash
python3 pruebas.py
```

Para cambiar la variante desde código:

```python
from modelo import variante
variante.usar("B")
```

**Ejemplo (caso de referencia, variante A).** Un combo con silpancho (Bs 35) y un vaso de mocochinchi (Bs 6) cuesta 41 × 0,90 = **Bs 36,90**. Dos combos por delivery a Quillacollo suman 73,80 + 15 = **Bs 88,80**.

### Los cuatro pilares en el código

| Pilar | Dónde se ve |
| --- | --- |
| Encapsulación | Atributos protegidos (`_atributo`) con `@property` y setters que validan. `Pedido.items` y `Combo.productos` devuelven tuplas: nadie modifica la lista desde fuera. |
| Herencia | Jerarquías `Producto` (6 subclases), `Pedido` (3) y `MetodoPago` (3), con `super().__init__()` y sin atributos comunes repetidos. |
| Polimorfismo | `calcular_precio()`, `esta_disponible()`, `contar_platos()`, `calcular_cargos()` y `procesar_pago()` se sobrescriben. `Pedido` calcula todo recorriendo sus ítems, sin `isinstance`, `type()` ni `if/elif` por tipo. |
| Abstracción | `Producto`, `Pedido` y `MetodoPago` heredan de `ABC` con `@abstractmethod`; instanciarlas lanza `TypeError`. |

### Supuestos de diseño

1. Solo se cobra un pedido en estado `ENTREGADO`; si hubo retraso, el total a pagar descuenta la compensación.
2. El pedido mínimo de delivery y el envío gratis se evalúan sobre el subtotal, antes de descuentos. El mínimo se valida al pasar a `EN_PREPARACION`.
3. Variante F: el "5 % más Bs 5 fijos" se calcula como `suma × 0,95 − 5`.
4. Variante D: "3 productos o más" cuenta los productos directos del combo.
5. El reporte de "más vendidos" cuenta unidades por ítem del pedido (un combo cuenta como un producto).
6. Los días se escriben sin tildes (`miercoles`, `sabado`); el sistema acepta tildes y mayúsculas y las normaliza.

## Estructura del proyecto

```
sabor_valluno/
├── modelo/
│   ├── productos.py     Producto (ABC), Plato, Bebida (ABC), RefrescoNatural, Gaseosas, Combo
│   ├── pedidos.py       Pedido (ABC), ItemPedido, PedidoLocal, PedidoParaLlevar, PedidoDelivery
│   ├── pagos.py         MetodoPago (ABC), Efectivo, PagoQR, Tarjeta
│   ├── clientes.py      Cliente
│   ├── variante.py      Parámetros de las variantes A–F
│   └── utilidades.py    Excepciones del dominio y normalización de días
├── restaurante.py       Gestor del menú, clientes, pedidos y reportes
├── main.py              Menú de consola
├── pruebas.py           Pruebas con assert (97 verificaciones)
└── docs/
    ├── diagrama_v1.png
    ├── diagrama_v2.png
    ├── bitacora_ia.md
    └── acta_consultas.md
```

#