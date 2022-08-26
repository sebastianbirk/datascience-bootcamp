// Databricks notebook source
// MAGIC 
// MAGIC %md-sandbox
// MAGIC 
// MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
// MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
// MAGIC </div>

// COMMAND ----------

// MAGIC %md
// MAGIC # AutoML
// MAGIC 
// MAGIC In this notebook, we will use Sparkling Water's AutoML (get it: H2O + Spark = Sparkling Water) to see if we can find an optimal model for our dataset.
// MAGIC 
// MAGIC Required libraries (PyPI):
// MAGIC * colorama==0.3.8
// MAGIC * h2o-pysparkling-2.4
// MAGIC 
// MAGIC **NOTE**: You will have to change your Databricks runtime to the non-ML Runtime (e.g. 5.2) because H2O's AutoML installs XGBoost, which conflicts with the XGBoost installed in the ML Runtime.
// MAGIC 
// MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
// MAGIC  - Use AutoML to automate the training of various types of models

// COMMAND ----------

// MAGIC %run "../Includes/Classroom-Setup"

// COMMAND ----------

// MAGIC %md
// MAGIC ## Library Isolation
// MAGIC 
// MAGIC We can use [library utilities](https://docs.azuredatabricks.net/user-guide/dev-tools/dbutils.html#dbutils-library) to install Python libraries and create an environment scoped to a notebook session.

// COMMAND ----------

// MAGIC %python
// MAGIC dbutils.library.installPyPI("colorama", "0.3.8")
// MAGIC dbutils.library.installPyPI("h2o-pysparkling-2.4")

// COMMAND ----------

// MAGIC %md
// MAGIC ## Train-Test Split
// MAGIC 
// MAGIC We want to compare apples to apples here, so we are going to do the same train-test split before we get started with H2O.

// COMMAND ----------

// MAGIC %python
// MAGIC filePath = "dbfs:/mnt/training/airbnb/sf-listings/sf-listings-2019-03-06-clean.parquet/"
// MAGIC airbnbDF = spark.read.parquet(filePath)
// MAGIC (trainDF, testDF) = airbnbDF.randomSplit([.8, .2], seed=42)
// MAGIC display(trainDF)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Setting up H2O
// MAGIC 
// MAGIC **NOTE**: You will not be able to view the H2O UI on [Azure Databricks](https://docs.azuredatabricks.net/spark/latest/mllib/third-party-libraries.html#h2o-sparkling-water).

// COMMAND ----------

// MAGIC %python
// MAGIC from pysparkling import *
// MAGIC from pyspark.sql import SparkSession
// MAGIC import h2o
// MAGIC from h2o.automl import H2OAutoML
// MAGIC 
// MAGIC #Set up H2O Configurations
// MAGIC spark = SparkSession.builder.appName("SparklingWaterApp").getOrCreate()
// MAGIC h2oConf = H2OConf(spark).set("spark.ui.enabled", "false")
// MAGIC hc = H2OContext.getOrCreate(spark, conf=h2oConf)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Convert to H2O Frame and Display

// COMMAND ----------

// MAGIC %python
// MAGIC trainH2O = hc.as_h2o_frame(trainDF)
// MAGIC testH2O = hc.as_h2o_frame(testDF)
// MAGIC 
// MAGIC trainH2O[:,0:6].describe() # Unable to display all columns without odd overlap on output

// COMMAND ----------

// MAGIC %md
// MAGIC ## AutoML
// MAGIC 
// MAGIC Now we will use AutoML to train the various models. This may take a few minutes (`max_runtime_secs` set to 300)

// COMMAND ----------

// MAGIC %python
// MAGIC x = trainH2O.columns
// MAGIC y = "price"
// MAGIC x.remove(y)
// MAGIC # Defaults to 5 fold cross-val
// MAGIC aml = H2OAutoML(max_runtime_secs=300, seed=42, project_name="airbnb_dataset", stopping_metric="RMSE", sort_metric="RMSE")
// MAGIC aml.train(x=x, y=y, training_frame=trainH2O)
// MAGIC 
// MAGIC # View the AutoML Leaderboard
// MAGIC lb = aml.leaderboard
// MAGIC lb.head(rows=lb.nrows)  # Print all rows instead of default (10 rows)
// MAGIC # Note: deep learning model results are not reproducible

// COMMAND ----------

// MAGIC %md
// MAGIC ## Predict Test Data

// COMMAND ----------

// MAGIC %python
// MAGIC import pandas as pd
// MAGIC predict = aml.predict(testH2O).as_data_frame()
// MAGIC actual = testH2O["price"].as_data_frame()
// MAGIC display(pd.concat([predict, actual],axis=1))

// COMMAND ----------

// MAGIC %python
// MAGIC perf = aml.leader.model_performance(testH2O)
// MAGIC perf

// COMMAND ----------

// MAGIC %python
// MAGIC aml.leader

// COMMAND ----------

// MAGIC %md
// MAGIC ## Save Model

// COMMAND ----------

// MAGIC %python
// MAGIC h2o.save_model(aml.leader, path = userhome + "/machine-learning-p/h2o")

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
// MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
// MAGIC <br/>
// MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>