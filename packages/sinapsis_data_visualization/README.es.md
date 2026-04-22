<h1 align="center"><br/><a href="https://sinapsis.tech/"><img alt="" src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true" width="300"/></a><br/>Sinapsis Data Visualization
<br/></h1>
<h4 align="center"> Paquete con plantillas para visualizar imágenes y distribución de datos utilizando diferentes bibliotecas y técnicas</h4>
<p align="center"><a href="#installation">🐍 Instalación</a> •
<a href="#features">🚀 Características</a> •
<a href="#usage">📚 Ejemplo de uso</a> •
<a href="#documentation">📙 Documentación</a> •
<a href="#license">🔍 Licencia</a>

<h2 id="installation">🐍 Instalación</h2>

Instala el administrador de paquetes de tu elección. Alentamos el uso de <code>uv</code>


Ejemplo con <code>uv</code>:



```bash
  uv pip install sinapsis-data-visualization --extra-index-url https://pypi.sinapsis.tech
```

o con solo <code>pip</code>:

```bash
  pip install sinapsis-data-visualization --extra-index-url https://pypi.sinapsis.tech
```

<blockquote>

[!IMPORTANT]
Las plantillas en cada paquete pueden requerir dependencias adicionales. Para el desarrollo, recomendamos instalar el paquete con todas las dependencias opcionales:

</blockquote>

con <code>uv</code>:

```bash
  uv pip install sinapsis-data-visualization[all] --extra-index-url https://pypi.sinapsis.tech
```

o con solo <code>pip</code>:

```bash
  pip install sinapsis-data-visualization[all] --extra-index-url https://pypi.sinapsis.tech
```
<h2 id="features">🚀 Características</h2>
<blockquote>

[! TIP]
Usa el comando de CLI <code>sinapsis info --all-template-names</code> para mostrar una lista con todos los nombres de plantilla disponibles instalados con Sinapsis Data Tools.

[! TIP]
Usa el comando de CLI <code>sinapsis info --example-template-config TEMPLATE_NAME</code> para producir un ejemplo Agente config para la Plantilla especificado en <strong><em>TEMPLATE_NAME</em></strong>.

</blockquote>

Por ejemplo, para <strong><em>ImageSaver</em></strong> usa <code>sinapsis info --example-template-config ImageSaver</code> para producir el siguiente ejemplo de configuración:


<details id="packages"><summary><strong><span style="font-size: 1.0em;"> Config</span></strong></summary>
</details>


```yaml
agent:
    name: my_test_agent
    description: agent to read images from a local folder and draw annotations if available
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
- template_name: BBoxDrawer
  class_name: BBoxDrawer
  template_input: FolderImageDatasetCV2
  attributes:
    overwrite: false
    randomized_color: true
    draw_confidence: true
    draw_extra_labels: true
    text_style:
      font: 0
      font_scale: 0.5
      thickness: 2
    draw_classification_label: false
    classification_label_position: top_right
    text_box_to_border_offset: 0.01
```
<h2 id="usage">📚 Ejemplo de uso</h2>
Puedes copiar y pegar la siguiente configuración y ejecutarlo usando el cli sinapsis, cambiando el <code>data_dir</code> atributo en el <code>FolderImageDatasetCV2</code> y el <code>root_dir</code> atributo en el <code>ImageSaver</code> plantilla



<details id="usage"><summary><strong><span style="font-size: 1.0em;"> Ejemplo de configuración de agente</span></strong></summary>
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
- template_name: BBoxDrawer
  class_name: BBoxDrawer
  template_input: FolderImageDatasetCV2
  attributes:
    overwrite: false
    randomized_color: true
    draw_confidence: true
    draw_extra_labels: true
    text_style:
      font: 0
      font_scale: 0.5
      thickness: 2
    draw_classification_label: false
    classification_label_position: top_right
    text_box_to_border_offset: 0.01
- template_name: ImageSaver
  class_name: ImageSaver
  template_input: BBoxDrawer
  attributes:
    save_dir: /path/to/save/dir
    extension: jpg
    root_dir: '/path/to/sinapsis/cache'
    save_full_image: true
    save_bbox_crops: false
    save_mask_crops: false
    min_bbox_dim: 5
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

