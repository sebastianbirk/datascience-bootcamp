// Databricks notebook source
// MAGIC 
// MAGIC %md-sandbox
// MAGIC 
// MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
// MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
// MAGIC </div>

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC <img src="http://spark-mooc.github.io/web-assets/images/cs110x/movie-camera.png" style="float:right; height: 200px; margin: 10px; border: 1px solid #ddd; border-radius: 15px 15px 15px 15px; padding: 10px"/>
// MAGIC 
// MAGIC # Predicting Movie Ratings
// MAGIC 
// MAGIC One of the most common uses of big data is to predict what users want.  This allows Google to show you relevant ads, Amazon to recommend relevant products, and Netflix to recommend movies that you might like.  This lab will demonstrate how we can use Apache Spark to recommend movies to a user.  We will start with some basic techniques, and then use the SparkML library's Alternating Least Squares method to make more sophisticated predictions. Here are the SparkML [Python docs](https://spark.apache.org/docs/latest/api/python/pyspark.ml.html) and the [Scala docs](https://spark.apache.org/docs/latest/api/scala/#org.apache.spark.ml.package).
// MAGIC 
// MAGIC For this lab, we will use 1 million movie ratings from the [MovieLens stable benchmark rating dataset](http://grouplens.org/datasets/movielens/). 
// MAGIC 
// MAGIC ## ![Spark Logo Tiny](https://files.training.databricks.com/images/105/logo_spark_tiny.png) In this lesson you:<br>
// MAGIC  - Exploring the dataset and build a baseline model
// MAGIC  - Build a Collaborative Filtering model
// MAGIC  - Make customized movie predictions for yourself

// COMMAND ----------

// MAGIC %md
// MAGIC ##### Motivation: Want to win $1,000,000?
// MAGIC 
// MAGIC All you needed to do was improve Netflix’s movie recommendation system by 10% in 2008. This competition is known as the [Netflix Prize](https://en.wikipedia.org/wiki/Netflix_Prize). 
// MAGIC 
// MAGIC Good recommendations are vital to sites such as Netflix, where 75 percent of what consumers watch come from movie recommendations.
// MAGIC 
// MAGIC So, how do we create recommendations and evaluate their relevance?

// COMMAND ----------

// MAGIC %run "../Includes/Classroom-Setup"

// COMMAND ----------

// MAGIC %md
// MAGIC ## Part 1: Exploring our Dataset
// MAGIC 
// MAGIC First, let's take a look at the directory containing our files.

// COMMAND ----------

// MAGIC %fs ls /mnt/training/movielens

// COMMAND ----------

// MAGIC %md
// MAGIC ### Load and Cache
// MAGIC 
// MAGIC We're going to be accessing this data a lot. 
// MAGIC 
// MAGIC Rather than reading it from source over and over again, we'll cache both the movies DataFrame and the ratings DataFrame into the executor's memory.

// COMMAND ----------

val moviesDF = spark.read.parquet("dbfs:/mnt/training/movielens/movies.parquet/").cache
val ratingsDF = spark.read.parquet("dbfs:/mnt/training/movielens/ratings.parquet/").cache

val ratingsCount = ratingsDF.count
val moviesCount = moviesDF.count

println(f"There are $ratingsCount ratings and $moviesCount movies in the datasets")
println("-" * 80)

// COMMAND ----------

// MAGIC %md
// MAGIC Let's take a quick look at some of the data in the two DataFrames.

// COMMAND ----------

display(moviesDF)

// COMMAND ----------

display(ratingsDF)

// COMMAND ----------

// MAGIC %md
// MAGIC ## **Part 2: Collaborative Filtering**

// COMMAND ----------

// MAGIC %md
// MAGIC ### (2a) Creating a Training Set
// MAGIC 
// MAGIC Before we jump into using machine learning, we need to break up the `ratingsDF` dataset into two DataFrames:
// MAGIC * A training set, which we will use to train models
// MAGIC * A test set, which we will use for our experiments
// MAGIC 
// MAGIC To randomly split the dataset into the multiple groups, we can use the [randomSplit()](http://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.DataFrame.randomSplit) transformation. `randomSplit()` takes a set of splits and a seed and returns multiple DataFrames. Use the seed given below.

