<h1 align="center"><br/><a href="https://sinapsis.tech/"><img alt="" src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true" width="300"/></a><br/>Sinapsis Data Readers
<br/></h1>
<h4 align="center"> Paquete para leer datos en diferentes formatos y asignarlos a un tipo específico de paquete</h4>
<p align="center"><a href="#installation">🐍 Instalación</a> •
<a href="#features">🚀 Características</a> •
<a href="#usage">📚 Ejemplo de uso</a> •
<a href="#documentation">📙 Documentación</a> •
<a href="#license">🔍 Licencia</a>

<h2 id="installation">🐍 Instalación</h2>

Instala el administrador de paquetes de tu elección. Alentamos el uso de <code>uv</code>


Ejemplo con <code>uv</code>:



```bash
  uv pip install sinapsis-data-readers --extra-index-url https://pypi.sinapsis.tech
```

o con solo <code>pip</code>:

```bash
  pip install sinapsis-data-readers --extra-index-url https://pypi.sinapsis.tech
```

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

<blockquote>

[!NOTE]
Algunas plantillas también necesitan dependencias del sistema (por ejemplo, ffmpeg). La instalación
depende de su sistema operativo. Para Linux:

</blockquote>

```bash
apt-get install -y ffmpeg
```
<h2 id="features">🚀 Características</h2><ul>
<li><strong>Sinapsis Data Readers</strong><ul>
<li><strong>Audio Readers</strong>\
<em>Lee archivos de audio de varios formatos usando Pydub, Soundfile, entre otros.</em></li>

<li><strong>Dataset Readers</strong>\
<em>Lee y manipula los conjuntos de datos tabulares de las bibliotecas de scikit, entre otros.</em></li>

<li><strong>Image Readers</strong>\
<em>Leer y manipular imágenes de COCO, caminos en CSVs, carpetas enteras, etc.</em></li>

<li><strong>Text Readers</strong>\
<em>Lee los datos de texto de una cadena simple y otras fuentes.</em></li>

<li><strong>Video Readers</strong>\
<em>Leer videoframes usando CV2, Dali, FFMPEG, Torch, entre otros.</em></li>
</ul></li>
</ul>
<blockquote>

[! TIP]
Usa el comando de CLI <code>sinapsis info --all-template-names</code> para mostrar una lista con todos los nombres de plantilla disponibles instalados con Sinapsis Data Tools.

[! TIP]
Usa el comando de CLI <code>sinapsis info --example-template-config TEMPLATE_NAME</code> para producir un ejemplo Agente config para la Plantilla especificado en <strong><em>TEMPLATE_NAME</em></strong>.

</blockquote>

Por ejemplo, para <strong><em>FolderImageDatasetCV2</em></strong> usa <code>sinapsis info --example-template-config ImageSaver</code> para producir el siguiente ejemplo de configuración:

```yaml
agent:
  name: my_test_agent
  description: Agent to read images from a folder using OpenCV
templates:
- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}
- template_name: FolderImageDatasetCV2
  class_name: FolderImageDatasetCV2
  template_input: InputTemplate
  attributes:
    data_dir: '/path/to/sinapsis/cache/dir'
    pattern: '**/*'
    batch_size: 1
    shuffle_data: false
    samples_to_load: -1
    load_on_init: false
    label_path_index: -2
    is_ground_truth: false
```
<h2 id="usage">📚 Ejemplo de uso</h2>


<details id="usage"><summary><strong><span style="font-size: 1.0em;"> Ejemplo de configuración de agente</span></strong></summary>Puedes copiar y pegar la siguiente configuración y ejecutarlo usando el cli sinapsis, cambiando el <code>data_dir</code> atributo en el <code>FolderImageDatasetCV2</code> y el <code>root_dir</code> atributo en el <code>ImageSaver</code> plantilla
</details>


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
```

Para correr, simplemente usa:

```bash
sinapsis run name_of_the_config.yml
```


<h2 id="documentation">📙 Documentación</h2>
La documentación para este y otros paquetes de sinapsis está disponible en <a href="https://docs.sinapsis.tech/docs">web de sinapsis</a>

Los tutoriales para diferentes proyectos dentro de sinapsis están disponibles en <a href="https://docs.sinapsis.tech/tutorials">sinapsis tutoriales página</a>
<h2 id="license">🔍 Licencia</h2>
Este proyecto está licenciado bajo la licencia AGPLv3, que fomenta la colaboración abierta y el intercambio. Para más detalles, consulta el archivo <a href="LICENSE">LICENSE</a>.

Para uso comercial, consulta el  <a href="https://sinapsis.tech"> sitio web oficial de Sinapsis</a> para información sobre la obtención de una licencia comercial.

