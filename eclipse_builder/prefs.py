# -*- coding: utf-8 -*-
"""Helpers to install preferences."""
from __future__ import print_function

import glob
import os
import shutil
import subprocess
import tempfile
import lxml.etree as ET
import zipfile


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
    products = plugins.findall("./artifacts/artifact[@id='{}']"
                               .format(product_match))
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

    jdt_core_jar = 'org.eclipse.jdt.core'
    jdt_core_jar_el = plugins.findall("./artifacts/artifact[@id='{}']"
                                      .format(jdt_core_jar))
    if not jdt_core_jar_el:
        print('jdt_core_jar not found')
        return
    jdt_pattern = '{}_{}.jar'.format(jdt_core_jar, jdt_core_jar_el[0].get('version'))
    jdt_matches = glob.glob(os.path.join(eclipse_home, 'plugins', jdt_pattern))
    if len(jdt_matches) != 1:
        print('{} candidate(s) found for jdt core, aborting'.format(len(jdt_matches)))
        return
    with zipfile.ZipFile(jdt_matches[0], mode='r') as jar:
        plugin_xml_info = jar.getinfo('plugin.xml')
        plugin_xml = jar.read(plugin_xml_info)
    root = ET.fromstring(plugin_xml)
    modified = False
    for item in root.findall("./extension[@point='org.eclipse.core.contenttype.contentTypes']/content-type[@default-charset='ISO-8859-1']"):
        item.set('default-charset', 'UTF-8')
        modified = True
    if not modified:
        print("Content-type of Properties file cannot be updated")
    tmp_plugin_xml_path = tempfile.mkdtemp()
    tmp_plugin_xml_file = os.path.join(tmp_plugin_xml_path, 'plugin.xml')
    with open(tmp_plugin_xml_file, 'w') as tmp_plugin_xml:
        tmp_plugin_xml.write(ET.tostring(root, encoding='utf-8'))
    args = [
        'zip',
        '-j',
        jdt_matches[0],
        tmp_plugin_xml_file
    ]
    subprocess.check_call(args)
