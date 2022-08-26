# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Scikit-Learn and Spark
# MAGIC 
# MAGIC How can we leverage our existing experience with modeling libraries like <a href="http://scikit-learn.org/stable/index.html" target="_blank">scikit-learn</a>?  
# MAGIC 
# MAGIC Although scikit-learn builds models on a single machine, we can still benefit from the parallelism provided by Spark to build multiple models concurrently for hyperparameter search, etc.
# MAGIC 
# MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
# MAGIC  - Perform hyperparameter search in parallel using spark-sklearn.

# COMMAND ----------

# MAGIC %run "../Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Install Libraries
# MAGIC 
# MAGIC We need to start by installing <a href="https://github.com/databricks/spark-sklearn" target="_blank">Spark-Sklearn</a> by creating a library with PyPI: `spark-sklearn==0.3.0`. 
# MAGIC 
# MAGIC To verify that the libraries are properly attached, run the following cell proving that we can import the class `GridSearchCV` from the `spark-sklearn` library:

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC from spark_sklearn import GridSearchCV

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC 
# MAGIC In this lab, we are trying to predict iris type given different features 
# MAGIC * sepal length
# MAGIC * sepal width
# MAGIC * petal length
# MAGIC * and petal width 
# MAGIC 
# MAGIC Below are the three types of irises. 
# MAGIC 
# MAGIC Can you form any hypotheses about the differences among these irises?
# MAGIC 
# MAGIC <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Iris_dataset_scatterplot.svg/600px-Iris_dataset_scatterplot.svg.png" style="float:center; height: 200px; margin: 10px"/>

# COMMAND ----------

# MAGIC %md
# MAGIC Load the data from `sklearn.datasets`.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC import numpy as np
# MAGIC from sklearn import datasets
# MAGIC 
# MAGIC # Load the iris data
# MAGIC iris = datasets.load_iris()

# COMMAND ----------

# MAGIC %md
# MAGIC With the dataset loaded, let's take a look at it's description:

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC print(iris.DESCR)

# COMMAND ----------

# MAGIC %md
# MAGIC Let's take a look at some of the details of this dataset:

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC print(f"Target Names: {iris.target_names}")
# MAGIC print(f"Feature Names: {iris.feature_names}")
# MAGIC print(f"Flower #0:   {iris.target[0]}, {iris.data[0]}")
# MAGIC print(f"Flower #50:  {iris.target[50]}, {iris.data[50]}")
# MAGIC print(f"Flower #100: {iris.target[100]}, {iris.data[100]}")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC This tables shows the relationships among the 4 predictors.
# MAGIC 
# MAGIC <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/5/56/Iris_dataset_scatterplot.svg/1024px-Iris_dataset_scatterplot.svg.png" style="float:center; height: 400px; margin: 10px"/>

# COMMAND ----------

# MAGIC %md
# MAGIC Before we get into running K-Nearest Neighbors, let's start by using a <a href="https://en.wikipedia.org/wiki/Voronoi_diagram" target="_blank">Voronoi diagram</a> to visualize the partitioning of space. 
# MAGIC 
# MAGIC Note: we can look at only two of the four features at a time:

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC import matplotlib.pyplot as plt
# MAGIC from scipy.spatial import Voronoi, voronoi_plot_2d
# MAGIC 
# MAGIC # features = iris.data[:,:2] # sepal length vs sepal width
# MAGIC features = iris.data[:,2:4] # petal length vs petal width
# MAGIC 
# MAGIC labels = iris.target
# MAGIC 
# MAGIC vor = Voronoi(features)
# MAGIC voronoi_plot_2d(vor)
# MAGIC plt.xlabel('Sepal Length')
# MAGIC plt.ylabel('Sepal Width')
# MAGIC 
# MAGIC display(plt.show())

# COMMAND ----------

# MAGIC %md
# MAGIC Next we are going to create the test and training sets using <a href="http://scikit-learn.org/stable/modules/generated/sklearn.model_selection.train_test_split.html" target="_blank">sklearn.model_selection.train_test_split</a>. 
# MAGIC 
# MAGIC In this case, we will use 80% for training and save 20% for testing.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC from sklearn.model_selection import train_test_split
# MAGIC 
# MAGIC y_train, y_test, X_train, X_test = train_test_split(
# MAGIC   iris.target,     # Our targets
# MAGIC   iris.data,       # Our features
# MAGIC   test_size=0.2,   # Hold out 20%
# MAGIC   random_state=42  # For reproducibility 
# MAGIC )

# COMMAND ----------

# MAGIC %md
# MAGIC We are going to use scikit-learn's `KNeighborsClassifier`, but use Spark to distribute the training. 
# MAGIC 
# MAGIC Let's take a look at the different parameters we can vary.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC from sklearn.neighbors import KNeighborsClassifier
# MAGIC 
# MAGIC knn = KNeighborsClassifier()
# MAGIC 
# MAGIC for key, value in knn.get_params().items():
# MAGIC   print(f"{key}:  {value}")

# COMMAND ----------

# MAGIC %md
# MAGIC For the current configuration, the number of neighbors is 5.
# MAGIC 
# MAGIC Next we will train with 10 different permutations: 1 to 10 neighbors.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC from spark_sklearn import GridSearchCV
# MAGIC 
# MAGIC parameters = {
# MAGIC   'n_neighbors':[1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
# MAGIC }
# MAGIC clf = GridSearchCV(
# MAGIC   spark.sparkContext,   # The Spark Context
# MAGIC   knn,                  # KNeighborsClassifier
# MAGIC   parameters            # All the different parameters
# MAGIC )
# MAGIC clf.n_splits_ = 3       # Set the number of folds
# MAGIC clf.fit(X_train, y_train) # Train the model
# MAGIC 
# MAGIC clf.cv_results_

# COMMAND ----------

# MAGIC %md
# MAGIC Let's examine the `mean_test_score` of each hyperparameter configuration.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC for i,r in enumerate(clf.cv_results_["mean_test_score"]):
# MAGIC   print(f"#{i}: {r*100:.2f}")

# COMMAND ----------

# MAGIC %md
# MAGIC **Question**: When multiple estimators produce the same result, how is the "best" one determined?
# MAGIC 
# MAGIC We can now ask for the best estimator and from there, evaluate its various parameters:

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC best = clf.best_estimator_
# MAGIC 
# MAGIC print(f"algorithm:     {best.algorithm}")
# MAGIC print(f"leaf_size:     {best.leaf_size}")
# MAGIC print(f"metric:        {best.metric}")
# MAGIC print(f"metric_params: {best.metric_params}")
# MAGIC print(f"n_jobs:        {best.n_jobs}")
# MAGIC print(f"n_neighbors:   {best.n_neighbors}")
# MAGIC print(f"p:             {best.p}")
# MAGIC print(f"weights:       {best.weights}")

# COMMAND ----------

# MAGIC %md
# MAGIC Now that we have our best estimator, let's apply it to our test set.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC predictions = best.predict(X_test)

# COMMAND ----------

# MAGIC %md
# MAGIC And now we can view our predictions in the following cell:

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC # Print out the accuracy of the classifier on the test set
# MAGIC accuracy = __builtin__.sum(predictions == y_test) * 100.0 / __builtin__.len(y_test)
# MAGIC print(f"Accuracy: {accuracy:.2f}%")
# MAGIC print(f"Test Set:    {y_test}")
# MAGIC print(f"Predictions: {predictions}")

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>