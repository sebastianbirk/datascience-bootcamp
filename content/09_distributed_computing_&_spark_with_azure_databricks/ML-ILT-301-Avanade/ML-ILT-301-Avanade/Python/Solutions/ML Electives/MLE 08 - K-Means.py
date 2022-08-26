# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Distributed K-Means
# MAGIC 
# MAGIC In this notebook, we are going to use K-Means to cluster our data. We will be using the Iris dataset, which has labels (the type of iris), but we will only use the labels to evaluate the model, not to train it. 
# MAGIC 
# MAGIC At the end, we will look at how it is implemented in the distributed setting.
# MAGIC 
# MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
# MAGIC  - Build a K-Means model
# MAGIC  - Analyze the computation and communication of K-Means in a distributed setting

# COMMAND ----------

# MAGIC %run "../Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC baseDir = "/mnt/training/iris/"
# MAGIC irisPath = baseDir + "iris.scale"
# MAGIC irisDF = spark.read.format("libsvm").load(irisPath).cache()
# MAGIC 
# MAGIC # Note that the libSVM format uses SparseVectors.
# MAGIC display(irisDF)

# COMMAND ----------

# MAGIC %md
# MAGIC #### Loading the data
# MAGIC 
# MAGIC In this lab, we will be working with the famous Iris dataset. 
# MAGIC 
# MAGIC The goal is to predict the type of Iris (Setosa, Versicolour, Virginica) given measurements on four different features: sepal length, sepal width, petal length, and petal width.
# MAGIC 
# MAGIC First, we need to load data into Spark.  
# MAGIC 
# MAGIC We'll use a built-in utility to load a <a href="http://www.csie.ntu.edu.tw/~cjlin/libsvm/faq.html" target="_blank">libSVM file</a>

# COMMAND ----------

# MAGIC %python
# MAGIC # Create a new DataFrame with the features from irisDF and with labels that are zero-indexed (just subtract one).
# MAGIC # Also make sure your label column is still called label.
# MAGIC 
# MAGIC irisZeroIndexDF = irisDF.selectExpr("features", "label - 1 as label")
# MAGIC display(irisZeroIndexDF)

# COMMAND ----------

# MAGIC %md
# MAGIC Notice that we have four values that are stored as a `SparseVector` within the `features` column.  We'll reduce those down to two values (for visualization purposes) and convert them to a `DenseVector`.  To do that we'll need to create a `udf` and apply it to our dataset. 

# COMMAND ----------

# MAGIC %python
# MAGIC from pyspark.sql.functions import udf
# MAGIC # Note that VectorUDT and MatrixUDT are found in linalg while other types are in sql.types
# MAGIC # VectorUDT should be the return type of the udf
# MAGIC from pyspark.ml.linalg import Vectors, VectorUDT
# MAGIC 
# MAGIC # Take the first two values from features and convert them to a DenseVector
# MAGIC firstTwoFeatures = udf(lambda sv: Vectors.dense(sv.toArray()[:2]), VectorUDT())
# MAGIC 
# MAGIC irisTwoFeaturesDF = irisZeroIndexDF.select(firstTwoFeatures("features").alias("features"), "label").cache()
# MAGIC display(irisTwoFeaturesDF)

# COMMAND ----------

# MAGIC %python
# MAGIC from pyspark.ml.clustering import KMeans
# MAGIC 
# MAGIC # Create a KMeans Estimator and set k=3, seed=221, maxIter=20
# MAGIC kmeans = (KMeans()
# MAGIC           .setK(3)
# MAGIC           .setSeed(221)
# MAGIC           .setMaxIter(20))
# MAGIC 
# MAGIC #  Call fit on the estimator and pass in irisTwoFeaturesDF
# MAGIC model = kmeans.fit(irisTwoFeaturesDF)
# MAGIC 
# MAGIC # Obtain the clusterCenters from the KMeansModel
# MAGIC centers = model.clusterCenters()
# MAGIC 
# MAGIC # Use the model to transform the DataFrame by adding cluster predictions
# MAGIC transformedDF = model.transform(irisTwoFeaturesDF)
# MAGIC 
# MAGIC # Let's print the three centroids of our model
# MAGIC print(centers)

# COMMAND ----------

# MAGIC %python
# MAGIC from pyspark.ml.clustering import KMeans
# MAGIC 
# MAGIC modelCenters = []
# MAGIC iterations = [0, 2, 4, 7, 10, 20]
# MAGIC for i in iterations:
# MAGIC     kmeans = KMeans(k=3, seed=221, maxIter=i, initSteps=1)
# MAGIC     model = kmeans.fit(irisTwoFeaturesDF)
# MAGIC     modelCenters.append(model.clusterCenters())   

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC print("modelCenters:")
# MAGIC for centroids in modelCenters:
# MAGIC   print(centroids)

# COMMAND ----------

