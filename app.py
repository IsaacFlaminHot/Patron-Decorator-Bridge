from flask import Flask, render_template, request
from abc import ABC, abstractmethod
from PIL import Image as PILImage, ImageEnhance, ImageOps
from io import BytesIO
import base64
import os

app = Flask(__name__)

CARPETAS_SUBIDAS = "static/uploads"
os.makedirs(CARPETAS_SUBIDAS, exist_ok=True)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limite de 16MB para uploads

# Interfaz (Patron Bridge) -- Motor del formato
# =========================================================
class InterfaceFormato(ABC):
    @abstractmethod
    def procesar(self, imagen_pil) -> str:
        """Debe recibir un objeto PIL y devolver un string Base64 """
        pass

# Implementaciones concretas del formato (Patron Bridge)
# =========================================================
class FormatoJPG(InterfaceFormato):
    def procesar(self, imagen_pil) -> str:
        if imagen_pil.mode in ("RGBA", "P"):
            imagen_pil = imagen_pil.convert("RGB")

        buffered = BytesIO()
        imagen_pil.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/jpeg;base64,{img_str}" 

class FormatoPNG(InterfaceFormato):
    def procesar(self, imagen_pil) -> str:
        buffered = BytesIO()
        imagen_pil.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        return f"data:image/png;base64,{img_str}"

# Componente Base (Patron Decorator)
# =========================================================
class ImagenComponente(ABC):
    @abstractmethod
    def renderizar(self):
        """Ahora renderizar devuelve un objeto visual PIL.Image"""
        pass

# Patron Bridge
# =========================================================
class Imagen(ImagenComponente):
    def __init__(self, imagen_pil, formato: InterfaceFormato):
        self._imagen_pil = imagen_pil
        self._formato = formato #Agregamos el formato como parte de la clase Imagen, lo que permite separar la abstracción (Imagen) de su implementación (Formato)

    # Método para cambiar el formato de la imagen en tiempo de ejecución. 
    def asignar_formato(self, formato: InterfaceFormato):
        self._formato = formato

    def renderizar(self):
        # Procesamos una copia de la imagen original para no modificarla directamente y permitir aplicar múltiples filtros.
        return self._imagen_pil.copy()

    def exportar_web(self, imagen_final_pil) -> str:
        return self._formato.procesar(imagen_final_pil)

# Patron Decorator
# =========================================================
class FiltroDecorador(ImagenComponente):
    def __init__(self, imagen: ImagenComponente):
        self._imagen = imagen

    @abstractmethod
    def renderizar(self) -> str:
        pass

class FiltroBlancoNegro(FiltroDecorador):
    def renderizar(self):
        img = self._imagen.renderizar()
        return ImageOps.grayscale(img)

class FiltroBrillo(FiltroDecorador):
    def renderizar(self):
        img = self._imagen.renderizar()
        enhancer = ImageEnhance.Brightness(img)
        return enhancer.enhance(1.5)  # Aumenta el brillo en un 50%

class FiltroSepia(FiltroDecorador):
    def renderizar(self):
        img = self._imagen.renderizar()
        gris = ImageOps.grayscale(img)
        return ImageOps.colorize(gris, black="#402000", white="#ffcc99")  # Tonos sepia


# --- Rutas ---
@app.route('/', methods=['GET', 'POST'])
def index():
    imagen_b64 = None
    error = None
    nombre_archivo = None

    if request.method == 'POST':
        archivo = request.files.get("archivo")
        # Ahora solo recibimos el nombre de la imagen en lugar de todo el código gigante
        nombre_archivo_oculto = request.form.get("nombre_archivo_oculto")

        try:
            # ESCENARIO A: El usuario subió un archivo NUEVO
            if archivo and archivo.filename:
                nombre_archivo = archivo.filename
                # Creamos la ruta completa: static/uploads/mi_foto.jpg
                ruta_guardado = os.path.join(CARPETAS_SUBIDAS, nombre_archivo)
                # Guardamos la foto en tu computadora
                archivo.save(ruta_guardado)
                # La abrimos desde la carpeta
                imagen_pil = PILImage.open(ruta_guardado)

            # ESCENARIO B: Ya habíamos subido una foto y solo cambiamos los filtros
            elif nombre_archivo_oculto:
                nombre_archivo = nombre_archivo_oculto
                ruta_guardado = os.path.join(CARPETAS_SUBIDAS, nombre_archivo)
                # La abrimos directamente desde la carpeta sin pedirla de nuevo
                imagen_pil = PILImage.open(ruta_guardado)
            
            else:
                return render_template('index.html', error="Por favor, sube una imagen.")

            # --- LA LÓGICA SIGUE INTACTA ---
            extension = nombre_archivo.lower().split('.')[-1]

            if extension in ["jpg", "jpeg"]:
                formato = FormatoJPG()
            elif extension == "png":
                formato = FormatoPNG()
            else:
                return render_template('index.html', error="Formato no soportado.")

            imagen_base = Imagen(imagen_pil, formato)
            imagen_procesada = imagen_base
            filtros_seleccionados = request.form.getlist("filtros")

            if "bn" in filtros_seleccionados:
                imagen_procesada = FiltroBlancoNegro(imagen_procesada)
            if "brillo" in filtros_seleccionados:
                imagen_procesada = FiltroBrillo(imagen_procesada)
            if "sepia" in filtros_seleccionados:
                imagen_procesada = FiltroSepia(imagen_procesada)    

            resultado_pil = imagen_procesada.renderizar()
            imagen_b64 = imagen_base.exportar_web(resultado_pil)

        except Exception as e:
            error = f"Error al procesar la imagen: {str(e)}"

    return render_template('index.html', 
                           imagen_b64=imagen_b64, 
                           nombre_archivo=nombre_archivo, 
                           error=error)

if __name__ == '__main__':
    app.run(debug=True,)
    