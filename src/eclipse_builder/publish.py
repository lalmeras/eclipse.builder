import os
import os.path
import pathlib
import requests
import requests.auth


def publish_package(spec: dict[str, str]):
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
    package = pathlib.Path("eclipse-{}.x86_64.rpm".format(spec["version"]))
    if not package.exists():
        raise Exception("File {} is missing", package)
    target = str(pathlib.Path(spec["repository"]["rpm"]) / os.path.basename(package))
    auth = requests.auth.HTTPBasicAuth(login, password)
    print("Pushing to {}".format(target))
    with open(package, mode = "rb") as f:
        requests.put(target, auth=auth, stream=f)
    