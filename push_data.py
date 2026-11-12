import json
import os
import sys

import certifi
import pandas as pd
import pymongo
from dotenv import load_dotenv

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL") or os.getenv("MONGODB_URL_KEY")


class NetworkDataExtract:
    def __init__(self):
        pass

    def csv_to_json_convertor(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            return list(json.loads(data.T.to_json()).values())
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc

    def insert_data_mongodb(self, records, database, collection):
        try:
            if not MONGO_DB_URL:
                raise RuntimeError(
                    "Set MONGO_DB_URL before inserting data "
                    "(MONGODB_URL_KEY is accepted for backward compatibility)."
                )

            mongo_client = pymongo.MongoClient(
                MONGO_DB_URL, tlsCAFile=certifi.where()
            )
            target_database = mongo_client[database]
            target_collection = target_database[collection]
            target_collection.insert_many(records)
            return len(records)
        except Exception as exc:
            raise NetworkSecurityException(exc, sys) from exc


if __name__ == "__main__":
    file_path = "Network_Data/phisingData.csv"
    database = "SamAI"
    collection = "NetworkData"

    network_obj = NetworkDataExtract()
    records = network_obj.csv_to_json_convertor(file_path=file_path)
    inserted_count = network_obj.insert_data_mongodb(records, database, collection)
    print(f"Inserted {inserted_count} records into MongoDB.")
