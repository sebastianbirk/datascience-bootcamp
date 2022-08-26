# Databricks notebook source
# MAGIC 
# MAGIC %scala
# MAGIC val tags = com.databricks.logging.AttributionContext.current.tags
# MAGIC 
# MAGIC //*******************************************
# MAGIC // GET VERSION OF APACHE SPARK
# MAGIC //*******************************************
# MAGIC 
# MAGIC // Get the version of spark
# MAGIC val Array(sparkMajorVersion, sparkMinorVersion, _) = spark.version.split("""\.""")
# MAGIC 
# MAGIC // Set the major and minor versions
# MAGIC spark.conf.set("com.databricks.training.spark.major-version", sparkMajorVersion)
# MAGIC spark.conf.set("com.databricks.training.spark.minor-version", sparkMinorVersion)
# MAGIC 
# MAGIC //*******************************************
# MAGIC // GET VERSION OF DATABRICKS RUNTIME
# MAGIC //*******************************************
# MAGIC 
# MAGIC // Get the version of the Databricks Runtime
# MAGIC val version = {
# MAGIC   val dbr = com.databricks.spark.util.SparkServerContext.serverVersion.replace("dbr-", "")
# MAGIC   val scalaMinMajVer = util.Properties.versionNumberString
# MAGIC   val index = scalaMinMajVer.lastIndexOf(".")
# MAGIC   val len = scalaMinMajVer.length
# MAGIC   dbr + ".x-scala" + scalaMinMajVer.dropRight(len - index)
# MAGIC }
# MAGIC 
# MAGIC val runtimeVersion = if (version != "") {
# MAGIC   spark.conf.set("com.databricks.training.job", "false")
# MAGIC   version
# MAGIC } else {
# MAGIC   spark.conf.set("com.databricks.training.job", "true")
# MAGIC   dbutils.widgets.get("sparkVersion")
# MAGIC }
# MAGIC 
# MAGIC val runtimeVersions = runtimeVersion.split("""-""")
# MAGIC // The GPU and ML runtimes push the number of elements out to 5
# MAGIC // so we need to account for every scenario here. There should
# MAGIC // never be a case in which there is less than two so we can fail
# MAGIC // with an helpful error message for <2 or >5
# MAGIC val (dbrVersion, scalaVersion) = {
# MAGIC   runtimeVersions match {
# MAGIC     case Array(d, _, _, _, s) => (d, s.replace("scala", ""))
# MAGIC     case Array(d, _, _, s)    => (d, s.replace("scala", ""))
# MAGIC     case Array(d, _, s)       => (d, s.replace("scala", ""))
# MAGIC     case Array(d, s)          => (d, s.replace("scala", ""))
# MAGIC     case _ =>
# MAGIC       throw new IllegalArgumentException(s"""Dataset-Mounts: Cannot parse version(s) from "${runtimeVersions.mkString(", ")}".""")
# MAGIC   }
# MAGIC }
# MAGIC val Array(dbrMajorVersion, dbrMinorVersion, _*) = dbrVersion.split("""\.""")
# MAGIC 
# MAGIC // Set the the major and minor versions
# MAGIC spark.conf.set("com.databricks.training.dbr.version", version)
# MAGIC spark.conf.set("com.databricks.training.dbr.major-version", dbrMajorVersion)
# MAGIC spark.conf.set("com.databricks.training.dbr.minor-version", dbrMinorVersion)
# MAGIC 
# MAGIC //*******************************************
# MAGIC // GET USERNAME AND USERHOME
# MAGIC //*******************************************
# MAGIC 
# MAGIC // Get the user's name
# MAGIC val name = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_USER, java.util.UUID.randomUUID.toString.replace("-", ""))
# MAGIC val username = if (name != "unknown") name else dbutils.widgets.get("databricksUsername")
# MAGIC 
# MAGIC val userhome = s"dbfs:/user/$username"
# MAGIC 
# MAGIC // Set the user's name and home directory
# MAGIC spark.conf.set("com.databricks.training.username", username)
# MAGIC spark.conf.set("com.databricks.training.userhome", userhome)
# MAGIC 
# MAGIC //**********************************
# MAGIC // GET TAG VALUE
# MAGIC // Find a given tag's value or return a supplied default value if not found
# MAGIC //**********************************
# MAGIC 
# MAGIC def getTagValue(tagName: String, defaultValue: String = null): String = {
# MAGIC   val tags = com.databricks.logging.AttributionContext.current.tags
# MAGIC   val values = tags.collect({ case (t, v) if t.name == tagName => v }).toSeq
# MAGIC   values.size match {
# MAGIC     case 0 => defaultValue
# MAGIC     case _ => values.head.toString
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC //**********************************
# MAGIC // GET EXPERIMENT ID
# MAGIC // JobId fallback in production mode
# MAGIC //**********************************
# MAGIC 
# MAGIC def getExperimentId(): Long = {
# MAGIC   val notebookId = getTagValue("notebookId", null)
# MAGIC   val jobId = getTagValue("jobId", null)
# MAGIC   
# MAGIC   (notebookId != null) match { 
# MAGIC       case true => notebookId.toLong
# MAGIC       case false => (jobId != null) match { 
# MAGIC         case true => jobId.toLong
# MAGIC         case false => 0
# MAGIC       }
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC 
# MAGIC spark.conf.set("com.databricks.training.experimentId", getExperimentId())
# MAGIC 
# MAGIC //**********************************
# MAGIC // VARIOUS UTILITY FUNCTIONS
# MAGIC //**********************************
# MAGIC 
# MAGIC def assertSparkVersion(expMajor:Int, expMinor:Int):String = {
# MAGIC   val major = spark.conf.get("com.databricks.training.spark.major-version")
# MAGIC   val minor = spark.conf.get("com.databricks.training.spark.minor-version")
# MAGIC 
# MAGIC   if ((major.toInt < expMajor) || (major.toInt == expMajor && minor.toInt < expMinor)) {
# MAGIC     throw new Exception(s"This notebook must be ran on Spark version $expMajor.$expMinor or better, found Spark $major.$minor")
# MAGIC   }
# MAGIC   return s"$major.$minor"
# MAGIC }
# MAGIC 
# MAGIC def assertDbrVersion(expMajor:Int, expMinor:Int):String = {
# MAGIC   val major = spark.conf.get("com.databricks.training.dbr.major-version")
# MAGIC   val minor = spark.conf.get("com.databricks.training.dbr.minor-version")
# MAGIC 
# MAGIC   if ((major.toInt < expMajor) || (major.toInt == expMajor && minor.toInt < expMinor)) {
# MAGIC     throw new Exception(s"This notebook must be ran on Databricks Runtime (DBR) version $expMajor.$expMinor or better, found $major.$minor.")
# MAGIC   }
# MAGIC   return s"$major.$minor"
# MAGIC }
# MAGIC 
# MAGIC def assertIsMlRuntime():Unit = {
# MAGIC   if (version.contains("-ml-") == false) {
# MAGIC     throw new RuntimeException(s"This notebook must be ran on a Databricks ML Runtime, found $version.")
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC // **********************************
# MAGIC //  GET AZURE DATASOURCE
# MAGIC // **********************************
# MAGIC 
# MAGIC def getAzureDataSource(): (String,String,String) = {
# MAGIC   val datasource = spark.conf.get("com.databricks.training.azure.datasource").split("\t")
# MAGIC   val source = datasource(0)
# MAGIC   val sasEntity = datasource(1)
# MAGIC   val sasToken = datasource(2)
# MAGIC   return (source, sasEntity, sasToken)
# MAGIC }
# MAGIC 
# MAGIC def initializeBrowserSideStats(): Unit = {
# MAGIC   import java.net.URLEncoder.encode
# MAGIC   import scala.collection.Map
# MAGIC   import org.json4s.DefaultFormats
# MAGIC   import org.json4s.jackson.JsonMethods._
# MAGIC   import org.json4s.jackson.Serialization.write
# MAGIC   import org.json4s.JsonDSL._
# MAGIC 
# MAGIC   implicit val formats: DefaultFormats = DefaultFormats
# MAGIC 
# MAGIC   val tags = com.databricks.logging.AttributionContext.current.tags
# MAGIC 
# MAGIC   // Get the user's name and home directory
# MAGIC   val username = spark.conf.get("com.databricks.training.username", "unknown-username")
# MAGIC   val userhome = spark.conf.get("com.databricks.training.userhome", "unknown-userhome")
# MAGIC   
# MAGIC   val courseName = spark.conf.get("com.databricks.training.courseName", "unknown-course")
# MAGIC   val moduleName = spark.conf.get("com.databricks.training.moduleName", "unknown-module")
# MAGIC 
# MAGIC   // Get the the major and minor versions
# MAGIC   val dbrVersion = spark.conf.get("com.databricks.training.dbr.version", "0.0")
# MAGIC   val dbrMajorVersion = spark.conf.get("com.databricks.training.dbr.major-version", "0")
# MAGIC   val dbrMinorVersion = spark.conf.get("com.databricks.training.dbr.minor-version", "0")
# MAGIC 
# MAGIC   val sessionId = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_SESSION_ID, "unknown-sessionId")
# MAGIC   val hostName = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_HOST_NAME, "unknown-host-name")
# MAGIC   val clusterMemory = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_CLUSTER_MEMORY, "unknown-cluster-memory")
# MAGIC   val clientBranchName = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_BRANCH_NAME, "unknown-branch-name")
# MAGIC   val notebookLanguage = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_NOTEBOOK_LANGUAGE, "unknown-notebook-language")
# MAGIC   val browserUserAgent = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_USER_AGENT, "unknown-user-agent")
# MAGIC   val browserHostName = tags.getOrElse(com.databricks.logging.BaseTagDefinitions.TAG_HOST_NAME, "unknown-host-name")
# MAGIC 
# MAGIC // Need to find docs or JAR file for com.databricks.logging.BaseTagDefinitions.TAG_ definitions  
# MAGIC // Guessing TAG_BRANCH_NAME == clientBranchName
# MAGIC //   val clientBranchName = (tags.filter(tup => tup._1.toString.contains("clientBranchName")).map(tup => tup._2).head)
# MAGIC // Guessing TAG_USER_AGENT == browserUserAgent
# MAGIC //   val browserUserAgent = (tags.filter(tup => tup._1.toString.contains("browserUserAgent")).map(tup => tup._2).head)
# MAGIC // Guessing TAG_HOST_NAME == browserHostName
# MAGIC //   val browserHostName = (tags.filter(tup => tup._1.toString.contains("browserHostName")).map(tup => tup._2).head)
# MAGIC 
# MAGIC // No TAG_ matches for these - wrap in try/catch if necessary
# MAGIC   val sourceIpAddress = try { (tags.filter(tup => tup._1.toString.contains("sourceIpAddress")).map(tup => tup._2).head) } catch { case e: Exception => "unknown-source-ip"}
# MAGIC   val browserHash = try { (tags.filter(tup => tup._1.toString.contains("browserHash")).map(tup => tup._2).head) } catch { case e: Exception => "unknown-browser-hash"}
# MAGIC 
# MAGIC   val json = Map(
# MAGIC     "time" -> java.time.Instant.now.toEpochMilli,
# MAGIC     "username" -> username,
# MAGIC     "userhome" -> userhome,
# MAGIC     "dbrVersion" -> s"$dbrMajorVersion.$dbrMinorVersion",
# MAGIC     "tags" -> tags.map(tup => (tup._1.name, tup._2))
# MAGIC   )
# MAGIC 
# MAGIC   val jsonString = write(json)
# MAGIC   val tags_dump = write(tags.map(tup => (tup._1.name, tup._2)))
# MAGIC   
# MAGIC   val utf8 = java.nio.charset.StandardCharsets.UTF_8.toString;
# MAGIC   
# MAGIC   val html = s"""
# MAGIC <html>
# MAGIC <head>
# MAGIC   <script src="https://files.training.databricks.com/static/js/classroom-support.min.js"></script>
# MAGIC   <script>
# MAGIC <!--  
# MAGIC     window.setTimeout( // Defer until bootstrap has enough time to async load
# MAGIC       function(){ 
# MAGIC           Cookies.set("_academy_username", "$username", {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_module_name", "$moduleName", {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_course_name", "$courseName", {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_sessionId", "$sessionId", {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_hostName", '$hostName', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_clusterMemory", '$clusterMemory', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_clientBranchName", '$clientBranchName', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_notebookLanguage", '$notebookLanguage', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_sourceIpAddress", '$sourceIpAddress', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_browserUserAgent", '$browserUserAgent', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_browserHostName", '$browserHostName', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_browserHash", '$browserHash', {"domain":".databricksusercontent.com"});
# MAGIC           Cookies.set("_academy_tags", $jsonString, {"domain":".databricksusercontent.com"});
# MAGIC       }, 2000
# MAGIC     );
# MAGIC -->    
# MAGIC   </script>
# MAGIC </head>
# MAGIC <body>
# MAGIC   Class Setup Complete
# MAGIC <script>
# MAGIC </script>  
# MAGIC </body>
# MAGIC </html>
# MAGIC """
# MAGIC displayHTML(html)
# MAGIC   
# MAGIC }
# MAGIC 
# MAGIC def showStudentSurvey():Unit = {
# MAGIC   import java.net.URLEncoder.encode
# MAGIC   val utf8 = java.nio.charset.StandardCharsets.UTF_8.toString;
# MAGIC   val username = encode(spark.conf.get("com.databricks.training.username", "unknown-user"), utf8)
# MAGIC   val courseName = encode(spark.conf.get("com.databricks.training.courseName", "unknown-course"), utf8)
# MAGIC   val moduleNameUnencoded = spark.conf.get("com.databricks.training.moduleName", "unknown-module")
# MAGIC   val moduleName = encode(moduleNameUnencoded, utf8)
# MAGIC 
# MAGIC   import scala.collection.Map
# MAGIC   import org.json4s.DefaultFormats
# MAGIC   import org.json4s.jackson.JsonMethods._
# MAGIC   import org.json4s.jackson.Serialization.write
# MAGIC   import org.json4s.JsonDSL._
# MAGIC 
# MAGIC   implicit val formats: DefaultFormats = DefaultFormats
# MAGIC 
# MAGIC   val json = Map(
# MAGIC     "courseName" -> courseName,
# MAGIC     "moduleName" -> moduleName, // || "unknown",
# MAGIC     "name" -> name,
# MAGIC     "time" -> java.time.Instant.now.toEpochMilli,
# MAGIC     "username" -> username,
# MAGIC     "userhome" -> userhome,
# MAGIC     "dbrVersion" -> s"$dbrMajorVersion.$dbrMinorVersion",
# MAGIC     "tags" -> tags.map(tup => (tup._1.name, tup._2))
# MAGIC   )
# MAGIC 
# MAGIC   val jsonString = write(json)
# MAGIC   val feedbackUrl = s"https://engine-prod.databricks.training/feedback/$username/$courseName/$moduleName/";
# MAGIC   
# MAGIC   val html = s"""
# MAGIC   <html>
# MAGIC   <head>
# MAGIC     <script src="https://files.training.databricks.com/static/js/classroom-support.min.js"></script>
# MAGIC     <script>
# MAGIC <!--    
# MAGIC       window.setTimeout( // Defer until bootstrap has enough time to async load
# MAGIC         () => { 
# MAGIC         //console.log($jsonString);
# MAGIC         //console.log(JSON.stringify("$jsonString");
# MAGIC           var allCookies = Cookies.get();
# MAGIC           Cookies.set("_academy_module_name", "$moduleName", {"domain":".databricksusercontent.com"});
# MAGIC 
# MAGIC           $$("#divComment").css("display", "visible");
# MAGIC 
# MAGIC           // Emulate radio-button like feature for multiple_choice
# MAGIC           $$(".multiple_choicex").on("click", (evt) => {
# MAGIC                 const container = $$(evt.target).parent();
# MAGIC                 $$(".multiple_choicex").removeClass("checked"); 
# MAGIC                 $$(".multiple_choicex").removeClass("checkedRed"); 
# MAGIC                 $$(".multiple_choicex").removeClass("checkedGreen"); 
# MAGIC                 container.addClass("checked"); 
# MAGIC                 if (container.hasClass("thumbsDown")) { 
# MAGIC                     container.addClass("checkedRed"); 
# MAGIC                 } else { 
# MAGIC                     container.addClass("checkedGreen"); 
# MAGIC                 };
# MAGIC                 
# MAGIC                 // Send the like/dislike before the comment is shown so we at least capture that.
# MAGIC                 // In analysis, always take the latest feedback for a module (if they give a comment, it will resend the like/dislike)
# MAGIC                 var json = { data: { liked: $$(".multiple_choicex.checked").attr("value"), cookies: Cookies.get() } };
# MAGIC                 $$.ajax({
# MAGIC                   type: 'PUT', 
# MAGIC                   url: '$feedbackUrl', 
# MAGIC                   data: JSON.stringify(json),
# MAGIC                   dataType: 'json',
# MAGIC                   processData: false
# MAGIC                 });
# MAGIC                 $$("#divComment").show("fast");
# MAGIC           });
# MAGIC 
# MAGIC 
# MAGIC            // Set click handler to do a PUT
# MAGIC           $$("#btnSubmit").on("click", (evt) => {
# MAGIC               // Use .attr("value") instead of .val() - this is not a proper input box
# MAGIC               var json = { data: { liked: $$(".multiple_choicex.checked").attr("value"), comment: $$("#taComment").val(), cookies: Cookies.get() } };
# MAGIC 
# MAGIC               const msgThanks = "Thank you for your feedback!";
# MAGIC               const msgError = "There was an error submitting your feedback";
# MAGIC               const msgSending = "Sending feedback...";
# MAGIC 
# MAGIC               $$("#feedback").hide("fast");
# MAGIC               $$("#feedback-response").html(msgSending);
# MAGIC 
# MAGIC               $$.ajax({
# MAGIC                 type: 'PUT', 
# MAGIC                 url: '$feedbackUrl', 
# MAGIC                 data: JSON.stringify(json),
# MAGIC                 dataType: 'json',
# MAGIC                 processData: false
# MAGIC               })
# MAGIC                 .done(function() {
# MAGIC                   $$("#feedback-response").html(msgThanks);
# MAGIC                 })
# MAGIC                 .fail(function() {
# MAGIC                   $$("#feedback-response").html(msgError);
# MAGIC                 })
# MAGIC                 ; // End of .ajax chain
# MAGIC           });
# MAGIC         }, 2000
# MAGIC       );
# MAGIC -->
# MAGIC     </script>    
# MAGIC     <style>
# MAGIC .multiple_choicex > img:hover {    
# MAGIC     background-color: white;
# MAGIC     border-width: 0.15em;
# MAGIC     border-radius: 5px;
# MAGIC     border-style: solid;
# MAGIC }
# MAGIC .multiple_choicex.choice1 > img:hover {    
# MAGIC     border-color: green;
# MAGIC     background-color: green;
# MAGIC }
# MAGIC .multiple_choicex.choice2 > img:hover {    
# MAGIC     border-color: red;
# MAGIC     background-color: red;
# MAGIC }
# MAGIC .multiple_choicex {
# MAGIC     margin: 1em;
# MAGIC     padding: 0em;
# MAGIC     background-color: white;
# MAGIC     border: 0em;
# MAGIC     border-style: solid;
# MAGIC     border-color: green;
# MAGIC }
# MAGIC .multiple_choicex.checked {
# MAGIC     border: 0.15em solid black;
# MAGIC     background-color: white;
# MAGIC     border-width: 0.5em;
# MAGIC     border-radius: 5px;
# MAGIC }
# MAGIC .multiple_choicex.checkedGreen {
# MAGIC     border-color: green;
# MAGIC     background-color: green;
# MAGIC }
# MAGIC .multiple_choicex.checkedRed {
# MAGIC     border-color: red;
# MAGIC     background-color: red;
# MAGIC }
# MAGIC     </style>
# MAGIC   </head>
# MAGIC   <body>
# MAGIC     <h2 style="font-size:28px; line-height:34.3px"><img style="vertical-align:middle" src="https://files.training.databricks.com/images/105/logo_spark_tiny.png"/>What did you think?</h2>
# MAGIC     <p>Please let us know how if you liked this module, <b>$moduleNameUnencoded</b></p>
# MAGIC     <div id="feedback" style="clear:both;display:table;">
# MAGIC       <span class="multiple_choicex choice1 thumbsUp" value="true"><img style="width:100px" src="https://files.training.databricks.com/images/feedback/thumbs-up.png"/></span>
# MAGIC       <span class="multiple_choicex choice2 thumbsDown" value="false"><img style="width:100px" src="https://files.training.databricks.com/images/feedback/thumbs-down.png"/></span>
# MAGIC       <span>
# MAGIC         <div id="divComment" style="display:none">
# MAGIC           <textarea id="taComment" placeholder="How can we make this module better? (optional)" style="margin:1em;width:100%;height:200px;display:block"></textarea>
# MAGIC           <button id="btnSubmit">Send</button>
# MAGIC         </div>
# MAGIC       </span>
# MAGIC     </div>
# MAGIC     <div id="feedback-response" style="color:green; margin-top: 1em">&nbsp;</div>
# MAGIC   </body>
# MAGIC   </html>
# MAGIC   """
# MAGIC   displayHTML(html);  
# MAGIC }
# MAGIC 
# MAGIC class StudentsStatsService() extends org.apache.spark.scheduler.SparkListener {
# MAGIC   import org.apache.spark.scheduler._
# MAGIC 
# MAGIC   val hostname = "engine-prod.databricks.training"
# MAGIC 
# MAGIC   def logEvent(eventType: String):Unit = {
# MAGIC     import org.apache.http.entity._
# MAGIC     import org.apache.http.impl.client.{HttpClients}
# MAGIC     import org.apache.http.client.methods.HttpPost
# MAGIC     import java.net.URLEncoder.encode
# MAGIC     import org.json4s.jackson.Serialization
# MAGIC     implicit val formats = org.json4s.DefaultFormats
# MAGIC 
# MAGIC     var client:org.apache.http.impl.client.CloseableHttpClient = null
# MAGIC 
# MAGIC     try {
# MAGIC       val utf8 = java.nio.charset.StandardCharsets.UTF_8.toString;
# MAGIC       val username = encode(spark.conf.get("com.databricks.training.username", "unknown-user"), utf8)
# MAGIC       val courseName = encode(spark.conf.get("com.databricks.training.courseName", "unknown-course"), utf8)
# MAGIC       val moduleName = encode(spark.conf.get("com.databricks.training.moduleName", "unknown-module"), utf8)
# MAGIC       val event = encode(eventType, utf8)
# MAGIC       val url = s"https://$hostname/tracking/$courseName/$moduleName/$username/$event"
# MAGIC     
# MAGIC       val content = Map(
# MAGIC         "tags" -> tags.map(tup => (tup._1.name, s"$tup._2")),
# MAGIC         "courseName" -> courseName, 
# MAGIC         "moduleName" -> moduleName,
# MAGIC         "username" -> username,
# MAGIC         "eventType" -> eventType,
# MAGIC         "eventTime" -> s"${System.currentTimeMillis}"
# MAGIC       )
# MAGIC       
# MAGIC       val output = Serialization.write(content)
# MAGIC     
# MAGIC       // Future: (clues from Brian) 
# MAGIC       // Threadpool - don't use defaultExecutionContext; create our own EC; EC needs to be in scope as an implicit (Future calls will pick it up)
# MAGIC       // apply() on Future companion
# MAGIC       // onSuccess(), onFailure() (get exception from failure); map over future, final future, onComplete() gives Try object (can )
# MAGIC       //    Future {
# MAGIC       val client = HttpClients.createDefault()
# MAGIC       val httpPost = new HttpPost(url)
# MAGIC       val entity = new StringEntity(Serialization.write(Map("data" -> content)))      
# MAGIC 
# MAGIC       httpPost.setEntity(entity)
# MAGIC       httpPost.setHeader("Accept", "application/json")
# MAGIC       httpPost.setHeader("Content-type", "application/json")
# MAGIC 
# MAGIC       client.execute(httpPost)
# MAGIC       
# MAGIC     } catch {
# MAGIC       case e:Exception => org.apache.log4j.Logger.getLogger(getClass).error("Databricks Academey stats service failure", e)
# MAGIC       
# MAGIC     } finally {
# MAGIC       if (client != null) {
# MAGIC         try { client.close() } 
# MAGIC         catch { case _:Exception => () }
# MAGIC       }
# MAGIC     }
# MAGIC   }
# MAGIC   override def onJobEnd(jobEnd: SparkListenerJobEnd): Unit = logEvent("JobEnd" + jobEnd.jobId)
# MAGIC   override def onJobStart(jobStart: SparkListenerJobStart): Unit = logEvent("JobStart: " + jobStart.jobId)
# MAGIC }
# MAGIC 
# MAGIC val studentStatsService = new StudentsStatsService()
# MAGIC if (spark.conf.get("com.databricks.training.studentStatsService.registered", null) != "registered") {
# MAGIC   sc.addSparkListener(studentStatsService)
# MAGIC   spark.conf.set("com.databricks.training.studentStatsService", "registered")
# MAGIC }
# MAGIC studentStatsService.logEvent("Classroom-Setup")
# MAGIC   
# MAGIC //*******************************************
# MAGIC // CHECK FOR REQUIRED VERIONS OF SPARK & DBR
# MAGIC //*******************************************
# MAGIC 
# MAGIC assertDbrVersion(4, 0)
# MAGIC assertSparkVersion(2, 3)
# MAGIC 
# MAGIC displayHTML("Initialized classroom variables & functions...")

