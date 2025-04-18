# eclipse.builder

Helpers to build custom Eclipse packages

* Free software: MIT license

## Build and run

```
pipx install hatch
hatch run eclipse-builder eclipse [RELEASE_FILE]

# build, rpm and publish on repository
# need 'version' in release file
# need 'repository.rpm' in release file
# need RPM_CREDENTIALS environment variable
hatch run eclipse-builder eclipse --rpm --publish [RELEASE_FILE]
```

## History

### 0.3.0 (2023-01-28)

* eclipse subcommand handle package generation
* eclipse subcommand supports `--rpm` and `--deb` flags to generate packages
  with nfpm (https://nfpm.goreleaser.com/)
* eclipse package command added to package an existing eclipse tree

### 0.2.0 (2022-10-15)

* pep-517 / pep-660 build system

### 0.1.1 (2018-10-26)

* #1 Add epp.package.jee to PROTECTED_PACKAGES

### 0.1.0 (2017-10-24)

* First release on PyPI.
