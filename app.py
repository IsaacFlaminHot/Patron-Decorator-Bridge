from abc import ABC, abstractmethod

# Interfaz (Patron Bridge)
# =========================================================
class InterfaceFormato(ABC):
    @abstractmethod
    def procesar(self) -> str:
        pass

class FormatoJPG(InterfaceFormato):
    def procesar(self) -> str:
        return "Procesando imagen JPG"

class FormatoPNG(InterfaceFormato):
    def procesar(self) -> str:
        return "Procesando imagen PNG"

# Componente Base (Patron Decorator)
# =========================================================
class ImagenComponente(ABC):
    @abstractmethod
    def renderizar(self) -> str:
        pass

# Patron Bridge
# =========================================================
class Imagen(ImagenComponente):
    def __init__(self, nombre: str,formato: InterfaceFormato):
        self.nombre = nombre
        self._formato = formato #Agregamos el formato como parte de la clase Imagen, lo que permite separar la abstracción (Imagen) de su implementación (Formato)

    # Método para cambiar el formato de la imagen en tiempo de ejecución. 
    def asignar_formato(self, formato: InterfaceFormato):
        self._formato = formato

    def renderizar(self) -> str:
        return f"Mostrando imagen '{self.nombre}'  {self._formato.procesar()}"

# Patron Decorator
# =========================================================
class FiltroDecorador(ImagenComponente):
    def __init__(self, imagen: ImagenComponente):
        self._imagen = imagen

    @abstractmethod
    def renderizar(self) -> str:
        pass

class FiltroBlancoNegro(FiltroDecorador):
    def renderizar(self) -> str:
        return f"{self._imagen.renderizar()} con filtro blanco y negro"

class FiltroBrillo(FiltroDecorador):
    def renderizar(self) -> str:
        return f"{self._imagen.renderizar()} con filtro de brillo"  

class FiltroSepia(FiltroDecorador):
    def renderizar(self) -> str:
        return f"{self._imagen.renderizar()} con filtro sepia"  

# --- Programa Principal ---
if __name__ == "__main__":
    # Instanciamos el Bridge con una imagen y un formato
    mi_foto = Imagen("foto_vacaciones.jpg", FormatoJPG())

    #aplicamos varios filtros usando el Decorator
    foto_editada = FiltroBlancoNegro(mi_foto)
    foto_editada = FiltroBrillo(foto_editada)
    foto_editada = FiltroSepia(foto_editada)

    print("Resultado final:")
    print(foto_editada.renderizar())

    # Cambiamos el formato de la imagen usando el Bridge
    mi_foto.asignar_formato(FormatoPNG())

    print("Resultado con nuevo formato:")
    print(mi_foto.renderizar())