"""Jerarquia Pedido, ItemPedido y estados."""
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional

from modelo import variante
from modelo.clientes import Cliente
from modelo.pagos import MetodoPago
from modelo.productos import Producto
from modelo.utilidades import (ErrorValidacion, ErrorDisponibilidad, ErrorEstadoPedido,
                               ErrorPago, normalizar_dia, clave_texto)

REGISTRADO, EN_PREPARACION, LISTO, ENTREGADO, CANCELADO = (
    "REGISTRADO", "EN_PREPARACION", "LISTO", "ENTREGADO", "CANCELADO")
TRANSICIONES = {
    REGISTRADO: (EN_PREPARACION, CANCELADO),
    EN_PREPARACION: (LISTO,),
    LISTO: (ENTREGADO,),
    ENTREGADO: (),
    CANCELADO: (),
}
ZONAS_DELIVERY = {"Cercado": 8.0, "Quillacollo": 15.0, "Sacaba": 15.0, "Vinto": 20.0}
MINUTOS_RETRASO = 60  # regla 9 (acta de consultas): retraso si se entrega pasados 60 min


class ItemPedido:
    def __init__(self, producto: Producto, cantidad: int):
        self._producto = producto
        self._cantidad = 1
        self.cantidad = cantidad

    @staticmethod
    def validar_cantidad(cantidad: int) -> int:
        if isinstance(cantidad, bool) or not isinstance(cantidad, int) or not 1 <= cantidad <= 20:
            raise ErrorValidacion("La cantidad de un producto debe estar entre 1 y 20")
        return cantidad

    @property
    def producto(self) -> Producto:
        return self._producto

    @property
    def cantidad(self) -> int:
        return self._cantidad

    @cantidad.setter
    def cantidad(self, valor: int) -> None:
        self._cantidad = self.validar_cantidad(valor)

    def calcular_subtotal(self) -> float:
        return round(self._producto.calcular_precio() * self._cantidad, 2)


class Pedido(ABC):
    def __init__(self, numero: int, cliente: Cliente, dia: str, registrado_en: Optional[datetime] = None):
        self._numero = numero
        self._cliente = cliente
        self._dia = normalizar_dia(dia)
        self._items = []
        self._estado = REGISTRADO
        self._registrado_en = registrado_en or datetime.now()
        self._entregado_en = None
        self._pagado = False
        self._metodo_pago = None

    # ---- acceso controlado ----
    @property
    def numero(self) -> int: return self._numero
    @property
    def cliente(self) -> Cliente: return self._cliente
    @property
    def dia(self) -> str: return self._dia
    @property
    def estado(self) -> str: return self._estado
    @property
    def items(self) -> tuple: return tuple(self._items)   # copia inmutable
    @property
    def registrado_en(self) -> datetime: return self._registrado_en
    @property
    def entregado_en(self) -> Optional[datetime]: return self._entregado_en
    @property
    def pagado(self) -> bool: return self._pagado

    # ---- metodos abstractos ----
    @abstractmethod
    def calcular_cargos(self) -> float: ...

    @abstractmethod
    def nombre_tipo(self) -> str: ...

    # ---- ganchos polimorficos (con valor por defecto) ----
    def _etiqueta_cargos(self) -> str:
        return "Cargos"

    def _validar_confirmacion(self) -> None:
        if not self._items:
            raise ErrorEstadoPedido("No se puede confirmar un pedido sin productos")

    def _validar_metodo(self, metodo: MetodoPago) -> None:
        pass

    def calcular_compensacion(self) -> float:
        return 0.0

    def ocupa_mesa(self, mesa: int) -> bool:
        return False

    # ---- items (solo en REGISTRADO) ----
    def _exigir_registrado(self) -> None:
        if self._estado != REGISTRADO:
            raise ErrorEstadoPedido(f"Solo se pueden modificar productos en REGISTRADO (estado actual: {self._estado})")

    def agregar_producto(self, producto: Producto, cantidad: int) -> None:
        self._exigir_registrado()
        ItemPedido.validar_cantidad(cantidad)
        if not producto.esta_disponible(self._dia):
            raise ErrorDisponibilidad(f"'{producto.nombre}' no esta disponible el {self._dia}")
        for item in self._items:
            if item.producto is producto:
                item.cantidad = item.cantidad + cantidad   # el setter valida el tope de 20
                return
        self._items.append(ItemPedido(producto, cantidad))

    def quitar_producto(self, codigo: str) -> None:
        self._exigir_registrado()
        for item in self._items:
            if item.producto.codigo == codigo:
                self._items.remove(item)
                return
        raise ErrorValidacion(f"El producto '{codigo}' no esta en el pedido")

    # ---- calculos ----
    def calcular_subtotal(self) -> float:
        return round(sum(i.calcular_subtotal() for i in self._items), 2)

    def contar_platos(self) -> int:
        return sum(i.cantidad * i.producto.contar_platos() for i in self._items)

    def contar_productos(self) -> int:
        return sum(i.cantidad * i.producto.contar_productos() for i in self._items)

    def calcular_descuentos(self) -> float:
        return round(sum(i.producto.unidades_gratis(self._dia, i.cantidad) * i.producto.calcular_precio()
                         for i in self._items), 2)

    def calcular_total(self) -> float:
        return round(self.calcular_subtotal() - self.calcular_descuentos() + self.calcular_cargos(), 2)

    def calcular_total_a_pagar(self) -> float:
        return round(self.calcular_total() - self.calcular_compensacion(), 2)

    # ---- estados ----
    def cambiar_estado(self, nuevo_estado: str, momento: Optional[datetime] = None) -> None:
        if nuevo_estado not in TRANSICIONES.get(self._estado, ()):
            raise ErrorEstadoPedido(f"Transicion invalida: {self._estado} -> {nuevo_estado}")
        if nuevo_estado == EN_PREPARACION:
            self._validar_confirmacion()
        if nuevo_estado == ENTREGADO:
            momento = momento or datetime.now()
            if momento < self._registrado_en:
                raise ErrorValidacion("La entrega no puede ser anterior al registro")
            self._entregado_en = momento
        self._estado = nuevo_estado

    # ---- pago ----
    def aceptar_pago(self, metodo: MetodoPago) -> bool:
        if self._pagado:
            raise ErrorPago("El pedido ya fue pagado")
        if self._estado != ENTREGADO:
            raise ErrorPago(f"Solo se cobra un pedido ENTREGADO (estado actual: {self._estado})")
        self._validar_metodo(metodo)
        metodo.procesar_pago(self.calcular_total_a_pagar())
        self._metodo_pago = metodo
        self._pagado = True
        return True

    def comprobante(self) -> str:
        if not self._pagado:
            return "El pedido aun no esta pagado"
        return self.generar_detalle() + "\n  " + self._metodo_pago.comprobante()

    def monto_cobrado(self) -> float:
        return self._metodo_pago._total_cobrado if self._pagado else 0.0

    def generar_detalle(self) -> str:
        l = [f"Pedido #{self._numero} [{self.nombre_tipo()}] - {self._cliente} - {self._dia} - {self._estado}"]
        for i in self._items:
            l.append(f"  {i.cantidad:>2} x {i.producto.nombre:<26} Bs {i.producto.calcular_precio():>7.2f}"
                     f" = Bs {i.calcular_subtotal():>8.2f}")
        l.append(f"  Subtotal:     Bs {self.calcular_subtotal():>8.2f}")
        l.append(f"  Descuentos:  -Bs {self.calcular_descuentos():>8.2f}")
        l.append(f"  {self._etiqueta_cargos() + ':':<13} Bs {self.calcular_cargos():>8.2f}")
        if self.calcular_compensacion() > 0:
            l.append(f"  Compensacion por retraso: -Bs {self.calcular_compensacion():.2f}")
        l.append(f"  TOTAL:        Bs {self.calcular_total_a_pagar():>8.2f}")
        return "\n".join(l)


