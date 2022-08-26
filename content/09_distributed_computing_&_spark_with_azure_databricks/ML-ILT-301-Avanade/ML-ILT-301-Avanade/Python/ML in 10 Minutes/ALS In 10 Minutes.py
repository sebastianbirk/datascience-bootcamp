# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # **Collaborative Filtering**
# MAGIC 
# MAGIC ##![Spark Logo Tiny](https://s3-us-west-2.amazonaws.com/curriculum-release/images/105/logo_spark_tiny.png) Introduction
# MAGIC 
# MAGIC In this course, you have learned about many of the basic transformations and actions that Spark allows us to apply to distributed datasets.  Spark also exposes some higher level functionality; in particular, Machine Learning using a component of Spark called [SparkML][SparkML].  In this part, you will learn how to use SparkML to make personalized movie recommendations using the movie data we have been analyzing.
# MAGIC 
# MAGIC We are going to use a technique called [collaborative filtering][collab]. Collaborative filtering is a method of making automatic predictions (filtering) about the interests of a user by collecting preferences or taste information from many users (collaborating). The underlying assumption of the collaborative filtering approach is that if a person A has the same opinion as a person B on an issue, A is more likely to have B's opinion on a different issue x than to have the opinion on x of a person chosen randomly. You can read more about collaborative filtering [here][collab2].
# MAGIC 
# MAGIC The image below (from [Wikipedia][collab]) shows an example of predicting of the user's rating using collaborative filtering. At first, people rate different items (like videos, images, games). After that, the system is making predictions about a user's rating for an item, which the user has not rated yet. These predictions are built upon the existing ratings of other users, who have similar ratings with the active user. For instance, in the image below the system has made a prediction, that the active user will not like the video.
# MAGIC <br>
# MAGIC ![collaborative filtering](https://courses.edx.org/c4x/BerkeleyX/CS100.1x/asset/Collaborative_filtering.gif)
# MAGIC 
# MAGIC [SparkML]: http://spark.apache.org/docs/latest/ml-guide.html
# MAGIC [collab]: https://en.wikipedia.org/?title=Collaborative_filtering
# MAGIC [collab2]: http://recommender-systems.org/collaborative-filtering/

# COMMAND ----------

# MAGIC %md
# MAGIC In our next lab we are working with movie recommendations.
# MAGIC 
# MAGIC For movie recommendations, we start with a matrix whose entries are movie ratings by users (shown in red in the diagram below).  Each column represents a user (shown in green) and each row represents a particular movie (shown in blue).
# MAGIC 
# MAGIC Since not all users have rated all movies, we do not know all of the entries in this matrix, which is precisely why we need collaborative filtering.  For each user, we have ratings for only a subset of the movies.  With collaborative filtering, the idea is to approximate the ratings matrix by factorizing it as the product of two matrices: one that describes properties of each user (shown in green), and one that describes properties of each movie (shown in blue).
# MAGIC 
# MAGIC ![factorization](http://spark-mooc.github.io/web-assets/images/matrix_factorization.png)
# MAGIC We want to select these two matrices such that the error for the users/movie pairs where we know the correct ratings is minimized.  The [Alternating Least Squares][als] algorithm does this by first randomly filling the users matrix with values and then optimizing the value of the movies such that the error is minimized.  Then, it holds the movies matrix constrant and optimizes the value of the user's matrix.  This alternation between which matrix to optimize is the reason for the "alternating" in the name.
# MAGIC 
# MAGIC This optimization is what's being shown on the right in the image above.  Given a fixed set of user factors (i.e., values in the users matrix), we use the known ratings to find the best values for the movie factors using the optimization written at the bottom of the figure.  Then we "alternate" and pick the best user factors given fixed movie factors.

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://s3-us-west-2.amazonaws.com/curriculum-release/images/105/logo_spark_tiny.png) Documentation
# MAGIC 
# MAGIC 
# MAGIC * [ALS Python docs](https://spark.apache.org/docs/latest/api/python/pyspark.ml.html#pyspark.ml.recommendation.ALS)
# MAGIC * [ALS Scala docs](https://spark.apache.org/docs/latest/api/scala/#org.apache.spark.ml.recommendation.ALS)

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://s3-us-west-2.amazonaws.com/curriculum-release/images/105/logo_spark_tiny.png) ALS in Action
# MAGIC 
# MAGIC Let's predict if `userid=100` likes `movieid=2` or not.

# COMMAND ----------

from pyspark.sql import Row

d = [
  Row(userid=1, movieid=1, likes=1),
  Row(userid=1, movieid=2, likes=0),

  Row(userid=2, movieid=1, likes=0),
  Row(userid=2, movieid=2, likes=1),

  Row(userid=3, movieid=1, likes=1),
  Row(userid=3, movieid=2, likes=0),

  Row(userid=5, movieid=1, likes=1),
  Row(userid=5, movieid=2, likes=0),

  Row(userid=6, movieid=1, likes=1),
  Row(userid=6, movieid=2, likes=1),

  Row(userid=100, movieid=1, likes=1)
  # Rating for userid=100 & movieid=2 missing
]

df = spark.createDataFrame(d)
display(df)

# COMMAND ----------

from pyspark.sql.functions import array, col, explode, lit, struct
from pyspark.sql import DataFrame
from typing import Iterable

def melt_df(
        df: DataFrame,
        id_vars: Iterable[str], value_vars: Iterable[str],
        var_name: str="variable", value_name: str="value") -> DataFrame:
    """Convert :class:`DataFrame` from wide to long format."""

    # Create array<struct<variable: str, value: ...>>
    _vars_and_vals = array(*(
        struct(lit(c).alias(var_name), col(c).alias(value_name))
        for c in value_vars))

    # Add to the DataFrame and explode
    _tmp = df.withColumn("_vars_and_vals", explode(_vars_and_vals))

    cols = id_vars + [
            col("_vars_and_vals")[x].alias(x) for x in [var_name, value_name]]
    return _tmp.select(*cols)

# COMMAND ----------

display(melt_df(df, ["userid"], ["movieid", "likes"]))

# COMMAND ----------

# MAGIC %md
# MAGIC How much do you think *User id 100* likes *Movie id 2*?

# COMMAND ----------

from pyspark.ml.recommendation import ALS

als = ALS()
print(als.explainParams())

# COMMAND ----------

(als.setSeed(273)
    .setColdStartStrategy("drop")
    .setUserCol("userid")
    .setItemCol("movieid")
    .setRatingCol("likes"))

display(als.fit(df).recommendForAllUsers(2))

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2018 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>