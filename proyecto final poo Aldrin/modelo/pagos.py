"""Jerarquia MetodoPago."""
import math
import re
from abc import ABC, abstractmethod
from modelo import variante
from modelo.utilidades import ErrorPago


class MetodoPago(ABC):
    def __init__(self):
        self._total_cobrado = 0.0

    @abstractmethod
    def procesar_pago(self, total: float) -> float:
        """Valida el pago y devuelve el monto realmente cobrado."""

    @abstractmethod
    def comprobante(self) -> str: ...

    def permitido_en_delivery(self) -> bool:
        return True


class Efectivo(MetodoPago):
    def __init__(self, monto_recibido: float):
        super().__init__()
        if isinstance(monto_recibido, bool) or not isinstance(monto_recibido, (int, float)) or monto_recibido <= 0:
            raise ErrorPago("El monto recibido debe ser mayor que cero")
        self._monto_recibido = round(float(monto_recibido), 2)
        self._cambio = 0.0

    def procesar_pago(self, total: float) -> float:
        paso = variante.actual().efectivo_redondeo
        a_cobrar = round(math.floor(total / paso + 1e-9) * paso, 2) if paso else round(total, 2)
        if self._monto_recibido < a_cobrar:
            raise ErrorPago(f"Monto insuficiente: recibido Bs {self._monto_recibido:.2f}, total Bs {a_cobrar:.2f}")
        self._total_cobrado = a_cobrar
        self._cambio = round(self._monto_recibido - a_cobrar, 2)
        return a_cobrar

    def comprobante(self) -> str:
        return (f"Pago en EFECTIVO | Total cobrado: Bs {self._total_cobrado:.2f} | "
                f"Recibido: Bs {self._monto_recibido:.2f} | Cambio: Bs {self._cambio:.2f}")


class PagoQR(MetodoPago):
    def __init__(self, codigo_transaccion: str):
        super().__init__()
        if not isinstance(codigo_transaccion, str) or re.fullmatch(r"\d{10}", codigo_transaccion) is None:
            raise ErrorPago("El codigo de transaccion QR debe tener exactamente 10 digitos")
        self._codigo_transaccion = codigo_transaccion

    def procesar_pago(self, total: float) -> float:
        self._total_cobrado = round(total, 2)
        return self._total_cobrado

    def comprobante(self) -> str:
        return f"Pago por QR | Total cobrado: Bs {self._total_cobrado:.2f} | Transaccion: {self._codigo_transaccion}"


class Tarjeta(MetodoPago):
    COMISION = 0.03

    def __init__(self, ultimos_digitos: str):
        super().__init__()
        if not isinstance(ultimos_digitos, str) or re.fullmatch(r"\d{4}", ultimos_digitos) is None:
            raise ErrorPago("Se requieren los ultimos 4 digitos de la tarjeta")
        self._ultimos_digitos = ultimos_digitos
        self._comision = 0.0

    def procesar_pago(self, total: float) -> float:
        self._comision = round(total * self.COMISION, 2)
        self._total_cobrado = round(total + self._comision, 2)
        return self._total_cobrado

    def comprobante(self) -> str:
        return (f"Pago con TARJETA **** {self._ultimos_digitos} | Comision 3%: Bs {self._comision:.2f} | "
                f"Total cobrado: Bs {self._total_cobrado:.2f}")

    def permitido_en_delivery(self) -> bool:
        return False
