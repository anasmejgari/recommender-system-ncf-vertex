from kfp import compiler


from components.config import GCP_PROJECT_ID, REPO_REGION
from pipeline import rec_sys_pipeline


if __name__ == "__main__":
    pipeline_filename = "mlplatform_pipeline.json"
    compiler.Compiler().compile(
        pipeline_func=rec_sys_pipeline, package_path=pipeline_filename
    )

    from google.cloud import aiplatform

    aiplatform.init(project=GCP_PROJECT_ID, location=REPO_REGION)
    aiplatform.PipelineJob(
        display_name="rec-sys-pipeline",
        template_path=pipeline_filename,
        parameter_values={
            "blob_ratings": "ratings.csv",
            "blob_movies": "movies.csv",
            "bucket_name": "recommander-system-input-1937",
            "model_name": "model",
            "image_serving": "europe-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-11:latest",
        },
        enable_caching=True,
    ).submit(
        service_account="artifact-writer@summer-reef-450313-k4.iam.gserviceaccount.com"
    )
