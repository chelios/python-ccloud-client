#!/usr/bin/env python

from sys import stdout
from pathlib import Path

import argparse
import os
import stat
import urllib.request
import shutil
import json

alias = 'ccloud'
auth_url = 'https://api.cloud.catalyst.net.nz:5000/v3'
disable_prompts = False
install_dir = ''
tools_dir = 'ccloud_client'
config_dir = '.config/ccloud-client/'
config_file = 'config.json'
credentials_file = 'credentials'
scriptname = 'ccloud-client-install.py'
script_url = 'https://raw.githubusercontent.com/chelios/python-ccloud-client/master/ccloud-client-install.py'

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def usage():  # TODO: this can probably be removed in favour of argparse output

    scriptname = os.path.basename(__file__)

    usageMsg = ''' [ --disable-prompts ] [ --install-dir DIRECTORY ] [ --alias alias_NAME ] [ --url auth_url]'

    Installs the pre-built Catalyst Cloud Openstack command line tools container by downloading the setup script
    ($scriptname) into a directory of your choosing, and then runs this script to
    create an alias to allow easy launching of the tools container.

    -d, --disable-prompts
    Disables prompts. Prompts are always disabled when there is no controlling
    tty. Alternatively export CLOUDSDK_CORE_disable_prompts=1 before running
    the script.

    -i, --install-dir=DIRECTORY
    Sets the installation root directory to DIRECTORY. The launcher script will be
    installed in DIRECTORY/$tools_dir. The default location is \$HOME.

    -a, --alias
    The alias name to use for running openstack command via the containerised tools

    -u, --url
    The authentication URL of the OpenStack Cloud that you wish to connect to.
    '''

    print(f'    {scriptname}{usageMsg}')


def get_args():
    parser = argparse.ArgumentParser(
        description='Installer script for Catalyst Cloud \
        containerised OpenStack tools '
    )
    parser.add_argument(
        '-d',
        '--disable-prompts',
        action='store_true',
        help='Disable interactive prompts.',
    )
    parser.add_argument(
        '-i', '--install-dir', type=str, help='Directory to install CLI tool into.'
    )
    parser.add_argument(
        '-a', '--alias', type=str, help='local alias to use in place of openstack.'
    )
    parser.add_argument(
        '-u',
        '--url',
        type=str,
        help='Authentication URL for the cloud you wish to connect to.',
    )
    args = parser.parse_args()

    if args.disable_prompts:
        global disable_prompts
        disable_prompts = True

    return args


def check_tty():
    # If not running on a terminal, disable prompts
    if not stdout.isatty():
        global disable_prompts
        disable_prompts = True


def fetch_script(script_url, scriptname):
    # retrieve the installer script from Github
    try:
        with urllib.request.urlopen(script_url) as response:
            with open(scriptname, 'wb') as out_file:
                shutil.copyfileobj(response, out_file)
    except (urllib.error.HTTPError) as e:
        print(f'Problem retrieving script : error : {e}')
    except (FileNotFoundError) as e:
        print(f'Error writing script file : {e}')


def prompt_with_default(question, default):
    if not disable_prompts:
        response = input(f'{question} [{default}]: ')
        if not response:
            response = default
    else:
        # not running interactively so assign default to response
        response = default
    return response


def write_config(args):
    global alias
    global auth_url

    if args.alias:
        alias = args.alias
    if args.url:
        auth_url = args.url

    configDict = {'install-dir': install_dir,
                  'auth-url': auth_url,
                  'alias': alias
                 }

    try:
        p = Path(Path.home(), config_dir)
        p.mkdir(parents=True, exist_ok=True)
        with open(f'{p}/{config_file}', 'w+') as fh:
            json.dump(configDict, fh)
    except (PermissionError) as e:
        print(f'There was an error writing the file : {e}')


def install(args):
    global install_dir
    install_msg = (
        "This will install the launcher scripts in a subdirectory "
        f"called {bcolors.BOLD}{tools_dir}{bcolors.ENDC} \nin the installation "
        "directory selected below:\n"
        ""
    )

    homedir = str(Path.home())
    if not install_dir:
        print(install_msg)
        install_dir = prompt_with_default('select the installation directory', homedir)

    destdir = Path(install_dir, tools_dir)
    destdir.mkdir(parents=True, exist_ok=True)

    # copy script to local
    script_locn = f"{destdir}/{scriptname}"
    fetch_script(script_url, script_locn)
    os.chmod(script_locn, stat.S_IRWXU | stat.S_IRGRP | stat.S_IWGRP)

    # output required settings to config file, to be consumed by installer
    write_config(args)

    # run the launcher setup script
    print("Running launcher setup script...\n")
    cmd = f"{script_locn} {install_dir} {tools_dir}"
    os.system(cmd)


if __name__ == '__main__':
    args = get_args()
    install(args)
