import json


ARCHIVO = "estado_biblioteca.json"


class Usuario:
    def __init__(self, carne, nombre, estado="activo"):
        self.carne = carne
        self.nombre = nombre
        self.estado = estado


class Material:
    def __init__(self, codigo, nombre, cantidad_total):
        self.codigo = codigo
        self.nombre = nombre
        self.cantidad_total = cantidad_total


class Prestamo:
    def __init__(self, carne, nombre_estudiante, codigo_material, nombre_material, horas,
                 devuelto=False):
        self.carne = carne
        self.nombre_estudiante = nombre_estudiante
        self.codigo_material = codigo_material
        self.nombre_material = nombre_material
        self.horas = horas
        self.devuelto = devuelto

    def mostrar(self):
        print(f"Estudiante: {self.nombre_estudiante} (carné {self.carne})")
        print(f"Material: {self.nombre_material} (código {self.codigo_material})")
        print(f"Horas autorizadas: {self.horas}")


class Biblioteca:
    def __init__(self, archivo):
        self.archivo = archivo
        self.usuarios = {}
        self.materiales = {}
        self.prestamos = []

    def cargar(self):
        try:
            with open(self.archivo, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
        except FileNotFoundError:
            self.guardar()
            return True

        if not isinstance(datos["prestamos"], list):
            print("Se esperaba una lista de préstamos.")
            return False

        for carne, usuario in datos["usuarios"].items():
            self.usuarios[carne] = Usuario(carne, usuario["nombre"], usuario["estado"])

        for codigo, material in datos["materiales"].items():
            self.materiales[codigo] = Material(codigo, material["nombre"], material["cantidad_total"])

        for prestamo in datos["prestamos"]:
            self.prestamos.append(Prestamo(
                prestamo["carne"],
                prestamo["nombre_estudiante"],
                prestamo["codigo_material"],
                prestamo["nombre_material"],
                prestamo["horas"],
                prestamo.get("devuelto", False),
            ))
        return True

    def guardar(self):
        datos = {"usuarios": {}, "materiales": {}, "prestamos": []}
        for carne, usuario in self.usuarios.items():
            datos["usuarios"][carne] = {"nombre": usuario.nombre, "estado": usuario.estado}

        for codigo, material in self.materiales.items():
            datos["materiales"][codigo] = {
                "nombre": material.nombre,
                "cantidad_total": material.cantidad_total,
            }

        for prestamo in self.prestamos:
            datos["prestamos"].append(vars(prestamo))

        with open(self.archivo, "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, ensure_ascii=False, indent=4)

    def crear_usuario(self, carne, nombre):
        if carne == "" or nombre == "":
            print("El carné y el nombre son obligatorios.")
            return
        if carne in self.usuarios:
            print("Ya existe un usuario con ese carné.")
            return

        self.usuarios[carne] = Usuario(carne, nombre)
        self.guardar()
        print(f"Usuario {nombre} creado con estado activo.")

    def cambiar_estado_usuario(self, carne, estado):
        if carne not in self.usuarios:
            print("No existe un usuario con ese carné.")
            return
        if estado != "activo" and estado != "inactivo":
            print("Escriba activo o inactivo.")
            return

        self.usuarios[carne].estado = estado
        self.guardar()
        print(f"Estado actualizado a {estado}.")

    def eliminar_usuario(self, carne):
        if carne not in self.usuarios:
            print("No existe un usuario con ese carné.")
            return
        for prestamo in self.prestamos:
            if prestamo.carne == carne and not prestamo.devuelto:
                print("El usuario tiene préstamos pendientes.")
                return

        del self.usuarios[carne]
        self.guardar()
        print("Usuario eliminado.")

    def agregar_material(self, codigo, nombre, cantidad):
        if codigo == "" or nombre == "":
            print("El código y el nombre son obligatorios.")
            return
        if codigo in self.materiales:
            print("Ya existe un material con ese código.")
            return
        if cantidad < 1:
            print("La cantidad debe ser positiva.")
            return

        self.materiales[codigo] = Material(codigo, nombre, cantidad)
        self.guardar()
        print(f"Material {nombre} agregado con {cantidad} unidad(es).")

    def unidades_disponibles(self, codigo):
        disponibles = self.materiales[codigo].cantidad_total
        for prestamo in self.prestamos:
            if prestamo.codigo_material == codigo and not prestamo.devuelto:
                disponibles -= 1
        return disponibles

    def eliminar_material(self, codigo):
        if codigo not in self.materiales:
            print("No existe un material con ese código.")
            return
        if self.unidades_disponibles(codigo) < self.materiales[codigo].cantidad_total:
            print("El material tiene unidades prestadas.")
            return

        del self.materiales[codigo]
        self.guardar()
        print("Material eliminado.")

    def registrar_prestamo(self, carne, codigo, horas):
        if carne not in self.usuarios:
            print("No existe un usuario con ese carné.")
            return
        usuario = self.usuarios[carne]
        if usuario.estado != "activo":
            print("El usuario está inactivo.")
            return
        if codigo not in self.materiales:
            print("No existe un material con ese código.")
            return
        if self.unidades_disponibles(codigo) < 1:
            print("No hay unidades disponibles de ese material.")
            return
        if horas < 1 or horas > 5:
            print("La duración debe ser de 1 a 5 horas.")
            return

        material = self.materiales[codigo]
        prestamo = Prestamo(carne, usuario.nombre, codigo, material.nombre, horas)
        self.prestamos.append(prestamo)
        self.guardar()
        print("\nPréstamo registrado.")
        prestamo.mostrar()

    def devolver_prestamo(self, carne):
        pendientes = []
        for prestamo in self.prestamos:
            if prestamo.carne == carne and not prestamo.devuelto:
                pendientes.append(prestamo)

        if len(pendientes) == 0:
            print(f"No hay préstamos pendientes para el carné {carne}.")
            return

        for numero, prestamo in enumerate(pendientes, start=1):
            print(f"{numero}. {prestamo.nombre_material} (código {prestamo.codigo_material})"
                  f" | Horas autorizadas: {prestamo.horas}")
        print("0. Cancelar")
        numero = pedir_entero("Elija el préstamo que desea devolver: ", 0, len(pendientes))
        if numero == 0:
            return

        pendientes[numero - 1].devuelto = True
        self.guardar()
        print("Devolución registrada. Se liberó una unidad del material.")

    def consultar_prestamos(self, carne):
        encontrados = False
        for prestamo in self.prestamos:
            if prestamo.carne == carne:
                encontrados = True
                print()
                prestamo.mostrar()
                if prestamo.devuelto:
                    print("Estado: devuelto")
                else:
                    print("Estado: pendiente")
        if not encontrados:
            print(f"No hay préstamos registrados para el carné {carne}.")

    def consultar_material(self, codigo):
        if codigo not in self.materiales:
            print("No existe un material con ese código.")
            return

        material = self.materiales[codigo]
        disponibles = self.unidades_disponibles(codigo)
        print(f"Material: {material.nombre} (código {material.codigo})")
        print(f"Cantidad total: {material.cantidad_total}")
        print(f"Unidades disponibles: {disponibles}")
        if disponibles > 0:
            print("Estado: disponible")
        else:
            print("Estado: prestado")


def pedir_texto(mensaje):
    while True:
        texto = input(mensaje).strip()
        if texto != "":
            return texto
        print("Este dato no puede quedar vacío.")


def pedir_entero(mensaje, minimo, maximo=None):
    while True:
        try:
            numero = int(input(mensaje))
        except ValueError:
            print("Ingrese un número entero.")
            continue
        if numero < minimo or (maximo is not None and numero > maximo):
            print("El número está fuera del rango indicado.")
            continue
        return numero


if __name__ == "__main__":
    biblioteca = Biblioteca(ARCHIVO)
    try:
        datos_cargados = biblioteca.cargar()
    except (OSError, ValueError, TypeError, KeyError, AttributeError) as error:
        print(f"No se pudieron cargar o inicializar los datos: {error}")
        datos_cargados = False

    if datos_cargados:
        try:
            opcion = None
            while opcion != 0:
                print("\n===== PRÉSTAMOS DE BIBLIOTECA =====")
                print("1. Registrar préstamo")
                print("2. Crear usuario")
                print("3. Cambiar estado de usuario")
                print("4. Eliminar usuario")
                print("5. Agregar material")
                print("6. Eliminar material")
                print("7. Consultar préstamos")
                print("8. Consultar material")
                print("9. Registrar devolución")
                print("0. Salir")
                opcion = pedir_entero("Elija una opción (0-9): ", 0, 9)

                if opcion == 1:
                    carne = pedir_texto("Carné: ")
                    codigo = pedir_texto("Código del material: ")
                    horas = pedir_entero("Duración en horas (1-5): ", 1, 5)
                    biblioteca.registrar_prestamo(carne, codigo, horas)
                elif opcion == 2:
                    carne = pedir_texto("Carné: ")
                    nombre = pedir_texto("Nombre: ")
                    biblioteca.crear_usuario(carne, nombre)
                elif opcion == 3:
                    carne = pedir_texto("Carné: ")
                    estado = pedir_texto("Nuevo estado (activo/inactivo): ").lower()
                    biblioteca.cambiar_estado_usuario(carne, estado)
                elif opcion == 4:
                    carne = pedir_texto("Carné: ")
                    biblioteca.eliminar_usuario(carne)
                elif opcion == 5:
                    codigo = pedir_texto("Código: ")
                    nombre = pedir_texto("Nombre: ")
                    cantidad = pedir_entero("Cantidad (mínimo 1): ", 1)
                    biblioteca.agregar_material(codigo, nombre, cantidad)
                elif opcion == 6:
                    codigo = pedir_texto("Código del material: ")
                    biblioteca.eliminar_material(codigo)
                elif opcion == 7:
                    carne = pedir_texto("Carné: ")
                    biblioteca.consultar_prestamos(carne)
                elif opcion == 8:
                    codigo = pedir_texto("Código del material: ")
                    biblioteca.consultar_material(codigo)
                elif opcion == 9:
                    carne = pedir_texto("Carné: ")
                    biblioteca.devolver_prestamo(carne)

            print("Programa finalizado. Hasta luego.")
        except OSError as error:
            print(f"No se pudieron guardar los cambios. El programa se cerrará: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nPrograma finalizado.")
