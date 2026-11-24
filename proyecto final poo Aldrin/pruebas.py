"Pruebas de todos los casos de uso y escenarios de error. Ejecutar: python3 pruebas.py"
from datetime import datetime, timedelta
from modelo import variante
from modelo.clientes import Cliente
from modelo.pagos import MetodoPago, Efectivo, PagoQR, Tarjeta
from modelo.pedidos import Pedido, ItemPedido
from modelo.productos import Producto, Bebida, Combo, Plato
from modelo.utilidades import (ErrorValidacion, ErrorDisponibilidad, ErrorEstadoPedido, ErrorPago)
from restaurante import Restaurante

total_asserts = 0


def seccion(t):
    print(f"\n{'=' * 70}\n{t}\n{'=' * 70}")


def verificar(cond, msg):
    global total_asserts
    assert cond, f"FALLO: {msg}"
    total_asserts += 1
    print(f"  [OK] {msg}")


def debe_fallar(excepcion, f, msg):
    global total_asserts
    try:
        f()
    except excepcion as e:
        total_asserts += 1
        print(f"  [OK] {msg} -> {type(e).__name__}: {e}")
        return
    raise AssertionError(f"FALLO: no lanzo {excepcion.__name__}: {msg}")


def pedido_listo(r, p, minutos=0):
    """Lleva un pedido hasta ENTREGADO."""
    p.cambiar_estado("EN_PREPARACION")
    p.cambiar_estado("LISTO")
    p.cambiar_estado("ENTREGADO", datetime.now() + timedelta(minutes=minutos) if minutos else None)


def nuevo_restaurante():
    r = Restaurante()
    r.cargar_menu_base()
    return r


variante.usar("A")
r = nuevo_restaurante()
ana = r.registrar_cliente("Ana Rojas", "71234567")
luis = r.registrar_cliente("Luis Mamani", "69876543")

# ---------------------------------------------------------------- 1
seccion("1. CASO DE REFERENCIA (variante A)")
c1 = r.armar_combo("C01", "Combo Silpancho + Mocochinchi", ["P01", "B01"])
verificar(c1.calcular_precio() == 36.90, f"Combo (35 + 6) x 0.90 = Bs {c1.calcular_precio():.2f}")
ped = r.crear_pedido("delivery", ana, "lunes", zona="Quillacollo")
ped.agregar_producto(c1, 2)
print(ped.generar_detalle())
verificar(ped.calcular_subtotal() == 73.80, "Subtotal de 2 combos = Bs 73.80")
verificar(ped.calcular_cargos() == 15.0, "Envio a Quillacollo = Bs 15")
verificar(ped.calcular_total() == 88.80, "Total = Bs 88.80")
pedido_listo(r, ped, minutos=30)
print(r.cobrar_pedido(ped.numero, Efectivo(100)))
verificar(ped.pagado, "Pedido pagado en efectivo, cambio Bs 11.20")

# ---------------------------------------------------------------- 2
seccion("2. COMBOS: anidados, ciclos y minimo de productos")
c2 = r.armar_combo("C02", "Super combo", ["C01", "B02"])
verificar(c2.calcular_precio() == 37.71, f"Combo con otro combo: (36.90 + 5) x 0.90 = Bs {c2.calcular_precio():.2f}")
verificar(c2.contar_platos() == 1 and c2.contar_productos() == 3, "Combo anidado cuenta 1 plato y 3 productos")
debe_fallar(ErrorValidacion, lambda: c1.agregar_producto(c1), "Un combo no puede contenerse a si mismo")
debe_fallar(ErrorValidacion, lambda: c1.agregar_producto(c2), "Ciclo indirecto: C01 no puede contener a C02 que ya lo contiene")
debe_fallar(ErrorValidacion, lambda: Combo("X", "Solo uno", [r.obtener_producto("P01")]), "Combo con menos de 2 productos")
debe_fallar(AttributeError, lambda: c1.productos.append(1), "La lista de productos del combo no se modifica desde fuera")

