#! /bin/env python
"""Plugin installed"""
from __future__ import print_function

import os.path
import subprocess


PROTECTED_FEATURES = set([
    'epp.package.java',
    'epp.package.rcp'
])


def install_features(eclipse_home, features, repositories, java_home=None,
                     proxy_host=None, proxy_port=3128):
    """Install features in an Eclipse instance"""
    vmargs = []
    vm = []
    if proxy_host:
        vmargs.extend([
            '-Dhttp.proxyHost=%s' % (proxy_host,),
            '-Dhttps.proxyHost=%s' % (proxy_host,)
        ])
        vmargs.extend([
            '-Dhttp.proxyPort=%s' % (proxy_port,),
            '-Dhttps.proxyPort=%s' % (proxy_port,)
        ])
    if java_home:
        vm.extend([
            '-vm', os.path.join(java_home, 'bin', 'java')
        ])
    # vmargs must be preceded by -vmargs
    if vmargs:
        vmargs.insert(0, '-vmargs')
    eclipse_bin = os.path.join(os.path.abspath(eclipse_home), 'eclipse')

    list_args = [
        eclipse_bin,
        '-noSplash', '-application', 'org.eclipse.equinox.p2.director',
        '-listInstalledRoots'
    ]
    list_args.extend(vm)
    list_args.extend(vmargs)
    installed_features = [
        line.split('/')[0]
        for line in subprocess.check_output(list_args).splitlines()
        if line
        and 'org.eclipse.m2e.logback.configuration' not in line
        and 'Operation completed' not in line
        and '/' in line
    ]
    print(installed_features)

    to_install_features = set()
    to_install_features = set([feature for feature in features])
    to_uninstall_features = set(installed_features) - PROTECTED_FEATURES
    to_install_features.update(to_uninstall_features)
    print("installing %s" % (' '.join(to_install_features),))
    print("uninstalling %s" % (' '.join(to_uninstall_features),))

    args = [
        eclipse_bin,
        '-nosplash', '-application', 'org.eclipse.equinox.p2.director',
        '-repository', ','.join(repositories),
        '-installIU', ','.join(to_install_features),
        '-uninstallIU', ','.join(to_uninstall_features)
    ]
    args.extend(vm)
    args.extend(vmargs)
    subprocess.check_call(args)

    clean_args = [
        eclipse_bin,
        '-nosplash', '-application',
        'org.eclipse.equinox.p2.garbagecollector.application',
    ]
    clean_args.extend(vm)
    clean_args.extend(vmargs)
    subprocess.check_call(clean_args)
