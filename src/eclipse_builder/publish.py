import os
import os.path
import pathlib
import requests
import requests.auth
import urllib.parse


def publish_package(artifact: pathlib.Path, spec: dict[str, str]):
    if not spec.get("version", None):
        raise Exception("'version' setting is needed in release yaml file")
    if not spec.get("repository", None) \
            or not type(spec["repository"]) is dict \
            or not spec["repository"].get("rpm", None):
        raise Exception("'repository.rpm' setting is needed in release yaml file")
    try:
        login, password = [i for i in os.getenv("RPM_CREDENTIALS").split(":", 1)]
    except:
        raise Exception("Credentials cannot be extracted from RPM_CREDENTIALS")
    if not artifact.exists():
        raise Exception("File {} is missing", artifact)
    target = urllib.parse.urljoin(spec["repository"]["rpm"], os.path.basename(artifact))
    auth = requests.auth.HTTPBasicAuth(login, password)
    print("Pushing to {}".format(target))
    with open(artifact, mode = "rb") as f:
        requests.put(target, auth=auth, stream=f)
    