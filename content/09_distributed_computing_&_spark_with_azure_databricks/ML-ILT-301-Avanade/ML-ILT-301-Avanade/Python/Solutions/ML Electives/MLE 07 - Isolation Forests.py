# Databricks notebook source
# MAGIC 
# MAGIC %md-sandbox
# MAGIC 
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # Fraud Detection Using Isolation Forests
# MAGIC 
# MAGIC In this notebook, we will use [Isolation Forests](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) for anomaly detection. As of this writing, SparkML does not support Isolation Forests, so we will perform our feature engineering in Spark and use scikit-learn to build the Isolation Forest.
# MAGIC 
# MAGIC Isolation forests ‘isolate’ observations by randomly selecting a feature and then randomly selecting a split value between the maximum and minimum values of the selected feature.
# MAGIC 
# MAGIC Since recursive partitioning can be represented by a tree structure, the number of splittings required to isolate a sample is equivalent to the path length from the root node to the terminating node.
# MAGIC 
# MAGIC This path length, averaged over a forest of such random trees, is a measure of normality and our decision function.
# MAGIC 
# MAGIC Random partitioning produces noticeably shorter paths for anomalies. Hence, when a forest of random trees collectively produce shorter path lengths for particular samples, they are highly likely to be anomalies.
# MAGIC 
# MAGIC ![](https://scikit-learn.org/stable/_images/sphx_glr_plot_isolation_forest_001.png)
# MAGIC 
# MAGIC We start with a dataset with fraudulent and non-fraudulent transactions. We will determine if a transaction is fraudulent based on various features such as the change in balance of the original account and destination account. Although our dataset has true labels (fraud/not fraud), in reality, we do not know it a priori. Our model will identify fraud in an unsupervised setting.
# MAGIC 
# MAGIC [Financial Transactions Dataset](https://www.kaggle.com/ntnu-testimon/paysim1)
# MAGIC 
# MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:
# MAGIC * Build an isolation forest to identify fraud 
# MAGIC * Use Logistic Regression and a Random Forest to determine feature importance using spark-sklearn
# MAGIC 
# MAGIC **Required Libraries**:
# MAGIC * spark-sklearn

# COMMAND ----------

# MAGIC %run "../Includes/Classroom-Setup"

# COMMAND ----------

# MAGIC %python
# MAGIC import pandas as pd
# MAGIC import numpy as np
# MAGIC from pyspark.sql.functions import col
# MAGIC from sklearn.ensemble import IsolationForest
# MAGIC 
# MAGIC filePath = "dbfs:/mnt/training/fraud/paysim-fraud-detection.csv"
# MAGIC fraudDF = spark.read.csv(filePath, inferSchema=True, header=True)
# MAGIC 
# MAGIC fraudDF = fraudDF.filter((col("type")=="TRANSFER") | (col("type")=="CASH_OUT")) # Only these types of transactions are associated with fraud
# MAGIC numericCols = [field for (field, dataType) in fraudDF.dtypes if ((dataType == "double") | (dataType=='int'))] 
# MAGIC fraudNumeric = fraudDF.select(numericCols) # Isolation forest only works with numeric features

# COMMAND ----------

# MAGIC %md
# MAGIC We can see that there are many more non-fraudulent transactions than fraudulent transactions.

# COMMAND ----------

# MAGIC %python
# MAGIC display(fraudNumeric.groupby('isFraud').count())

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Engineering

# COMMAND ----------

# MAGIC %python
# MAGIC display(fraudNumeric)

# COMMAND ----------

# MAGIC %md
# MAGIC We see that there are errors in the amount transferred. There are several instances where the difference between the original balance and new balance of the destination account differ from the amount transferred. For example, old and new balance for a destination account is 0 even though the amount transferred is nonzero. These may be indicators of fraud.

# COMMAND ----------

# MAGIC %python
# MAGIC fraudNumeric = fraudNumeric.withColumn("DestinationDiff", col("newBalanceDest") - col("oldbalanceDest"))
# MAGIC 
# MAGIC display(fraudNumeric.filter((col("amount")) != (col("DestinationDiff"))).orderBy(col("isFraud").desc()))

