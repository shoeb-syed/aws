import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from awsglue.dynamicframe import DynamicFrame
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import udf, array
from pyspark.sql.types import StringType
from pyspark.sql.functions import *

glueContext = GlueContext(SparkContext.getOrCreate())

args = getResolvedOptions(sys.argv, ['JOB_NAME', 'bucket', 'path', 'outputBucket'])
bucket = args['bucket']
csvPath = args['path']
outputBucket = args['outputBucket']

print(bucket, csvPath)

newFile = glueContext.create_dynamic_frame_from_options(
    "s3", {'paths': ["s3://" + bucket + "/" + csvPath]}, format= "csv", format_options = {'withHeader': True})

staticFile = glueContext.create_dynamic_frame_from_options(
    "s3", {'paths': ["s3://input-bucket-1611/names.csv"]}, format= "csv", format_options = {'withHeader': True})

sparkDF = Join.apply(staticFile, newFile, 'id', 'id').drop_fields(['id', 'sort_name'])

print("record count:  ", sparkDF.count())

sparkDF.toDF().repartition(1).write.parquet("s3://" + outputBucket + "/" + csvPath)

par = glueContext.create_dynamic_frame.from_options(connection_type = "parquet", connection_options = {"paths": ["s3://input-bucket-1611/outputPar.snappy.parquet"]})
par.printSchema()
