FROM python:3.12

ARG PROJECT_ID
ARG PACKAGE_NAME
ARG LOCATION
ARG REPO

RUN python -m pip install --upgrade pip
RUN pip install keyring
RUN pip install keyrings.google-artifactregistry-auth

RUN --mount=type=secret,id=key_repo,target=/run/secrets/credentials_gcp.json \ 
    GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/credentials_gcp.json \
    pip install --extra-index-url "https://${LOCATION}-python.pkg.dev/${PROJECT_ID}/${REPO}/simple/" ${PACKAGE_NAME}