# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # MLeap: Deploy Spark Pipelines to Production
# MAGIC 
# MAGIC In this notebook we will export our SparkML models using [MLeap](https://github.com/combust/mleap) for fast inference.
# MAGIC 
# MAGIC Because the Java/Scala client for MLflow does not support logging models, we will build the model in Python, and deploy using Scala, a common best practice :-).
# MAGIC 
# MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
# MAGIC * Discuss deployment options
# MAGIC * Export a SparkML model using MLflow + MLeap
# MAGIC * Make predictions in real-time using MLeap
# MAGIC 
# MAGIC **Required Libraries:**
# MAGIC * `ml.combust.mleap:mleap-spark_2.11:0.13.0` via Maven
# MAGIC * `mlflow==1.2.0` via PyPI

# COMMAND ----------

# MAGIC %run "./Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Define Pipeline
# MAGIC 
# MAGIC We will use the same Pipeline as in the Linear Regression Lab.

# COMMAND ----------

# MAGIC %python
# MAGIC from pyspark.ml.feature import OneHotEncoderEstimator, StringIndexer, VectorAssembler
# MAGIC from pyspark.ml import Pipeline
# MAGIC from pyspark.ml.regression import LinearRegression
# MAGIC 
# MAGIC filePath = "dbfs:/mnt/training/airbnb/sf-listings/sf-listings-2019-03-06-clean.parquet/"
# MAGIC airbnbDF = spark.read.parquet(filePath)
# MAGIC (trainDF, testDF) = airbnbDF.randomSplit([.8, .2], seed=42)
# MAGIC trainDF.createOrReplaceTempView("trainDF")
# MAGIC 
# MAGIC categoricalColumns = [field for (field, dataType) in trainDF.dtypes if dataType == "string"]
# MAGIC stages = [] 
# MAGIC for categoricalCol in categoricalColumns:
# MAGIC     stringIndexer = StringIndexer(inputCol=categoricalCol, outputCol=categoricalCol + "Index", handleInvalid="skip")
# MAGIC     encoder = OneHotEncoderEstimator(inputCols=[stringIndexer.getOutputCol()], outputCols=[categoricalCol + "OHE"])
# MAGIC     stages += [stringIndexer, encoder]
# MAGIC 
# MAGIC oheCols = [c + "OHE" for c in categoricalColumns]
# MAGIC numericCols = [field for (field, dataType) in trainDF.dtypes if ((dataType == "double") & (field != "price"))]
# MAGIC assemblerInputs = oheCols + numericCols
# MAGIC assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="features")
# MAGIC 
# MAGIC stagesWithAssembler = stages + [assembler]
# MAGIC 
# MAGIC lr = LinearRegression(labelCol="price", featuresCol="features")
# MAGIC pipeline = Pipeline(stages = stagesWithAssembler + [lr])

# COMMAND ----------

# MAGIC %md
# MAGIC ## Log MLeap Model
# MAGIC 
# MAGIC [MLflow](https://mlflow.org) has a built-in module to export SparkML PipelineModels to MLeap. Let's use it!
# MAGIC 
# MAGIC Here, we need to provide the PipelineModel, sample_input to get the schema, and an artifact path to the [log_model](https://mlflow.org/docs/latest/python_api/mlflow.mleap.html#mlflow-mleap).

# COMMAND ----------

# MAGIC %python
# MAGIC import mlflow
# MAGIC from mlflow.mleap import log_model
# MAGIC 
# MAGIC mlflow.set_experiment(f"/Users/{username}/tr-mlflow")
# MAGIC 
# MAGIC with mlflow.start_run() as run:
# MAGIC   experiment_id = run.info.experiment_id
# MAGIC   run_id = run.info.run_id
# MAGIC   spark.conf.set("mlflow.experiment_id", experiment_id)
# MAGIC   spark.conf.set("mlflow.run_id", run_id)
# MAGIC   pipelineModel = pipeline.fit(trainDF)
# MAGIC   mlflow.mleap.log_model(spark_model=pipelineModel, sample_input=testDF, artifact_path="mleap-model")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Model
# MAGIC 
# MAGIC Let's now switch to Scala to [load](http://mleap-docs.combust.ml/) in our saved MLeap model.

# COMMAND ----------

# MAGIC %scala
# MAGIC import ml.combust.bundle.BundleFile
# MAGIC import ml.combust.mleap.runtime.MleapSupport._
# MAGIC import resource.managed 
# MAGIC 
# MAGIC val experimentId = spark.conf.get("mlflow.experiment_id")
# MAGIC val runId = spark.conf.get("mlflow.run_id")
# MAGIC val zipBundleModel = (for(bundle <- managed(BundleFile("file:/dbfs/databricks/mlflow/" + experimentId + "/" + runId + "/artifacts/mleap-model/mleap/model"))) yield {
# MAGIC   bundle.loadMleapBundle().get
# MAGIC }).opt.get
# MAGIC val model = zipBundleModel.root

# COMMAND ----------

# MAGIC %md
# MAGIC ## LeapFrame
# MAGIC 
# MAGIC Instead of making predictions on a Spark DataFrame, we will make predictions on a MLeap LeapFrame. It is conceptually very similar to a Spark DataFrame.

# COMMAND ----------

# MAGIC %scala
# MAGIC import ml.combust.mleap.runtime.frame.{DefaultLeapFrame, Row}
# MAGIC import ml.combust.mleap.core.types._
# MAGIC 
# MAGIC val trainDF = spark.table("trainDF")
# MAGIC val schema = org.apache.spark.sql.mleap.TypeConverters.sparkSchemaToMleapSchema(trainDF)
# MAGIC 
# MAGIC val transformedData = trainDF.limit(1)
# MAGIC     .collect
# MAGIC     .map { sparkRow: org.apache.spark.sql.Row =>
# MAGIC       ml.combust.mleap.runtime.frame.Row(org.apache.spark.sql.Row.unapplySeq(sparkRow).get: _*)
# MAGIC     }
# MAGIC 
# MAGIC val frame = DefaultLeapFrame(schema, transformedData)

# COMMAND ----------

# MAGIC %md
# MAGIC ### MLeap vs Spark Prediction Speed
# MAGIC 
# MAGIC While Spark is great for batch predictions, it isn't that great for making predictions on a single row. Let's see a rough speed comparison of MLeap vs Spark for predictions on a single record of data.

# COMMAND ----------

# MAGIC %scala
# MAGIC 
# MAGIC // MLeap Prediction Speed
# MAGIC model.transform(frame).get.dataset(0).getDouble(49)

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC # SparkML Prediction Speed
# MAGIC pipelineModel.transform(trainDF.limit(1)).select("prediction").first()[0]

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>