# COMMAND ----------

# MAGIC %python
# MAGIC diff_transfer_change_fraud = (fraudNumeric.filter((col("amount")!=0) & (col("DestinationDiff")==0) & (col('isFraud')==1)).count())
# MAGIC diff_transfer_change_fraud_pct = 100*diff_transfer_change_fraud/(fraudNumeric.filter("isFraud = 1").count())
# MAGIC print(f"Percent of fraudulent transactions where transfer amount != change in destination balance: {diff_transfer_change_fraud_pct}%")
# MAGIC 
# MAGIC diff_transfer_change_not_fraud = (fraudNumeric.filter((col("amount")!=0) & (col("DestinationDiff")==0) & (col('isFraud')==0)).count())
# MAGIC diff_transfer_change_not_fraud_pct = 100*diff_transfer_change_not_fraud/(fraudNumeric.filter("isFraud = 0").count())
# MAGIC print(f"Percent of non-fraudulent transactions where transfer amount != change in destination balance: {diff_transfer_change_not_fraud_pct}%")

# COMMAND ----------

# MAGIC %md
# MAGIC We see that having a nonzero transfer amount with a zero change in destination account balance seems to indicate fraud. We'll create a feature that captures the difference between the amount transferred and the actual change in destination account balance.

# COMMAND ----------

# MAGIC %python
# MAGIC errorBalance = (fraudNumeric
# MAGIC                 .withColumn("errorBalanceOrig", col("newbalanceOrig") + col("amount") - col("oldbalanceOrg"))
# MAGIC                 .withColumn("errorBalanceDest", col("oldbalanceDest") + col("amount") - col("newbalanceDest")))

# COMMAND ----------

# MAGIC %md
# MAGIC ### Pandas
# MAGIC 
# MAGIC Now that we have done our feature engineering in Spark, we will now convert our DataFrame to a Pandas DataFrame to build an Isolation Forest using sklearn.

# COMMAND ----------

# MAGIC %python
# MAGIC spark.conf.set("spark.sql.execution.arrow.enabled", "true")
# MAGIC 
# MAGIC fraudPandas = errorBalance.drop("DestinationDiff").toPandas()
# MAGIC 
# MAGIC y = fraudPandas["isFraud"].apply(lambda x: 1 if x==0 else -1).reset_index(drop=True) # 1 if not fraud, -1 if fraud (consistent with isolation forests)
# MAGIC X = fraudPandas.drop(["isFlaggedFraud", "isFraud"], axis=1).reset_index(drop=True) # Removing labels
# MAGIC 
# MAGIC display(X)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Building an Isolation Forest
# MAGIC 
# MAGIC An [isolation forest](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.IsolationForest.html) determines outliers by random splitting on features and randomly selecting a split value. The number of splits required to isolate a sample is equal to the path length. Outliers tend to have significantly shorter path lengths. If the average of path lengths over the forest of random trees is short for a particular sample, it is likely to be an outlier.
# MAGIC 
# MAGIC The isolation forest accepts several parameters, such as:
# MAGIC * `n_estimators`: The number of trees used in the ensemble.
# MAGIC * `contamination`: The proportion of outliers in the data.
# MAGIC * `max_samples`: The number of samples from the data that are used to train each tree
# MAGIC 
# MAGIC We will first calculate contamination for this dataset.

# COMMAND ----------

# MAGIC %python
# MAGIC fraudContamination = fraudDF.filter("isFraud = 1").count() / fraudDF.count()
# MAGIC print(f"Contamination for fraud dataset {fraudContamination:.4f}.")

# COMMAND ----------

# MAGIC %md
# MAGIC We train the isolation forest on the dataset with a contamination of 0.003. 
# MAGIC 
# MAGIC **NOTE**: This command might take a few minutes to run. 

# COMMAND ----------

