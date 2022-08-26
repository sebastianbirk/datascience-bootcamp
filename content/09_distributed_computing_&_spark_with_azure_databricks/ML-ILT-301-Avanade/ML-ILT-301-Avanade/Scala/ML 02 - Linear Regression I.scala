// Databricks notebook source
// MAGIC 
// MAGIC %md-sandbox
// MAGIC 
// MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
// MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
// MAGIC </div>

// COMMAND ----------

// MAGIC %md
// MAGIC # Regression: Predicting Rental Price
// MAGIC 
// MAGIC In this notebook, we will use the dataset we cleansed in the previous lab to predict Airbnb rental prices in San Francisco.
// MAGIC 
// MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
// MAGIC  - Use the SparkML API to build a linear regression model
// MAGIC  - Identify the differences between estimators and transformers

// COMMAND ----------

// MAGIC %run "./Includes/Classroom-Setup"

// COMMAND ----------

val filePath = "dbfs:/mnt/training/airbnb/sf-listings/sf-listings-2019-03-06-clean.parquet/"
val airbnbDF = spark.read.parquet(filePath)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Train/Test Split
// MAGIC 
// MAGIC When we are building ML models, we don't want to look at our test data (why is that?). 
// MAGIC 
// MAGIC Let's keep 80% for the training set and set aside 20% of our data for the test set. We will use the `randomSplit` method [Python](https://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.DataFrame.randomSplit)/[Scala](https://spark.apache.org/docs/latest/api/scala/#org.apache.spark.sql.Dataset).
// MAGIC 
// MAGIC **Question**: Why is it necessary to set a seed? What happens if I change my cluster configuration?

// COMMAND ----------

val Array(trainDF, testDF) = airbnbDF.randomSplit(Array(.8, .2), seed=42)
println(trainDF.cache().count)

// COMMAND ----------

// MAGIC %md
// MAGIC Let's change the # of partitions (to simulate a different cluster configuration), and see if we get the same number of data points in our training set. 

// COMMAND ----------

val Array(trainRepartitionDF, testRepartitionDF) = airbnbDF
  .repartition(24)
  .randomSplit(Array(.8, .2), seed=42)

println(trainRepartitionDF.count())

// COMMAND ----------

// MAGIC %md
// MAGIC ## Linear Regression
// MAGIC 
// MAGIC We are going to build a very simple model predicting `price` just given the number of `bedrooms`.
// MAGIC 
// MAGIC **Question**: What are some assumptions of the linear regression model?

// COMMAND ----------

display(trainDF.select("price", "bedrooms"))

// COMMAND ----------

display(trainDF.select("price", "bedrooms").summary())

// COMMAND ----------

display(trainDF)

// COMMAND ----------

// MAGIC %md
// MAGIC There do appear some outliers in our dataset for the price ($10,000 a night??). Just keep this in mind when we are building our models :).
// MAGIC 
// MAGIC We will use `LinearRegression` to build our first model [Python](https://spark.apache.org/docs/latest/api/python/pyspark.ml.html#pyspark.ml.regression.LinearRegression)/[Scala](https://spark.apache.org/docs/latest/api/scala/#org.apache.spark.ml.regression.LinearRegression).

// COMMAND ----------

import org.apache.spark.ml.regression.LinearRegression

val lr = new LinearRegression()
            .setFeaturesCol("bedrooms")
            .setLabelCol("price")

// Uncomment when running
// val lrModel = lr.fit(trainDF)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Vector Assembler
// MAGIC 
// MAGIC What went wrong? Turns out that the Linear Regression **estimator** (`.fit()`) expected a column of Vector type as input.
// MAGIC 
// MAGIC We can easily get the values from the `bedrooms` column into a single vector using `VectorAssembler` [Python](https://spark.apache.org/docs/latest/api/python/pyspark.ml.html#pyspark.ml.feature.VectorAssembler)/[Scala](https://spark.apache.org/docs/latest/api/scala/#org.apache.spark.ml.feature.VectorAssembler). VectorAssembler is an example of a **transformer**. Transformers take in a DataFrame, and return a new DataFrame with one or more columns appended to it. They do not learn from your data, but apply rule based transformations.

// COMMAND ----------

import org.apache.spark.ml.feature.VectorAssembler

val vecAssembler = new VectorAssembler()
                       .setInputCols(Array("bedrooms"))
                       .setOutputCol("features")

val vecTrainDF = vecAssembler.transform(trainDF)

// COMMAND ----------

val lr = new LinearRegression()
             .setFeaturesCol("features")
             .setLabelCol("price")

val lrModel = lr.fit(vecTrainDF)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Inspect the model

// COMMAND ----------

val m = lrModel.coefficients(0)
val b = lrModel.intercept

println(s"The formula for the linear regression line is y = ${m}x + ${b}")
println("*-"*80)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Apply model to test set

// COMMAND ----------

val vecTestDF = vecAssembler.transform(testDF)

val predDF = lrModel.transform(vecTestDF)

predDF.select("bedrooms", "features", "price", "prediction").show()

// COMMAND ----------

// MAGIC %md
// MAGIC ## Evaluate Model
// MAGIC 
// MAGIC Let's see how our linear regression model with just one variable does. Does it beat our baseline model?

// COMMAND ----------

import org.apache.spark.ml.evaluation.RegressionEvaluator

val regressionEvaluator = new RegressionEvaluator()
                              .setPredictionCol("prediction")
                              .setLabelCol("price")
                              .setMetricName("rmse")

val rmse = regressionEvaluator.evaluate(predDF)
println(f"RMSE is ${rmse}")

// COMMAND ----------

// MAGIC %md
// MAGIC Wahoo! Our RMSE is better than our baseline model. However, it's still not that great. Let's see how we can further decrease it in future notebooks.

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
// MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
// MAGIC <br/>
// MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>