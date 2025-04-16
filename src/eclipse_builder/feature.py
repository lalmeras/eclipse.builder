#! /bin/env python
"""Plugin installed"""

import os.path
import subprocess
import tempfile

# eclipse 2022-03: httpclient is verbose if logback is not set
LOGBACK_CONFIGURATION = """<configuration>

  <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">
    <!-- encoders are assigned the type
         ch.qos.logback.classic.encoder.PatternLayoutEncoder by default -->
    <encoder>
      <pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern>
    </encoder>
  </appender>

  <root level="warn">
    <appender-ref ref="STDOUT" />
  </root>
</configuration>
"""


def install_features(eclipse_home, features, uninstall_features,
                     repositories, java_home=None, proxy_host=None, proxy_port=3128):
    """Install features in an Eclipse instance"""
    with tempfile.NamedTemporaryFile('w', encoding='utf-8', delete=True, suffix='.xml') as logback:
        logback.write(LOGBACK_CONFIGURATION)
        logback.flush()
        _install_features(logback.name, eclipse_home, features, uninstall_features,
                          repositories, java_home, proxy_host, proxy_port)

def _install_features(logback_file, eclipse_home, features, uninstall_features,
                      repositories, java_home=None, proxy_host=None, proxy_port=3128):
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
    if logback_file:
        vmargs.append(f'-Dlogback.configurationFile={logback_file}')
    if java_home:
        vm.extend([
            '-vm', os.path.join(java_home, 'bin', 'java')
        ])
    # vmargs must be preceded by -vmargs
    if vmargs:
        vmargs.insert(0, '-vmargs')
    eclipse_bin = os.path.join(os.path.abspath(eclipse_home), 'eclipse')

    to_install_features = set([feature for feature in features])
    to_uninstall_features = set([feature for feature in uninstall_features])
    print("installing %s" % (' '.join(to_install_features),))

    args = [
        eclipse_bin,
        '-nosplash', '-application', 'org.eclipse.equinox.p2.director',
        '-repository', ','.join(repositories),
        '-installIU', ','.join(to_install_features)
    ]
    if to_uninstall_features:
        args.extend(["-uninstallIU", ','.join(to_uninstall_features)])
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
