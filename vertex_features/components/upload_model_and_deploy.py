from kfp import dsl
from kfp.dsl import Model, Input

from .config import GCP_PROJECT_ID, REPO_REGION


@dsl.component(
    base_image="python:3.12", packages_to_install=["google-cloud-aiplatform"]
)
def deploy_model(
    model_name: str,
    model: Input[Model],
    serving_image: str = "python:3.12",
    project: str = GCP_PROJECT_ID,
    region: str = REPO_REGION,
):
    """
    Deploy the optimal model to a Vertex AI endpoint.
    """
    from google.cloud import aiplatform
    import logging

    aiplatform.init(project=project, location=region)

    model_name = "ncf-recsys"

    logging.info(f"Model URI: {model.uri}")

    model_upload = aiplatform.Model.upload(
        display_name=model_name,
        artifact_uri=model.uri.rpartition("/")[0],
        serving_container_image_uri=serving_image,
        serving_container_health_route=f"/v1/models/{model_name}",
        serving_container_predict_route=f"/v1/models/{model_name}:predict",
        serving_container_environment_variables={"MODEL_NAME": model_name},
    )

    logging.info(f"Model uploaded: {model_upload.resource_name}")

    endpoint = aiplatform.Endpoint.create(
        display_name=model_name, project=project, location=region
    )

    model_deployed = endpoint.deploy(
        model=model_upload,
        deployed_model_display_name=model_name,
        traffic_split={"0": 100},
        machine_type="n1-standard-4",
    )

    logging.info(f"Model deployed to endpoint: {endpoint.resource_name}")

    return (endpoint.resource_name,)