# ---------------------------------------------------------------- 3
seccion("3. VALIDACIONES DE PRODUCTO, CANTIDAD Y TELEFONO")
debe_fallar(ErrorValidacion, lambda: Plato("Z", "Gratis", 0), "Precio 0")
debe_fallar(ErrorValidacion, lambda: Plato("Z", "Negativo", -5), "Precio negativo")
debe_fallar(ErrorValidacion, lambda: r.registrar_producto(Plato("P01", "Repetido", 10)), "Codigo duplicado")
debe_fallar(ErrorValidacion, lambda: r.registrar_cliente("Pedro", "12345678"), "Telefono que no empieza en 6 o 7")
debe_fallar(ErrorValidacion, lambda: r.registrar_cliente("Pedro", "7123456"), "Telefono con 7 digitos")
debe_fallar(ErrorValidacion, lambda: r.registrar_cliente("Pedro", "7123456a"), "Telefono con letras")
debe_fallar(ErrorValidacion, lambda: r.registrar_cliente("Otra Ana", "71234567"), "Telefono repetido")
verificar(Cliente.validar_telefono("60000000") and Cliente.validar_telefono("79999999"), "Telefonos validos 6xxxxxxx y 7xxxxxxx")
t = r.crear_pedido("llevar", ana, "lunes")
debe_fallar(ErrorValidacion, lambda: t.agregar_producto(r.obtener_producto("P01"), 0), "Cantidad 0")
debe_fallar(ErrorValidacion, lambda: t.agregar_producto(r.obtener_producto("P01"), 21), "Cantidad 21")
t.agregar_producto(r.obtener_producto("P01"), 15)
debe_fallar(ErrorValidacion, lambda: t.agregar_producto(r.obtener_producto("P01"), 6), "15 + 6 supera el maximo de 20")
debe_fallar(ErrorValidacion, lambda: t.quitar_producto("NOEXISTE"), "Quitar producto que no esta en el pedido")
t.quitar_producto("P01")
verificar(len(t.items) == 0, "Producto quitado en REGISTRADO")
debe_fallar(AttributeError, lambda: setattr(t, "items", []), "No se puede reemplazar la lista de items")
debe_fallar(AttributeError, lambda: t.items.append(1), "La lista de items no se modifica desde fuera")

# ---------------------------------------------------------------- 4
seccion("4. DISPONIBILIDAD POR DIA (chicharron solo domingos)")
c3 = r.armar_combo("C03", "Combo Chicharron", ["P03", "B01"])
verificar(not r.obtener_producto("P03").esta_disponible("lunes"), "Chicharron NO disponible el lunes")
verificar(r.obtener_producto("P03").esta_disponible("Domingo"), "Chicharron disponible el domingo")
verificar(not c3.esta_disponible("lunes") and c3.esta_disponible("domingo"), "Combo disponible solo si todos sus productos lo estan")
print(r.listar_menu("lunes"))
print(r.listar_menu("domingo"))
debe_fallar(ErrorDisponibilidad, lambda: t.agregar_producto(c3, 1), "Agregar combo con chicharron un lunes")
debe_fallar(ErrorValidacion, lambda: r.listar_menu("feriado"), "Dia invalido")

# ---------------------------------------------------------------- 5
seccion("5. PEDIDO LOCAL (mesas 1-15, una mesa un pedido abierto)")
debe_fallar(ErrorValidacion, lambda: r.crear_pedido("local", ana, "lunes", mesa=16), "Mesa 16")
debe_fallar(ErrorValidacion, lambda: r.crear_pedido("local", ana, "lunes", mesa=0), "Mesa 0")
pl = r.crear_pedido("local", ana, "lunes", mesa=5)
pl.agregar_producto(r.obtener_producto("P02"), 2)
pl.agregar_producto(r.obtener_producto("B03"), 1)
print(pl.generar_detalle())
verificar(pl.calcular_cargos() == 0.0, "Pedido local sin cargos adicionales")
verificar(pl.calcular_total() == 128.0, "Total local = 2 x 55 + jarra (3 x 6 = 18) = Bs 128.00")
debe_fallar(ErrorValidacion, lambda: r.crear_pedido("local", luis, "lunes", mesa=5), "Mesa 5 con pedido abierto")
pl.cambiar_estado("CANCELADO")
r.crear_pedido("local", luis, "lunes", mesa=5)
verificar(True, "Mesa 5 liberada al cancelar el pedido anterior")
debe_fallar(ErrorValidacion, lambda: r.crear_pedido("mesa", ana, "lunes"), "Tipo de pedido invalido")

# ---------------------------------------------------------------- 6
seccion("6. PEDIDO PARA LLEVAR (envase por plato, incluso dentro de combos)")
pw = r.crear_pedido("llevar", ana, "martes")
pw.agregar_producto(c1, 1)                        # 1 plato dentro del combo
pw.agregar_producto(r.obtener_producto("P02"), 2)  # 2 platos
pw.agregar_producto(c2, 1)                        # combo dentro de combo: 1 plato
pw.agregar_producto(r.obtener_producto("B04"), 3)  # bebidas: sin envase en variante A
print(pw.generar_detalle())
verificar(pw.contar_platos() == 4, "4 platos (2 sueltos + 1 en C01 + 1 en C02 anidado)")
verificar(pw.calcular_cargos() == 8.0, "Envases = 4 x Bs 2 = Bs 8.00")

