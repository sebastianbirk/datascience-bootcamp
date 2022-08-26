// Databricks notebook source
// MAGIC 
// MAGIC %md-sandbox
// MAGIC 
// MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
// MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
// MAGIC </div>

// COMMAND ----------

// MAGIC %md
// MAGIC # Deployment Options
// MAGIC 
// MAGIC There are three main deployment options when working with SparkML:
// MAGIC * Batch pre-compute
// MAGIC * Structured streaming
// MAGIC * Low-latency model serving (technically have to get the model out of SparkML, e.g. using MLeap)
// MAGIC 
// MAGIC We have already seen how to do batch predictions using Spark. Now let's look at how to make predictions on streaming data.
// MAGIC 
// MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
// MAGIC  - Apply a SparkML model on a simulated stream of data 

// COMMAND ----------

// MAGIC %run "../Includes/Classroom-Setup"

// COMMAND ----------

// MAGIC %md
// MAGIC ## Load in Model & Data

// COMMAND ----------

import org.apache.spark.ml.PipelineModel

val pipelinePath = "dbfs:/mnt/training/airbnb/sf-listings/models/sf-listings-2019-03-06/pipeline_model"
val pipelineModel = PipelineModel.load(pipelinePath)

val repartitionedPath =  "dbfs:/mnt/training/airbnb/sf-listings/sf-listings-2019-03-06-clean-100p.parquet/"
val schema = spark.read.parquet(repartitionedPath).schema

// COMMAND ----------

// MAGIC %md
// MAGIC ## Simulate streaming data.
// MAGIC 
// MAGIC **NOTE**: You must specify a schema when creating a streaming source DataFrame.

// COMMAND ----------

val streamingData = spark
                   .readStream
                   .schema(schema) // Can set the schema this way
                   .option("maxFilesPerTrigger", 1)
                   .parquet(repartitionedPath)

// COMMAND ----------

// MAGIC %md
// MAGIC ## Make Predictions

// COMMAND ----------

val streamPred = pipelineModel.transform(streamingData)

// COMMAND ----------

// MAGIC %md
// MAGIC Let's save our results.

// COMMAND ----------

val checkpointDir = userhome + "/machine-learning/pred_stream_1s_checkpoint"
// Clear out the checkpointing directory
dbutils.fs.rm(checkpointDir, true) 

streamPred
 .writeStream
 .format("memory")
 .option("checkpointLocation", checkpointDir)
 .outputMode("append")
 .queryName("pred_stream_1s")
 .start()

// COMMAND ----------

untilStreamIsReady("pred_stream_1s")

// COMMAND ----------

display(
  sql("select * from pred_stream_1s")
)

// COMMAND ----------

display(
  sql("select count(*) from pred_stream_1s")
)

// COMMAND ----------

// MAGIC %md
// MAGIC Now that we are done, make sure to stop the stream

// COMMAND ----------

for (stream <- spark.streams.active) {
  println("Stopping " + stream.name)
  stream.stop() // Stop the stream
}


// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
// MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
// MAGIC <br/>
// MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>