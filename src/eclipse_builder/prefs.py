"""Helpers to install preferences."""

import glob
import os
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
import zipfile

GOOGLE_JAVA_FORMAT_OPENS = [
    "--add-exports=jdk.compiler/com.sun.tools.javac.api=ALL-UNNAMED",
    "--add-exports=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED",
    "--add-exports=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED",
    "--add-exports=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED",
    "--add-exports=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED",
    "--add-exports=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED"
]


def install_preferences(eclipse_home, conf_path, prefs):
    # open eclipse.ini to find product and perform modifications
    eclipse_ini_path = os.path.join(eclipse_home, 'eclipse.ini')
    with open(eclipse_ini_path) as eclipse_ini_file:
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
    products = plugins.findall(f"./artifacts/artifact[@id='{product_match}']")
    if not products:
        raise Exception(f'Product xml {product_match} not found')
    folder_match = '{}_{}'.format(product_match, products[0].get('version'))
    matches = glob.glob(os.path.join(eclipse_home, 'plugins', folder_match,
                                     'plugin_customization.ini'))
    if len(matches) != 1:
        raise Exception(f'Product folder {product_match} not found')
    match = matches[0]

    # add options needed by google-java-format plugin
    vmargs_index = eclipse_ini.index('-vmargs\n')
    if vmargs_index == -1:
        raise Exception("vmargs line not found in eclipse.ini")
    else:
        for opt in GOOGLE_JAVA_FORMAT_OPENS:
            eclipse_ini.insert(vmargs_index + 1, opt + "\n")

    # write back eclipse.ini
    with open(eclipse_ini_path, 'w', encoding="utf-8") as eclipse_ini_file:
        eclipse_ini_file.writelines(eclipse_ini)
        eclipse_ini_file.flush()

    with open(match, 'a') as plugin_customization:
        for pref in prefs:
            pref_path = os.path.join(conf_path, pref)
            pref_matches = glob.glob(pref_path)
            for pref_match in pref_matches:
                if os.path.isfile(pref_match):
                    with open(pref_match) as pref_file:
                        shutil.copyfileobj(pref_file, plugin_customization)
                        plugin_customization.write('\n')
                    plugin_customization.flush()
                else:
                    print(f'{pref_match} not found, ignored')

    jdt_core_jar = 'org.eclipse.jdt.core'
    jdt_core_jar_el = plugins.findall(f"./artifacts/artifact[@id='{jdt_core_jar}']")
    if not jdt_core_jar_el:
        print('jdt_core_jar not found')
        return
    jdt_pattern = '{}_{}.jar'.format(jdt_core_jar, jdt_core_jar_el[0].get('version'))
    jdt_matches = glob.glob(os.path.join(eclipse_home, 'plugins', jdt_pattern))
    if len(jdt_matches) != 1:
        print(f'{len(jdt_matches)} candidate(s) found for jdt core, aborting')
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
        tmp_plugin_xml.write(ET.tostring(root, encoding='unicode'))
    args = [
        'zip',
        '-j',
        jdt_matches[0],
        tmp_plugin_xml_file
    ]
    subprocess.check_call(args)
