<h1 align="center">
<br>
<a href="https://sinapsis.tech/">
  <img
    src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true"
    alt="" width="300">
</a><br>
Sinapsis Data Analysis
<br>
</h1>

<h4 align="center">Module for machine learning model training, analysis, and inference, using the Scikit-learn and XGBoost libraries.</h4>

<p align="center">
<a href="#installation">🐍  Installation</a> •
<a href="#features"> 🚀 Features</a> •
<a href="#example"> 📚 Usage Example</a> •
<a href="#documentation">📙 Documentation</a> •
<a href="#license"> 🔍 License </a>
</p>

**Sinapsis Data Analysis** provides a comprehensive set of tools for machine learning model training, evaluation, and inference using industry-standard libraries like scikit-learn and XGBoost.

<h2 id="installation"> 🐍  Installation </h2>

Install using your package manager of choice. We encourage the use of <code>uv</code>

Example with <code>uv</code>:

```bash
  uv pip install sinapsis-data-analysis --extra-index-url https://pypi.sinapsis.tech
```
 or with raw <code>pip</code>:
```bash
  pip install sinapsis-data-analysis --extra-index-url https://pypi.sinapsis.tech
```


<h2 id="features">🚀 Features</h2>

<h3> Templates Supported</h3>

**Sinapsis Data Analysis** provides a variety of templates for machine learning workflows:

<details>
<summary><strong><span style="font-size: 1.25em;">Scikit-Learn Models</span></strong></summary>

The following model types are supported:

- **Linear Models**: LinearRegression, Ridge, Lasso, ElasticNet, LogisticRegression, etc.
- **Neighbors Models**: KNeighborsClassifier, KNeighborsRegressor, RadiusNeighborsClassifier, etc.
- **Neural Network Models**: MLPClassifier, MLPRegressor, BernoulliRBM
- **Tree Models**: DecisionTreeClassifier, DecisionTreeRegressor, ExtraTreeClassifier, etc.

Each template uses the same base attributes:
- **`generic_field_key` (str, required)**: Key of the generic field where datasets are stored
- **`model_save_path` (str, required)**: Path where the trained model will be saved
</details>

<details>
<summary><strong><span style="font-size: 1.25em;">XGBoost Models</span></strong></summary>

XGBoost model templates include:
- XGBClassifier
- XGBRegressor
- XGBRanker
- XGBRFClassifier
- XGBRFRegressor
- Booster

Attributes are the same as those for Scikit-learn templates.
</details>

<details>
<summary><strong><span style="font-size: 1.25em;">Manifold Learning</span></strong></summary>

Templates for dimensionality reduction using scikit-learn's manifold learning techniques:

- **SKLearnManifold**: Base class for all manifold learning algorithms
  - **`generic_field_key` (str, required)**: Key of the generic field where the input data is stored

Specific algorithms include t-SNE, MDS, Isomap, LocallyLinearEmbedding, and more.
</details>

<details>
<summary><strong><span style="font-size: 1.25em;">Inference Templates</span></strong></summary>

Templates for using trained models to make predictions on new data:

- **SKLearnInference**: For inference with scikit-learn models
- **XGBoostInference**: For inference with XGBoost models

To use these templates, you should replace the **`model_path`** to point to the path of the trained model.
</details>

> [!TIP]
> Use CLI command ``` sinapsis info --all-template-names``` to show a list with all the available Template names installed with Sinapsis Data Analysis.

> [!TIP]
> Use CLI command ```sinapsis info --example-template-config TEMPLATE_NAME``` to produce an example Agent config for the Template specified in ***TEMPLATE_NAME***.

For example, for ***LinearRegression*** use ```sinapsis info --example-template-config LinearRegression``` to produce an example config.

<h2 id="example"> 📚 Usage Example </h2>
Below is an example configuration for **Sinapsis Data Analysis** using LinearRegressionWrapper for regression.

<details>
<summary><strong><span style="font-size: 1.25em;">Example config</span></strong></summary>

```yaml
agent:
  name: sklearn_linear_models_agent
  description: agent to train a LinearRegression model from scikit-learn using the load_diabetes dataset

templates:
- template_name: InputTemplate
  class_name: InputTemplate
  attributes: {}

- template_name: load_diabetesWrapper
  class_name: load_diabetesWrapper
  template_input: InputTemplate
  attributes:
    split_dataset: true
    train_size: 0.8
    load_diabetes:
      return_X_y: false
      as_frame: true

- template_name: LinearRegressionWrapper
  class_name: LinearRegressionWrapper
  template_input: load_diabetesWrapper
  attributes:
    generic_field_for_data: load_diabetesWrapper
    model_save_path: "artifacts/linear_regression.joblib"
    linearregression_init:
      fit_intercept: true
      copy_X: true
      n_jobs: null
      positive: false
```
</details>

To run the config, use the CLI:
```bash
sinapsis run name_of_config.yml
```

<h2 id="documentation">📙 Documentation</h2>

Documentation for this and other sinapsis packages is available on the [sinapsis website](https://docs.sinapsis.tech/docs)

Tutorials for different projects within sinapsis are available at [sinapsis tutorials page](https://docs.sinapsis.tech/tutorials)

<h2 id="license">🔍 License</h2>

This project is licensed under the AGPLv3 license, which encourages open collaboration and sharing. For more details, please refer to the [LICENSE](LICENSE) file.

For commercial use, please refer to our [official Sinapsis website](https://sinapsis.tech) for information on obtaining a commercial license.
