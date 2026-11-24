import re
from modelo.utilidades import ErrorValidacion


class Cliente:
    def __init__(self, nombre: str, telefono: str):
        self._nombre = ""
        self._telefono = ""
        self.nombre = nombre
        self.telefono = telefono

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion("El nombre del cliente no puede estar vacio")
        self._nombre = valor.strip()

    @property
    def telefono(self) -> str:
        return self._telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        if not self.validar_telefono(valor):
            raise ErrorValidacion("Telefono invalido: 8 digitos y debe empezar en 6 o 7")
        self._telefono = valor

    @staticmethod
    def validar_telefono(tel: str) -> bool:
        return isinstance(tel, str) and re.fullmatch(r"[67]\d{7}", tel) is not None

    def __str__(self) -> str:
        return f"{self._nombre} ({self._telefono})"
