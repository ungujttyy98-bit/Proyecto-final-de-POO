"""Menu de consola de Sabor Valluno. Ejecutar: python3 main.py"""
from datetime import datetime
from modelo import variante
from modelo.pagos import Efectivo, PagoQR, Tarjeta
from modelo.utilidades import ErrorDominio
from restaurante import Restaurante

OPCIONES = """
 1. Listar menu de un dia          7. Cambiar estado del pedido
 2. Registrar plato                8. Cobrar pedido
 3. Registrar bebida               9. Reporte de ventas del dia
 4. Armar combo                   10. Cargar menu de ejemplo
 5. Registrar cliente             11. Demostracion automatica (pruebas.py)
 6. Crear pedido / agregar o quitar productos       0. Salir"""


def leer(texto):
    return input(texto + ": ").strip()


def menu_pedido(r):
    tipo = leer("Tipo (local/llevar/delivery)")
    cliente = r._clientes.get(leer("Telefono del cliente"))
    if cliente is None:
        print("  Cliente no registrado (use la opcion 5)")
        return
    dia = leer("Dia de la semana")
    mesa = int(leer("Mesa (1-15)")) if tipo == "local" else None
    zona = leer("Zona (Cercado/Quillacollo/Sacaba/Vinto)") if tipo == "delivery" else None
    pedido = r.crear_pedido(tipo, cliente, dia, mesa=mesa, zona=zona)
    print(f"  Pedido #{pedido.numero} creado")
    while True:
        accion = leer("[a]gregar, [q]uitar, [d]etalle, [f]in")
        if accion == "a":
            pedido.agregar_producto(r.obtener_producto(leer("Codigo")), int(leer("Cantidad")))
        elif accion == "q":
            pedido.quitar_producto(leer("Codigo"))
        elif accion == "d":
            print(pedido.generar_detalle())
        else:
            return


def cobrar(r):
    numero = int(leer("Numero de pedido"))
    print(r.obtener_pedido(numero).generar_detalle())
    forma = leer("Pago (efectivo/qr/tarjeta)")
    if forma == "efectivo":
        metodo = Efectivo(float(leer("Monto recibido")))
    elif forma == "qr":
        metodo = PagoQR(leer("Codigo de transaccion (10 digitos)"))
    else:
        metodo = Tarjeta(leer("Ultimos 4 digitos"))
    print(r.cobrar_pedido(numero, metodo))


def cambiar_estado(r):
    pedido = r.obtener_pedido(int(leer("Numero de pedido")))
    pedido.cambiar_estado(leer("Nuevo estado (EN_PREPARACION/LISTO/ENTREGADO/CANCELADO)").upper())
    print(f"  Estado actual: {pedido.estado}")


def main():
    variante.usar(leer("Variante asignada (A-F)") or "A")
    r = Restaurante()
    while True:
        print(OPCIONES)
        op = leer("Opcion")
        try:
            if op == "0":
                return
            elif op == "1":
                print(r.listar_menu(leer("Dia")))
            elif op == "2":
                r.crear_plato(leer("Codigo"), leer("Nombre"), float(leer("Precio")))
            elif op == "3":
                r.crear_bebida(leer("Codigo"), leer("Nombre"), float(leer("Precio por vaso")),
                               leer("Tipo (refresco/gaseosa)"), leer("Tamano (vaso/jarra)"))
            elif op == "4":
                r.armar_combo(leer("Codigo"), leer("Nombre"), leer("Codigos separados por coma").replace(" ", "").split(","))
            elif op == "5":
                print("  Registrado:", r.registrar_cliente(leer("Nombre"), leer("Telefono")))
            elif op == "6":
                menu_pedido(r)
            elif op == "7":
                cambiar_estado(r)
            elif op == "8":
                cobrar(r)
            elif op == "9":
                print(r.generar_reporte())
            elif op == "10":
                r.cargar_menu_base()
                print("  Menu de ejemplo cargado")
            elif op == "11":
                import pruebas  # noqa: F401  (ejecuta todas las pruebas al importar)
            else:
                print("  Opcion invalida")
        except (ErrorDominio, ValueError) as e:
            print(f"  ERROR: {e}")


if __name__ == "__main__":
    main()
