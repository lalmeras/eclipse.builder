# -*- coding: utf-8 -*-
"""Helpers to install preferences."""
from __future__ import print_function

import glob
import os
import shutil
import xml.etree.ElementTree as ET


def install_preferences(eclipse_home, conf_path, prefs):
    eclipse_ini_path = os.path.join(eclipse_home, 'eclipse.ini')
    with open(eclipse_ini_path, 'r') as eclipse_ini_file:
        eclipse_ini = eclipse_ini_file.readlines()
    product_line = False
    product = None
    for line in eclipse_ini:
        if line.strip() == '-product':
            product_line = True
            continue
        if product_line:
            product = line.strip()
            break
    if product is None:
        raise Exception('Eclipse product not found')
    if not product.endswith('.product'):
        raise Exception('Eclipse product does not end with .product')
    product_match = product[0:-len('.product')]
    plugins = ET.parse(os.path.join(eclipse_home, 'artifacts.xml'))
    products = plugins.findall("/artifacts/artifact[@id='{}']"
                               .format(product_match))
    import ipdb
    ipdb.set_trace()
    if not products:
        raise Exception('Product xml {} not found'.format(product_match))
    folder_match = '{}_{}'.format(product_match, products[0].get('version'))
    matches = glob.glob(os.path.join(eclipse_home, 'plugins', folder_match,
                                     'plugin_customization.ini'))
    if len(matches) != 1:
        raise Exception('Product folder {} not found'.format(product_match))
    match = matches[0]

    with open(match, 'a') as plugin_customization:
        for pref in prefs:
            pref_path = os.path.join(conf_path, pref)
            pref_matches = glob.glob(pref_path)
            for pref_match in pref_matches:
                if os.path.isfile(pref_match):
                    with open(pref_match, 'r') as pref_file:
                        shutil.copyfileobj(pref_file, plugin_customization)
                        plugin_customization.write('\n')
                    plugin_customization.flush()
                else:
                    print('{} not found, ignored'.format(pref_match))
