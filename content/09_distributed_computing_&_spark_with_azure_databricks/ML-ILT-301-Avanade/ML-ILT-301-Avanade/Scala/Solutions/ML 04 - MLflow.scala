// Databricks notebook source
// MAGIC 
// MAGIC %md-sandbox
// MAGIC 
// MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
// MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
// MAGIC </div>

// COMMAND ----------

// MAGIC %md
// MAGIC # MLflow
// MAGIC 
// MAGIC [MLflow](https://mlflow.org/docs/latest/concepts.html) seeks to address these three core issues:
// MAGIC 
// MAGIC * It’s difficult to keep track of experiments
// MAGIC * It’s difficult to reproduce code
// MAGIC * There’s no standard way to package and deploy models
// MAGIC 
// MAGIC In the past, when examining a problem, you would have to manually keep track of the many models you created, as well as their associated parameters and metrics. This can quickly become tedious and take up valuable time, which is where MLflow comes in.
// MAGIC 
// MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
// MAGIC * Use MLflow to track experiments, log metrics, and compare runs
// MAGIC 
// MAGIC **Required Libraries**: 
// MAGIC * `mlflow==1.2.0` via PyPI

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC <div><img src="https://files.training.databricks.com/images/eLearning/ML-Part-4/mlflow-tracking.png" style="height: 400px; margin: 20px"/></div>

// COMMAND ----------

// MAGIC %run "./Includes/Classroom-Setup"

// COMMAND ----------

// MAGIC %md
// MAGIC Let's start by loading in our SF Airbnb Dataset.

// COMMAND ----------

// MAGIC %python
// MAGIC filePath = "dbfs:/mnt/training/airbnb/sf-listings/sf-listings-2019-03-06-clean.parquet/"
// MAGIC airbnbDF = spark.read.parquet(filePath)
// MAGIC 
// MAGIC (trainDF, testDF) = airbnbDF.randomSplit([.8, .2], seed=42)
// MAGIC print(trainDF.cache().count())

// COMMAND ----------

// MAGIC %md
// MAGIC ### MLflow Tracking
// MAGIC 
// MAGIC MLflow Tracking is a logging API specific for machine learning and agnostic to libraries and environments that do the training.  It is organized around the concept of **runs**, which are executions of data science code.  Runs are aggregated into **experiments** where many runs can be a part of a given experiment and an MLflow server can host many experiments.
// MAGIC 
// MAGIC 
// MAGIC MLflow tracking also serves as a **model registry** so tracked models can easily be stored and, as necessary, deployed into production. This also standardizes this process, which significantly accelerates it and allows for scalability. Experiments can be tracked using libraries in Python, R, and Java as well as by using the CLI and REST calls.  This module will use Python, though the majority of MLflow functionality is also exposed in these other APIs.

// COMMAND ----------

// MAGIC %md
// MAGIC ### Track Runs
// MAGIC 
// MAGIC Each run can record the following information:<br><br>
// MAGIC 
// MAGIC - **Parameters:** Key-value pairs of input parameters such as the number of trees in a random forest model
// MAGIC - **Metrics:** Evaluation metrics such as RMSE or Area Under the ROC Curve
// MAGIC - **Artifacts:** Arbitrary output files in any format.  This can include images, pickled models, and data files
// MAGIC - **Source:** The code that originally ran the experiment
// MAGIC 
// MAGIC **NOTE**: MLflow can only log PipelineModels.

// COMMAND ----------