# COMMAND ----------

# MAGIC %python
# MAGIC 
# MAGIC #**********************************
# MAGIC # VARIOUS UTILITY FUNCTIONS
# MAGIC #**********************************
# MAGIC 
# MAGIC def assertSparkVersion(expMajor, expMinor):
# MAGIC   major = spark.conf.get("com.databricks.training.spark.major-version")
# MAGIC   minor = spark.conf.get("com.databricks.training.spark.minor-version")
# MAGIC 
# MAGIC   if (int(major) < expMajor) or (int(major) == expMajor and int(minor) < expMinor):
# MAGIC     msg = "This notebook must run on Spark version {}.{} or better, found.".format(expMajor, expMinor, major, minor)
# MAGIC     raise Exception(msg)
# MAGIC     
# MAGIC   return major+"."+minor
# MAGIC 
# MAGIC def assertDbrVersion(expMajor, expMinor):
# MAGIC   major = spark.conf.get("com.databricks.training.dbr.major-version")
# MAGIC   minor = spark.conf.get("com.databricks.training.dbr.minor-version")
# MAGIC 
# MAGIC   if (int(major) < expMajor) or (int(major) == expMajor and int(minor) < expMinor):
# MAGIC     msg = "This notebook must run on Databricks Runtime (DBR) version {}.{} or better, found.".format(expMajor, expMinor, major, minor)
# MAGIC     raise Exception(msg)
# MAGIC     
# MAGIC   return major+"."+minor
# MAGIC 
# MAGIC def assertIsMlRuntime():
# MAGIC   version = spark.conf.get("com.databricks.training.dbr.version")
# MAGIC   if "-ml-" not in version:
# MAGIC     raise Exception("This notebook must be ran on a Databricks ML Runtime, found {}.".format(version))
# MAGIC 
# MAGIC     
# MAGIC #**********************************
# MAGIC # GET AZURE DATASOURCE
# MAGIC #**********************************
# MAGIC 
# MAGIC 
# MAGIC def getAzureDataSource(): 
# MAGIC   datasource = spark.conf.get("com.databricks.training.azure.datasource").split("\t")
# MAGIC   source = datasource[0]
# MAGIC   sasEntity = datasource[1]
# MAGIC   sasToken = datasource[2]
# MAGIC   return (source, sasEntity, sasToken)
# MAGIC 
# MAGIC     
# MAGIC #**********************************
# MAGIC # GET EXPERIMENT ID
# MAGIC #**********************************
# MAGIC 
# MAGIC def getExperimentId():
# MAGIC   return spark.conf.get("com.databricks.training.experimentId")
# MAGIC 
# MAGIC #**********************************
# MAGIC # INIT VARIOUS VARIABLES
# MAGIC #**********************************
# MAGIC 
# MAGIC username = spark.conf.get("com.databricks.training.username", "unknown-username")
# MAGIC userhome = spark.conf.get("com.databricks.training.userhome", "unknown-userhome")
# MAGIC 
# MAGIC import sys
# MAGIC pythonVersion = spark.conf.set("com.databricks.training.python-version", sys.version[0:sys.version.index(" ")])
# MAGIC 
# MAGIC None # suppress output

