import sys,os
import numpy 
import pandas as pd
from sklearn.impute import KNNImputer
from sklearn.pipeline import Pipeline

from networksecurity.constant.training_pipeline import TARGET_COLUMN,DATA_TRANSFORMATION_IMPUTER_PARAMS,=
from networksecurity.entity.artifact_entity import (
    DataTransformationArtifact, 
    DataValidationArtifact
)
from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging
from networksecurity.entity.config_entity import DataTransformationConfig
from networksecurity.utils.main_utils.utils import save_numpy_array,save_object

class DataTransformation:
    def __init__(self,data_validation_atifact:DataValidationArtifact,
                 data_tranformation_config:DataTransformationConfig):
        try:
            self.data_validation_artifact:DataValidationArtifact=data_validation_atifact
            self.data_transformation_config:DataTransformationConfig=data_tranformation_config
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    
    @staticmethod
    def read_data(file_path)->pd.DataFrame:
        try:
            return pd.read_csv(file_path)   
        except Exception as e:
            raise NetworkSecurityException(e,sys)
    def initiate_data_transformation(self)->DataTransformationArtifact:
        logging.info("Entered initiate_data_tranformation method of DataTranformation class")
        try:
            logging.info("Starting data transformation")
            train_df=DataTransformation.read_data(self.data_validation_artifact.valid_train_file_path)
            test_df=DataTransformation.read_data(self.data_validation_artifact.valid_test_file_path)
            
        except Exception as e:
            raise NetworkSecurityException(e,sys)
        