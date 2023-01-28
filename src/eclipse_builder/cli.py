# -*- coding: utf-8 -*-
"""Console script for eclipse_builder."""
from __future__ import print_function

import logging
import os
import pathlib
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
from . import nfpm


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


@click.group()
@click.option(
    '-v', '--verbose', count=True
)
def main(verbose):
    if verbose >= 1:
        cli_logger.setLevel(logging.INFO)
        cli_logger.info("using INFO logging level")


@main.command()
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
    '--rpm',
    is_flag=True,
    help='build rpm package',
    type=click.BOOL,
    default=False)
@click.option(
    '--deb',
    is_flag=True,
    help='build deb package',
    type=click.BOOL,
    default=False)
@click.argument(
    'specfile',
    type=click.File(mode='r', encoding='UTF-8'))
def eclipse(specfile, workdir: pathlib.Path, java_home, proxy_host, proxy_port,
        rpm: bool, deb: bool):
    """
    Console script for eclipse_builder.

    * SPECFILE is yml description of the release.
    """
    spec = _load_spec(specfile)
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
    if rpm or deb:
        cli_logger.info(u"packaging...")
        nfpm.build_package(target, spec, workdir, rpm, deb)


@main.command()
@click.option(
    '--content',
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, writable=True,
        readable=True, resolve_path=True
    ),
    help='Directory containing eclipse tree.')
@click.option(
    '--workdir',
    type=click.Path(
        exists=False, file_okay=False, dir_okay=True, writable=True,
        readable=True, resolve_path=True
    ),
    help='directory used to extract and manipulate built eclipse instance',
    default=os.getcwd())
@click.option(
    '--rpm',
    is_flag=True,
    help='build rpm package',
    type=click.BOOL,
    default=False)
@click.option(
    '--deb',
    is_flag=True,
    help='build deb package',
    type=click.BOOL,
    default=False)
@click.argument(
    'specfile',
    type=click.File(mode='r', encoding='UTF-8'))
def package(content, specfile, workdir, rpm, deb):
    spec = _load_spec(specfile)
    nfpm.build_package(content, spec, workdir, rpm, deb)


def _load_spec(specfile):
    try:
        cli_logger.info(u"using {} as specfile".format(specfile.name))
        return yaml.safe_load(specfile)
    except:
        cli_logger.critical(u"error loading specfile {}"
                                .format(specfile.name),
                            exc_info=True)
    finally:
        specfile.close()


if __name__ == "__main__":
    main()