// MAGIC %python
// MAGIC import mlflow
// MAGIC import mlflow.spark
// MAGIC from pyspark.ml.regression import LinearRegression
// MAGIC from pyspark.ml.feature import VectorAssembler
// MAGIC from pyspark.ml import Pipeline
// MAGIC from pyspark.ml.evaluation import RegressionEvaluator
// MAGIC 
// MAGIC mlflow.set_experiment(f"/Users/{username}/tr-mlflow")
// MAGIC 
// MAGIC with mlflow.start_run(run_name="LR-Single-Feature") as run:
// MAGIC   # Define pipeline
// MAGIC   vecAssembler = VectorAssembler(inputCols=["bedrooms"], outputCol="features")
// MAGIC   lr = LinearRegression(featuresCol="features", labelCol="price")
// MAGIC   pipeline = Pipeline(stages=[vecAssembler, lr])
// MAGIC   pipelineModel = pipeline.fit(trainDF)
// MAGIC   
// MAGIC   # Log parameters
// MAGIC   mlflow.log_param("label", "price-bedrooms")
// MAGIC   
// MAGIC   # Log model
// MAGIC   mlflow.spark.log_model(pipelineModel, "model")
// MAGIC   
// MAGIC   # Evaluate predictions
// MAGIC   predDF = pipelineModel.transform(testDF)
// MAGIC   regressionEvaluator = RegressionEvaluator(predictionCol="prediction", labelCol="price", metricName="rmse")
// MAGIC   rmse = regressionEvaluator.evaluate(predDF)
// MAGIC   
// MAGIC   # Log metrics
// MAGIC   mlflow.log_metric("rmse", rmse)
// MAGIC 
// MAGIC # display_run_uri(run.info.experiment_id, run.info.run_id)

// COMMAND ----------

// MAGIC %md
// MAGIC There, all done! Let's go through the other two linear regression models and then compare our runs. Does anyone remember the RMSE of the other runs?
// MAGIC 
// MAGIC Next let's build our linear regression model but use all of our features.

// COMMAND ----------

// MAGIC %python
// MAGIC from pyspark.ml.feature import RFormula
// MAGIC with mlflow.start_run(run_name="LR-All-Features") as run:
// MAGIC   # Create pipeline
// MAGIC   rFormula = RFormula(formula="price ~ .", featuresCol="features", labelCol="price", handleInvalid="skip")
// MAGIC   lr = LinearRegression(labelCol="price", featuresCol="features")
// MAGIC   pipeline = Pipeline(stages = [rFormula, lr])
// MAGIC   pipelineModel = pipeline.fit(trainDF)
// MAGIC   
// MAGIC   # Log pipeline
// MAGIC   mlflow.spark.log_model(pipelineModel, "model")
// MAGIC   
// MAGIC   # Log parameter
// MAGIC   mlflow.log_param("label", "price-all-features")
// MAGIC   
// MAGIC   # Create predictions and metrics
// MAGIC   predDF = pipelineModel.transform(testDF)
// MAGIC   regressionEvaluator = RegressionEvaluator(labelCol="price", predictionCol="prediction")
// MAGIC   rmse = regressionEvaluator.setMetricName("rmse").evaluate(predDF)
// MAGIC   r2 = regressionEvaluator.setMetricName("r2").evaluate(predDF)
// MAGIC   
// MAGIC   # Log both metrics
// MAGIC   mlflow.log_metric("rmse", rmse)
// MAGIC   mlflow.log_metric("r2", r2)
// MAGIC 
// MAGIC # display_run_uri(run.info.experiment_id, run.info.run_id)

// COMMAND ----------

// MAGIC %md
// MAGIC Finally, we will use Linear Regression to predict the log of the price, due to its log normal distribution.
// MAGIC 
// MAGIC We'll also practice logging artifacts to keep a visual of our log normal histogram.

// COMMAND ----------

