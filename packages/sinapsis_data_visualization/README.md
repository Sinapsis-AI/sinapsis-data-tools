<h1 align="center">
<br>
<a href="https://sinapsis.tech/">
  <img
    src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true"
    alt="" width="300">
</a>

<br>
Sinapsis Data Visualization
<br>
</h1>

<h4 align="center"> Package with templates to visualize images and data distribution using different libraries and techniques</h4>

<p align="center">
<a href="#installation">🐍 Installation</a> •
<a href="#features">🚀 Features</a> •
<a href="#usage">📚 Usage example</a> •
<a href="#documentation">📙 Documentation</a> •
<a href="#license">🔍 License</a>
</p>

<h2 id="installation">🐍 Installation</h2>

Install using your package manager of choice. We encourage the use of <code>uv</code>

Example with <code>uv</code>:

```bash
  uv pip install sinapsis-data-visualization --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-data-visualization --extra-index-url https://pypi.sinapsis.tech
```

> [!IMPORTANT]
> Templates in each package may require extra dependencies. For development, we recommend installing the package with all the optional dependencies:
>

with <code>uv</code>:

```bash
  uv pip install sinapsis-data-visualization[all] --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-data-visualization[all] --extra-index-url https://pypi.sinapsis.tech
```


<h2 id="features">🚀 Features</h2>



> [!TIP]
> Use CLI command ``` sinapsis info --all-template-names``` to show a list with all the available Template names installed with Sinapsis Data Tools.

> [!TIP]
> Use CLI command ```sinapsis info --example-template-config TEMPLATE_NAME``` to produce an example Agent config for the Template specified in ***TEMPLATE_NAME***.

For example, for ***ImageSaver*** use ```sinapsis info --example-template-config ImageSaver``` to produce the following example config:
<details id='packages'><summary><strong><span style="font-size: 1.0em;"> Config</span></strong></summary>

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


<h2 id="usage">📚 Usage example</h2>
You can copy and paste the following config and run it using the sinapsis cli, changing the <code>data_dir</code> attribute in the <code>FolderImageDatasetCV2</code> and the <code>root_dir</code> attribute in the <code>ImageSaver</code> template

<details id='usage'><summary><strong><span style="font-size: 1.0em;"> Example agent config</span></strong></summary>

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
</details>

To run, simply use:

```bash
sinapsis run name_of_the_config.yml
```
</details>
<h2 id="documentation">📙 Documentation</h2>

Documentation for this and other sinapsis packages is available on the [sinapsis website](https://docs.sinapsis.tech/docs)

Tutorials for different projects within sinapsis are available at [sinapsis tutorials page](https://docs.sinapsis.tech/tutorials)

<h2 id="license">🔍 License</h2>

This project is licensed under the AGPLv3 license, which encourages open collaboration and sharing. For more details, please refer to the [LICENSE](LICENSE) file.

For commercial use, please refer to our [official Sinapsis website](https://sinapsis.tech) for information on obtaining a commercial license.