// COMMAND ----------

// TODO

// We'll hold out 80% for training and leave 20% for testing 
val seed = 42
val Array(trainingDF, testDF) = <FILL_IN>

println(f"Training: ${trainingDF.count}, test: ${testDF.count}")

trainingDF.show(3)
testDF.show(3)

// COMMAND ----------

// MAGIC %md
// MAGIC ### (2b) Benchmark Model
// MAGIC 
// MAGIC Let's always predict the average movie rating in our dataset to use as our benchmark model, and see what our RMSE is.

// COMMAND ----------

import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.sql.functions.{lit, avg}

val averageRating = trainingDF.select(avg("rating")).first()(0)

val benchmarkDF = trainingDF.withColumn("prediction", lit(averageRating))

val regEval = new RegressionEvaluator().setPredictionCol("prediction").setLabelCol("rating").setMetricName("rmse")
val baselineRmse = regEval.evaluate(benchmarkDF)

println(f"Baseline RMSE: $baselineRmse%.2f")

// COMMAND ----------

// MAGIC %md
// MAGIC ### (2c) Alternating Least Squares
// MAGIC 
// MAGIC In this part, we will use the Apache Spark ML Pipeline implementation of Alternating Least Squares, [ALS (Python)](http://spark.apache.org/docs/latest/api/python/pyspark.ml.html#pyspark.ml.recommendation.ALS) or [ALS (Scala)](https://spark.apache.org/docs/latest/api/scala/index.html#org.apache.spark.ml.recommendation.ALS). To determine the best values for the hyperparameters, we will use ALS to train several models, and then we will select the best model and use the parameters from that model in the rest of this lab exercise.
// MAGIC 
// MAGIC The process we will use for determining the best model is as follows:
// MAGIC 1. Pick a set of model parameters. The most important parameter to model is the *rank*, which is the number of columns in the Users matrix or the number of rows in the Movies matrix. In general, a lower rank will mean higher error on the training dataset, but a high rank may lead to [overfitting](https://en.wikipedia.org/wiki/Overfitting).  We will train models with ranks of 4 and 12 using the `trainingDF` dataset.
// MAGIC 
// MAGIC 2. Set the appropriate parameters on the `ALS` object:
// MAGIC     * The "User" column will be set to the values in our `userId` DataFrame column.
// MAGIC     * The "Item" column will be set to the values in our `movieId` DataFrame column.
// MAGIC     * The "Rating" column will be set to the values in our `rating` DataFrame column.
// MAGIC     * `nonnegative` = True (whether to use nonnegative constraint for least squares)
// MAGIC     * `regParam` = 0.1.
// MAGIC     
// MAGIC    **Note**: Read the documentation for the ALS class **carefully**. It will help you accomplish this step.
// MAGIC 
// MAGIC 4. Create multiple models using the `ParamGridBuilder` and the `CrossValidator`, one for each of our rank values.
// MAGIC 
// MAGIC 6. We'll keep the model with the lowest error rate. Such a model will be selected automatically by the CrossValidator.

// COMMAND ----------

// TODO
import org.apache.spark.ml.recommendation.ALS

val als = new ALS()
             .setMaxIter(5)
             .setSeed(seed)
             .setColdStartStrategy("drop")
             .<FILL_IN>

// COMMAND ----------

// TEST  - Run this cell to test your solution.
assert(als.getItemCol == "movieId", f"Incorrect choice of ${als.getItemCol} for ALS item column.")
assert(als.getUserCol == "userId", f"Incorrect choice of ${als.getUserCol} for ALS user column.")
assert(als.getRatingCol == "rating", f"Incorrect choice of ${als.getRatingCol} for ALS rating column.")

// COMMAND ----------

// MAGIC %md
// MAGIC Now that we have initialized a model, we need to fit it to our training data, and evaluate how well it does on the validation dataset. Create a `CrossValidator` and `ParamGridBuilder` that will decide whether *rank* value *4* or *12* gives a lower *RMSE*.  
// MAGIC 
// MAGIC NOTE: This cell may take a few minutes to run.

// COMMAND ----------

// TODO

import org.apache.spark.ml.tuning._
import org.apache.spark.ml.evaluation.RegressionEvaluator
import org.apache.spark.ml.recommendation.ALSModel