# COMMAND ----------

# MAGIC %scala
# MAGIC 
# MAGIC //**********************************
# MAGIC // CREATE THE MOUNTS
# MAGIC //**********************************
# MAGIC 
# MAGIC def getAwsRegion():String = {
# MAGIC   try {
# MAGIC     import scala.io.Source
# MAGIC     import scala.util.parsing.json._
# MAGIC 
# MAGIC     val jsonString = Source.fromURL("http://169.254.169.254/latest/dynamic/instance-identity/document").mkString // reports ec2 info
# MAGIC     val map = JSON.parseFull(jsonString).getOrElse(null).asInstanceOf[Map[Any,Any]]
# MAGIC     map.getOrElse("region", null).asInstanceOf[String]
# MAGIC 
# MAGIC   } catch {
# MAGIC     // We will use this later to know if we are Amazon vs Azure
# MAGIC     case _: java.io.FileNotFoundException => null
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC def getAzureRegion():String = {
# MAGIC   import com.databricks.backend.common.util.Project
# MAGIC   import com.databricks.conf.trusted.ProjectConf
# MAGIC   import com.databricks.backend.daemon.driver.DriverConf
# MAGIC 
# MAGIC   new DriverConf(ProjectConf.loadLocalConfig(Project.Driver)).region
# MAGIC }
# MAGIC 
# MAGIC val awsAccessKey = "AKIAJBRYNXGHORDHZB4A"
# MAGIC val awsSecretKey = "a0BzE1bSegfydr3%2FGE3LSPM6uIV5A4hOUfpH8aFF"
# MAGIC val awsAuth = s"${awsAccessKey}:${awsSecretKey}"
# MAGIC 
# MAGIC def getAwsMapping(region:String):(String,Map[String,String]) = {
# MAGIC 
# MAGIC   val MAPPINGS = Map(
# MAGIC     "ap-northeast-1" -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-ap-northeast-1/common", Map[String,String]()),
# MAGIC     "ap-northeast-2" -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-ap-northeast-2/common", Map[String,String]()),
# MAGIC     "ap-south-1"     -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-ap-south-1/common", Map[String,String]()),
# MAGIC     "ap-southeast-1" -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-ap-southeast-1/common", Map[String,String]()),
# MAGIC     "ap-southeast-2" -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-ap-southeast-2/common", Map[String,String]()),
# MAGIC     "ca-central-1"   -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-ca-central-1/common", Map[String,String]()),
# MAGIC     "eu-central-1"   -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-eu-central-1/common", Map[String,String]()),
# MAGIC     "eu-west-1"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-eu-west-1/common", Map[String,String]()),
# MAGIC     "eu-west-2"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-eu-west-2/common", Map[String,String]()),
# MAGIC 
# MAGIC     // eu-west-3 in Paris isn't supported by Databricks yet - not supported by the current version of the AWS library
# MAGIC     // "eu-west-3"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-eu-west-3/common", Map[String,String]()),
# MAGIC     
# MAGIC     // Use Frankfurt in EU-Central-1 instead
# MAGIC     "eu-west-3"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-eu-central-1/common", Map[String,String]()),
# MAGIC     
# MAGIC     "sa-east-1"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-sa-east-1/common", Map[String,String]()),
# MAGIC     "us-east-1"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-us-east-1/common", Map[String,String]()),
# MAGIC     "us-east-2"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training-us-east-2/common", Map[String,String]()),
# MAGIC     "us-west-2"      -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training/common", Map[String,String]()),
# MAGIC     "_default"       -> (s"s3a://${awsAccessKey}:${awsSecretKey}@databricks-corp-training/common", Map[String,String]())
# MAGIC   )
# MAGIC 
# MAGIC   MAPPINGS.getOrElse(region, MAPPINGS("_default"))
# MAGIC }
# MAGIC 
# MAGIC def getAzureMapping(region:String):(String,Map[String,String]) = {
# MAGIC 
# MAGIC   var MAPPINGS = Map(
# MAGIC     "australiacentral"    -> ("dbtrainaustraliasoutheas",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=br8%2B5q2ZI9osspeuPtd3haaXngnuWPnZaHKFoLmr370%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "australiacentral2"   -> ("dbtrainaustraliasoutheas",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=br8%2B5q2ZI9osspeuPtd3haaXngnuWPnZaHKFoLmr370%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "australiaeast"       -> ("dbtrainaustraliaeast",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=FM6dy59nmw3f4cfN%2BvB1cJXVIVz5069zHmrda5gZGtU%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "australiasoutheast"  -> ("dbtrainaustraliasoutheas",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=br8%2B5q2ZI9osspeuPtd3haaXngnuWPnZaHKFoLmr370%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "canadacentral"       -> ("dbtraincanadacentral",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=dwAT0CusWjvkzcKIukVnmFPTmi4JKlHuGh9GEx3OmXI%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "canadaeast"          -> ("dbtraincanadaeast",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=SYmfKBkbjX7uNDnbSNZzxeoj%2B47PPa8rnxIuPjxbmgk%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "centralindia"        -> ("dbtraincentralindia",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=afrYm3P5%2BB4gMg%2BKeNZf9uvUQ8Apc3T%2Bi91fo/WOZ7E%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "centralus"           -> ("dbtraincentralus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=As9fvIlVMohuIV8BjlBVAKPv3C/xzMRYR1JAOB%2Bbq%2BQ%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "eastasia"            -> ("dbtraineastasia",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=sK7g5pki8bE88gEEsrh02VGnm9UDlm55zTfjZ5YXVMc%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "eastus"              -> ("dbtraineastus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=tlw5PMp1DMeyyBGTgZwTbA0IJjEm83TcCAu08jCnZUo%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "eastus2"             -> ("dbtraineastus2",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=Y6nGRjkVj6DnX5xWfevI6%2BUtt9dH/tKPNYxk3CNCb5A%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "japaneast"           -> ("dbtrainjapaneast",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=q6r9MS/PC9KLZ3SMFVYO94%2BfM5lDbAyVsIsbBKEnW6Y%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "japanwest"           -> ("dbtrainjapanwest",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=M7ic7/jOsg/oiaXfo8301Q3pt9OyTMYLO8wZ4q8bko8%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "northcentralus"      -> ("dbtrainnorthcentralus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=GTLU0g3pajgz4dpGUhOpJHBk3CcbCMkKT8wxlhLDFf8%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "northcentralus"      -> ("dbtrainnorthcentralus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=GTLU0g3pajgz4dpGUhOpJHBk3CcbCMkKT8wxlhLDFf8%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "northeurope"         -> ("dbtrainnortheurope",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=35yfsQBGeddr%2BcruYlQfSasXdGqJT3KrjiirN/a3dM8%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "southcentralus"      -> ("dbtrainsouthcentralus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=3cnVg/lzWMx5XGz%2BU4wwUqYHU5abJdmfMdWUh874Grc%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "southcentralus"      -> ("dbtrainsouthcentralus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=3cnVg/lzWMx5XGz%2BU4wwUqYHU5abJdmfMdWUh874Grc%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "southindia"          -> ("dbtrainsouthindia",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=0X0Ha9nFBq8qkXEO0%2BXd%2B2IwPpCGZrS97U4NrYctEC4%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "southeastasia"       -> ("dbtrainsoutheastasia",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=H7Dxi1yqU776htlJHbXd9pdnI35NrFFsPVA50yRC9U0%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "uksouth"             -> ("dbtrainuksouth",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=SPAI6IZXmm%2By/WMSiiFVxp1nJWzKjbBxNc5JHUz1d1g%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "ukwest"              -> ("dbtrainukwest",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=olF4rjQ7V41NqWRoK36jZUqzDBz3EsyC6Zgw0QWo0A8%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "westcentralus"       -> ("dbtrainwestcentralus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=UP0uTNZKMCG17IJgJURmL9Fttj2ujegj%2BrFN%2B0OszUE%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "westeurope"          -> ("dbtrainwesteurope",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=csG7jGsNFTwCArDlsaEcU4ZUJFNLgr//VZl%2BhdSgEuU%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "westindia"           -> ("dbtrainwestindia",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=fI6PNZ7YvDGKjArs1Et2rAM2zgg6r/bsKEjnzQxgGfA%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "westus"              -> ("dbtrainwestus",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=%2B1XZDXbZqnL8tOVsmRtWTH/vbDAKzih5ThvFSZMa3Tc%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "westus2"             -> ("dbtrainwestus2",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=DD%2BO%2BeIZ35MO8fnh/fk4aqwbne3MAJ9xh9aCIU/HiD4%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z"),
# MAGIC     "_default"            -> ("dbtrainwestus2",
# MAGIC                               "?ss=b&sp=rl&sv=2018-03-28&st=2018-04-01T00%3A00%3A00Z&sig=DD%2BO%2BeIZ35MO8fnh/fk4aqwbne3MAJ9xh9aCIU/HiD4%3D&srt=sco&se=2023-04-01T00%3A00%3A00Z")
# MAGIC   )
# MAGIC 
# MAGIC   val (account: String, sasKey: String) = MAPPINGS.getOrElse(region, MAPPINGS("_default"))
# MAGIC 
# MAGIC   val blob = "training"
# MAGIC   val source = s"wasbs://$blob@$account.blob.core.windows.net/"
# MAGIC   val configMap = Map(
# MAGIC     s"fs.azure.sas.$blob.$account.blob.core.windows.net" -> sasKey
# MAGIC   )
# MAGIC 
# MAGIC   (source, configMap)
# MAGIC }
# MAGIC 
# MAGIC def mountFailed(msg:String): Unit = {
# MAGIC   println(msg)
# MAGIC }
# MAGIC 
# MAGIC def retryMount(source: String, mountPoint: String): Unit = {
# MAGIC   try { 
# MAGIC     // Mount with IAM roles instead of keys for PVC
# MAGIC     dbutils.fs.mount(source, mountPoint)
# MAGIC   } catch {
# MAGIC     case e: Exception => mountFailed(s"*** ERROR: Unable to mount $mountPoint: ${e.getMessage}")
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC def mount(source: String, extraConfigs:Map[String,String], mountPoint: String): Unit = {
# MAGIC   try {
# MAGIC     dbutils.fs.mount(source, mountPoint, extraConfigs=extraConfigs)
# MAGIC   } catch {
# MAGIC     case ioe: java.lang.IllegalArgumentException => retryMount(source, mountPoint)
# MAGIC     case e: Exception => mountFailed(s"*** ERROR: Unable to mount $mountPoint: ${e.getMessage}")
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC def autoMount(fix:Boolean = false, failFast:Boolean = false, mountDir:String = "/mnt/training"): Unit = {
# MAGIC   var awsRegion = getAwsRegion()
# MAGIC 
# MAGIC   val (source, extraConfigs) = if (awsRegion != null)  {
# MAGIC     spark.conf.set("com.databricks.training.region.name", awsRegion)
# MAGIC     getAwsMapping(awsRegion)
# MAGIC 
# MAGIC   } else {
# MAGIC     val azureRegion = getAzureRegion()
# MAGIC     spark.conf.set("com.databricks.training.region.name", azureRegion)
# MAGIC     initAzureDataSource(azureRegion)
# MAGIC   }
# MAGIC   
# MAGIC   val resultMsg = mountSource(fix, failFast, mountDir, source, extraConfigs)
# MAGIC   displayHTML(resultMsg)
# MAGIC }
# MAGIC 
# MAGIC def initAzureDataSource(azureRegion:String):(String,Map[String,String]) = {
# MAGIC   val mapping = getAzureMapping(azureRegion)
# MAGIC   val (source, config) = mapping
# MAGIC   val (sasEntity, sasToken) = config.head
# MAGIC 
# MAGIC   val datasource = "%s\t%s\t%s".format(source, sasEntity, sasToken)
# MAGIC   spark.conf.set("com.databricks.training.azure.datasource", datasource)
# MAGIC 
# MAGIC   return mapping
# MAGIC }
# MAGIC 
# MAGIC def mountSource(fix:Boolean, failFast:Boolean, mountDir:String, source:String, extraConfigs:Map[String,String]): String = {
# MAGIC   val mntSource = source.replace(awsAuth+"@", "")
# MAGIC 
# MAGIC   if (dbutils.fs.mounts().map(_.mountPoint).contains(mountDir)) {
# MAGIC     val mount = dbutils.fs.mounts().filter(_.mountPoint == mountDir).head
# MAGIC     if (mount.source == mntSource) {
# MAGIC       return s"""Datasets are already mounted to <b>$mountDir</b> from <b>$mntSource</b>"""
# MAGIC       
# MAGIC     } else if (failFast) {
# MAGIC       throw new IllegalStateException(s"Expected $mntSource but found ${mount.source}")
# MAGIC       
# MAGIC     } else if (fix) {
# MAGIC       println(s"Unmounting existing datasets ($mountDir from $mntSource)")
# MAGIC       dbutils.fs.unmount(mountDir)
# MAGIC       mountSource(fix, failFast, mountDir, source, extraConfigs)
# MAGIC 
# MAGIC     } else {
# MAGIC       return s"""<b style="color:red">Invalid Mounts!</b></br>
# MAGIC                       <ul>
# MAGIC                       <li>The training datasets you are using are from an unexpected source</li>
# MAGIC                       <li>Expected <b>$mntSource</b> but found <b>${mount.source}</b></li>
# MAGIC                       <li>Failure to address this issue may result in significant performance degradation. To address this issue:</li>
# MAGIC                       <ol>
# MAGIC                         <li>Insert a new cell after this one</li>
# MAGIC                         <li>In that new cell, run the command <code style="color:blue; font-weight:bold">%scala fixMounts()</code></li>
# MAGIC                         <li>Verify that the problem has been resolved.</li>
# MAGIC                       </ol>"""
# MAGIC     }
# MAGIC   } else {
# MAGIC     println(s"""Mounting datasets to $mountDir from $mntSource""")
# MAGIC     mount(source, extraConfigs, mountDir)
# MAGIC     return s"""Mounted datasets to <b>$mountDir</b> from <b>$mntSource<b>"""
# MAGIC   }
# MAGIC }
# MAGIC 
# MAGIC def fixMounts(): Unit = {
# MAGIC   autoMount(true)
# MAGIC }
# MAGIC 
# MAGIC autoMount(true)