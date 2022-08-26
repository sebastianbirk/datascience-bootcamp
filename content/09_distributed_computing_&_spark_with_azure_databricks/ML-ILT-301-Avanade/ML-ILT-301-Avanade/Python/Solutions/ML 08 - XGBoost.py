# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # XGBoost/LightGBM
# MAGIC 
# MAGIC Up until this point, we have only used SparkML. Let's look at using some third party libraries for Gradient Boosted Trees. 
# MAGIC 
# MAGIC Install these packages before we start using Maven Coordinates:
# MAGIC  * `Azure:mmlspark:0.15` (Light GBM). 
# MAGIC  
# MAGIC Ensure that you are using the [Databricks Runtime for ML](https://docs.microsoft.com/en-us/azure/databricks/runtime/mlruntime) because that has Distributed XGBoost already implemented. 
# MAGIC 
# MAGIC **NOTE:** There is currently only a distributed version of XGBoost for Scala, not Python. We will switch to Scala for that section.
# MAGIC 
# MAGIC **Question**: How do gradient boosted trees differ from random forests? Which parts can be parallelized?
# MAGIC 
# MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
# MAGIC  - Use 3rd party libraries (XGBoost and LightGBM) to further improve your model

# COMMAND ----------

# MAGIC %run "./Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Data Preparation
# MAGIC 
# MAGIC Let's go ahead and index all of our categorical features, and set our label to be `log(price)`.

# COMMAND ----------

from pyspark.ml import Pipeline
from pyspark.ml.feature import *
from pyspark.sql.functions import log, col

filePath = "dbfs:/mnt/training/airbnb/sf-listings/sf-listings-2019-03-06-clean.parquet/"
airbnbDF = spark.read.parquet(filePath)
(trainDF, testDF) = (airbnbDF
                     .withColumn("label", log(col("price")))
                     .randomSplit([.8, .2], seed=42))

categoricalColumns = [field for (field, dataType) in trainDF.dtypes if dataType == "string"]
stages = [] 
for categoricalCol in categoricalColumns:
    stages += [StringIndexer(inputCol=categoricalCol, outputCol=categoricalCol + "Index", handleInvalid="skip")]
    
indexCols = [c + "Index" for c in categoricalColumns]
numericCols = [field for (field, dataType) in trainDF.dtypes if ((dataType == "double") & (field != "price")  & (field != "label"))]
assemblerInputs = indexCols + numericCols
assembler = VectorAssembler(inputCols=assemblerInputs, outputCol="features")
stages += [assembler]
pipeline = Pipeline(stages = stages)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Scala
# MAGIC 
# MAGIC Distributed XGBoost with Spark only has a Scala API, so we are going to create views of our DataFrames to use in Scala, as well as save our (untrained) pipeline to load in to Scala.

# COMMAND ----------

trainDF.createOrReplaceTempView("trainDF")
testDF.createOrReplaceTempView("testDF")

fileName = userhome + "/machine-learning/xgboost_feature_pipeline"
pipeline.write().overwrite().save(fileName)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data/Pipeline in Scala
# MAGIC 
# MAGIC This section is only available in Scala because there is no distributed Python API for XGBoost in Spark yet.
# MAGIC 
# MAGIC Let's load in our data/pipeline that we defined in Python. 

# COMMAND ----------

# MAGIC %scala
# MAGIC import org.apache.spark.ml.Pipeline
# MAGIC 
# MAGIC val fileName = userhome + "/machine-learning/xgboost_feature_pipeline"
# MAGIC val pipeline = Pipeline.load(fileName)
# MAGIC 
# MAGIC val trainDF = spark.table("trainDF")
# MAGIC val testDF = spark.table("testDF")

# COMMAND ----------

# MAGIC %md
# MAGIC ## XGBoost
# MAGIC 
# MAGIC Now we are ready to train our XGBoost model!

# COMMAND ----------

