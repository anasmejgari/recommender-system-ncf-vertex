FROM python:3.12

ARG LOCATION
ARG PROJECT
ARG REPOSITORY
ARG PACKAGE_NAME


RUN pip install keyring
RUN pip install keyrings.google-artifactregistry-auth

RUN --mount=type=secret,id=key_repo,target=/run/secrets/credentials_gcp.json \ 
    GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/credentials_gcp.json \
    pip install --extra-index-url https://_json_key_base64:$(cat /run/secrets/credentials_gcp.json | base64 -w 0)@ ${LOCATION}-python.pkg.dev/${PROJECT}/${REPOSITORY}/simple/ ${PACKAGE_NAME}