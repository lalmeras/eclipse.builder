# -*- coding: utf-8 -*-
"""Console script for eclipse_builder."""
from __future__ import print_function

import logging
import os
import shutil
import tarfile
import tempfile
import sys

import click
import coloredlogs
import yaml

from . import util
from . import feature
from . import prefs


def bootstrap():
    logger_name = __package__
    logger = logging.getLogger(logger_name)
    stdout = logging.getLogger('.'.join(['stdout', logger_name]))
    raw = logging.getLogger('.'.join(['raw', logger_name]))
    logging.getLogger().addFilter(filter)
    logger_format = '*** %(name)s %(levelname)-7s %(message)s'
    stdout_format = '* %(levelname)-7s %(message)s'
    raw_format = '%(message)s'
    coloredlogs.install(level='DEBUG', logger=logger, fmt=logger_format)
    coloredlogs.install(level='DEBUG', logger=stdout, fmt=stdout_format)
    coloredlogs.install(level='DEBUG', logger=raw, fmt=raw_format)
    logger.setLevel(logging.WARN)
    stdout.setLevel(logging.INFO)
    raw.setLevel(logging.INFO)
    return logger, stdout, raw


(root_logger, cli_logger, raw_logger) = bootstrap()

@click.command()
@click.option(
    '--workdir',
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, writable=True,
        readable=True, resolve_path=True
    ),
    help='directory used to extract and manipulate built eclipse instance',
    default=os.getcwd())
@click.option(
    '--java-home',
    type=click.Path(
        exists=True, file_okay=False, dir_okay=True, writable=False,
        readable=True, resolve_path=True),
    help='java home used to launch eclipse',
    default=None)
@click.option(
    '--proxy-host',
    help='http proxy hostname',
    type=click.STRING,
    default=None)
@click.option(
    '--proxy-port',
    help='http proxy port',
    type=click.INT,
    default=None)
@click.option(
    '-v', '--verbose', count=True
)
@click.argument(
    'specfile',
    type=click.File(mode='r', encoding='UTF-8'))
def main(specfile, workdir, java_home, proxy_host, proxy_port, verbose):
    """
    Console script for eclipse_builder.

    * SPECFILE is yml description of the release.
    """
    if verbose >= 1:
        cli_logger.setLevel(logging.INFO)
        cli_logger.info("using INFO logging level")
    try:
        cli_logger.info(u"using {} as specfile".format(specfile.name))
        spec = yaml.safe_load(specfile)
    except:
        cli_logger.critical(u"error loading specfile {}"
                                .format(specfile.name),
                            exc_info=True)
    finally:
        specfile.close()
    cli_logger.info(u"downloading {}".format(spec['url']))
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