val regEval = <FILL_IN> // Create RegressionEvaluator

val grid = <FILL_IN> // Create grid for rank values 4 and 12 

val seed = 42
val cv = new CrossValidator()          
            .setSeed(seed)
            <FILL_IN> // Set number of folds to 3. Add grid, als and regEval

val cvModel = cv.fit(trainingDF)

val myModel = cvModel.bestModel.asInstanceOf[ALSModel]
println(f"The best model was trained with rank ${myModel.rank}")

// COMMAND ----------

// TEST - Run this cell to test your solution.
assert(myModel.rank == 12, f"Unexpected value for best rank. Expected 12, got ${myModel.rank}")

// COMMAND ----------

// MAGIC %md
// MAGIC ### (2d) Testing Your Model
// MAGIC 
// MAGIC So far, we used the `trainingDF` dataset to select the best model. Since we used this dataset to determine what model is best, we cannot use it to test how good the model is; otherwise, we would be very vulnerable to [overfitting](https://en.wikipedia.org/wiki/Overfitting).  To decide how good our model is, we need to use the `testDF` dataset.  We will use the best model you created in part (2b) for predicting the ratings for the test dataset and then we will compute the RMSE.
// MAGIC 
// MAGIC The steps you should perform are:
// MAGIC * Run a prediction, using `myModel` as created above, on the test dataset (`testDF`), producing a new `predictedTestDF` DataFrame.
// MAGIC * Use the previously created RMSE evaluator, `regEval` to evaluate the filtered DataFrame.

// COMMAND ----------

// TODO

val predictedTestDF = myModel.<FILL_IN>

// Run the previously created RMSE evaluator, regEval, on the predictedTestDF DataFrame
val testRmse = <FILL_IN>

println(f"The model had a RMSE on the test set of $testRmse%.3f")

// COMMAND ----------

// MAGIC %md
// MAGIC ## Part 3: Predictions for Yourself
// MAGIC The ultimate goal of this lab exercise is to predict what movies to recommend to yourself.  In order to do that, you will first need to add ratings for yourself to the `ratingsDF` dataset.

// COMMAND ----------

// MAGIC %md
// MAGIC **(3a) Your Movie Ratings**
// MAGIC 
// MAGIC To help you provide ratings for yourself, we have included the following code to list the names and movie IDs of the 50 highest-rated movies that have at least 500 ratings.

// COMMAND ----------

moviesDF.createOrReplaceTempView("movies")
ratingsDF.createOrReplaceTempView("ratings")

// COMMAND ----------

// MAGIC %sql
// MAGIC SELECT movieId, title, AVG(rating) AS avg_rating, COUNT(*) AS num_ratings
// MAGIC FROM ratings r JOIN movies m ON (r.movieID = m.ID)
// MAGIC GROUP BY r.movieId, m.title
// MAGIC HAVING COUNT(*) > 500
// MAGIC ORDER BY avg_rating DESC
// MAGIC LIMIT 100

// COMMAND ----------

// MAGIC %md
// MAGIC The user ID 0 is unassigned, so we will use it for your ratings. We set the variable `myUserId` to 0 for you. 
// MAGIC 
// MAGIC Next, create a new DataFrame called `myRatingsDF`, with your ratings for at least 10 movie ratings. Each entry should be formatted as `(myUserId, movieId, rating)`.  As in the original dataset, ratings should be between 1 and 5 (inclusive). 
// MAGIC 
// MAGIC If you have not seen at least 10 of these movies, you can increase the parameter passed to `LIMIT` in the above cell until there are 10 movies that you have seen (or you can also guess what your rating would be for movies you have not seen).

// COMMAND ----------

// TODO
val myUserId = 0

// Note that the movie IDs are the *last* number on each line. A common error was to use the number of ratings as the movie ID.
val myRatedMovies = List(
     <FILL_IN>
      // The format of each line is (myUserId, movie ID, your rating)
      // For example, to give the movie "Star Wars: Episode IV - A New Hope (1977)" a five rating, you would add the following line:
      // (myUserId, 260, 5),
     )

val myRatingsRDD = sc.parallelize(myRatedMovies)
val myRatingsDF = myRatingsRDD.toDF("userId", "movieId", "rating")
println("My movie ratings:")
display(myRatingsDF.limit(10))