// MAGIC %python
// MAGIC from pyspark.ml.feature import RFormula
// MAGIC from pyspark.sql.functions import col, log, exp
// MAGIC import matplotlib.pyplot as plt
// MAGIC 
// MAGIC with mlflow.start_run(run_name="LR-Log-Price") as run:
// MAGIC   # Take log of price
// MAGIC   logTrainDF = trainDF.withColumn("log_price", log(col("price")))
// MAGIC   logTestDF = testDF.withColumn("log_price", log(col("price")))
// MAGIC   
// MAGIC   # Log parameter
// MAGIC   mlflow.log_param("label", "log-price")
// MAGIC   
// MAGIC   # Create pipeline
// MAGIC   rFormula = RFormula(formula="log_price ~ . - price", featuresCol="features", labelCol="log_price", handleInvalid="skip")  
// MAGIC   lr = LinearRegression(labelCol="log_price", predictionCol="log_prediction")
// MAGIC   pipeline = Pipeline(stages = [rFormula, lr])
// MAGIC   pipelineModel = pipeline.fit(logTrainDF)
// MAGIC   
// MAGIC   # Log model
// MAGIC   mlflow.spark.log_model(pipelineModel, "log-model")
// MAGIC   
// MAGIC   # Make predictions
// MAGIC   predDF = pipelineModel.transform(logTestDF)
// MAGIC   expDF = predDF.withColumn("prediction", exp(col("log_prediction")))
// MAGIC   
// MAGIC   # Evaluate predictions
// MAGIC   rmse = regressionEvaluator.setMetricName("rmse").evaluate(expDF)
// MAGIC   r2 = regressionEvaluator.setMetricName("r2").evaluate(expDF)
// MAGIC   
// MAGIC   # Log metrics
// MAGIC   mlflow.log_metric("rmse", rmse)
// MAGIC   mlflow.log_metric("r2", r2)
// MAGIC   
// MAGIC   # Log artifact
// MAGIC   plt.clf()
// MAGIC   logTrainDF.toPandas().hist(column="log_price", bins=100)
// MAGIC   figPath = username + "logNormal.png" 
// MAGIC   plt.savefig(figPath)
// MAGIC   mlflow.log_artifact(figPath)
// MAGIC   display(plt.show())
// MAGIC   
// MAGIC # display_run_uri(run.info.experiment_id, run.info.run_id)

// COMMAND ----------

// MAGIC %md
// MAGIC That's it! Now, let's use MLflow to easily look over our work and compare model performance. You can either query past runs programmatically or use the MLflow UI.

// COMMAND ----------

// MAGIC %md
// MAGIC ### Querying Past Runs
// MAGIC 
// MAGIC You can query past runs programatically in order to use this data back in Python.  The pathway to doing this is an `MlflowClient` object. 

// COMMAND ----------

// MAGIC %python
// MAGIC from mlflow.tracking import MlflowClient
// MAGIC 
// MAGIC client = MlflowClient()

// COMMAND ----------

// MAGIC %python
// MAGIC client.list_experiments()

// COMMAND ----------

// MAGIC %md
// MAGIC You can also use [search_runs](https://mlflow.org/docs/latest/search-syntax.html) to find all runs for a given experiment.

// COMMAND ----------

// MAGIC %python
// MAGIC experiment_id = run.info.experiment_id
// MAGIC runs_df = mlflow.search_runs(experiment_id)
// MAGIC 
// MAGIC display(runs_df)

// COMMAND ----------

// MAGIC %md
// MAGIC Pull the last run and look at metrics.

// COMMAND ----------

// MAGIC %python
// MAGIC runs = client.search_runs(experiment_id, order_by=["attributes.start_time desc"], max_results=1)
// MAGIC runs[0].data.metrics

// COMMAND ----------

// MAGIC %python
// MAGIC run_id = runs[0].info.run_id
// MAGIC # display_run_uri(run.info.experiment_id, run_id)

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC Examine the results in the UI.  Look for the following:<br><br>
// MAGIC 
// MAGIC 1. The `Experiment ID`
// MAGIC 2. The artifact location.  This is where the artifacts are stored in DBFS.
// MAGIC 3. The time the run was executed.  **Click this to see more information on the run.**
// MAGIC 4. The code that executed the run.
// MAGIC 
// MAGIC 
// MAGIC After clicking on the time of the run, take a look at the following:<br><br>
// MAGIC 
// MAGIC 1. The Run ID will match what we printed above
// MAGIC 2. The model that we saved, included a pickled version of the model as well as the Conda environment and the `MLmodel` file.
// MAGIC 
// MAGIC Note that you can add notes under the "Notes" tab to help keep track of important information about your models. 
// MAGIC 
// MAGIC Also, click on the run for the log normal distribution and see that the histogram is saved in "Artifacts".

