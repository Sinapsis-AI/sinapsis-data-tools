<h1 align="center">
<br/>
<a href="https://sinapsis.tech/">
<img alt="" src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true" width="300"/>
</a>
<br/>Sinapsis Herramientas de datos
<br/>
</h1>

<h4 align="center"> mono-repositorio con paquetes para leer, escribir, procesar datos, incluyendo imágenes, audios, videos, bytes objetos. Los paquetes
puede ser fácilmente extensible para manejar otros tipos de datos.</h4>

<p align="center">
<a href="#installation">🐍 Instalación</a> •
<a href="#packages">📦 Paquetes</a> •
<a href="#usage">📚 Ejemplo de uso</a> •
<a href="#documentation">📙 Documentación</a> •
<a href="#license">🔍 Licencia</a>
</p>
<h2 id="installation">🐍 Instalación</h2>

Este mono-repositorio consiste en diferentes paquetes para manejar datos:

* <code>sinapsis-data-analysis</code>
* <code>sinapsis-data-readers</code>
* <code>sinapsis-data-visualization</code>
* <code>sinapsis-data-writers</code>
* <code>sinapsis-generic-data-tools</code>

Instala el administrador de tu paquete de elección. Alentamos el uso de <code>uv</code>

Ejemplo con <code>uv</code>:

```bash
  uv pip install sinapsis-data-readers --extra-index-url https://pypi.sinapsis.tech
```

o con solo <code>pip</code>:

```bash
  pip install sinapsis-data-readers --extra-index-url https://pypi.sinapsis.tech
```

**Cambia el nombre del paquete para el que deseas instalar**.

<blockquote>

[!IMPORTANT]
Las plantillas en cada paquete pueden requerir dependencias adicionales. Para el desarrollo, recomendamos instalar el paquete con todas las dependencias opcionales:

</blockquote>

con <code>uv</code>:

```bash
  uv pip install sinapsis-data-readers[all] --extra-index-url https://pypi.sinapsis.tech
```

o con solo <code>pip</code>:

```bash
  pip install sinapsis-data-readers[all] --extra-index-url https://pypi.sinapsis.tech
```

**Cambia el nombre del paquete en consecuencia**.

<blockquote>

[!TIP]
También puedes instalar todos los paquetes dentro de este proyecto:

</blockquote>

```bash
  uv pip install sinapsis-data-tools[all] --extra-index-url https://pypi.sinapsis.tech
```

<blockquote>

[!NOTE]
Algunas plantillas también necesitan dependencias del sistema (por ejemplo, ffmpeg). La instalación
depende de su sistema operativo. Para Linux:

</blockquote>

```bash
apt-get install -y ffmpeg
```

<h2 id="packages">📦 Paquetes</h2>

<details id="packages">
<summary><strong><span style="font-size: 1.0em;"> Resumen de paquetes</span></strong></summary>

- **Sinapsis Data Readers**
  - **Audio Readers**\
<em>Lee archivos de audio de varios formatos usando Pydub, Soundfile, entre otros.</em>
  - **Dataset Readers**\
<em>Lee y manipula los conjuntos de datos tabulares de las bibliotecas de scikit, entre otros.</em>
  - **Image Readers**\
<em>Lee y manipula imágenes de COCO, caminos en CSVs, carpetas enteras, etc.</em>
  - **Text Readers**\
<em>Lee los datos de texto de una cadena simple y otras fuentes.</em>
  - **Video Readers**\
<em>Lee cuadros de video usando CV2, Dali, FFMPEG, Torch, entre otros.</em>

- **Sinapsis Data Visualization**\
<em>Visualizar distribuciones de datos y múltiples, así como dibujar todo tipo de anotaciones en imágenes, como cajas delimitadoras, puntos clave, etiquetas, cajas delimitadoras orientadas, máscaras de segmentación, etc.</em>

- **Sinapsis Data Writers**\
<em>Escribe datos a muchos tipos de archivos.</em>

