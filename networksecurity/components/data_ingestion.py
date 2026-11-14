from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.entity.config_entity import DataIngestionConfig
from networksecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys

import certifi
import numpy as np
import pandas as pd
import pymongo
from dotenv import load_dotenv
from sklearn.model_selection import train_test_split

from networksecurity.utils.security_config import resolve_mongo_db_url

load_dotenv()


class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc

    def export_collection_as_dataframe(self):
        """Read the configured MongoDB collection into a dataframe."""
        try:
            database_name = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            mongo_db_url = resolve_mongo_db_url()

            with pymongo.MongoClient(
                mongo_db_url, tlsCAFile=certifi.where()
            ) as mongo_client:
                collection = mongo_client[database_name][collection_name]
                dataframe = pd.DataFrame(list(collection.find()))

            logging.info(
                "Fetched MongoDB collection %s.%s with shape %s",
                database_name,
                collection_name,
                dataframe.shape,
            )
            if "_id" in dataframe.columns:
                dataframe = dataframe.drop(columns=["_id"])

            dataframe.replace({"na": np.nan}, inplace=True)
            return dataframe
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc

    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            directory_path = os.path.dirname(feature_store_file_path)
            os.makedirs(directory_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)
            return dataframe
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc

    def split_data_as_train_test(self, dataframe: pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio
            )
            logging.info("Performed train test split on the dataframe")
            logging.info("Exited split_data_as_train_test method of Data_Ingestion class")

            directory_path = os.path.dirname(
                self.data_ingestion_config.training_file_path
            )
            os.makedirs(directory_path, exist_ok=True)

            logging.info("Exporting train and test file path.")
            train_set.to_csv(
                self.data_ingestion_config.training_file_path,
                index=False,
                header=True,
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path,
                index=False,
                header=True,
            )
            logging.info("Exported train and test file path.")
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc

    def initiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe)
            self.split_data_as_train_test(dataframe)

            return DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path,
            )
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc
