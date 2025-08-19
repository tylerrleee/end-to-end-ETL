"""
Retrieve Stock Data From Polygon API

"""

from pyspark.sql import SparkSession
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, LongType

from pyspark.sql.functions import col, from_json
from polygon import RESTClient
from api_keys import POLYGON_API_KEY
import json
import logging
import requests
from datetime import datetime, timedelta
import time

logging.basicConfig(
    level=logging.INFO,
    format= '%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("KafkaStockProducer")

producer_params = {
    'kafka.bootstrap.servers': 'broker:29092',
    'topic': 'stock-market-producer'
}
url = "http://flask-api:5000/api/market"


def create_spark_session():
    APP_NAME = "KafkaProducerStreaming"
    SPARK_PACKAGE_TYPE = "spark.jars.packages"
    SPARK_PACKAGE_ID = "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0"
    spark = SparkSession.builder \
        .appName(APP_NAME) \
        .config(SPARK_PACKAGE_TYPE, SPARK_PACKAGE_ID) \
        .getOrCreate()
    return spark


def fetch_data():
    TICKER = "AAPL"
    FROM_DATE = (datetime.now() - timedelta(days=31)).strftime('%Y-%m-%d')
    TO_DATE = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    #if client.get_market_status():

    try:
        # check if market is open

        client = RESTClient(api_key=POLYGON_API_KEY)
        daily_ohcl_aggs = client.list_aggs(
            ticker=TICKER,
            multiplier= 1,
            from_=FROM_DATE,
            to=TO_DATE,
            timespan='day',
            adjusted='true',
            sort='desc'
        )
        messages = []
        count = 0
        for agg in daily_ohcl_aggs:
            count += 1
            msg = {
                "symbol": TICKER,
                "timestamp": agg.timestamp, # epoch in ms

                "datetime": time.strftime('%Y-%m-%d', time.gmtime(agg.timestamp / 1000)),
                "open": agg.open,
                "high": agg.high,
                "low": agg.low,
                "close": agg.close,
                "volume": agg.volume,
                "vwap": agg.vwap,
                "transactions": agg.transactions,
                "otc": agg.otc
                }
                # Serialize to JSON string; Kafka producers typically send bytes/strings
            messages.append(json.dumps(msg, separators=(",", ":"), allow_nan=False))
        if count == 0:
            logger.info(f"No data found for {TICKER} between {FROM_DATE} and {TO_DATE}")
        return messages
        
    except Exception as e:
        logger.error(f"Request error: {e}")
        print(f"Error: {e}")
        return None
    
def get_mock_data():
    mock = ['{"symbol":"AAPL","timestamp":1755230400000,"datetime":"2025-08-15","open":234,"high":234.28,"low":229.335,"close":231.59,"volume":56038657.0,"vwap":231.5464,"transactions":503028,"otc":null}', '{"symbol":"AAPL","timestamp":1755144000000,"datetime":"2025-08-14","open":234.055,"high":235.12,"low":230.85,"close":232.78,"volume":51916275.0,"vwap":232.7455,"transactions":558697,"otc":null}', '{"symbol":"AAPL","timestamp":1755057600000,"datetime":"2025-08-13","open":231.07,"high":235,"low":230.43,"close":233.33,"volume":69878546.0,"vwap":232.7762,"transactions":740719,"otc":null}', '{"symbol":"AAPL","timestamp":1754971200000,"datetime":"2025-08-12","open":228.005,"high":230.8,"low":227.07,"close":229.65,"volume":55672301.0,"vwap":229.3355,"transactions":561508,"otc":null}', '{"symbol":"AAPL","timestamp":1754884800000,"datetime":"2025-08-11","open":227.92,"high":229.56,"low":224.76,"close":227.18,"volume":61806132.0,"vwap":227.323,"transactions":692122,"otc":null}', '{"symbol":"AAPL","timestamp":1754625600000,"datetime":"2025-08-08","open":220.83,"high":231,"low":219.25,"close":229.35,"volume":113853967.0,"vwap":227.3071,"transactions":1135405,"otc":null}', '{"symbol":"AAPL","timestamp":1754539200000,"datetime":"2025-08-07","open":218.875,"high":220.85,"low":216.58,"close":220.03,"volume":90224834.0,"vwap":219.3267,"transactions":1007838,"otc":null}', '{"symbol":"AAPL","timestamp":1754452800000,"datetime":"2025-08-06","open":205.63,"high":215.38,"low":205.59,"close":213.25,"volume":108483103.0,"vwap":212.8573,"transactions":1104103,"otc":null}', '{"symbol":"AAPL","timestamp":1754366400000,"datetime":"2025-08-05","open":203.4,"high":205.34,"low":202.16,"close":202.92,"volume":44155079.0,"vwap":203.548,"transactions":491748,"otc":null}', '{"symbol":"AAPL","timestamp":1754280000000,"datetime":"2025-08-04","open":204.505,"high":207.88,"low":201.675,"close":203.35,"volume":75109298.0,"vwap":204.2151,"transactions":785189,"otc":null}', '{"symbol":"AAPL","timestamp":1754020800000,"datetime":"2025-08-01","open":210.865,"high":213.58,"low":201.5,"close":202.38,"volume":104434473.0,"vwap":204.507,"transactions":1201399,"otc":null}', '{"symbol":"AAPL","timestamp":1753934400000,"datetime":"2025-07-31","open":208.49,"high":209.84,"low":207.16,"close":207.57,"volume":80698431.0,"vwap":208.9948,"transactions":827514,"otc":null}', '{"symbol":"AAPL","timestamp":1753848000000,"datetime":"2025-07-30","open":211.895,"high":212.39,"low":207.72,"close":209.05,"volume":45512514.0,"vwap":209.5067,"transactions":542351,"otc":null}', '{"symbol":"AAPL","timestamp":1753761600000,"datetime":"2025-07-29","open":214.175,"high":214.81,"low":210.82,"close":211.27,"volume":51411723.0,"vwap":212.1244,"transactions":537963,"otc":null}', '{"symbol":"AAPL","timestamp":1753675200000,"datetime":"2025-07-28","open":214.03,"high":214.845,"low":213.06,"close":214.05,"volume":37858017.0,"vwap":214.04,"transactions":425354,"otc":null}', '{"symbol":"AAPL","timestamp":1753416000000,"datetime":"2025-07-25","open":214.7,"high":215.24,"low":213.4,"close":213.88,"volume":40268781.0,"vwap":214.1284,"transactions":409972,"otc":null}', '{"symbol":"AAPL","timestamp":1753329600000,"datetime":"2025-07-24","open":213.9,"high":215.69,"low":213.53,"close":213.76,"volume":46022620.0,"vwap":214.3924,"transactions":505013,"otc":null}', '{"symbol":"AAPL","timestamp":1753243200000,"datetime":"2025-07-23","open":215,"high":215.15,"low":212.41,"close":214.15,"volume":46989301.0,"vwap":213.7982,"transactions":497904,"otc":null}', '{"symbol":"AAPL","timestamp":1753156800000,"datetime":"2025-07-22","open":213.14,"high":214.95,"low":212.2301,"close":214.4,"volume":46404072.0,"vwap":213.6492,"transactions":549182,"otc":null}', '{"symbol":"AAPL","timestamp":1753070400000,"datetime":"2025-07-21","open":212.1,"high":215.78,"low":211.63,"close":212.48,"volume":51377434.0,"vwap":213.3495,"transactions":651657,"otc":null}', '{"symbol":"AAPL","timestamp":1752811200000,"datetime":"2025-07-18","open":210.87,"high":211.79,"low":209.7045,"close":211.18,"volume":48974591.0,"vwap":210.8567,"transactions":478858,"otc":null}']

schema = StructType([
    StructField("symbol", StringType()),
    StructField("timestamp", LongType()),
    StructField("datetime", StringType()),
    StructField("open", DoubleType()),
    StructField("high", DoubleType()),
    StructField("low", DoubleType()),
    StructField("close", DoubleType()),
    StructField("volume", DoubleType()),
    StructField("vwap", DoubleType()),
    StructField("transactions", LongType()),
    StructField("otc", StringType())
])

def create_spark_dataframe():
    #print('here')
    spark = create_spark_session()
    print('here')
    json_data = get_mock_data()
    df = spark.createDataFrame([(data,) for data in json_data], ['value'])
    df = df.withColumn(
            'json',
            from_json(col('value'), schema))
    df = df.select('json.*')
    df.show()
    print(df)



if __name__ == "__main__":
    create_spark_dataframe()