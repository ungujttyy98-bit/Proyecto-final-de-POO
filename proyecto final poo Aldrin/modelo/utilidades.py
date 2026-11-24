"""Excepciones del dominio y utilidades comunes."""
import unicodedata

DIAS_SEMANA = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")


class ErrorDominio(Exception):
    """Base de todos los errores de reglas de negocio."""


class ErrorValidacion(ErrorDominio):
    """Dato invalido (precio, cantidad, telefono, mesa, etc.)."""


class ErrorDisponibilidad(ErrorDominio):
    """Producto no disponible el dia del pedido."""


class ErrorEstadoPedido(ErrorDominio):
    """Transicion de estado u operacion no permitida en el estado actual."""


class ErrorPago(ErrorDominio):
    """Pago invalido o rechazado."""


def clave_texto(texto: str) -> str:
    """Minusculas y sin tildes, para comparar nombres."""
    s = unicodedata.normalize("NFD", str(texto).strip().lower())
    return "".join(c for c in s if unicodedata.category(c) != "Mn")


def normalizar_dia(dia: str) -> str:
    clave = clave_texto(dia)
    if clave not in DIAS_SEMANA:
        raise ErrorValidacion(f"Dia invalido: '{dia}'. Use: {', '.join(DIAS_SEMANA)}")
    return clave
