# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://raw.githubusercontent.com/databricks/koalas/master/Koalas-logo.png" width="220"/>
# MAGIC </div>
# MAGIC 
# MAGIC The Koalas project makes data scientists more productive when interacting with big data, by implementing the pandas DataFrame API on top of Apache Spark. By unifying the two ecosystems with a familiar API, Koalas offers a seamless transition between small and large data.
# MAGIC 
# MAGIC **Goals of this notebook:**
# MAGIC * Demonstrate the similarities of the Koalas API with the pandas API
# MAGIC * Understand the differences in syntax for the same DataFrame operations in Koalas vs PySpark
# MAGIC 
# MAGIC [Koalas Docs](https://koalas.readthedocs.io/en/latest/index.html)
# MAGIC 
# MAGIC [Koalas Github](https://github.com/databricks/koalas)
# MAGIC 
# MAGIC **Requirements:**
# MAGIC * `koalas==0.20.0` (PyPI)
# MAGIC 
# MAGIC **Data:**
# MAGIC * *[Moro et al., 2014] S. Moro, P. Cortez and P. Rita. A Data-Driven Approach to Predict the Success of Bank Telemarketing. Decision Support Systems, Elsevier, 62:22-31, June 2014*

# COMMAND ----------

# MAGIC %md
# MAGIC We will be using the [UCI Machine Learning Repository 
# MAGIC Bank Marketing Data Set](https://archive.ics.uci.edu/ml/datasets/bank+marketing) throughout this demo.

# COMMAND ----------

# MAGIC %run "../Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %sh wget https://archive.ics.uci.edu/ml/machine-learning-databases/00222/bank.zip -O /tmp/bank.zip

# COMMAND ----------

# MAGIC %sh unzip -o /tmp/bank.zip -d /tmp/bank

# COMMAND ----------

# MAGIC %python
# MAGIC file_path = userhome + "/bank-full.csv"
# MAGIC dbutils.fs.cp("file:/tmp/bank/bank-full.csv", file_path)
# MAGIC dbutils.fs.head(file_path)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loading the dataset as a Spark DataFrame

# COMMAND ----------

# MAGIC %python
# MAGIC df = (spark
# MAGIC       .read
# MAGIC       .option("inferSchema", "true")
# MAGIC       .option("header", "true")
# MAGIC       .option("delimiter", ";")
# MAGIC       .option("quote", '"')
# MAGIC       .csv(file_path))
# MAGIC 
# MAGIC display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loading the dataset as a pandas DataFrame

# COMMAND ----------

# MAGIC %python
# MAGIC import pandas as pd
# MAGIC 
# MAGIC csv_path = userhome.replace("dbfs:", "/dbfs") + "/bank-full.csv"
# MAGIC 
# MAGIC # Read in using pandas read_csv
# MAGIC pdf = pd.read_csv(csv_path, header=0, sep=";", quotechar='"')
# MAGIC display(pdf.head())

# COMMAND ----------

# MAGIC %md
# MAGIC ### Loading the dataset as a Koalas Dataframe

# COMMAND ----------

# MAGIC %python
# MAGIC import databricks.koalas as ks
# MAGIC 
# MAGIC # Read in using Koalas read_csv
# MAGIC kdf = ks.read_csv(file_path, header=0, sep=";", quotechar='"')
# MAGIC 
# MAGIC display(kdf.head())

# COMMAND ----------

# MAGIC %python
# MAGIC # Converting to Koalas DataFrame from Spark DataFrame
# MAGIC 
# MAGIC # Creating a Koalas DataFrame from PySpark DataFrame
# MAGIC # kdf = ks.DataFrame(df)
# MAGIC 
# MAGIC # # Alternative way of creating a Koalas DataFrame from PySpark DataFrame
# MAGIC kdf = df.to_koalas()

# COMMAND ----------

# MAGIC %md
# MAGIC Note that calling `.head()` in Koalas may not return return the same results as pandas here. Unlike pandas, the data in a Spark DataFrame is not ordered - it has no intrinsic notion of index. When asked for the head of a DataFrame, Spark will just take the requested number of rows from a partition. Do not rely on it to return specific rows, instead use `.loc` or `iloc`.

# COMMAND ----------

# MAGIC %md
# MAGIC ### Indexing Rows

# COMMAND ----------

# MAGIC %python
# MAGIC pdf.iloc[:3]

# COMMAND ----------

# MAGIC %python
# MAGIC try:
# MAGIC   kdf.iloc[3]
# MAGIC except:
# MAGIC   print("SparkPandasNotImplementedError: .iloc requires numeric slice or conditional boolean Index")

# COMMAND ----------

# MAGIC %md
# MAGIC Using a scalar integer for row selection is not allowed in Koalas, instead we must supply either a *slice* object or boolean condition.

# COMMAND ----------

# MAGIC %python
# MAGIC kdf.iloc[:4]

# COMMAND ----------

# MAGIC %python
# MAGIC display(df.limit(4))

# COMMAND ----------

# MAGIC %python
# MAGIC # Koalas DataFrame -> PySpark DataFrame
# MAGIC display(kdf.to_spark())