* **Escritores de anotación**\
<em>Guarda anotaciones de texto a JSON, geometrías a polígonos, etc.</em>
  - **Escritores de audio**\
<em>Guarda a archivos de audio usando Soundfile, entre otros.</em>
  - **Escritores de imagen** <em>Guardar a archivos de imagen utilizando CV2, entre otros.</em>
  - **Escritores de vídeo**\
<em>Guarda a archivos de vídeo usando CV2 o FFMPEG, entre otros.</em>

- **Sinapsis Herramientas de datos genéricos**\
<em>Amplia gama de herramientas diversas para manipular datos.</em>

</details>
<blockquote>

[!TIP]
Usa el comando de CLI <code>sinapsis info --all-template-names</code> para mostrar una lista con todos los nombres de plantilla disponibles instalados con Sinapsis Data Tools.

[!TIP]
Usa el comando de CLI <code>sinapsis info --example-template-config TEMPLATE_NAME</code> para producir un ejemplo Agente config para la Plantilla especificado en **<em>TEMPLATE_NAME</em>**.

[!TIP]
Ejecuta la imagen de docker <code>docker run -it --gpus all sinapsis-data-tools:base bash</code>Necesita activar el entorno dentro de la imagen
fuente <code>.venv/bin/activate</code>

</blockquote>

Por ejemplo, para **<em>ImageSaver</em>**
usa <code>sinapsis info --example-template-config ImageSaver</code> para producir el siguiente ejemplo de configuración:

```yaml
agent:
  name: my_test_agent
  description: agent to save image locally
templates:
- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}
- template_name: ImageSaver
  class_name: ImageSaver
  template_input: InputTemplate
  attributes:
    save_dir: /path/to/save/dir
    extension: jpg
    root_dir: '/path/to/sinapsis/cache'
    save_full_image: true
    save_bbox_crops: false
    save_mask_crops: false
    min_bbox_dim: 5
```

<h2 id="usage">📚 Ejemplo de uso</h2>

<details id="usage">
<summary><strong><span style="font-size: 1.0em;"> Ejemplo de configuración de agente</strong></summary>Puedes copiar y pegar la siguiente configuración, y ejecutarla usando el CLI de sinapsis, cambiando el atributo  <code>data_dir</code> en el <code>FolderImageDatasetCV2</code> y el <code>root_dir</code> atributo en la plantilla <code>ImageSaver</code></details>

```yaml
agent:
  name: my_test_agent
  description: agent to save image locally
templates:
- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}
- template_name: FolderImageDatasetCV2
  class_name: FolderImageDatasetCV2
  attributes:
    data_dir: /path/to/image
    pattern: '**/*'
    batch_size: 1
    load_on_init: true
    label_path_index: 0
    is_ground_truth: false

- template_name: ImageSaver
  class_name: ImageSaver
  template_input: FolderImageDatasetCV2
  attributes:
    save_dir: /path/to/save/dir
    extension: jpg
    root_dir: '/path/to/sinapsis/cache'
    save_full_image: true
    save_bbox_crops: false
    save_mask_crops: false
    min_bbox_dim: 5
```

Para ejecutar, simplemente usa:

```bash
sinapsis run name_of_the_config.yml
```

<h2 id="documentation">📙 Documentación</h2>

La documentación para este y otros paquetes de sinapsis está disponible en la <a href="https://docs.sinapsis.tech/docs">web de sinapsis</a>

Los tutoriales para diferentes proyectos dentro de sinapsis están disponibles en <a href="https://docs.sinapsis.tech/tutorials">la página de tutoriales de sinapsis</a>

<h2 id="license">🔍 Licencia</h2>

Este proyecto está licenciado bajo la licencia AGPLv3, que fomenta la colaboración abierta y el intercambio. Para más detalles, consulta el <a href="LICENSE">LICENSE</a> archivo.

Para uso comercial, consulta nuestra página <a href="https://sinapsis.tech">Sitio web de Sinapsis</a> para información sobre la obtención de una licencia comercial.

