from kfp import dsl
from kfp.dsl import Model, Input


@dsl.component(
    base_image="python:3.12", packages_to_install=["google-cloud-aiplatform"]
)
def deploy_model(
    model: Input[Model],
    project: str,
    region: str,
    serving_image: str,
) -> str:
    """Deploy the model to a Vertex AI endpoint."""
    from google.cloud import aiplatform
    import logging

    aiplatform.init(project=project, location=region)

    model_name = "ncf-recsys"

    logging.info(f"Model URI: {model.uri}")
    # Upload the model
    model_upload = aiplatform.Model.upload(
        display_name=model_name,
        artifact_uri=model.uri,
        serving_container_image_uri=serving_image,
        serving_container_health_route=f"/ping",
        serving_container_predict_route=f"/predictions/{model_name}",
        serving_container_environment_variables={"MODEL_NAME": model_name},
        serving_container_ports=[7080],
    )

    logging.info(f"Model uploaded: {model_upload.resource_name}")

    endpoint = aiplatform.Endpoint.create(
        display_name=model_name, project=project, location=region
    )
    # Deploy the model to endpoint
    endpoint.deploy(
        model=model_upload,
        deployed_model_display_name=model_name,
        traffic_percentage=100,
        sync=True,
        machine_type="n1-standard-4",
    )

    logging.info(f"Model deployed to endpoint: {endpoint.resource_name}")

    return str(endpoint.resource_name)
