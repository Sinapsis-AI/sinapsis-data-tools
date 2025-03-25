<h1 align="center">
<br>
<a href="https://sinapsis.tech/">
  <img
    src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true"
    alt="" width="300">
</a>

<br>
Sinapsis Generic Data Tools
<br>
</h1>

<h4 align="center"> Package with generic data tools for image color conversion, buffering of data packets and other useful tools for handling data</h4>

<p align="center">
<a href="#installation">🐍 Installation</a> •
<a href="#documentation">📙 Documentation</a> •
<a href="#license">🔍 License</a>
</p>

<h2 id="installation">🐍 Installation</h2>


Install using your package manager of choice. We encourage the use of <code>uv</code>

Example with <code>uv</code>:

```bash
  uv pip install sinapsis-generic-data-tools --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-generic-data-tools --extra-index-url https://pypi.sinapsis.tech
```

> [!IMPORTANT]
> Templates in each package may require extra dependencies. For development, we recommend installing the package with all the optional dependencies:
>

with <code>uv</code>:

```bash
  uv pip install sinapsis-generic-data-tools[all] --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-generic-data-tools[all] --extra-index-url https://pypi.sinapsis.tech
```



> [!TIP]
> Use CLI command ``` sinapsis info --all-template-names``` to show a list with all the available Template names installed with Sinapsis Data Tools.

> [!TIP]
> Use CLI command ```sinapsis info --example-template-config TEMPLATE_NAME``` to produce an example Agent config for the Template specified in ***TEMPLATE_NAME***.

For example, for ***ColorConversion*** use ```sinapsis info --example-template-config ImageColorConversion``` to produce the following example config:


```yaml
agent:
    name: my_test_agent
templates:
-   template_name: InputTemplate
    class_name: InputTemplate
    attributes: {}
-   template_name: ImageColorConversion
    class_name: ImageColorConversion
    template_input: InputTemplate
    attributes:
        target_color_space: 2
```


<h2 id="usage">📚 Usage example</h2>
<details id='usage'><summary><strong><span style="font-size: 1.0em;"> Example agent config</span></strong></summary>
You can copy and paste the following config and run it using the sinapsis cli, changing the <code>data_dir</code> attribute in the <code>FolderImageDatasetCV2</code> and the <code>root_dir</code> attribute in the <code>ImageSaver</code> template

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
- template_name: ImageColorConversion
  class_name: ImageColorConversion
  template_input: FolderImageDatasetCV2
  attributes:
        target_color_space: 2
- template_name: ImageSaver
  class_name: ImageSaver
  template_input: ColorConversion
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
**NOTE**: Make sure to update the `data_dir` attribute in the `FolderImageDatasetCV2`, and the `save_dir` and `root_dir` attributes in the `ImageSaver` templates to actual directories

<h2 id="documentation">📙 Documentation</h2>

Documentation for this and other sinapsis packages is available on the [sinapsis website](https://docs.sinapsis.tech/docs)

Tutorials for different projects within sinapsis are available at [sinapsis tutorials page](https://docs.sinapsis.tech/tutorials)

<h2 id="license">🔍 License</h2>

This project is licensed under the AGPLv3 license, which encourages open collaboration and sharing. For more details, please refer to the [LICENSE](LICENSE) file.

For commercial use, please refer to our [official Sinapsis website](https://sinapsis.tech) for information on obtaining a commercial license.



