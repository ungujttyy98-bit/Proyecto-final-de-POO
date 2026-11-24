"""Jerarquia Producto. Combo aplica el patron Composite: es un Producto que contiene Productos."""
from abc import ABC, abstractmethod
from modelo import variante
from modelo.utilidades import ErrorValidacion, normalizar_dia, DIAS_SEMANA


class Producto(ABC):
    def __init__(self, codigo: str, nombre: str, precio: float):
        self._codigo = ""
        self._nombre = ""
        self._precio = 0.0
        self.codigo = codigo
        self.nombre = nombre
        self.precio = precio

    @property
    def codigo(self) -> str:
        return self._codigo

    @codigo.setter
    def codigo(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion("El codigo del producto no puede estar vacio")
        self._codigo = valor.strip()

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ErrorValidacion("El nombre del producto no puede estar vacio")
        self._nombre = valor.strip()

    @property
    def precio(self) -> float:
        return self._precio

    @precio.setter
    def precio(self, valor: float) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or valor <= 0:
            raise ErrorValidacion("El precio debe ser un numero mayor que cero")
        self._precio = round(float(valor), 2)

    @abstractmethod
    def calcular_precio(self) -> float: ...

    @abstractmethod
    def esta_disponible(self, dia: str) -> bool: ...

    @abstractmethod
    def contar_platos(self) -> int: ...

    @abstractmethod
    def contar_productos(self) -> int: ...

    def contiene(self, producto: "Producto") -> bool:
        return producto is self

    def unidades_gratis(self, dia: str, cantidad: int) -> int:
        """Promociones por unidad (ej. 2x1). Por defecto no hay."""
        return 0

    def __str__(self) -> str:
        return f"[{self._codigo}] {self._nombre} - Bs {self.calcular_precio():.2f}"


class Plato(Producto):
    def __init__(self, codigo: str, nombre: str, precio: float, dias_venta=None):
        super().__init__(codigo, nombre, precio)
        self._dias_venta = []
        self.dias_venta = dias_venta if dias_venta else list(DIAS_SEMANA)

    @property
    def dias_venta(self) -> tuple:
        return tuple(self._dias_venta)

    @dias_venta.setter
    def dias_venta(self, dias) -> None:
        normalizados = [normalizar_dia(d) for d in dias]
        if not normalizados:
            raise ErrorValidacion("Un plato debe venderse al menos un dia")
        self._dias_venta = normalizados

    def calcular_precio(self) -> float:
        return round(self._precio, 2)

    def esta_disponible(self, dia: str) -> bool:
        return normalizar_dia(dia) in self._dias_venta

    def contar_platos(self) -> int:
        return 1

    def contar_productos(self) -> int:
        return 1


class Bebida(Producto):
    """Abstracta: cada tipo de bebida define como calcula su precio."""
    FACTOR_JARRA = 3

    def __init__(self, codigo: str, nombre: str, precio: float, tamano: str = "vaso"):
        super().__init__(codigo, nombre, precio)
        self._tamano = "vaso"
        self.tamano = tamano

    @property
    def tamano(self) -> str:
        return self._tamano

    @tamano.setter
    def tamano(self, valor: str) -> None:
        if valor not in ("vaso", "jarra"):
            raise ErrorValidacion("El tamano debe ser 'vaso' o 'jarra'")
        self._tamano = valor

    def _precio_por_tamano(self) -> float:
        factor = self.FACTOR_JARRA if self._tamano == "jarra" else 1
        return round(self._precio * factor, 2)

    def esta_disponible(self, dia: str) -> bool:
        normalizar_dia(dia)
        return True

    def contar_platos(self) -> int:
        return 0

    def contar_productos(self) -> int:
        return 1


class RefrescoNatural(Bebida):
    def calcular_precio(self) -> float:
        return self._precio_por_tamano()

    def unidades_gratis(self, dia: str, cantidad: int) -> int:
        v = variante.actual()
        if v.promo_2x1_dia and normalizar_dia(dia) == v.promo_2x1_dia and self._tamano == "vaso":
            return cantidad // 2
        return 0


class Gaseosas(Bebida):
    def calcular_precio(self) -> float:
        return self._precio_por_tamano()


class Combo(Producto):
    def __init__(self, codigo: str, nombre: str, productos: list):
        if len(productos) < 2:
            raise ErrorValidacion("Un combo necesita 2 o mas productos")
        super().__init__(codigo, nombre, sum(p.calcular_precio() for p in productos))
        self._productos = []
        for p in productos:
            self.agregar_producto(p)

    @property
    def productos(self) -> tuple:
        return tuple(self._productos)

    def agregar_producto(self, producto: Producto) -> None:
        if producto is self or producto.contiene(self):
            raise ErrorValidacion("Un combo no puede contenerse a si mismo")
        maximo = variante.actual().combo_max_productos
        if maximo is not None and len(self._productos) >= maximo:
            raise ErrorValidacion(f"En la variante {variante.actual().letra} un combo tiene como maximo {maximo} productos")
        self._productos.append(producto)
        self._precio = round(sum(p.calcular_precio() for p in self._productos), 2)  # precio sin descuento

    def calcular_precio(self) -> float:
        v = variante.actual()
        suma = sum(p.calcular_precio() for p in self._productos)  # recursivo: acepta combos
        pct = v.descuento_combo if len(self._productos) >= v.combo_min_para_descuento else 0.0
        return round(max(suma * (1 - pct) - v.descuento_fijo_combo, 0.0), 2)

    def esta_disponible(self, dia: str) -> bool:
        return all(p.esta_disponible(dia) for p in self._productos)

    def contar_platos(self) -> int:
        return sum(p.contar_platos() for p in self._productos)

    def contar_productos(self) -> int:
        return sum(p.contar_productos() for p in self._productos)

    def contiene(self, producto: Producto) -> bool:
        return producto is self or any(p.contiene(producto) for p in self._productos)