# MAGIC %python
# MAGIC isolation_forest = IsolationForest(n_estimators=80, n_jobs=-1, contamination=.003, max_samples=512, random_state=42)
# MAGIC isolation_forest.fit(X)
# MAGIC y_predict = isolation_forest.predict(X)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Outliers
# MAGIC 
# MAGIC We can look at the decision function to determine how abnormal various points are. The lower the score, the more abnormal it is. Negative points are classified as outliers. 
# MAGIC 
# MAGIC Let's look at a predicted outlier.

# COMMAND ----------

# MAGIC %python
# MAGIC minPoint = np.argmin(isolation_forest.decision_function(X[0:1000]))
# MAGIC print(f"Minimum point: {minPoint}") #finds point with lowest score
# MAGIC print(f"Decision score {isolation_forest.decision_function(X.iloc[minPoint:minPoint+1,:])}")
# MAGIC fraudPandas.iloc[minPoint,:]

# COMMAND ----------

# MAGIC %md
# MAGIC The isolation forest will return -1 if it predicts that a transaction is fraudulent (an outlier) and 1 for non-fraudulent transactions.

# COMMAND ----------

# MAGIC %python
# MAGIC display(pd.concat([pd.DataFrame(y_predict, columns=["Outlier Value"]), X], axis=1))

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Plotting a Confusion Matrix
# MAGIC 
# MAGIC We can now plot a confusion matrix that will allow us to visualize the number of false positive and false negatives along with the true positives and negatives. 

# COMMAND ----------

# MAGIC %python
# MAGIC from sklearn.metrics import confusion_matrix, f1_score, accuracy_score, fbeta_score, precision_score, recall_score
# MAGIC import matplotlib.pyplot as plt
# MAGIC import numpy as np
# MAGIC def plot_confusion_matrix(y_true, y_pred, classes, title=None, cmap=plt.cm.Blues):
# MAGIC     """
# MAGIC     This function prints and plots the confusion matrix.
# MAGIC     """
# MAGIC 
# MAGIC     # Compute confusion matrix
# MAGIC     cm = confusion_matrix(y_true, y_pred)
# MAGIC 
# MAGIC     fig, ax = plt.subplots()
# MAGIC     im = ax.imshow(cm, interpolation='nearest', cmap=cmap)
# MAGIC     ax.figure.colorbar(im, ax=ax)
# MAGIC     ax.set(xticks=np.arange(cm.shape[1]),
# MAGIC            yticks=np.arange(cm.shape[0]),
# MAGIC            xticklabels=classes, yticklabels=classes,
# MAGIC            title=title,
# MAGIC            ylabel='True label',
# MAGIC            xlabel='Predicted label')
# MAGIC 
# MAGIC     plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
# MAGIC              rotation_mode="anchor")
# MAGIC 
# MAGIC     fmt = 'd'
# MAGIC     thresh = cm.max() / 2.
# MAGIC     for i in range(cm.shape[0]):
# MAGIC         for j in range(cm.shape[1]):
# MAGIC             ax.text(j, i, format(cm[i, j], fmt),
# MAGIC                     ha="center", va="center",
# MAGIC                     color="white" if cm[i, j] > thresh else "black")
# MAGIC     fig.tight_layout()
# MAGIC     return fig
# MAGIC 
# MAGIC np.set_printoptions(precision=2)

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC For every 8 cases the isolation forest marks as fraud, it is able to detect 1 true fraud, even though it has no access to labels. However, it was only able to detect 20% of the fraud cases overall. Given no labeled information about our data, this isn't too bad!

# COMMAND ----------

# MAGIC %python
# MAGIC fig = plot_confusion_matrix(y, y_predict, np.array(["Fraud", "Not Fraud"]), title="Isolation Forest Fraud Prediction")
# MAGIC display(fig)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Feature Importance using Logistic Regression
# MAGIC [Logistic Regression](https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html#sklearn.linear_model.LogisticRegression) is a linear model for classification that models the probabilities of possible outcomes using a logistic function.
# MAGIC 
# MAGIC Isolation forests do not have a built-in feature importance function; however, we can infer feature importances by training a model that uses the predictions of the isolation forest as labels and the features used as inputs. We can use logistic regression to predict if the isolation forest would mark the transaction as fraud or not, and we can treat the feature importances of the logistic regression model as the feature importance of the isolation forest. By using a linear model, we get both importance and direction (i.e. increasing the feature value leads to the model predicting the transaction as more or less likely to be fraudulent)
# MAGIC 
# MAGIC We will combine the best of spark + sklearn by using [spark-sklearn](https://github.com/databricks/spark-sklearn) to distribute the search of various hyperparameters of our logistic regression model.

