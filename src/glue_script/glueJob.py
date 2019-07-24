import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from pyspark.sql import SQLContext
from awsglue.job import Job
from pyspark.sql.functions import udf, array
from pyspark.sql.types import StringType
from pyspark.sql.functions import *

glueContext = GlueContext(SparkContext.getOrCreate())
spark_session = glueContext.spark_session
sqlContext = SQLContext(spark_session.sparkContext, spark_session)

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'bucket', 'path', 'outputBucket', 'staticCSVPath'])
bucket = args['bucket']
csvPath = args['path']
outputBucket = args['outputBucket']
staticCSVPath = args['staticCSVPath']

print(bucket, csvPath)

newFile = glueContext.create_dynamic_frame_from_options(
    "s3", {'paths': ["s3://" + bucket + "/" + csvPath]}, format= "csv", format_options = {'withHeader': True}).drop_fields(['name']).toDF()

staticFile = glueContext.create_dynamic_frame_from_options(
    "s3", {'paths': [staticCSVPath]}, format= "csv", format_options = {'withHeader': True}).toDF()

newFile.registerTempTable("newCSV")
staticFile.registerTempTable("staticCSV")

sparkDF = sqlContext.sql('select t.name, q.* from newCSV q inner join staticCSV t on t.id = q.id')

# sparkDF1 = newFile.join(staticFile, "id")
# sparkDF2 = Join.apply(staticFile, newFile, 'id', 'id').drop_fields(['.id'])

print("record count:  ", sparkDF.count())

sparkDF.repartition(1).write.parquet("s3://" + outputBucket + "/" + csvPath)

par = glueContext.create_dynamic_frame.from_options(connection_type = "parquet", connection_options = {"paths": ["s3://input-bucket-1611/outputPar.snappy.parquet"]})
par.printSchema()
