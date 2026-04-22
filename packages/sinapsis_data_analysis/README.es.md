<h1 align="center"><br/><a href="https://sinapsis.tech/"><img alt="" src="https://github.com/Sinapsis-AI/brand-resources/blob/main/sinapsis_logo/4x/logo.png?raw=true" width="300"/></a><br/>Sinapsis Análisis de datos
<br/></h1>
<h4 align="center">Módulo para capacitación, análisis e inferencia de modelos de aprendizaje automático, utilizando las bibliotecas Scikit-learn y XGBoost.</h4>
<p align="center"><a href="#installation">🐍 Instalación</a> •
<a href="#features"> 🚀 Características</a> •
<a href="#example"> 📚 Ejemplo de uso</a> •
<a href="#documentation">📙 Documentación</a> •
<a href="#license"> 🔍 Licencia </a>


<strong>Sinapsis Análisis de datos</strong> proporciona un conjunto completo de herramientas para la formación de modelos de aprendizaje automático, evaluación e inferencia utilizando bibliotecas estándar de la industria como scikit-learn y XGBoost.

<h2 id="installation"> 🐍 Instalación </h2>

Instala el administrador de paquetes de tu elección. Alentamos el uso de <code>uv</code>


Ejemplo con <code>uv</code>:



```bash
  uv pip install sinapsis-data-analysis --extra-index-url https://pypi.sinapsis.tech
```

o con solo <code>pip</code>:

```bash
  pip install sinapsis-data-analysis --extra-index-url https://pypi.sinapsis.tech
```
<h2 id="features">🚀 Características</h2><h3> Plantillas soportadas</h3>
<strong>Sinapsis Análisis de datos</strong> proporciona una variedad de plantillas para los flujos de trabajo de aprendizaje automático:


<details><summary><strong><span style="font-size: 1.25em;">Modelos Scikit-Learn</span></strong></summary>
</details>


Se admiten los siguientes tipos de modelos:
<ul>
<li><strong>Modelos lineales</strong>: Regresión lineal, Ridge, Lasso, ElasticNet, LogisticRegression, etc.</li>

<li><strong>Modelos de vecinos</strong>: KNeighborsClassifier, KNeighborsRegressor, RadiusNeighborsClassifier, etc.</li>

<li><strong>Modelos de Red Neural</strong>: MLPClassifier, MLPRegressor, BernoulliRBM</li>

<li><strong>Modelos de árbol</strong>: DecisiónTreeClassifier, DecisionTreeRegressor, ExtraTreeClassifier, etc.</li>
</ul>
Cada plantilla utiliza los mismos atributos base:
<ul>
<li><strong><code>generic_field_key</code> (estr, requerido)</strong>: Clave del campo genérico donde se almacenan los conjuntos de datos</li>

<li><strong><code>model_save_path</code> (estr, requerido)</strong>: Camino donde se salvará el modelo entrenado
</li>
</ul>

<details><summary><strong><span style="font-size: 1.25em;">Modelos XGBoost</span></strong></summary>
</details>


Las plantillas modelo XGBoost incluyen:
<ul>
<li>XGBClassifier</li>

<li>XGBRegressor</li>

<li>XGBRanker</li>

<li>XGBRFClassifier</li>

<li>XGBRFRegressor</li>

<li>Booster</li>
</ul>
Los atributos son los mismos que los de las plantillas Scikit-learn.



<details><summary><strong><span style="font-size: 1.25em;">Manifold Learning</span></strong></summary>
</details>


Plantillas para la reducción de la dimensionalidad utilizando técnicas de aprendizaje múltiple de scikit-learn:
<ul>
<li><strong>SKLearnManifold</strong>: Clase base para todos los algoritmos de aprendizaje múltiple</li>

<li><strong><code>generic_field_key</code> (estr, requerido)</strong>: Clave del campo genérico donde se almacenan los datos de entrada</li>
</ul>
Los algoritmos específicos incluyen t-SNE, MDS, Isomap, LocallyLinear Embedding, y más.



<details><summary><strong><span style="font-size: 1.25em;">Plantillas de referencia</span></strong></summary>
</details>


Plantillas para utilizar modelos entrenados para hacer predicciones sobre nuevos datos:
<ul>
<li><strong>SKLearnInference</strong>: Para inferencia con los modelos de aprendiz</li>

<li><strong>XGBoostInference</strong>: Para inferencia con modelos XGBoost</li>
</ul>
Para usar estas plantillas, debe reemplazar las <strong><code>model_path</code></strong> apuntar al camino del modelo entrenado.


<blockquote>

[! TIP]
Usa el comando de CLI <code>sinapsis info --all-template-names</code> para mostrar una lista con todos los nombres disponibles de Plantillas instalados con Sinapsis Data Analysis.

[! TIP]
Usa el comando de CLI <code>sinapsis info --example-template-config TEMPLATE_NAME</code> para producir un ejemplo Agente config para la Plantilla especificado en <strong><em>TEMPLATE_NAME</em></strong>.

</blockquote>

Por ejemplo, para <strong><em>Regreso lineal</em></strong> usa <code>sinapsis info --example-template-config LinearRegression</code> para producir un config de ejemplo.
<h2 id="example"> 📚 Ejemplo de uso </h2>
A continuación se muestra una configuración de ejemplo para <strong>Sinapsis Análisis de datos</strong> usando LinearRegressionWrapper para regresión.


<details><summary><strong><span style="font-size: 1.25em;">Ejemplo de configuración</span></strong></summary>
</details>


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



Para ejecutar la configuración, utilice el CLI:

```bash
sinapsis run name_of_config.yml
```
<h2 id="documentation">📙 Documentación</h2>
La documentación para este y otros paquetes de sinapsis está disponible en <a href="https://docs.sinapsis.tech/docs">web de sinapsis</a>

Los tutoriales para diferentes proyectos dentro de sinapsis están disponibles en <a href="https://docs.sinapsis.tech/tutorials">sinapsis tutoriales página</a>
<h2 id="license">🔍 Licencia</h2>
Este proyecto está licenciado bajo la licencia AGPLv3, que fomenta la colaboración abierta y el intercambio. Para más detalles, consulta el archivo <a href="LICENSE">LICENSE</a>.

Para uso comercial, consulta el  <a href="https://sinapsis.tech"> sitio web oficial de Sinapsis</a> para información sobre la obtención de una licencia comercial.