// COMMAND ----------

// MAGIC %md
// MAGIC ### (3b) Add Your Movies to Training Dataset
// MAGIC 
// MAGIC Now that you have ratings for yourself, you need to add your ratings to the `trainingDF` dataset so that the model you train will incorporate your preferences.  Spark's [union()](http://spark.apache.org/docs/latest/api/python/pyspark.sql.html#pyspark.sql.DataFrame.union) transformation combines two DataFrames; use `union()` to create a new training dataset that includes your ratings and the data in the original training dataset.

// COMMAND ----------

// TODO
val trainingWithMyRatingsDF = <FILL_IN>

val countDiff = trainingWithMyRatingsDF.count - trainingDF.count
println(f"The training dataset now has $countDiff more entries than the original training dataset")
assert (countDiff == myRatingsDF.count)

// COMMAND ----------

// MAGIC %md
// MAGIC ### (3c) Train a Model with Your Ratings
// MAGIC 
// MAGIC Now, train a model with your ratings added and the parameters you used in in part (2b) and (2c). Make sure you include **all** of the parameters.
// MAGIC 
// MAGIC **Note**: This cell will take about 1 minute to run.

// COMMAND ----------

// TODO

als.<FILL_IN>

// Create the model with these parameters.
val myRatingsModel = als.<FILL_IN>

// COMMAND ----------

// MAGIC %md
// MAGIC ### (3d) Predict Your Ratings
// MAGIC 
// MAGIC Now that we have trained a new model, let's predict what ratings you would give to the movies that you did not already provide ratings for. The code below filters out all of the movies you have rated, and creates a `predictedRatingsDF` DataFrame of the predicted ratings for all of your unseen movies.

// COMMAND ----------

import org.apache.spark.sql.functions.lit

// Create a list of the my rated movie IDs 
val myRatedMovieIds = for ((userId, movieId, rating) <- myRatedMovies) yield {movieId}

// Filter out the movies I already rated.
val notRatedDF = moviesDF.filter(! $"ID".isin(myRatedMovieIds:_*))

// Rename the "ID" column to be "movieId", and add a column with myUserId as "userId".
val myUnratedMoviesDF = notRatedDF.withColumnRenamed("ID", "movieId").withColumn("userId", lit(myUserId))       
// Use myRatingModel to predict ratings for the movies that I did not manually rate.
val predictedRatingsDF = myRatingsModel.transform(myUnratedMoviesDF)

// COMMAND ----------

// MAGIC %md
// MAGIC ### (3e) Predict Your Ratings
// MAGIC 
// MAGIC We have our predicted ratings. Now we can print out the 25 movies with the highest predicted ratings.

// COMMAND ----------

predictedRatingsDF.createOrReplaceTempView("predictions")

// COMMAND ----------

// MAGIC %md
// MAGIC **NOTE:** Since Spark 2.3, it will be required to enable cross joins.
// MAGIC 
// MAGIC Or more specifically, disable the warning when a cross join is automatically detected.

// COMMAND ----------

spark.conf.set("spark.sql.crossJoin.enabled", "true")

// COMMAND ----------

// MAGIC %md
// MAGIC Let's take a look at the raw predictions:

// COMMAND ----------

// MAGIC %sql
// MAGIC SELECT * FROM predictions

// COMMAND ----------

// MAGIC %md
// MAGIC Now print out the 25 movies with the highest predicted ratings. We will only include movies that have at least 75 ratings in total.

// COMMAND ----------

// MAGIC %sql
// MAGIC SELECT p.title, p.prediction AS your_predicted_rating
// MAGIC FROM ratings r INNER JOIN predictions p 
// MAGIC ON (r.movieID = p.movieID)
// MAGIC WHERE p.userId = 0
// MAGIC GROUP BY p.title, p.prediction
// MAGIC HAVING COUNT(*) > 75
// MAGIC ORDER BY p.prediction DESC
// MAGIC LIMIT 25

// COMMAND ----------

// MAGIC %md-sandbox
// MAGIC &copy; 2019 Databricks, Inc. All rights reserved.<br/>
// MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
// MAGIC <br/>
// MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>