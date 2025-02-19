FROM python:3.12

ARG LOCATION
ARG PROJECT
ARG REPOSITORY
ARG PACKAGE_NAME


RUN pip install keyring
RUN pip install keyrings.google-artifactregistry-auth

RUN --mount=type=secret,id=key_repo \ 
    pip install --extra-index-url https://_json_key:/run/secrets/key_repo@${LOCATION}-python.pkg.dev/${PROJECT}/${REPOSITORY}/simple/ PACKAGE_NAME