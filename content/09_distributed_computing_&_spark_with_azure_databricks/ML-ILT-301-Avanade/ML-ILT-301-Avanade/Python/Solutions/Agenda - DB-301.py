# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Agenda
# MAGIC ## Apache Spark for Machine Learning and Data Science
# MAGIC 
# MAGIC In this course data analysts and data scientists practice the full data science workflow by exploring data, building features, training regression and classification models, and tuning and selecting the best model.  By the end of this course, you will have built end-to-end machine learning models ready to be used into production.
# MAGIC 
# MAGIC This course assumes basic data science familiarity with Sklearn and Pandas (or equivalent).
# MAGIC 
# MAGIC **Cluster Requirements:**
# MAGIC * 5.5 LTS ML 
# MAGIC * `mlflow==1.2.0` (PyPI)
# MAGIC * `Azure:mmlspark:0.15` (Maven) - LightGBM
# MAGIC * `koalas==0.20.0` (PyPI)
# MAGIC * `ml.combust.mleap:mleap-spark_2.11:0.13.0` (Maven) - MLeap
# MAGIC * `spark-sklearn==0.3.0` (PyPI)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Day 1 AM
# MAGIC | Time | Lesson &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | Description &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
# MAGIC |:----:|-------|-------------|
# MAGIC | 20m  | **Review**                               | *What did we cover in Day 1?* |
# MAGIC | 30m    | **ML Overview (slides)**    | Types of Machine Learning, Business applications of ML <br/>(NOTE: this class uses Airbnb's SF rental data to predict things such as price of rental) |
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 35m  | **[Data Cleansing]($./ML 01 - Data Cleansing)** | How to deal with null values, outliers, data imputation | 
# MAGIC | 40m  | **[Data Exploration Lab]($./Labs/ML 01L - Data Exploration Lab)**  | Exploring your data, log-normal distribution, determine baseline metric to beat |
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 30m    | **[Linear Regression I]($./ML 02 - Linear Regression I)**    | Build simple univariate linear regression model<br/> SparkML APIs: transformer vs estimator |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Day 1 PM
# MAGIC | Time | Lesson &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | Description &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
# MAGIC |:----:|-------|-------------|
# MAGIC | 20m  | **[Linear Regression I Lab]($./Labs/ML 02L - Linear Regression I Lab)**       | Build multivariate linear regression model; Evaluate RMSE and R2 |
# MAGIC | 30m  | **[Linear Regression II]($./ML 03 - Linear Regression II)**      | How to handle categorical variables (OHE)<br/> Pipeline API <br/>Save and load models|
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 40m |**[Linear Regression II Lab]($./Labs/ML 03L - Linear Regression II Lab)** | Simplify pipeline using RFormula <br/>Build linear regression model to predict on log-scale, then exponentiate prediction and evaluate |
# MAGIC | 30m  | **[MLflow & Lab]($./ML 04 - MLflow)** | Use MLflow to track experiments, log metrics, and compare runs| 
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 45m    | **[Decision Trees]($./ML 05 - Decision Trees)**    | Distributed implementation of decision trees and maxBins parameter (why you WILL get different results from sklearn)<br/> Feature importance |
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 30m | **[Deployment Options & MLeap]($./ML 07 - MLeap)** | Discuss deployment options </br>Export a SparkML model using MLflow + MLeap</br>Make predictions in real-time using MLeap |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Day 2 AM
# MAGIC | Time | Lesson &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | Description &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
# MAGIC |:----:|-------|-------------|
# MAGIC | 20m  | **Review**                               | *What did we cover in Day 2?* |
# MAGIC | 45m  | **[Hyperparameter Tuning]($./ML 06 - Hyperparameter Tuning)** | K-Fold cross-validation <br/>SparkML's Parallelism parameter (introduced in Spark 2.3) <br/> Speed up Pipeline model training by 4x | 
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 20m  | **Random Forests**| What is random about a random forest? Why does it do better than a single decision tree? |
# MAGIC | 40m  | **[Hyperparameter Tuning Lab]($./Labs/ML 06L - Hyperparameter Tuning Lab)**  | Perform grid search on a random forest <br/>Get the feature importances across the forest <br/>Save the model <br/>Identify differences between Sklearn's Random Forest and SparkML's |
# MAGIC | 10m  | **Break**                                               ||
# MAGIC | 35m    | **[XGBoost & LightGBM]($./ML 08 - XGBoost)**    | Discuss gradient boosted trees and their variants <br/>Using 3rd party libraries with Spark |

# COMMAND ----------

# MAGIC %md
# MAGIC ## Day 2 PM - Electives (Pick from the below)
# MAGIC | Time | Lesson &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; | Description &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; |
# MAGIC |:----:|-------|-------------|
# MAGIC | 90m    | **[Capstone Project]($./ML Electives/MLE 00 - Capstone Project)**    | Work in a small team to apply the skills you learned throughout the course to a new dataset |
# MAGIC | 20m    | **[Streaming Predictions]($./ML Electives/MLE 01 - Streaming Predictions)**    | Generate predictions using SparkML models on streaming data |
# MAGIC | 20m    | **[AutoML]($./ML Electives/MLE 02 - AutoML)**    | Use H2O's AutoML on Spark (Sparkling Water) and evaluate model performance |
# MAGIC | 25m  | **[spark-sklearn]($./ML Electives/MLE 03 - spark-sklearn)** | Use spark-sklearn to distribute the hyperparameter search for your sklearn model | 
# MAGIC | 25m  | **[Koalas]($./ML Electives/MLE 04 - Koalas)** | Use the new open-source library to write Pandas code that distributes using Spark under the hood|             
# MAGIC | 60m    | **[Collaborative Filtering Lab]($./ML Electives/MLE 05L - Collaborative Filtering Lab)**    | Self guided lab on making personalized movie recommendations |
# MAGIC | 35m  | **[GraphFrames Lab]($./ML Electives/MLE 06L - GraphFrames Lab)** | Use GraphFrames (Spark's graph library) for analyzing college football data to determine things such as conferences, strongest team, etc. | 
# MAGIC | 25m    | **[Isolation Forests]($./ML Electives/MLE 07 - Isolation Forests)**    | Outlier detection using sklearn's Isolation Forests |
# MAGIC | 25m  | **[K-Means]($./ML Electives/MLE 08 - K-Means)**  | Unsupervised ML: Clustering, and understand the distributed implementation of K-Means in Spark |  
# MAGIC | 45m  | **[Logistic Regression Lab]($./ML Electives/MLE 09L - Logistic Regression Lab)**  | Build a Logistic Regression model</br>Use various classification metrics to evaluate model performance |  

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>