import os
import pandas as pd
import sys
from datetime import datetime
from src.exception import CustomException
from src.logger import logging
from dataclasses import dataclass

@dataclass
class DataIngestionConfig:
    raw_data_path: str = os.path.join('artifacts', 'Raw_data.xlsx')
    clean_data_path: str = os.path.join('artifacts', 'clean_data.xlsx')

class DataIngestion:
    DEFAULT_CLUSTERS = ['Aurangabad', 'Nashik', 'Pune-1', 'Akola', 'Ahmednagar',
                        'Nagpur', 'Latur', 'Pune-3', 'Kolhapur', 'Pune-2', 'Goa', 'Solapur']
    DEFAULT_OPERATORS = ['Airtel Dumps', 'RJIO', 'Vodafone Dumps', 'Mobile']
    DEFAULT_ALARMS = ['DG on Load', 'Battery Discharge/Low battery', 'Mains Fail/EB Fail',
                      'SITE ON BATTERY', 'RU LOW VOLTAGE', '4G OUTAGE', '2G OUTAGE']
    DROP_COLUMNS = ['Status', 'Severity', 'TTNumber', 'CustomerSiteId', 'CreatedUser', 
                    'TTAgeing', 'Technician', 'Supervisor', 'COMH', 
                    'EscaltionstatusLastupdateddt', 'SystemRCAService', 
                    'EsclationStatus', 'ClearedDateTime', 'Circle', 
                    'SiteClasification', 'VNOCTTProcessTime', 'SourceInput']

    def __init__(self):
        self.ingestion_config = DataIngestionConfig()

    def initiate_data_ingestion(self, operator: list = None, alarm: list = None, cluster: list = None):
        logging.info('Data Ingestion method starts')

        try:
            # Check if raw data exists
            if not os.path.exists(self.ingestion_config.raw_data_path):
                raise FileNotFoundError(f"Raw data file not found at {self.ingestion_config.raw_data_path}")
            
            # Read raw data
            df = pd.read_excel(self.ingestion_config.raw_data_path, header=1)
            logging.info(f'Dataset read as pandas DataFrame with shape {df.shape}')

            # Convert 'OpenTime' to datetime and filter by today's date
            df['OpenTime'] = pd.to_datetime(df['OpenTime'], dayfirst=True)
            df_today = df[df['OpenTime'].dt.date == datetime.today().date()]
            logging.info(f'Filtered by today\'s date, resulting in {df_today.shape[0]} rows.')

            # Early exit if DataFrame is empty
            if df_today.empty:
                logging.warning("No data found for today's date.")
                return None

            # Apply cluster filter
            cluster = cluster or self.DEFAULT_CLUSTERS
            df_today = df_today[df_today['Cluster'].isin(cluster)]
            logging.info(f'Filtered by clusters, resulting in {df_today.shape[0]} rows.')

            if df_today.empty:
                logging.warning("No data found after filtering by clusters.")
                return None

            # Apply operator filter
            operator = operator or self.DEFAULT_OPERATORS
            df_today = df_today[df_today['SourceInput'].isin(operator)]
            logging.info(f'Filtered by operators, resulting in {df_today.shape[0]} rows.')

            if df_today.empty:
                logging.warning("No data found after filtering by operators.")
                return None

            # Keep only alarms that haven't been cleared
            df_today = df_today[df_today['ClearedDateTime'].isnull()]
            logging.info(f'Filtered by uncleared alarms, resulting in {df_today.shape[0]} rows.')

            if df_today.empty:
                logging.warning("No uncleared alarms found.")
                return None

            # Apply alarm filter
            alarm = alarm or self.DEFAULT_ALARMS
            df_today = df_today[df_today['EventName'].isin(alarm)]
            logging.info(f'Filtered by alarms, resulting in {df_today.shape[0]} rows.')

            if df_today.empty:
                logging.warning("No data found after filtering by alarms.")
                return None

            # Sort by 'ClusterIncharge' and 'ClusterEngineer'
            df_sorted = df_today.sort_values(by=['ClusterIncharge', 'ClusterEngineer'])
            logging.info(f'Data sorted, final shape: {df_sorted.shape}')

            # Drop unnecessary columns
            df_sorted = df_sorted.drop(columns=self.DROP_COLUMNS, errors='ignore')
            logging.info(f'Columns dropped, final DataFrame shape: {df_sorted.shape}')

            # Save the cleaned data
            os.makedirs(os.path.dirname(self.ingestion_config.clean_data_path), exist_ok=True)
            df_sorted.to_excel(self.ingestion_config.clean_data_path, index=False, header=True)
            logging.info(f'Data saved to {self.ingestion_config.clean_data_path}')

            return self.ingestion_config.clean_data_path

        except Exception as e:
            logging.error('Exception occurred during data ingestion', exc_info=True)
            raise CustomException(e, sys)
