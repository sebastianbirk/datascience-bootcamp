# Databricks notebook source
# MAGIC %md-sandbox
# MAGIC <div style="text-align: center; line-height: 0; padding-top: 9px;">
# MAGIC   <img src="https://databricks.com/wp-content/uploads/2018/03/db-academy-rgb-1200px.png" alt="Databricks Learning" style="width: 600px; height: 163px">
# MAGIC </div>

# COMMAND ----------

# MAGIC %md
# MAGIC # K-Means clustering
# MAGIC 
# MAGIC ##![Spark Logo Tiny](https://s3-us-west-2.amazonaws.com/curriculum-release/images/105/logo_spark_tiny.png) Introduction
# MAGIC 
# MAGIC Cluster analysis or clustering is the task of grouping a set of objects in such a way that objects in the same group (called a cluster) are more similar (in some sense) to each other than to those in other groups (clusters).
# MAGIC 
# MAGIC <a href="http://en.wikipedia.org/wiki/K-means_clustering" target="_blank">K-means</a> is one of the
# MAGIC most commonly used clustering algorithms that clusters the data points into a
# MAGIC predefined number of clusters. 

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://s3-us-west-2.amazonaws.com/curriculum-release/images/105/logo_spark_tiny.png) Documentation

# COMMAND ----------

# MAGIC %md
# MAGIC * <a href='https://spark.apache.org/docs/latest/ml-clustering.html#k-meanshttps://spark.apache.org/docs/latest/mllib-clustering.html' target="_blank">K-Means</a> in the Spark ML programming guide

# COMMAND ----------

# MAGIC %md
# MAGIC ##![Spark Logo Tiny](https://s3-us-west-2.amazonaws.com/curriculum-release/images/105/logo_spark_tiny.png) K-Means in Action

# COMMAND ----------

# MAGIC %md
# MAGIC **Let's visualize our data**
# MAGIC 
# MAGIC Create a Scatter plot and you set the **Values** to **x** and **y** in `Plot Options...`

# COMMAND ----------

# MAGIC %python
# MAGIC import numpy as np
# MAGIC num_points = 100
# MAGIC sd = 16
# MAGIC np.random.seed(273)
# MAGIC 
# MAGIC points = np.concatenate((
# MAGIC   np.random.normal((105,100), (sd,sd), size=[num_points,2]),
# MAGIC   np.random.normal((40,100), (sd,sd),  size=[num_points,2]),
# MAGIC   np.random.normal((50,40),  (sd,sd),  size=[num_points,2])
# MAGIC   )).tolist()
# MAGIC 
# MAGIC df = spark.createDataFrame(points, ["x","y"])
# MAGIC df.createOrReplaceTempView("points")
# MAGIC display(df)

# COMMAND ----------

# MAGIC %md
# MAGIC *Question:* How many clusters do you see here?

# COMMAND ----------

# MAGIC %md
# MAGIC #### Javascript visualization
# MAGIC 
# MAGIC Execute the next cell to see an interactive visualization of K-Means. 
# MAGIC 
# MAGIC 
# MAGIC The code is based on a demo published by <a href="https://github.com/nitoyon/tech.nitoyon.com/tree/master/ja/blog/2013/11/07/k-means" target="_blank">github.com/nitoyon</a>.

# COMMAND ----------