# COMMAND ----------

# MAGIC %python
# MAGIC from sklearn.linear_model import LogisticRegression
# MAGIC from spark_sklearn.grid_search import GridSearchCV
# MAGIC 
# MAGIC # Grid Search to find best Logistic regression model
# MAGIC params = {'C': [.1, .2, .3, 1.0]}
# MAGIC lr = LogisticRegression()
# MAGIC clf = GridSearchCV(sc, lr, params, cv=3)
# MAGIC clf.fit(X, y_predict)

# COMMAND ----------

# MAGIC %python
# MAGIC feature_importance = clf.best_estimator_.coef_[0]
# MAGIC data = list(zip(fraudPandas.columns, feature_importance))
# MAGIC importances_pd = pd.DataFrame(data, columns=['feature', 'importance'])
# MAGIC importances_pd = importances_pd.sort_values(by='importance', ascending=False)
# MAGIC display(spark.createDataFrame(importances_pd))

# COMMAND ----------

# MAGIC %md
# MAGIC We can graph the importance of the features to determine how the model chose to label something as an outlier or not. We pick transaction 335 since it's an outlier.

# COMMAND ----------

# MAGIC %python
# MAGIC import matplotlib
# MAGIC import matplotlib.pyplot as plt
# MAGIC 
# MAGIC fig,ax = plt.subplots(figsize=(10,6))
# MAGIC plt.gcf().subplots_adjust(bottom=0.45)
# MAGIC outlier_index=335
# MAGIC 
# MAGIC #Chose index 335 since it's classified as an outlier
# MAGIC #Multiplied by -1 so features predicting outliers are positive
# MAGIC row_coef = (X.iloc[outlier_index,:]*clf.best_estimator_.coef_[0]*-1)
# MAGIC row_coef.plot.bar()
# MAGIC fig.suptitle("Feature Importance")
# MAGIC display(fig)

# COMMAND ----------

# MAGIC %md
# MAGIC ##Finding Feature Importance using Random Forests
# MAGIC 
# MAGIC We can also find feature importances for the isolation forest using [Random Forest Classifiers](https://scikit-learn.org/stable/modules/generated/sklearn.ensemble.RandomForestClassifier.html#sklearn.ensemble.RandomForestClassifier). A random forest is made of many decision trees. Each decision tree is trained individually on a subset of the data and the average or most common prediction from the decision trees is used as the random forests' prediction. 
# MAGIC 
# MAGIC We take the same approach to determine feature importance as the Logistic Regression section; however, we only have feature importance, not direction.

# COMMAND ----------

# MAGIC %python
# MAGIC from sklearn.ensemble import RandomForestClassifier
# MAGIC 
# MAGIC #Grid Search to find best Random forest
# MAGIC params_rf = {"max_depth": [2, 5], "n_estimators": [5, 10]}
# MAGIC rf = RandomForestClassifier()
# MAGIC clf = GridSearchCV(sc, rf, params_rf, cv=3)
# MAGIC clf.fit(X, y)

# COMMAND ----------

# MAGIC %python
# MAGIC feature_importance=clf.best_estimator_.feature_importances_
# MAGIC data = list(zip(fraudPandas.columns,feature_importance))
# MAGIC importances_pd = pd.DataFrame(data, columns=["feature", "importance"])
# MAGIC importances_pd = importances_pd.sort_values(by="importance", ascending=False)

# COMMAND ----------

# MAGIC %python
# MAGIC display(spark.createDataFrame(importances_pd))

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>