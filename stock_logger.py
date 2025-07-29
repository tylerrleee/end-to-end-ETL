from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import logging
from pymongo import MongoClient

# Logging config

logging.basicConfig(
    level = logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s')
    # 
logger = logging.getLogger("KafkaStockLogger")

def initiate_spark_session():
    logger.info("Creating Spark Session ...")
    try:
        spark = SparkSession.builder \
        .appName("KafkaStockLogger")\
        .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0") \
        .getOrCreate()
        logger.info("Spark Session Created Successfully!")
        return spark
    except Exception as e:
        logger.error("Failed to create Spark session.")
        logger.error(e)
        raise None

def get_stock_schema():
    logger.info("Defining schema for stock data...")
    try:
        schema = StructType([
                    StructField("current_price", DoubleType(), True),
                    StructField("id", IntegerType(), True),
                    StructField("name", StringType(), True),
                    StructField("open", DoubleType(), True),
                    StructField("percent_change", DoubleType(), True),
                    StructField("symbol", StringType(), True),
                    StructField("timestamp", StringType(), True),
                    StructField("volume", DoubleType(), True)
        ])
        logger.info("Schema defined successfully.")
        return schema
    except Exception as e:
        logger.error("Failed to define schema.")
        logger.error(e)
        raise None

def consume_data(spark, schema):
    logger.info("Starting to consume data from Kafka...")
    try:
        raw_df = spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "broker:29092")\
            .option("subscribe", "stock-market-producer")\
            .option("startingOffsets", "earliest")\
            .load()
        parsed_array_df = raw_df.select(
                            from_json(
                                col("value").cast("string"), 
                                ArrayType(schema)).alias("data"))
        
        exploded_df = parsed_array_df.select(explode(col("data")).alias("stock"))
        df = exploded_df.select("stock.*")
        logger.info("Kafka stream configured successfully.")
        return df
    except Exception as e:
        logger.error("Failed to consume data from Kafka.")
        logger.error(e)
        raise None

def process_batch(df, epoch_id):
    if df.isEmpty():
        logger.info(f"[Epoch {epoch_id}] No data.")
        return None
    
    logger.info(f"[Epoch {epoch_id}] Processing {df.count()} rows.")
    # Convert dataframe to PySpark.Pandas, and then to MongoDB
    try:
        records = df.toPandas().to_dict("records")
        if records:
            client = MongoClient("mongodb://root:example@mongodb:27017")
            db = client["mydb"]
            collection = db["mycollection"]
            collection.insert_many(records)
            client.close()
            logger.info(f"[Epoch {epoch_id}] Successfully written to MongoDB")
    except Exception as e:
        logger.error(f"[Epoch {epoch_id}] MongoDB write failed: {e}")

def stream_main():
    logger.info("Initializing stream processing...")
    try:
        spark = initiate_spark_session()
        schema = get_stock_schema()
        df = consume_data(spark, schema)

        query = df.writeStream \
                .foreachBatch(process_batch) \
                .outputMode("append") \
                .start()
        
        logger.info("Streaming query started. Awaiting termination...")
        query.awaitTermination()
    except Exception as e:
        logger.error("Stream processing failed.")
        logger.error(e)

if __name__ == "__main__":
    stream_main() 