# MAGIC %python
# MAGIC import json
# MAGIC 
# MAGIC normalizer = max(max(points))
# MAGIC points_json = json.dumps(points)
# MAGIC displayHTML("""
# MAGIC <html>
# MAGIC <head>
# MAGIC   <meta charset="utf-8">
# MAGIC   <meta content="utf-8" http-equiv="encoding">
# MAGIC </head>
# MAGIC <body>
# MAGIC   <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js"></script>
# MAGIC   <H1>Interactive K-Means</H1>
# MAGIC   <div id="kmeans">
# MAGIC   <div><svg></svg></div>
# MAGIC   <div><button id="step">Step</button> <button id="restart" disabled>Restart</button></div>
# MAGIC   <fieldset style="display: inline; margin: .8em 0 1em 0; border: 1px solid #999; padding: .5em">
# MAGIC   <div><button id="reset">New</button></div>
# MAGIC   </fieldset>
# MAGIC   </div>
# MAGIC   
# MAGIC     <script>
# MAGIC   var flag = false;
# MAGIC var WIDTH = d3.select("#kmeans")[0][0].offsetWidth - 20;
# MAGIC var HEIGHT = Math.max(300, WIDTH * .7);
# MAGIC var svg = d3.select("#kmeans svg")
# MAGIC   .attr('width', WIDTH)
# MAGIC   .attr('height', HEIGHT)
# MAGIC   .style('padding', '10px')
# MAGIC   .style('background', '#223344')
# MAGIC   .style('cursor', 'pointer')
# MAGIC   .style('-webkit-user-select', 'none')
# MAGIC   .style('-khtml-user-select', 'none')
# MAGIC   .style('-moz-user-select', 'none')
# MAGIC   .style('-ms-user-select', 'none')
# MAGIC   .style('user-select', 'none')
# MAGIC   .on('click', function() {
# MAGIC     d3.event.preventDefault();
# MAGIC     step();
# MAGIC   });
# MAGIC 
# MAGIC d3.selectAll("#kmeans button")
# MAGIC   .style('padding', '.5em .8em');
# MAGIC 
# MAGIC d3.selectAll("#kmeans label")
# MAGIC   .style('display', 'inline-block')
# MAGIC   .style('width', '15em');
# MAGIC 
# MAGIC var lineg = svg.append('g');
# MAGIC var dotg = svg.append('g');
# MAGIC var centerg = svg.append('g');
# MAGIC d3.select("#step")
# MAGIC   .on('click', function() { step(); draw(); });
# MAGIC d3.select("#restart")
# MAGIC   .on('click', function() { restart(); draw(); });
# MAGIC d3.select("#reset")
# MAGIC   .on('click', function() { init(); draw(); });
# MAGIC 
# MAGIC 
# MAGIC var groups = [], dots = [];
# MAGIC 
# MAGIC function step() {
# MAGIC   d3.select("#restart").attr("disabled", null);
# MAGIC   if (flag) {
# MAGIC     moveCenter();
# MAGIC     draw();
# MAGIC   } else {
# MAGIC     updateGroups();
# MAGIC     draw();
# MAGIC   }
# MAGIC   flag = !flag;
# MAGIC }
# MAGIC 
# MAGIC function init() {
# MAGIC   d3.select("#restart").attr("disabled", "disabled");
# MAGIC 
# MAGIC   var N = 300;
# MAGIC   var K = 3;
# MAGIC   groups = [];
# MAGIC   for (var i = 0; i < K; i++) {
# MAGIC     var g = {
# MAGIC       dots: [],
# MAGIC       color: 'hsl(' + (i * 360 / K) + ',100%,50%)',
# MAGIC       center: {
# MAGIC         x: Math.random() * WIDTH,
# MAGIC         y: Math.random() * HEIGHT
# MAGIC       },
# MAGIC       init: {
# MAGIC         center: {}
# MAGIC       }
# MAGIC     };
# MAGIC     g.init.center = {
# MAGIC       x: g.center.x,
# MAGIC       y: g.center.y
# MAGIC     };
# MAGIC     groups.push(g);
# MAGIC   }
# MAGIC 
# MAGIC   dots = [];
# MAGIC   flag = false;
# MAGIC   points = """ + points_json + """;
# MAGIC   norm = """ + str(normalizer) + """;
# MAGIC   for (i = 0; i < points.length; i++) {
# MAGIC     var dot ={
# MAGIC       x: points[i][0] / norm * WIDTH,
# MAGIC       y: (norm - points[i][1]) / norm * HEIGHT,
# MAGIC       group: undefined
# MAGIC     };
# MAGIC     dot.init = {
# MAGIC       x: dot.x,
# MAGIC       y: dot.y,
# MAGIC       group: dot.group
# MAGIC     };
# MAGIC     dots.push(dot);
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC function restart() {
# MAGIC   flag = false;
# MAGIC   d3.select("#restart").attr("disabled", "disabled");
# MAGIC 
# MAGIC   groups.forEach(function(g) {
# MAGIC     g.dots = [];
# MAGIC     g.center.x = g.init.center.x;
# MAGIC     g.center.y = g.init.center.y;
# MAGIC   });
# MAGIC 
# MAGIC   for (var i = 0; i < dots.length; i++) {
# MAGIC     var dot = dots[i];
# MAGIC     dots[i] = {
# MAGIC       x: dot.init.x,
# MAGIC       y: dot.init.y,
# MAGIC       group: undefined,
# MAGIC       init: dot.init
# MAGIC     };
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC 
# MAGIC function draw() {
# MAGIC   var circles = dotg.selectAll('circle')
# MAGIC     .data(dots);
# MAGIC   circles.enter()
# MAGIC     .append('circle');
# MAGIC   circles.exit().remove();
# MAGIC   circles
# MAGIC     .transition()
# MAGIC     .duration(500)
# MAGIC     .attr('cx', function(d) { return d.x; })
# MAGIC     .attr('cy', function(d) { return d.y; })
# MAGIC     .attr('fill', function(d) { return d.group ? d.group.color : '#ffffff'; })
# MAGIC     .attr('r', 5);
# MAGIC 
# MAGIC   if (dots[0].group) {
# MAGIC     var l = lineg.selectAll('line')
# MAGIC       .data(dots);
# MAGIC     var updateLine = function(lines) {
# MAGIC       lines
# MAGIC         .attr('x1', function(d) { return d.x; })
# MAGIC         .attr('y1', function(d) { return d.y; })
# MAGIC         .attr('x2', function(d) { return d.group.center.x; })
# MAGIC         .attr('y2', function(d) { return d.group.center.y; })
# MAGIC         .attr('stroke', function(d) { return d.group.color; });
# MAGIC     };
# MAGIC     updateLine(l.enter().append('line'));
# MAGIC     updateLine(l.transition().duration(500));
# MAGIC     l.exit().remove();
# MAGIC   } else {
# MAGIC     lineg.selectAll('line').remove();
# MAGIC   }
# MAGIC 
# MAGIC   var c = centerg.selectAll('path')
# MAGIC     .data(groups);
# MAGIC   var updateCenters = function(centers) {
# MAGIC     centers
# MAGIC       .attr('transform', function(d) { return "translate(" + d.center.x + "," + d.center.y + ") rotate(45)";})
# MAGIC       .attr('fill', function(d,i) { return d.color; })
# MAGIC       .attr('stroke', '#aabbcc');
# MAGIC   };
# MAGIC   c.exit().remove();
# MAGIC   updateCenters(c.enter()
# MAGIC     .append('path')
# MAGIC     .attr('d', d3.svg.symbol().type('cross'))
# MAGIC     .attr('stroke', '#aabbcc'));
# MAGIC   updateCenters(c
# MAGIC     .transition()
# MAGIC     .duration(500));}
# MAGIC 
# MAGIC function moveCenter() {
# MAGIC   groups.forEach(function(group, i) {
# MAGIC     if (group.dots.length == 0) return;
# MAGIC 
# MAGIC     // get center of gravity
# MAGIC     var x = 0, y = 0;
# MAGIC     group.dots.forEach(function(dot) {
# MAGIC       x += dot.x;
# MAGIC       y += dot.y;
# MAGIC     });
# MAGIC 
# MAGIC     group.center = {
# MAGIC       x: x / group.dots.length,
# MAGIC       y: y / group.dots.length
# MAGIC     };
# MAGIC   });
# MAGIC   
# MAGIC }
# MAGIC 
# MAGIC function updateGroups() {
# MAGIC   groups.forEach(function(g) { g.dots = []; });
# MAGIC   dots.forEach(function(dot) {
# MAGIC     // find the nearest group
# MAGIC     var min = Infinity;
# MAGIC     var group;
# MAGIC     groups.forEach(function(g) {
# MAGIC       var d = Math.pow(g.center.x - dot.x, 2) + Math.pow(g.center.y - dot.y, 2);
# MAGIC       if (d < min) {
# MAGIC         min = d;
# MAGIC         group = g;
# MAGIC       }
# MAGIC     });
# MAGIC 
# MAGIC     // update group
# MAGIC     group.dots.push(dot);
# MAGIC     dot.group = group;
# MAGIC   });
# MAGIC }
# MAGIC 
# MAGIC init(); draw();
# MAGIC 
# MAGIC </script>
# MAGIC 
# MAGIC   </body>
# MAGIC   </html>
# MAGIC """)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Distributed K-Means in Spark
# MAGIC 
# MAGIC Let's see how you can use the K-Means Estimator in Spark:

# COMMAND ----------

from pyspark.ml.clustering import KMeans

kmeans = KMeans()

print(kmeans.explainParams())

# COMMAND ----------

# MAGIC %md
# MAGIC Take a look at the `initMode` parameter. By default, Spark doesn't start with random cluster centers. It rather uses `kmeans||`, a distributed implementation of the `kmeans++` algorithm, an algorithm which takes a quick look at the data finds meaningful initial cluster centers.
# MAGIC 
# MAGIC More info on `kmeans||` in the original <a href="http://theory.stanford.edu/~sergei/papers/vldb12-kmpar.pdf">research paper</a>.

# COMMAND ----------

# MAGIC %md
# MAGIC We are using a <a href="https://spark.apache.org/docs/latest/ml-features.html#vectorassembler" target="_blank">VectorAssembler</a> to create a Vector from the *x* and *y* column and then we are creating 3 clusters using K-Means:

# COMMAND ----------

from pyspark.ml.feature import VectorAssembler

assembler = VectorAssembler(inputCols=["x","y"], outputCol="features")
vecDF = assembler.transform(df)
kmeans.setK(3)
kmeans.setPredictionCol("clusterid")
kmeansModel = kmeans.fit(vecDF)

# COMMAND ----------

# MAGIC %md
# MAGIC Now take a look at the cluster centers:

# COMMAND ----------

print(kmeansModel.clusterCenters())

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC Let's associate each point with its cluster and display them:
# MAGIC 
# MAGIC *Create a Scatter plot and you set the **Values** to **x** and **y** and the **Keys** to **clusterid*** in  `Plot Options...`

# COMMAND ----------

clusteredDF = kmeansModel.transform(vecDF)
display(clusteredDF)

# COMMAND ----------

# MAGIC %md
# MAGIC ### Evaluating K-Means Performance
# MAGIC 
# MAGIC We are using the <a href="https://en.wikipedia.org/wiki/Silhouette_(clustering)" target="_blank">Silhouette  method</a> to evaluate the performance of our clustering. The Silhouette value ranges from -1 to +1, where a high value indicates that the objects are well matched to its own clusters. If we have a high value, then the clustering configuration is appropriate.

# COMMAND ----------

from pyspark.ml.evaluation import ClusteringEvaluator

evaluator = ClusteringEvaluator()
print(evaluator.explainParams())

# COMMAND ----------

silhouette = evaluator.setPredictionCol("clusterid").evaluate(clusteredDF)
print("Silhouette with squared euclidean distance = " + str(silhouette))

# COMMAND ----------

# MAGIC %md-sandbox
# MAGIC &copy; 2018 Databricks, Inc. All rights reserved.<br/>
# MAGIC Apache, Apache Spark, Spark and the Spark logo are trademarks of the <a href="http://www.apache.org/">Apache Software Foundation</a>.<br/>
# MAGIC <br/>
# MAGIC <a href="https://databricks.com/privacy-policy">Privacy Policy</a> | <a href="https://databricks.com/terms-of-use">Terms of Use</a> | <a href="http://help.databricks.com/">Support</a>