# MAGIC %md
# MAGIC Let's visualize how our clustering performed against the true labels of our data.
# MAGIC 
# MAGIC Remember: K-means doesn't use the true labels when training, but we can use them to evaluate. 
# MAGIC 
# MAGIC Here, the star marks the cluster center.

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC import matplotlib.pyplot as plt
# MAGIC import matplotlib.cm as cm
# MAGIC import numpy as np
# MAGIC 
# MAGIC def prepareSubplot(xticks, yticks, figsize=(10.5, 6), hideLabels=False, gridColor='#999999', 
# MAGIC                 gridWidth=1.0, subplots=(1, 1)):
# MAGIC     """Template for generating the plot layout."""
# MAGIC     plt.close()
# MAGIC     fig, axList = plt.subplots(subplots[0], subplots[1], figsize=figsize, facecolor='white', 
# MAGIC                                edgecolor='white')
# MAGIC     if not isinstance(axList, np.ndarray):
# MAGIC         axList = np.array([axList])
# MAGIC     
# MAGIC     for ax in axList.flatten():
# MAGIC         ax.axes.tick_params(labelcolor='#999999', labelsize='10')
# MAGIC         for axis, ticks in [(ax.get_xaxis(), xticks), (ax.get_yaxis(), yticks)]:
# MAGIC             axis.set_ticks_position('none')
# MAGIC             axis.set_ticks(ticks)
# MAGIC             axis.label.set_color('#999999')
# MAGIC             if hideLabels: axis.set_ticklabels([])
# MAGIC         ax.grid(color=gridColor, linewidth=gridWidth, linestyle='-')
# MAGIC         map(lambda position: ax.spines[position].set_visible(False), ['bottom', 'top', 'left', 'right'])
# MAGIC         
# MAGIC     if axList.size == 1:
# MAGIC         axList = axList[0]  # Just return a single axes object for a regular plot
# MAGIC     return fig, axList

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC data = irisTwoFeaturesDF.collect()
# MAGIC features, labels = zip(*data)
# MAGIC 
# MAGIC x, y = zip(*features)
# MAGIC centers = modelCenters[5]
# MAGIC centroidX, centroidY = zip(*centers)
# MAGIC colorMap = 'Set1'  # was 'Set2', 'Set1', 'Dark2', 'winter'
# MAGIC 
# MAGIC fig, ax = prepareSubplot(np.arange(-1, 1.1, .4), np.arange(-1, 1.1, .4), figsize=(8,6))
# MAGIC plt.scatter(x, y, s=14**2, c=labels, edgecolors='#8cbfd0', alpha=0.80, cmap=colorMap)
# MAGIC plt.scatter(centroidX, centroidY, s=22**2, marker='*', c='yellow')
# MAGIC cmap = cm.get_cmap(colorMap)
# MAGIC 
# MAGIC colorIndex = [.5, .99, .0]
# MAGIC for i, (x,y) in enumerate(centers):
# MAGIC     print(cmap(colorIndex[i]))
# MAGIC     for size in [.10, .20, .30, .40, .50]:
# MAGIC         circle1=plt.Circle((x,y),size,color=cmap(colorIndex[i]), alpha=.10, linewidth=2)
# MAGIC         ax.add_artist(circle1)
# MAGIC 
# MAGIC ax.set_xlabel('Sepal Length'), ax.set_ylabel('Sepal Width')
# MAGIC display(fig)

# COMMAND ----------

# MAGIC %md
# MAGIC In addition to seeing the overlay of the clusters at each iteration, we can see how the cluster centers moved with each iteration (and what our results would have looked like if we used fewer iterations).

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC x, y = zip(*features)
# MAGIC 
# MAGIC oldCentroidX, oldCentroidY = None, None
# MAGIC 
# MAGIC fig, axList = prepareSubplot(np.arange(-1, 1.1, .4), np.arange(-1, 1.1, .4), figsize=(11, 15),
# MAGIC                              subplots=(3, 2))
# MAGIC axList = axList.flatten()
# MAGIC 
# MAGIC for i,ax in enumerate(axList[:]):
# MAGIC     ax.set_title('K-means for {0} iterations'.format(iterations[i]), color='#999999')
# MAGIC     centroids = modelCenters[i]
# MAGIC     centroidX, centroidY = zip(*centroids)
# MAGIC     
# MAGIC     ax.scatter(x, y, s=10**2, c=labels, edgecolors='#8cbfd0', alpha=0.80, cmap=colorMap, zorder=0)
# MAGIC     ax.scatter(centroidX, centroidY, s=16**2, marker='*', c='yellow', zorder=2)
# MAGIC     if oldCentroidX and oldCentroidY:
# MAGIC       ax.scatter(oldCentroidX, oldCentroidY, s=16**2, marker='*', c='grey', zorder=1)
# MAGIC     cmap = cm.get_cmap(colorMap)
# MAGIC     
# MAGIC     colorIndex = [.5, .99, 0.]
# MAGIC     for i, (x1,y1) in enumerate(centroids):
# MAGIC       print(cmap(colorIndex[i]))
# MAGIC       circle1=plt.Circle((x1,y1),.35,color=cmap(colorIndex[i]), alpha=.40)
# MAGIC       ax.add_artist(circle1)
# MAGIC     
# MAGIC     ax.set_xlabel('Sepal Length'), ax.set_ylabel('Sepal Width')
# MAGIC     oldCentroidX, oldCentroidY = centroidX, centroidY
# MAGIC 
# MAGIC plt.tight_layout()
# MAGIC 
# MAGIC display(fig)

# COMMAND ----------

# MAGIC %md
# MAGIC So let's take a look at what's happening here in the distributed setting.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC <img src="https://files.training.databricks.com/images/Mapstage.png" height=200px>

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://files.training.databricks.com/images/Mapstage2.png" height=500px>

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://files.training.databricks.com/images/ReduceStage.png" height=500px>

# COMMAND ----------

# MAGIC %md
# MAGIC <img src="https://files.training.databricks.com/images/Communication.png" height=500px>

# COMMAND ----------

# MAGIC %md
# MAGIC ## Take Aways
# MAGIC 
# MAGIC When designing/choosing distributed ML algorithms
# MAGIC * Communication is key!
# MAGIC * Consider your data/model dimensions & how much data you need.
# MAGIC * Data partitioning/organization is important.

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>