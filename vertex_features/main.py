import os

from google.cloud import aiplatform
from kfp import compiler


from components.config import (
    BUCKET_TRAINING_DATA,
    GCP_PROJECT_ID,
    REPO_REGION,
    SERVICE_ACCOUNT_VERTEX_PIPELINE,
)
from pipeline import rec_sys_pipeline


def main():
    pipeline_filename = "mlplatform_pipeline.json"
    compiler.Compiler().compile(
        pipeline_func=rec_sys_pipeline, package_path=pipeline_filename
    )

    aiplatform.init(project=GCP_PROJECT_ID, location=REPO_REGION)
    aiplatform.PipelineJob(
        display_name="rec-sys-pipeline",
        template_path=pipeline_filename,
        parameter_values={
            "blob_ratings": "ratings.csv",
            "blob_movies": "movies.csv",
            "bucket_name": BUCKET_TRAINING_DATA,
            "model_name": "model",
            "image_serving": "europe-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-11:latest",
        },
        enable_caching=True,
    ).submit(service_account=SERVICE_ACCOUNT_VERTEX_PIPELINE)


if __name__ == "__main__":
    main()