class PedidoLocal(Pedido):
    def __init__(self, numero, cliente, dia, mesa: int, registrado_en=None):
        super().__init__(numero, cliente, dia, registrado_en)
        self._mesa = 0
        self.mesa = mesa

    @property
    def mesa(self) -> int:
        return self._mesa

    @mesa.setter
    def mesa(self, valor: int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, int) or not 1 <= valor <= 15:
            raise ErrorValidacion("La mesa debe ser un numero del 1 al 15")
        self._mesa = valor

    def calcular_cargos(self) -> float:
        return 0.0

    def ocupa_mesa(self, mesa: int) -> bool:
        return self._mesa == mesa

    def nombre_tipo(self) -> str:
        return "Local"

    def _etiqueta_cargos(self) -> str:
        return f"Cargos (mesa {self._mesa})"

    def calcular_descuentos(self) -> float:
        base = super().calcular_descuentos()
        v = variante.actual()
        if v.local_platos_para_descuento and self.contar_platos() >= v.local_platos_para_descuento:
            base += self.calcular_subtotal() * v.local_descuento
        return round(base, 2)


class PedidoParaLlevar(Pedido):
    def calcular_cargos(self) -> float:
        v = variante.actual()
        cantidad = self.contar_productos() if v.envase_por == "producto" else self.contar_platos()
        return round(cantidad * v.envase_monto, 2)

    def nombre_tipo(self) -> str:
        return "Para llevar"

    def _etiqueta_cargos(self) -> str:
        return "Envases"


class PedidoDelivery(Pedido):
    def __init__(self, numero, cliente, dia, zona: str, registrado_en=None):
        super().__init__(numero, cliente, dia, registrado_en)
        self._zona = ""
        self.zona = zona

    @property
    def zona(self) -> str:
        return self._zona

    @zona.setter
    def zona(self, valor: str) -> None:
        for nombre in ZONAS_DELIVERY:
            if clave_texto(nombre) == clave_texto(valor):
                self._zona = nombre
                return
        raise ErrorValidacion(f"Zona invalida: '{valor}'. Zonas: {', '.join(ZONAS_DELIVERY)}")

    def calcular_cargos(self) -> float:
        v = variante.actual()
        if (v.envio_gratis_desde is not None and self.calcular_subtotal() >= v.envio_gratis_desde
                and (not v.envio_gratis_solo_cercado or self._zona == "Cercado")):
            return 0.0
        return ZONAS_DELIVERY[self._zona]

    def nombre_tipo(self) -> str:
        return "Delivery"

    def _etiqueta_cargos(self) -> str:
        return f"Envio ({self._zona})"

    def _validar_confirmacion(self) -> None:
        super()._validar_confirmacion()
        minimo = variante.actual().pedido_minimo_delivery
        if self.calcular_subtotal() < minimo:
            raise ErrorEstadoPedido(f"Pedido minimo de delivery: Bs {minimo:.2f} (subtotal Bs {self.calcular_subtotal():.2f})")

    def _validar_metodo(self, metodo: MetodoPago) -> None:
        if not metodo.permitido_en_delivery():
            raise ErrorPago("El delivery solo acepta efectivo o QR")

    def calcular_compensacion(self) -> float:
        if self._entregado_en is None:
            return 0.0
        if self._entregado_en - self._registrado_en > timedelta(minutes=MINUTOS_RETRASO):
            return self.calcular_cargos()   # devolucion del costo de envio
        return 0.0