// COMMAND ----------

// MAGIC %md
// MAGIC ### Load Saved Model
// MAGIC 
// MAGIC Let's practice [loading](https://www.mlflow.org/docs/latest/python_api/mlflow.spark.html) our logged log-normal model.

// COMMAND ----------

// MAGIC %python
// MAGIC run_id = run.info.run_id
// MAGIC 
// MAGIC loaded_model = mlflow.spark.load_model(f"dbfs:/databricks/mlflow/{experiment_id}/{run_id}/artifacts/log-model")
// MAGIC display(loaded_model.transform(testDF))

// COMMAND ----------

// MAGIC %md
// MAGIC ## Log Param, Metrics, and Artifacts
// MAGIC 
// MAGIC Now it's your turn! Log your name, your height, and a fun [matplotlib visualization](https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/scatter_with_legend.html#sphx-glr-gallery-lines-bars-and-markers-scatter-with-legend-py) (by calling the `generate_plot` function below - feel free to modify the viz!) under a run with name `MLflow-Lab` in our new MLflow experiment.

// COMMAND ----------

// MAGIC %python
// MAGIC def generate_plot():
// MAGIC   import numpy as np
// MAGIC   np.random.seed(19680801)
// MAGIC   import matplotlib.pyplot as plt
// MAGIC 
// MAGIC   fig, ax = plt.subplots()
// MAGIC   for color in ['tab:blue', 'tab:orange', 'tab:green']:
// MAGIC       n = 750
// MAGIC       x, y = np.random.rand(2, n)
// MAGIC       scale = 200.0 * np.random.rand(n)
// MAGIC       ax.scatter(x, y, c=color, s=scale, label=color,
// MAGIC                  alpha=0.3, edgecolors='none')
// MAGIC 
// MAGIC   ax.legend()
// MAGIC   ax.grid(True)
// MAGIC #   display(plt.show())
// MAGIC   return fig, plt
// MAGIC 
// MAGIC generate_plot()

// COMMAND ----------

// MAGIC %python
// MAGIC # ANSWER
// MAGIC with mlflow.start_run(run_name="MLflow-Lab") as run:
// MAGIC   # Log your name (parameter)
// MAGIC   mlflow.log_param("name", "brooke")
// MAGIC   
// MAGIC   # Log your height (metric)
// MAGIC   mlflow.log_metric("height", 1.7)
// MAGIC   
// MAGIC   # Log a matplotlib viz
// MAGIC   fig, plt = generate_plot()
// MAGIC   outdir = userhome.replace("dbfs:", "/dbfs")
// MAGIC   figPath =  outdir + "/plot.png" 
// MAGIC   fig.savefig(figPath)
// MAGIC   mlflow.log_artifact(figPath)
// MAGIC   display(fig)
// MAGIC   
// MAGIC   runID = run.info.run_id
// MAGIC   print(f"Inside MLflow Run with id {runID}")
// MAGIC   
// MAGIC # display_run_uri(run.info.experiment_id, run.info.run_id)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Additional Resources
// MAGIC 
// MAGIC **Q:** What is MLflow at a high level?  
// MAGIC **A:** <a href="https://databricks.com/session/accelerating-the-machine-learning-lifecycle-with-mlflow-1-0" target="_blank">Listen to Spark and MLflow creator Matei Zaharia's talk at Spark Summit in 2019.</a>
// MAGIC 
// MAGIC **Q:** Where can I find the MLflow docs?  
// MAGIC **A:** <a href="https://www.mlflow.org/docs/latest/index.html" target="_blank">You can find the docs here.</a>

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
// MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
// MAGIC <br/>
// MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>