# ---------------------------------------------------------------- 7
seccion("7. DELIVERY: zonas, envio gratis, pedido minimo, metodos de pago")
for zona, esperado in [("Cercado", 8), ("Quillacollo", 15), ("Sacaba", 15), ("Vinto", 20)]:
    d = r.crear_pedido("delivery", ana, "viernes", zona=zona)
    d.agregar_producto(r.obtener_producto("P02"), 1)
    verificar(d.calcular_cargos() == esperado, f"Envio a {zona} = Bs {esperado}")
debe_fallar(ErrorValidacion, lambda: r.crear_pedido("delivery", ana, "viernes", zona="Tiquipaya"), "Zona inexistente")
dg = r.crear_pedido("delivery", ana, "viernes", zona="Cercado")
dg.agregar_producto(r.obtener_producto("P02"), 3)
verificar(dg.calcular_subtotal() == 165 and dg.calcular_cargos() == 0.0, "Cercado con subtotal Bs 165 >= 150: envio GRATIS")
dq = r.crear_pedido("delivery", ana, "viernes", zona="Quillacollo")
dq.agregar_producto(r.obtener_producto("P02"), 3)
verificar(dq.calcular_cargos() == 15.0, "Quillacollo con Bs 165: envio NO es gratis (solo Cercado)")
dm = r.crear_pedido("delivery", ana, "viernes", zona="Cercado")
dm.agregar_producto(r.obtener_producto("P01"), 1)
debe_fallar(ErrorEstadoPedido, lambda: dm.cambiar_estado("EN_PREPARACION"), "Delivery bajo el minimo (Bs 35 < 40)")
debe_fallar(ErrorEstadoPedido, lambda: r.crear_pedido("llevar", ana, "lunes").cambiar_estado("EN_PREPARACION"), "Confirmar pedido vacio")
dg.cambiar_estado("EN_PREPARACION"); dg.cambiar_estado("LISTO"); dg.cambiar_estado("ENTREGADO")
debe_fallar(ErrorPago, lambda: r.cobrar_pedido(dg.numero, Tarjeta("1234")), "Delivery no acepta tarjeta")
print(r.cobrar_pedido(dg.numero, PagoQR("1234567890")))

# ---------------------------------------------------------------- 8
seccion("8. ESTADOS DEL PEDIDO")
pe = r.crear_pedido("llevar", luis, "lunes")
pe.agregar_producto(r.obtener_producto("P04"), 2)
debe_fallar(ErrorEstadoPedido, lambda: pe.cambiar_estado("LISTO"), "REGISTRADO -> LISTO")
debe_fallar(ErrorEstadoPedido, lambda: pe.cambiar_estado("ENTREGADO"), "REGISTRADO -> ENTREGADO")
debe_fallar(ErrorEstadoPedido, lambda: pe.cambiar_estado("INVENTADO"), "Estado inexistente")
pe.cambiar_estado("EN_PREPARACION")
debe_fallar(ErrorEstadoPedido, lambda: pe.agregar_producto(r.obtener_producto("P01"), 1), "Agregar en EN_PREPARACION")
debe_fallar(ErrorEstadoPedido, lambda: pe.quitar_producto("P04"), "Quitar en EN_PREPARACION")
debe_fallar(ErrorEstadoPedido, lambda: pe.cambiar_estado("CANCELADO"), "Cancelar desde EN_PREPARACION")
debe_fallar(ErrorPago, lambda: r.cobrar_pedido(pe.numero, Efectivo(500)), "Cobrar antes de ENTREGADO")
pe.cambiar_estado("LISTO"); pe.cambiar_estado("ENTREGADO")
debe_fallar(ErrorEstadoPedido, lambda: pe.cambiar_estado("CANCELADO"), "Cancelar un pedido ENTREGADO")
pc = r.crear_pedido("llevar", luis, "lunes")
pc.cambiar_estado("CANCELADO")
debe_fallar(ErrorEstadoPedido, lambda: pc.agregar_producto(r.obtener_producto("P01"), 1), "Agregar a pedido cancelado")
verificar(pc.estado == "CANCELADO", "Cancelar desde REGISTRADO es valido")

