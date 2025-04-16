import os
import os.path
import pathlib
import urllib.parse

import requests
import requests.auth


def publish_package(artifact: pathlib.Path, spec: dict[str, str]):
    if not spec.get("version"):
        raise Exception("'version' setting is needed in release yaml file")
    if not spec.get("repository") \
            or type(spec["repository"]) is not dict \
            or not spec["repository"].get("rpm", None):
        raise Exception("'repository.rpm' setting is needed in release yaml file")
    try:
        login, password = (i for i in os.getenv("RPM_CREDENTIALS").split(":", 1))
    except:
        raise Exception("Credentials cannot be extracted from RPM_CREDENTIALS")
    if not artifact.exists():
        raise Exception("File {} is missing", artifact)
    target = urllib.parse.urljoin(spec["repository"]["rpm"], os.path.basename(artifact))
    length = os.stat(artifact).st_size
    auth = requests.auth.HTTPBasicAuth(login, password)
    print(f"Pushing to {target}")
    with open(artifact, mode = "rb") as f:
        response = requests.put(target, headers={"Content-Length": str(length)}, auth=auth, data=f)
        response.raise_for_status()

