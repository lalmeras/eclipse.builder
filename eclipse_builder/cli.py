# -*- coding: utf-8 -*-
"""Console script for eclipse_builder."""
from __future__ import print_function

import os
import shutil
import tarfile
import tempfile

import click
import ruamel.yaml

from . import util
from . import feature
from . import prefs

@click.command()
@click.option('--workdir', type=click.Path(
    exists=False, file_okay=False, dir_okay=True, writable=True,
    readable=True, resolve_path=True
), default=os.getcwd())
@click.option('--java-home', type=click.Path(
    exists=True, file_okay=False, dir_okay=True, writable=False,
    readable=True, resolve_path=True), default=None)
@click.option('--proxy-host', type=click.STRING)
@click.option('--proxy-port', type=click.INT)
@click.argument('specfile', type=click.File(mode='r', encoding='UTF-8'))
def main(specfile, workdir, java_home, proxy_host, proxy_port):
    """Console script for eclipse_builder."""
    try:
        spec = ruamel.yaml.YAML(typ='safe').load(specfile)
    finally:
        specfile.close()
    archive = util.download(workdir, spec['url'])
    tar = tarfile.open(fileobj=archive)
    target = tempfile.mkdtemp(dir=workdir)
    try:
        util.extract(tar, target)
    finally:
        tar.close()
    configuration_folder = os.path.join(target, 'configuration')
    configuration_protect = os.listdir(configuration_folder)
    feature.install_features(target, spec['features'], spec['repositories'],
                             proxy_host=proxy_host, proxy_port=proxy_port,
                             java_home=java_home)
    prefs.install_preferences(target, os.path.dirname(specfile.name),
                              spec['prefs'])
    configuration_content = os.listdir(configuration_folder)
    for content_item in configuration_content:
        if content_item not in configuration_protect:
            item_path = os.path.join(configuration_folder, content_item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
        else:
            print('{} protected'.format(content_item))
    util.archive(target, spec['basename'], spec['filename'])


if __name__ == "__main__":
    main()
