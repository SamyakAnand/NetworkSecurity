import os
import sys

from networksecurity.exception.exception import NetworkSecurityException
from networksecurity.logging.logger import logging

from networksecurity.components.data_ingestion import DataIngestion
from networksecurity.components.data_validation import DataValidation
from networksecurity.components.data_transformation import DataTransformation
from networksecurity.components.model_trainer import ModelTrainer

from networksecurity.entity.config_entity import (
    TrainingPipelineConfig,
    DataIngestionConfig,
    DataValidationConfig,
    DataTransformationConfig,
    ModelTrainerConfig,
)

from networksecurity.entity.artifact_entity import (
    DataIngestionArtifact,
    DataValidationArtifact,
    DataTransformationArtifact,
    ModelTrainerArtifact,
)

from networksecurity.constant.training_pipeline import TRAINING_BUCKET_NAME, SAVED_MODEL_DIR
from networksecurity.cloud.s3_syncer import S3Sync


class TrainingPipeline:
    def __init__(self):
        self.training_pipeline_config = TrainingPipelineConfig()
        self.s3_sync = S3Sync()

    def start_data_ingestion(self) -> DataIngestionArtifact:
        try:
            self.data_ingestion_config = DataIngestionConfig(training_pipeline_config=self.training_pipeline_config)
            logging.info("Starting Data Ingestion...")
            data_ingestion = DataIngestion(data_ingestion_config=self.data_ingestion_config)
            artifact = data_ingestion.initiate_data_ingestion()
            logging.info(f"Data Ingestion completed. Artifact: {artifact}")
            return artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_validation(self, data_ingestion_artifact: DataIngestionArtifact) -> DataValidationArtifact:
        try:
            config = DataValidationConfig(training_pipeline_config=self.training_pipeline_config)
            validation = DataValidation(data_ingestion_artifact=data_ingestion_artifact, data_validation_config=config)
            logging.info("Starting Data Validation...")
            return validation.initiate_data_validation()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_data_transformation(self, data_validation_artifact: DataValidationArtifact) -> DataTransformationArtifact:
        try:
            config = DataTransformationConfig(training_pipeline_config=self.training_pipeline_config)
            transformation = DataTransformation(data_validation_artifact=data_validation_artifact, data_transformation_config=config)
            logging.info("Starting Data Transformation...")
            return transformation.initiate_data_transformation()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def start_model_trainer(self, data_transformation_artifact: DataTransformationArtifact) -> ModelTrainerArtifact:
        try:
            config = ModelTrainerConfig(training_pipeline_config=self.training_pipeline_config)
            trainer = ModelTrainer(data_transformation_artifact=data_transformation_artifact, model_trainer_config=config)
            logging.info("Starting Model Training...")
            return trainer.initiate_model_trainer()
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def sync_artifact_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/artifact/{self.training_pipeline_config.timestamp}/"
            logging.info(f"Syncing local artifacts to S3: {aws_bucket_url}")
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.artifact_dir,
                aws_bucket_url=aws_bucket_url
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def sync_saved_model_dir_to_s3(self):
        try:
            aws_bucket_url = f"s3://{TRAINING_BUCKET_NAME}/final_model/{self.training_pipeline_config.timestamp}/"
            logging.info(f"Syncing saved model to S3: {aws_bucket_url}")
            self.s3_sync.sync_folder_to_s3(
                folder=self.training_pipeline_config.model_dir,
                aws_bucket_url=aws_bucket_url
            )
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def run_pipeline(self) -> ModelTrainerArtifact:
        try:
            logging.info("Training pipeline started.")
            ingestion_artifact = self.start_data_ingestion()
            validation_artifact = self.start_data_validation(ingestion_artifact)
            transformation_artifact = self.start_data_transformation(validation_artifact)
            trainer_artifact = self.start_model_trainer(transformation_artifact)

            self.sync_artifact_dir_to_s3()
            self.sync_saved_model_dir_to_s3()

            logging.info("Training pipeline completed successfully.")
            return trainer_artifact
        except Exception as e:
            raise NetworkSecurityException(e, sys)
