"""Parametros de cada variante (A-F). Solo aqui viven los valores que cambian por estudiante."""


class Variante:
    def __init__(self, letra, descuento_combo, envase_monto, envase_por,
                 envio_gratis_desde, envio_gratis_solo_cercado, pedido_minimo_delivery,
                 descuento_fijo_combo=0.0, combo_min_para_descuento=0,
                 combo_max_productos=None, dias_platos=None, promo_2x1_dia=None,
                 local_platos_para_descuento=None, local_descuento=0.0,
                 efectivo_redondeo=None):
        self.letra = letra
        self.descuento_combo = descuento_combo
        self.envase_monto = envase_monto
        self.envase_por = envase_por                      # "plato" | "producto"
        self.envio_gratis_desde = envio_gratis_desde      # None = sin envio gratis
        self.envio_gratis_solo_cercado = envio_gratis_solo_cercado
        self.pedido_minimo_delivery = pedido_minimo_delivery
        self.descuento_fijo_combo = descuento_fijo_combo
        self.combo_min_para_descuento = combo_min_para_descuento
        self.combo_max_productos = combo_max_productos
        self.dias_platos = dias_platos or {}              # nombre sin tildes -> dias de venta
        self.promo_2x1_dia = promo_2x1_dia
        self.local_platos_para_descuento = local_platos_para_descuento
        self.local_descuento = local_descuento
        self.efectivo_redondeo = efectivo_redondeo


VARIANTES = {
    "A": Variante("A", 0.10, 2.0, "plato", 150, True, 40,
                  dias_platos={"chicharron": ["domingo"]}),
    "B": Variante("B", 0.12, 2.5, "plato", 120, False, 50, promo_2x1_dia="martes"),
    "C": Variante("C", 0.08, 1.5, "producto", 200, True, 35, combo_max_productos=4),
    "D": Variante("D", 0.15, 2.0, "plato", None, True, 60, combo_min_para_descuento=3,
                  local_platos_para_descuento=6, local_descuento=0.05),
    "E": Variante("E", 0.10, 3.0, "plato", 180, True, 45, efectivo_redondeo=0.5),
    "F": Variante("F", 0.05, 2.0, "plato", 100, False, 30, descuento_fijo_combo=5.0,
                  dias_platos={"sopa de mani": ["lunes", "jueves"]}),
}

_activa = VARIANTES["A"]


def actual() -> Variante:
    return _activa


def usar(letra: str) -> Variante:
    global _activa
    _activa = VARIANTES[letra.upper()]
    return _activa