# ---------------------------------------------------------------- 9
seccion("9. PAGOS: efectivo, QR, tarjeta")
debe_fallar(ErrorPago, lambda: r.cobrar_pedido(pe.numero, Efectivo(10)), "Efectivo insuficiente (Bs 10 < 54)")
print(r.cobrar_pedido(pe.numero, Efectivo(100)))
debe_fallar(ErrorPago, lambda: r.cobrar_pedido(pe.numero, PagoQR("1234567890")), "Cobrar dos veces el mismo pedido")
debe_fallar(ErrorPago, lambda: PagoQR("12345"), "QR con 5 digitos")
debe_fallar(ErrorPago, lambda: PagoQR("12345678ab"), "QR con letras")
debe_fallar(ErrorPago, lambda: Tarjeta("12"), "Tarjeta con 2 digitos")
debe_fallar(ErrorPago, lambda: Efectivo(0), "Efectivo con monto 0")
ptar = r.crear_pedido("llevar", ana, "lunes")
ptar.agregar_producto(r.obtener_producto("P02"), 2)   # 110 + 2 envases (4) = 114
pedido_listo(r, ptar)
print(r.cobrar_pedido(ptar.numero, Tarjeta("4321")))
verificar(ptar.monto_cobrado() == 117.42, "Tarjeta: 114 + 3% = Bs 117.42")
pqr = r.crear_pedido("local", luis, "lunes", mesa=7)
pqr.agregar_producto(r.obtener_producto("P01"), 1)
pedido_listo(r, pqr)
print(r.cobrar_pedido(pqr.numero, PagoQR("9876543210")))

# ---------------------------------------------------------------- 10
seccion("10. RETRASO EN DELIVERY (> 60 min -> devolucion del envio)")
tarde = r.crear_pedido("delivery", ana, "viernes", zona="Sacaba", registrado_en=datetime.now() - timedelta(minutes=90))
tarde.agregar_producto(r.obtener_producto("P02"), 2)    # 110 + 15 envio
pedido_listo(r, tarde)
print(tarde.generar_detalle())
verificar(tarde.calcular_compensacion() == 15.0, "Entrega a los 90 min: compensacion = envio (Bs 15)")
verificar(tarde.calcular_total_a_pagar() == 110.0, "Total a pagar con compensacion = Bs 110.00")
print(r.cobrar_pedido(tarde.numero, PagoQR("1112223334")))
t0 = datetime.now() - timedelta(minutes=60)
a_tiempo = r.crear_pedido("delivery", ana, "viernes", zona="Sacaba", registrado_en=t0)
a_tiempo.agregar_producto(r.obtener_producto("P02"), 2)
a_tiempo.cambiar_estado("EN_PREPARACION"); a_tiempo.cambiar_estado("LISTO")
a_tiempo.cambiar_estado("ENTREGADO", t0 + timedelta(minutes=60))
verificar(a_tiempo.calcular_compensacion() == 0.0, "Entrega a los 60 min exactos: sin compensacion")
print(r.cobrar_pedido(a_tiempo.numero, Efectivo(200)))

# ---------------------------------------------------------------- 11
seccion("11. ABSTRACCION")
debe_fallar(TypeError, lambda: Producto("x", "x", 1), "Producto es abstracta")
debe_fallar(TypeError, lambda: Pedido(1, ana, "lunes"), "Pedido es abstracta")
debe_fallar(TypeError, lambda: MetodoPago(), "MetodoPago es abstracta")
debe_fallar(TypeError, lambda: Bebida("b", "b", 5), "Bebida (sin calcular_precio) no se instancia")

# ---------------------------------------------------------------- 12
seccion("12. REPORTE DE VENTAS DEL DIA")
print(r.generar_reporte())

# ---------------------------------------------------------------- 13
seccion("13. REGLAS DE CADA VARIANTE (combo de referencia = Bs 41 sin descuento)")
esperado = {"A": 36.90, "B": 36.08, "C": 37.72, "D": 41.00, "E": 36.90, "F": 33.95}
for letra, valor in esperado.items():
    variante.usar(letra)
    rv = nuevo_restaurante()
    c = rv.armar_combo("C01", "Combo", ["P01", "B01"])
    verificar(c.calcular_precio() == valor, f"Variante {letra}: combo = Bs {c.calcular_precio():.2f}")

