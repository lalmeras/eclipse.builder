# eclipse.builder

Helpers to build custom Eclipse packages

* Free software: MIT license

## Build and run

```
sudo dnf install python3-build
sudo dnf install pipenv

# build only
python -m build

# run with pipenv
pipenv --rm
pipenv install
pipenv run eclipse-builder
```

## History

### 0.2.0 (2022-10-15)

* pep-517 / pep-660 build system

### 0.1.1 (2018-10-26)

* #1 Add epp.package.jee to PROTECTED_PACKAGES

### 0.1.0 (2017-10-24)

* First release on PyPI.
