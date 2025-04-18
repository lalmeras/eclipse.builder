
import pathlib
import subprocess
import tempfile

NFPM_YAML = """
name: {package_name}
arch: amd64
platform: linux
version: {package_version}
version_schema: none
section: default
maintainer: laurent.almeras@kobalt.fr
description: Eclipse IDE
vendor: Kobalt
homepage: https://eclipse.org
license: Apache 2.0
contents:
  - src: {package_content}
    dst: /data/opt/{package_basename}
    type: tree
  - src: /data/opt/{package_basename}/eclipse
    dst: /usr/bin/{package_basename}
    type: symlink
  - src: {desktop_file}
    dst: /usr/share/applications/{package_basename}.desktop
"""

NFPM_DESKTOP = """
[Desktop Entry]
Name={desktop_name}
Exec=env WEBKIT_DISABLE_COMPOSITING_MODE=1 /usr/bin/{package_basename} {desktop_vm} {desktop_vm_args}
Type=Application
Description={desktop_description}
Icon=/data/opt/{package_basename}/icon.xpm
"""


def build_package(package_name: str, content: str, spec: dict[str, str], target_dir: pathlib.Path, rpm: bool, deb: bool):
    packages = []
    deb and packages.append("deb")
    rpm and packages.append("rpm")
    with open(tempfile.mktemp(suffix=".yaml"), mode="w", encoding="utf-8") as desktop_file:
        desktop_file.write(NFPM_DESKTOP.format(
            desktop_name="Eclipse {0}".format(spec["version"]),
            desktop_description="Eclipse {0}".format(spec["version"]),
            package_basename=spec["basename"],
            desktop_vm=f"-vm {vm}" if (vm := _check_dict(spec, "desktop", "vm")) else "",
            desktop_vm_args=f"-vmargs {vm_args}" if (vm_args := _check_dict(spec, "desktop", "vm-args")) else ""
        ))
    for package in packages:
        command = ['nfpm', 'pkg']
        command.extend(["--packager", package])
        command.extend(["--target", str(target_dir)])
        with open(tempfile.mktemp(suffix=".yaml"), mode="w", encoding="utf-8") as config_file:
            config_file.write(NFPM_YAML.format(
                package_name=package_name,
                package_version=spec["version"],
                package_content=content,
                package_basename=spec["basename"],
                desktop_file=desktop_file.name
            ))
            command.extend(["-f", config_file.name])
        subprocess.check_call(command)

def _check_dict(dict, *keys):
    try:
        if len(keys) == 0:
            return None
        if len(keys) == 1:
            return dict[keys[0]]
        else:
            return _check_dict(dict[keys[0]], *keys[1:])
    except KeyError:
        return None
