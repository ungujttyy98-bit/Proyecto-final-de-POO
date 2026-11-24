"""Gestor del menu, clientes y pedidos."""
from collections import Counter
from datetime import date
from modelo import variante
from modelo.clientes import Cliente
from modelo.pagos import MetodoPago
from modelo.pedidos import Pedido, PedidoLocal, PedidoParaLlevar, PedidoDelivery, ENTREGADO, CANCELADO
from modelo.productos import Producto, Plato, RefrescoNatural, Gaseosas, Combo
from modelo.utilidades import ErrorValidacion, DIAS_SEMANA, clave_texto, normalizar_dia


class Restaurante:
    def __init__(self, nombre: str = "Sabor Valluno"):
        self._nombre = nombre
        self._menu = {}
        self._clientes = {}
        self._pedidos = {}
        self._siguiente_numero = 1

    # mi menu 
    def registrar_producto(self, producto: Producto) -> Producto:
        if producto.codigo in self._menu:
            raise ErrorValidacion(f"Ya existe un producto con codigo '{producto.codigo}'")
        self._menu[producto.codigo] = producto
        return producto

    def obtener_producto(self, codigo: str) -> Producto:
        if codigo not in self._menu:
            raise ErrorValidacion(f"No existe el producto '{codigo}'")
        return self._menu[codigo]

    def crear_plato(self, codigo, nombre, precio, dias=None) -> Plato:
        if dias is None:   # los dias restringidos salen de la variante activa
            dias = variante.actual().dias_platos.get(clave_texto(nombre))
        return self.registrar_producto(Plato(codigo, nombre, precio, dias))

    def crear_bebida(self, codigo, nombre, precio, tipo="refresco", tamano="vaso"):
        clase = RefrescoNatural if tipo == "refresco" else Gaseosas
        return self.registrar_producto(clase(codigo, nombre, precio, tamano))

    def armar_combo(self, codigo: str, nombre: str, codigos_productos: list) -> Combo:
        return self.registrar_producto(Combo(codigo, nombre, [self.obtener_producto(c) for c in codigos_productos]))

    def cargar_menu_base(self) -> None:
        self.crear_plato("P01", "Silpancho", 35)
        self.crear_plato("P02", "Pique macho", 55)
        self.crear_plato("P03", "Chicharron", 50)
        self.crear_plato("P04", "Sopa de mani", 25)
        self.crear_bebida("B01", "Mocochinchi (vaso)", 6)
        self.crear_bebida("B02", "Limonada (vaso)", 5)
        self.crear_bebida("B03", "Mocochinchi (jarra)", 6, tamano="jarra")
        self.crear_bebida("B04", "Gaseosa cola (vaso)", 7, tipo="gaseosa")

    def listar_menu(self, dia: str) -> str:
        dia = normalizar_dia(dia)
        l = [f"=== MENU DEL {dia.upper()} (variante {variante.actual().letra}) ==="]
        for p in self._menu.values():
            if p.esta_disponible(dia):
                l.append("  " + str(p))
        return "\n".join(l)

    # mi clientes 
    def registrar_cliente(self, nombre: str, telefono: str) -> Cliente:
        cliente = Cliente(nombre, telefono)
        if telefono in self._clientes:
            raise ErrorValidacion(f"Ya existe un cliente con el telefono {telefono}")
        self._clientes[telefono] = cliente
        return cliente

    # mi pedidos 
    def crear_pedido(self, tipo: str, cliente: Cliente, dia: str, mesa=None, zona=None, registrado_en=None) -> Pedido:
        n = self._siguiente_numero
        if tipo == "local":
            for p in self._pedidos.values():
                if p.ocupa_mesa(mesa) and p.estado not in (ENTREGADO, CANCELADO):
                    raise ErrorValidacion(f"La mesa {mesa} ya tiene un pedido abierto (#{p.numero})")
            pedido = PedidoLocal(n, cliente, dia, mesa, registrado_en)
        elif tipo == "llevar":
            pedido = PedidoParaLlevar(n, cliente, dia, registrado_en)
        elif tipo == "delivery":
            pedido = PedidoDelivery(n, cliente, dia, zona, registrado_en)
        else:
            raise ErrorValidacion("Tipo de pedido invalido: use 'local', 'llevar' o 'delivery'")
        self._pedidos[n] = pedido
        self._siguiente_numero += 1
        return pedido

    def obtener_pedido(self, numero: int) -> Pedido:
        if numero not in self._pedidos:
            raise ErrorValidacion(f"No existe el pedido #{numero}")
        return self._pedidos[numero]

    def cobrar_pedido(self, numero: int, metodo: MetodoPago) -> str:
        pedido = self.obtener_pedido(numero)
        pedido.aceptar_pago(metodo)
        return "----- COMPROBANTE -----\n" + pedido.comprobante()

    def generar_reporte(self, fecha: date = None) -> str:
        fecha = fecha or date.today()
        pagados = [p for p in self._pedidos.values()
                   if p.pagado and (p.entregado_en or p.registrado_en).date() == fecha]
        por_tipo, productos = {}, Counter()
        for p in pagados:
            cant, monto = por_tipo.get(p.nombre_tipo(), (0, 0.0))
            por_tipo[p.nombre_tipo()] = (cant + 1, monto + p.monto_cobrado())
            for item in p.items:
                productos[item.producto.nombre] += item.cantidad
        l = [f"===== REPORTE DE VENTAS {fecha} =====", "Ventas por tipo de pedido:"]
        for tipo, (cant, monto) in sorted(por_tipo.items()):
            l.append(f"  {tipo:<12} {cant} pedido(s)  Bs {monto:>9.2f}")
        l.append(f"  {'TOTAL':<12} {len(pagados)} pedido(s)  Bs {sum(m for _, m in por_tipo.values()):>9.2f}")
        l.append("Top 3 productos mas vendidos:")
        for i, (nombre, cant) in enumerate(productos.most_common(3), 1):
            l.append(f"  {i}. {nombre} ({cant} unidades)")
        if not productos:
            l.append("  (sin ventas)")
        return "\n".join(l)
