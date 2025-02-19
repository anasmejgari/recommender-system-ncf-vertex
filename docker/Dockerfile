FROM python:3.12

ARG LOCATION
ARG PROJECT
ARG REPOSITORY
ARG PACKAGE_NAME


RUN pip install keyring
RUN pip install keyrings.google-artifactregistry-auth

RUN --mount=type=secret,id=key_repo \ 
    pip download --extra-index-url https://_json_key_base64:$(cat /run/secrets/key_repo | base64 -w 0)@${LOCATION}-python.pkg.dev/${PROJECT}/${REPOSITORY}/simple/ PACKAGE_NAME