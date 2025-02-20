FROM python:3.12

ARG LINK_REPO_PYTHON
ARG PACKAGE_NAME

RUN python -m pip install --upgrade pip

RUN pip install keyring
RUN pip install keyrings.google-artifactregistry-auth

RUN --mount=type=secret,id=key_repo,target=/run/secrets/credentials_gcp.json \ 
    GOOGLE_APPLICATION_CREDENTIALS=/run/secrets/credentials_gcp.json \
    pip install --extra-index-url https://_json:@${LINK_REPO_PYTHON} ${PACKAGE_NAME}