variante.usar("B"); rb = nuevo_restaurante()
pb = rb.crear_pedido("local", ana, "martes", mesa=1)
pb.agregar_producto(rb.obtener_producto("B02"), 3)
verificar(pb.calcular_descuentos() == 5.0 and pb.calcular_total() == 10.0, "B martes 2x1: 3 vasos de refresco = Bs 10 (1 gratis)")
pb2 = rb.crear_pedido("local", ana, "lunes", mesa=2)
pb2.agregar_producto(rb.obtener_producto("B02"), 2)
verificar(pb2.calcular_descuentos() == 0.0, "B lunes: sin 2x1")
pb3 = rb.crear_pedido("local", ana, "martes", mesa=3)
pb3.agregar_producto(rb.obtener_producto("B04"), 2)
verificar(pb3.calcular_descuentos() == 0.0, "B martes: la gaseosa no entra al 2x1")
pd = rb.crear_pedido("delivery", ana, "viernes", zona="Vinto")
pd.agregar_producto(rb.obtener_producto("P02"), 3)
verificar(pd.calcular_cargos() == 0.0, "B: Vinto con Bs 165 -> envio gratis")

variante.usar("C"); rc = nuevo_restaurante()
debe_fallar(ErrorValidacion, lambda: rc.armar_combo("CX", "Gigante", ["P01", "P02", "P03", "P04", "B01"]), "C: combo de 5 productos")
pc2 = rc.crear_pedido("llevar", ana, "lunes")
pc2.agregar_producto(rc.obtener_producto("P01"), 1); pc2.agregar_producto(rc.obtener_producto("B01"), 2)
verificar(pc2.calcular_cargos() == 4.5, "C: envase por PRODUCTO (1 plato + 2 vasos) = 3 x 1.50")

variante.usar("D"); rd = nuevo_restaurante()
verificar(rd.armar_combo("C01", "Dos", ["P01", "B01"]).calcular_precio() == 41.0, "D: combo de 2 productos sin descuento")
verificar(rd.armar_combo("C02", "Tres", ["P01", "B01", "B02"]).calcular_precio() == 39.1, "D: combo de 3 productos 15% = Bs 39.10")
pl6 = rd.crear_pedido("local", ana, "lunes", mesa=1)
pl6.agregar_producto(rd.obtener_producto("P02"), 6)
verificar(pl6.calcular_descuentos() == 16.5 and pl6.calcular_total() == 313.5, "D: local de 6 platos 5% -> Bs 313.50")
pl5 = rd.crear_pedido("local", ana, "lunes", mesa=2)
pl5.agregar_producto(rd.obtener_producto("P02"), 5)
verificar(pl5.calcular_descuentos() == 0.0, "D: local de 5 platos sin descuento")
pdd = rd.crear_pedido("delivery", ana, "lunes", zona="Cercado")
pdd.agregar_producto(rd.obtener_producto("P02"), 4)
verificar(pdd.calcular_cargos() == 8.0, "D: no hay envio gratis (ni con Bs 220)")
debe_fallar(ErrorEstadoPedido, lambda: rd.crear_pedido("delivery", ana, "lunes", zona="Cercado").cambiar_estado("EN_PREPARACION"), "D: minimo Bs 60 / pedido vacio")

variante.usar("E"); re_ = nuevo_restaurante()
pe_ = re_.crear_pedido("llevar", ana, "lunes")
pe_.agregar_producto(re_.obtener_producto("P01"), 1); pe_.agregar_producto(re_.obtener_producto("B01"), 1)
verificar(pe_.calcular_cargos() == 3.0, "E: envase Bs 3 por plato, bebida sin cargo")
pe_.cambiar_estado("EN_PREPARACION"); pe_.cambiar_estado("LISTO"); pe_.cambiar_estado("ENTREGADO")   # total 44
pe2 = re_.crear_pedido("llevar", ana, "lunes")
pe2.agregar_producto(re_.armar_combo("C01", "Combo", ["P01", "B01"]), 1)  # 36.90 + 3 = 39.90
pe2.cambiar_estado("EN_PREPARACION"); pe2.cambiar_estado("LISTO"); pe2.cambiar_estado("ENTREGADO")
re_.cobrar_pedido(pe2.numero, Efectivo(50))
verificar(pe2.monto_cobrado() == 39.5, "E: efectivo Bs 39.90 -> redondeo hacia abajo a Bs 39.50")

variante.usar("F"); rf = nuevo_restaurante()
verificar(not rf.obtener_producto("P04").esta_disponible("martes"), "F: sopa de mani NO disponible el martes")
verificar(rf.obtener_producto("P04").esta_disponible("lunes") and rf.obtener_producto("P04").esta_disponible("jueves"), "F: sopa de mani lunes y jueves")
verificar(rf.obtener_producto("P03").esta_disponible("martes"), "F: chicharron todos los dias")

variante.usar("A")
print(f"\n{'=' * 70}\nTODAS LAS PRUEBAS PASARON ({total_asserts} verificaciones)\n{'=' * 70}")