# MAGIC %scala
# MAGIC 
# MAGIC import ml.dmlc.xgboost4j.scala.spark._
# MAGIC import org.apache.spark.sql.functions._
# MAGIC 
# MAGIC val paramMap = List("num_round" -> 100, "eta" -> 0.1, "max_leaf_nodes" -> 50, "seed" -> 42, "missing" -> 0).toMap
# MAGIC 
# MAGIC val xgboostEstimator = new XGBoostRegressor(paramMap)
# MAGIC 
# MAGIC val xgboostPipeline = new Pipeline().setStages(pipeline.getStages ++ Array(xgboostEstimator))
# MAGIC 
# MAGIC val xgboostPipelineModel = xgboostPipeline.fit(trainDF)
# MAGIC val xgboostLogPredictedDF = xgboostPipelineModel.transform(testDF)
# MAGIC 
# MAGIC val expXgboostDF = xgboostLogPredictedDF.withColumn("prediction", exp(col("prediction")))
# MAGIC expXgboostDF.createOrReplaceTempView("expXgboostDF")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Evaluate
# MAGIC 
# MAGIC Now we can evaluate how well our XGBoost model performed.

# COMMAND ----------

expXgboostDF = spark.table("expXgboostDF")

display(expXgboostDF.select("price", "prediction"))

# COMMAND ----------

from pyspark.ml.evaluation import RegressionEvaluator

regressionEvaluator = RegressionEvaluator(predictionCol="prediction", labelCol="price", metricName="rmse")

rmse = regressionEvaluator.evaluate(expXgboostDF)
r2 = regressionEvaluator.setMetricName("r2").evaluate(expXgboostDF)
print(f"RMSE is {rmse}")
print(f"R2 is {r2}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Export to Python
# MAGIC 
# MAGIC We can also export our XGBoost model to use in Python for fast inference on small datasets.

# COMMAND ----------

# MAGIC %scala
# MAGIC 
# MAGIC val nativeModelPath = username + "_nativeModel"
# MAGIC val xgboostModel = xgboostPipelineModel.stages.last.asInstanceOf[XGBoostRegressionModel]
# MAGIC xgboostModel.nativeBooster.saveModel(nativeModelPath)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Predictions in Python
# MAGIC 
# MAGIC Let's pass in an example record to our Python XGBoost model and see how fast we can get predictions!!
# MAGIC 
# MAGIC Don't forget to exponentiate!

# COMMAND ----------

# MAGIC %python
# MAGIC import numpy as np
# MAGIC import xgboost as xgb
# MAGIC bst = xgb.Booster({'nthread': 4})
# MAGIC bst.load_model(username + "_nativeModel")
# MAGIC 
# MAGIC # Per https://stackoverflow.com/questions/55579610/xgboost-attributeerror-dataframe-object-has-no-attribute-feature-names, DMatrix did the trick
# MAGIC 
# MAGIC log_pred = bst.predict(xgb.DMatrix([0.0, 2.0, 0.0, 32.0, 9.0, 1.0, 1.0, 0.0, 0.0, 37.7431, -122.44509, 2.0, 1.0, 1.0, 1.0,
# MAGIC  1.0, 1.0, 100.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]))
# MAGIC print(f"The predicted price for this rental is ${np.exp(log_pred)[0]:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Light GBM
# MAGIC Perhaps try a different algorithm? Let's look at Light GBM (install this Spark package: `Azure:mmlspark:0.15`). Light GBM is an alternative gradient boosting technique to XGBoost to significantly speed up the computation. It also has a Python wrapper.
# MAGIC 
# MAGIC There is a great [blog post](https://towardsdatascience.com/catboost-vs-light-gbm-vs-xgboost-5f93620723db) which covers the differences between LightGBM, XGBoost and Catboost.

# COMMAND ----------

from mmlspark import LightGBMRegressor
from pyspark.sql.functions import exp

gbmModel = LightGBMRegressor(learningRate=.1, numIterations=100, numLeaves=50, labelCol="label")

gbmPipeline = Pipeline(stages = stages + [gbmModel])

gbmPipelineModel = gbmPipeline.fit(trainDF)
gbmLogPredictedDF = gbmPipelineModel.transform(testDF)

expGbmDF = gbmLogPredictedDF.withColumn("prediction", exp(col("prediction")))

# COMMAND ----------

display(expGbmDF.select("price", "prediction"))

# COMMAND ----------

regressionEvaluator = RegressionEvaluator(predictionCol="prediction", labelCol="price", metricName="rmse")

rmse = regressionEvaluator.evaluate(expGbmDF)
r2 = regressionEvaluator.setMetricName("r2").evaluate(expGbmDF)
print(f"RMSE is {rmse}")
print(f"R2 is {r2}")

# COMMAND ----------

# MAGIC %md
# MAGIC Alright! We are significantly improving our model. Later we'll take a look at doing some AutoML and see if we can get a better model!

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>