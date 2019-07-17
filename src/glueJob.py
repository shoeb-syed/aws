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

args = getResolvedOptions(sys.argv, ['JOB_NAME','path'])
csvPath = args['path']

print(args['JOB_NAME'], csvPath)
df = glueContext.create_dynamic_frame_from_options(
    "s3", {'paths': ["s3://input-bucket-1611/" + csvPath]}, format= "csv", format_options = {'withHeader': True})

func = udf(lambda x: x[1:] if x[0] == '-' else x, StringType())

sparkDF = df.toDF().drop('')
newSparkDF = sparkDF.withColumn('StartSegment', func("StartSegment"))
print("record count1:  ", newSparkDF.count())

df2 = newSparkDF.withColumnRenamed("StartSegment", "newStartSegment").withColumnRenamed("EndSegment", "StartSegment")
outputDF = newSparkDF.join(df2, ['StartSegment']).coalesce(1)

print("record count:  ", outputDF.count())

newdf = DynamicFrame.fromDF(outputDF, glueContext, "fromSparkDF")
newdf.printSchema()
glueContext.write_dynamic_frame.from_options(
       frame = newdf,
       connection_type = "s3",
       connection_options = {"path": "s3://output-bucket-1611/" + csvPath},
       format = "csv")
