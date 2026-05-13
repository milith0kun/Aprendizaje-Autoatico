# Proyecto: Aprendizaje Automático - Configuración de Skills

Este archivo establece las reglas fundamentales para el manejo de Jupyter Notebooks y archivos de Google Colab en este proyecto.

## Mandatos para Jupyter Notebooks (.ipynb)
- **Integridad del JSON:** Nunca edites un archivo `.ipynb` directamente con reemplazos de texto simples si existe riesgo de romper la estructura JSON. Usa siempre `nb_helper.py` para modificaciones estructurales.
- **Estructura de Celdas:** Mantén una organización lógica:
  1. **Imports y Configuración**: Primera celda de código.
  2. **Carga de Datos**: Segunda sección.
  3. **Procesamiento/Análisis**: Secciones numeradas.
  4. **Conclusión/Resultados**: Celda final de markdown.
- **Metadatos de Colab:** Preserva siempre los metadatos de Google Colab (ej. `id`, `colab` settings) para evitar problemas de sincronización al subir el archivo de nuevo a la nube.

## Optimización para Google Colab
- **Comandos de Sistema:** Comenta los comandos de instalación (`!pip install`) antes de guardar para evitar ejecuciones accidentales, o agrúpalos en una celda de "Configuración Inicial".
- **Rutas de Archivos:** Usa rutas relativas siempre que sea posible para asegurar la portabilidad entre el entorno local y Colab.
- **Google Drive:** Si se detecta el uso de archivos externos, incluye un comentario/instrucción para montar Google Drive:
  ```python
  # from google.colab import drive
  # drive.mount('/content/drive')
  ```

## Uso del Helper Script
Para modificaciones complejas, utiliza el script `nb_helper.py` incluido en este proyecto.
