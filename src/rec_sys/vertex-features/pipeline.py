from kfp.v2 import compiler
from kfp.v2.dsl import pipeline, component, Dataset, Input, Output
from datetime import datetime
from google.cloud import aiplatform
from typing import NamedTuple

# Ingest Data (BQ) ==> Model Training ==> Model Evaluation ==> Model Registry ==> Model Endpoint


@component
def gather_data(table_name: str, dataset_train: Output[Dataset]) -> None:
    import os

    from google.cloud import bigquery
    import pandas as pd

    project_id = os.getenv("GCP_PROJECT_ID")
    bq_dataset_name = os.getenv("BQ_DATASET_NAME")
    client = bigquery.Client(project=project_id)

    query = f"SELECT * FROM `{project_id}.{bq_dataset_name}.{table_name}`"
    rows = client.query_and_wait(query)
