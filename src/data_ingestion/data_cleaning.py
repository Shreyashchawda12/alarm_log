import pandas as pd
import os
import sys
from datetime import datetime
from src.exception import CustomException
from src.logger import logging
from dataclasses import dataclass

@dataclass
class DataIngestionconfig:
    raw_data_path: str = os.path.join('artifacts', 'Raw_data.xlsx')
    clean_data_path: str = os.path.join('artifacts', 'clean_data.xlsx')

class DataIngestion:
    def __init__(self):
        self.ingestion_config = DataIngestionconfig()

    def initiate_data_ingestion(self, operator: list = None, alarm: list = None,cluster:list = None):
        logging.info('Data Ingestion method starts')

        try:
            df = pd.read_excel(self.ingestion_config.raw_data_path, header=1)
            logging.info('Dataset read as pandas DataFrame')

            df['OpenTime'] = pd.to_datetime(df['OpenTime'], dayfirst=True)
            logging.info("Converted 'OpenTime' to datetime, specifying dayfirst=True")
            
            today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
            logging.info("Get today's date without time information")
            
            df_today = df[df['OpenTime'].dt.normalize() == today]
            logging.info("Filter rows where 'OpenTime' matches today's date")
            
            if cluster is None:
                cluster = ['Aurangabad', 'Nashik', 'Pune-1', 'Akola', 'Ahmednagar',
                            'Nagpur', 'Latur', 'Pune-3', 'Kolhapur', 'Pune-2', 'Goa',
                            'Solapur']
            
            df_today = df_today[df_today['Cluster'].isin(cluster)]
            
            if operator is None:
                operator = ['Airtel Dumps', 'RJIO', 'Vodafone Dumps', 'Mobile']
            
            df_today = df_today[df_today['SourceInput'].isin(operator)]
            df_today = df_today[df_today['ClearedDateTime'].isnull()]
            
            if alarm is None:
                alarm = ['DG on Load', 'Battery Discharge/Low battery', 'Mains Fail/EB Fail',
                         'SITE ON BATTERY', 'RU LOW VOLTAGE', '4G OUTAGE', '2G OUTAGE']
            df_today = df_today[df_today['EventName'].isin(alarm)]
            df_sorted = df_today.sort_values(by=['ClusterIncharge', 'ClusterEngineer'])
            
            drop_columns = ['Status', 'Severity', 'TTNumber', 'CustomerSiteId', 'CreatedUser', 'TTAgeing',
                            'Technician', 'Supervisor', 'COMH', 'EscaltionstatusLastupdateddt', 'SystemRCAService',
                            'EsclationStatus', 'ClearedDateTime', 'Circle', 'SiteClasification', 
                            'VNOCTTProcessTime', 'SourceInput']
            df_sorted = df_sorted.drop(drop_columns, axis=1)

            os.makedirs(os.path.dirname(self.ingestion_config.clean_data_path), exist_ok=True)
            df_sorted.to_excel(self.ingestion_config.clean_data_path, index=False, header=True)
            
            logging.info('Data cleaning completed')

            return self.ingestion_config.clean_data_path

        except Exception as e:
            logging.error('Exception occurred during data ingestion')
            raise CustomException(e, sys)
