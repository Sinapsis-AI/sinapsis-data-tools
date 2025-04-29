<h1 align="center">
<br>
<a href="https://sinapsis.tech/">
  <img
    src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true"
    alt="" width="300">
</a>

<br>
Sinapsis Data Tools
<br>
</h1>

<h4 align="center"> Mono repo with packages to read, write, process data, including images, audios, videos, bytes objects. The packages
can be easily extensible to handle other types of data.</h4>

<p align="center">
<a href="#installation">🐍 Installation</a> •
<a href="#packages">📦 Packages</a> •
<a href="#usage">📚 Usage example</a> •
<a href="#documentation">📙 Documentation</a> •
<a href="#license">🔍 License</a>
</p>

<h2 id="installation">🐍 Installation</h2>

This mono repo consists of different packages to handle data:
* <code>sinapsis-data-analysis</code>
* <code>sinapsis-data-readers</code>
* <code>sinapsis-data-visualization</code>
* <code>sinapsis-data-writers</code>
* <code>sinapsis-generic-data-tools</code>

Install using your package manager of choice. We encourage the use of <code>uv</code>

Example with <code>uv</code>:

```bash
  uv pip install sinapsis-data-readers --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-data-readers --extra-index-url https://pypi.sinapsis.tech
```


**Change the name of the package for the one you want to install**.

> [!IMPORTANT]
> Templates in each package may require extra dependencies. For development, we recommend installing the package with all the optional dependencies:
>

with <code>uv</code>:

```bash
  uv pip install sinapsis-data-readers[all] --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-data-readers[all] --extra-index-url https://pypi.sinapsis.tech
```


**Change the name of the package accordingly**.

> [!TIP]
> You can also install all the packages within this project:
>
```bash
  uv pip install sinapsis-data-tools[all] --extra-index-url https://pypi.sinapsis.tech
```
> [!NOTE]
> Some templates also need system dependencies (e.g., ffmpeg). The installation
> depends on your OS. For Linux:
>
```bash
apt-get install -y ffmpeg
```

<h2 id="packages">📦 Packages</h2>
<details id='packages'><summary><strong><span style="font-size: 1.0em;"> Packages summary</span></strong></summary>


- **Sinapsis Data Readers**
    - **Audio Readers**\
    _Read audio files from several formats using Pydub, Soundfile, among others._
    - **Dataset Readers**\
    _Read and manipulate tabular datasets from the scikit libraries, among others._
    - **Image Readers**\
    _Read and manipulate images from COCO, paths in CSVs, whole folders, etc._
    - **Text Readers**\
    _Read text data from a simple string and other sources._
    - **Video Readers**\
    _Read videoframes using CV2, Dali, FFMPEG, Torch, among others._

- **Sinapsis Data Visualization**\
_Visualize data distributions and manifolds, as well as draw all kinds of annotations on images, such as bounding boxes, keypoints, labels, oriented bounding boxes, segmentation masks, etc._
- **Sinapsis Data Writers**\
_Write data to many kinds of files._
    - **Annotation Writers**\
    _Save text annotations to JSON, geometries to polygons, etc._
    - **Audio Writers**\
    _Save to audio files using Soundfile, among others._
    - **Image Writers**
    _Save to image files using CV2, among others._
    - **Video Writers**\
    _Save to video files using CV2 or FFMPEG, among others._
- **Sinapsis Generic Data Tools**\
_Wide range of miscellaneous tools to manipulate your data._
</details>

> [!TIP]
> Use CLI command ``` sinapsis info --all-template-names``` to show a list with all the available Template names installed with Sinapsis Data Tools.

> [!TIP]
> Use CLI command ```sinapsis info --example-template-config TEMPLATE_NAME``` to produce an example Agent config for the Template specified in ***TEMPLATE_NAME***.

> [!TIP]
> Run the docker image ```docker run -it --gpus all sinapsis-data-tools:base bash```
> You need to activate the environment inside the image
> source ```.venv/bin/activate```

For example, for ***ImageSaver*** use ```sinapsis info --example-template-config ImageSaver``` to produce the following example config:


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



