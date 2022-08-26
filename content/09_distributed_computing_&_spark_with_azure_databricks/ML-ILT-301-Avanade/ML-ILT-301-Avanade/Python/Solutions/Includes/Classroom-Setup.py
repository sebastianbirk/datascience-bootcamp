# Databricks notebook source
# MAGIC 
# MAGIC %python
# MAGIC course_name = "Machine-learning"

# COMMAND ----------

# MAGIC %run "./Dataset-Mounts"

# COMMAND ----------

# MAGIC %python
# MAGIC def display_run_uri(experiment_id, run_id):
# MAGIC     host_name = dbutils.notebook.entry_point.getDbutils().notebook().getContext().tags().get("browserHostName").get()
# MAGIC     uri = "https://{}/#mlflow/experiments/{}/runs/{}".format(host_name, experiment_id, run_id)
# MAGIC     displayHTML("""<b>Run URI:</b> <a href="{}">{}</a>""".format(uri, uri))

# COMMAND ----------

# MAGIC %python
# MAGIC dbutils.fs.mkdirs("dbfs:/user/" + username)
# MAGIC dbutils.fs.mkdirs("dbfs:/user/" + username + "/machine-learning-p")
# MAGIC dbutils.fs.mkdirs("dbfs:/user/" + username + "/machine-learning-s")
# MAGIC None

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC def untilStreamIsReady(name):
# MAGIC   queries = list(filter(lambda query: query.name == name, spark.streams.active))
# MAGIC 
# MAGIC   if len(queries) == 0:
# MAGIC     print("The stream is not active.")
# MAGIC 
# MAGIC   else:
# MAGIC     while (queries[0].isActive and len(queries[0].recentProgress) == 0):
# MAGIC       pass # wait until there is any type of progress
# MAGIC 
# MAGIC     if queries[0].isActive:
# MAGIC       queries[0].awaitTermination(5)
# MAGIC       print("The stream is active and ready.")
# MAGIC     else:
# MAGIC       print("The stream is not active.")
# MAGIC 
# MAGIC None

# COMMAND ----------

# MAGIC %scala
# MAGIC 
# MAGIC def untilStreamIsReady(name:String):Unit = {
# MAGIC   val queries = spark.streams.active.filter(_.name == name)
# MAGIC 
# MAGIC   if (queries.length == 0) {
# MAGIC     println("The stream is not active.")
# MAGIC   } else {
# MAGIC     while (queries(0).isActive && queries(0).recentProgress.length == 0) {
# MAGIC       // wait until there is any type of progress
# MAGIC     }
# MAGIC 
# MAGIC     if (queries(0).isActive) {
# MAGIC       queries(0).awaitTermination(5*1000)
# MAGIC       println("The stream is active and ready.")
# MAGIC     } else {
# MAGIC       println("The stream is not active.")
# MAGIC     }
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC displayHTML("""
# MAGIC <div>Declared various utility methods:</div>
# MAGIC <li>Declared <b style="color:green">untilStreamIsReady(<i>name:String</i>)</b> to control workflow</li>
# MAGIC <br/>
# MAGIC <div>All done!</div>
# MAGIC """)