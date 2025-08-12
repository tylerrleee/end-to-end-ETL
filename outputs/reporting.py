import os 
import psycopg2
import logging
from datetime import date
import pandas as pd

report_date = date.today()

#os.makedirs(output_directory, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger("DailyReportGenerator")

def connect_postgres():
    try:
        logger.info("Connecting to PostgreSQL...")
        conn = psycopg2.connect(
            dbname = "airflow",
            user = "airflow",
            password = "airflow",
            host = "postgres",
            port = "5432"
        )

    except Exception as e:
        logger.error("PostgreSQL connection failed.")
        logger.error(e)

def report_top_volume(report_date, cursor):
    logger.info("Starting top volume report...")
    try:
        query = """
            SELECT companies.name, companies.symbol, prices.volume
            FROM companies 
            JOIN prices ON companies.id = prices.company_id
            WHERE prices.date = %s
            ORDER BY prices.volume DESC
            LIMIT 5;
    """
        cursor.execute(query, (report_date, ))
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"Company: {row[0]}, Symbol: {row[1]}, Volume: {row[2]}")
        logger.info("Top volume report completed successfully")
    except Exception as e:
        logger.error("Top volume report failed.")
        logger.error(e)

def report_top_gainers(report_date, cursor):
    logger.info("Starting top gainers report...")
    try:
        query = """
            SELECT c.name, c.symbol,
                   ROUND(((p.close - p.open) / NULLIF(p.open, 0)) * 100, 2) AS pct_change
            FROM companies c
            JOIN prices p ON c.id = p.company_id
            WHERE p.date = %s
            ORDER BY pct_change DESC
            LIMIT 5;
        """
        cursor.execute(query, (report_date,))
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"Company: {row[0]}, Symbol: {row[1]}, Change: {row[2]}%")
        logger.info("Top gainers report completed successfully.")
    except Exception as e:
        logger.error("Top gainers report failed.")
        logger.error(e)


def report_avg_close_by_sector(report_date, cursor):
    logger.info("Starting average close by sector report...")
    try:
        query = """
            SELECT s.name AS sector, ROUND(AVG(p.close), 2) AS avg_close
            FROM prices p
            JOIN companies c ON c.id = p.company_id
            JOIN sectors s ON c.sector_id = s.id
            WHERE p.date = %s
            GROUP BY s.name
            ORDER BY avg_close DESC;
        """
        cursor.execute(query, (report_date,))
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"Sector: {row[0]}, Avg Close Price: {row[1]}")
        logger.info("Average close by sector report completed successfully.")
    except Exception as e:
        logger.error("Average close by sector report failed.")
        logger.error(e)


def report_total_volume_by_exchange(report_date, cursor):
    logger.info("Starting total volume by exchange report...")
    try:
        query = """
            SELECT e.name AS exchange, SUM(p.volume) AS total_volume
            FROM prices p
            JOIN companies c ON c.id = p.company_id
            JOIN exchanges e ON c.exchange_id = e.id
            WHERE p.date = %s
            GROUP BY e.name
            ORDER BY total_volume DESC;
        """
        cursor.execute(query, (report_date,))
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"Exchange: {row[0]}, Total Volume: {row[1]}")
        logger.info("Total volume by exchange report completed successfully.")
    except Exception as e:
        logger.error("Total volume by exchange report failed.")
        logger.error(e)


def report_top_losers(report_date, cursor):
    logger.info("Starting top losers report...")
    try:
        query = """
            SELECT c.name, c.symbol,
                   ROUND(((p.close - p.open) / NULLIF(p.open, 0)) * 100, 2) AS pct_change
            FROM companies c
            JOIN prices p ON c.id = p.company_id
            WHERE p.date = %s AND p.open > 0 AND p.close < p.open
            ORDER BY pct_change ASC
            LIMIT 5;
        """
        cursor.execute(query, (report_date,))
        rows = cursor.fetchall()
        for row in rows:
            logger.info(f"Company: {row[0]}, Symbol: {row[1]}, Change: {row[2]}%")
        logger.info("Top losers report completed successfully.")
    except Exception as e:
        logger.error("Top losers report failed.")
        logger.error(e)
        
def write_to_csv(filename, data):
    try:
        df = pd.DataFrame(data)
        df.to_csv(filename, index=False)
        logger.info(f"Data written to {filename} successfully using pandas.")
    except Exception as e:
        logger.error(f"Failed to write data to {filename}: {e}")


##
output_directory = "/airflow/outputs"

def generate_daily_report():
    cursor, conn = connect_postgres()
    try:
        top_volume_companies  = report_top_volume(report_date, cursor)
        write_to_csv(os.path.join(output_directory, f"top_volume_companies{report_date}.csv"), top_volume_companies)
        
        top_gainer_companies = report_top_gainers(report_date, cursor)
        write_to_csv(os.path.join(output_directory, f"top_gainer_companies{report_date}.csv"), top_gainer_companies)
        
        avg_close_by_sector = report_avg_close_by_sector(report_date, cursor)
        write_to_csv(os.path.join(output_directory, f"avg_close_by_sector{report_date}.csv"), avg_close_by_sector)

        total_volume_by_exchange = report_total_volume_by_exchange(report_date, cursor)
        write_to_csv(os.path.join(output_directory, f"total_volume_by_exchange{report_date}.csv"), total_volume_by_exchange)
        
        top_loser_companies = report_top_losers(report_date, cursor)
        write_to_csv(os.path.join(output_directory, f"top_loser_companies{report_date}.csv"), top_loser_companies)
        
        logger.info("All reports completed.")
    finally:
        conn.close()
        logger.info("PostgreSQL connection closed.")


if __name__ == "__main__":
    generate_daily_report()