# COMMAND ----------

# MAGIC %python
# MAGIC # Getting the number of rows and columns in PySpark
# MAGIC print((df.count(), len(df.columns)))

# COMMAND ----------

# MAGIC %python
# MAGIC # Getting the number of rows and columns in Koalas
# MAGIC print(kdf.shape)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Column Manipulation

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Let's have a look at some column operations. Suppose we want to create a new column, where each last contact duration (the `duration` column) is 100 greater than the original duration entry. We will call this new column `duration_new`.

# COMMAND ----------

# MAGIC %python
# MAGIC # Creating a column with PySpark
# MAGIC from pyspark.sql.functions import col
# MAGIC 
# MAGIC df = df.withColumn("duration_new", col("duration") + 100)
# MAGIC display(df)

# COMMAND ----------

# MAGIC %python
# MAGIC # Creating a column with Koalas
# MAGIC kdf["duration_new"] = kdf["duration"] + 100
# MAGIC display(kdf.head())

# COMMAND ----------

# MAGIC %md
# MAGIC ###Filtering

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Let's now count the number of instances where `duration_new` is greater than or equal to 300.

# COMMAND ----------

# MAGIC %python
# MAGIC # Filtering with PySpark
# MAGIC df_filtered  = df.filter(col("duration_new") >= 300)
# MAGIC print(df_filtered.count())

# COMMAND ----------

# MAGIC %python
# MAGIC # Filtering with Koalas
# MAGIC kdf_filtered = kdf[kdf.duration_new >= 300]
# MAGIC print(kdf_filtered.shape[0])

# COMMAND ----------

# MAGIC %md
# MAGIC ### Value Counts

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Suppose we want to have a look at the number of clients for each unique job type.

# COMMAND ----------

# MAGIC %python
# MAGIC # To get value counts of the different job types with PySpark
# MAGIC display(df.groupby("job").count().orderBy("count", ascending=False))

# COMMAND ----------

# MAGIC %python
# MAGIC # Value counts in Koalas
# MAGIC kdf["job"].value_counts()

# COMMAND ----------

# MAGIC %md
# MAGIC ###GroupBy

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Let's compare group by operations in PySpark versus Koalas. We will create two DataFrames grouped by education, to get the average `age` and maximum `balance` for each education group.

# COMMAND ----------

# MAGIC %python
# MAGIC # Get average age per education group using PySpark
# MAGIC df_grouped_1 = (df.groupby("education")
# MAGIC                 .agg({"age": "mean"})
# MAGIC                 .select("education", col("avg(age)").alias("avg_age")))
# MAGIC 
# MAGIC display(df_grouped_1)

# COMMAND ----------

# MAGIC %python
# MAGIC # Get the maximum balance for each education group using PySpark
# MAGIC df_grouped_2 = (df.groupby("education")
# MAGIC                 .agg({"balance": "max"})
# MAGIC                 .select("education", col("max(balance)").alias("max_balance")))
# MAGIC 
# MAGIC display(df_grouped_2)

# COMMAND ----------

# MAGIC %python
# MAGIC # Get the average age per education group in Koalas
# MAGIC kdf_grouped_1 = kdf.groupby("education", as_index=False).agg({"age": "mean"})
# MAGIC 
# MAGIC # Rename our columns
# MAGIC kdf_grouped_1.columns = ["education", "avg_age"]
# MAGIC display(kdf_grouped_1)

# COMMAND ----------

# MAGIC %python
# MAGIC # Get the maximum balance for each education group in Koalas
# MAGIC kdf_grouped_2 = kdf.groupby("education", as_index=False).agg({"balance": "max"})
# MAGIC kdf_grouped_2.columns = ["education", "max_balance"]
# MAGIC display(kdf_grouped_2)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Joins

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Let's now look at doing an inner join between our grouped DataFrames, on the `education` attribute.

# COMMAND ----------

# MAGIC %python
# MAGIC # Joining the grouped DataFrames on education using PySpark
# MAGIC df_edu_joined = df_grouped_1.join(df_grouped_2, on="education", how="inner")
# MAGIC display(df_edu_joined)

# COMMAND ----------

# MAGIC %python
# MAGIC # Joining the grouped DataFrames on education using Koalas
# MAGIC kdf_edu_joined = kdf_grouped_1.merge(kdf_grouped_2, on="education", how="inner")
# MAGIC display(kdf_edu_joined)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Writing Data

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Finally, let's save our joined DataFrames as Parquet files.

# COMMAND ----------

# MAGIC %python
# MAGIC # Saving the Spark DataFrame as a Parquet file.
# MAGIC spark_out_path = userhome + "/bank_grouped_pyspark.parquet"
# MAGIC 
# MAGIC df_edu_joined.write.mode("overwrite").parquet(spark_out_path)

# COMMAND ----------

# MAGIC %python
# MAGIC # Saving the Koalas DataFrame as a Parquet file.
# MAGIC koalas_out_path = userhome + "/bank_grouped_koalas.parquet"
# MAGIC 
# MAGIC kdf.to_parquet(koalas_out_path, mode="overwrite")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>