#!/usr/bin/env python3

from sys import stdout
from pathlib import Path

import argparse
import os
import sys
import re
import urllib.request
import shutil
import json
import stat

install_dir = sys.argv[1]
tools_dir = sys.argv[2]
ccloud_launcher = "ccloud-client"
alias = 'ccloud'
auth_url = 'https://api.cloud.catalyst.net.nz:5000/v3'
config_file = ".config/ccloud-client/config.json"
tools_dir = 'ccloud_client'
dockerlink = 'https://docs.docker.com/engine/install/'+

script_text = '''#!/usr/bin/env python3

from sys import stdout
from pathlib import Path

import argparse
import os
import sys
import re
import urllib.request
import shutil
import signal
import time
import json
import stat

# install_dir = sys.argv[1]
# tools_dir = sys.argv[2]$
ccloud_launcher = "ccloud-client"
alias = 'ccloud'
auth_url = 'https://api.cloud.catalyst.net.nz:5000/v3'
config_file = ".config/ccloud-client/config.json"
tools_dir = 'ccloud_client'

openrcfile = False
localenv = False
mode = ''
filepath = '.openrc'
fileregex = '*-openrc.sh'
extraargs = ''
docker_tag = ''
dockerimage = "catalystcloud/ccloud-client_container"
os_identity_api_version = '3'
os_auth_url = ''


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def parse_args():
    parser = argparse.ArgumentParser(
        description='RT client for generating Support SLA details')
    parser.add_argument('-s', '--shell', help='drop to container shell', action='store_true')
    parser.add_argument('-v', '--version', type=str, help='ccloud container version')
    parser.add_argument('commands', nargs='*')
    args = parser.parse_args()
    return args


def terminateProcess(signalNumber, frame):
    print ('(SIGTERM) terminating the process')
    sys.exit()


def get_credentials():
    global localenv
    if os.getenv('OS_PROJECT_ID') and os.getenv('OS_TOKEN'):
        localenv = True
    else:
        msg = "No cloud authentication environment variables set, please source your openrc file"
        print(f"{bcolors.BOLD}{msg}{bcolors.ENDC}")
        sys.exit()


def get_config():
    p = Path(Path.home(), config_file)
    if Path.exists(p):
        with open(p, 'r') as json_file:
            data = json.load(json_file)
            install_dir = data['install-dir']
            auth_url = data['auth-url']
            alias= data['alias']
    else:
        print("No config file found,  re-run fetch-installer.sh")

    if auth_url:
        OS_AUTH_URL = auth_url


def run_container(args):
    global docker_tag
    global localenv
    # # check if cloud tools docker image exists, if not pull latest. If a tag is
    # # provided for a specific image version then pull that version

    cmd = f'docker images --filter "reference={dockerimage}:{docker_tag}" --format "{{.ID}}"'

    if docker_tag:
        imageid = os.system(cmd)
    else:
        docker_tag = 'latest'
        imageid = os.system(cmd)

    rc = ''
    cmd = f"docker pull {dockerimage}:{docker_tag}"
    if imageid and docker_tag:
        rc = os.system(cmd)

    if rc:
        print(f"Unable to retrieve {dockerimage}")

    if localenv:
        # if current shell has valid OS_* env variables set use them
        cmd = f"""docker run -it --rm \
        --security-opt=no-new-privileges \
        --cap-drop SETUID \
        -a stdin -a stdout -a stderr \
        --user={os.getuid()} \
        -v /etc/passwd:/etc/passwd:ro \
        -v /etc/group:/etc/group:ro \
        -v {Path.home()}:/mnt \
        -w /mnt \
        --env "LOCALENV"=True \
        --env "OS_REGION_NAME={os.environ['OS_REGION_NAME']}" \
        --env "OS_AUTH_TOKEN={os.environ['OS_AUTH_TOKEN']}" \
        --env "OS_AUTH_URL={os.environ['OS_AUTH_URL']}" \
        --env "OS_PROJECT_ID={os.environ['OS_PROJECT_ID']}" \
        --env "OS_AUTH_TYPE={os.environ['OS_AUTH_TYPE']}" \
        --env "OS_TOKEN={os.environ['OS_TOKEN']}" \
        --env "OS_IDENTITY_API_VERSION={os.environ['OS_IDENTITY_API_VERSION']}" \
        --hostname osclient-container {extraargs} {dockerimage} {' '.join(args.commands)}
        """
        os.system(cmd)

if __name__ == '__main__':

    # Handle ctrl-c (SIGINT)
    signal.signal(signal.SIGINT, terminateProcess)

    args = parse_args()
    get_credentials()
    get_config()
    run_container(args)
'''

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def usage():  # TODO: this can probably be removed in favour of argparse output

    scriptname = os.path.basename(__file__)

    usageMsg = '''This is a wrapper script to install the ccloud client
    '''
    print(f'    {scriptname}{usageMsg}')


def check_docker_exists():
    if shutil.which('docker') is None:
        msg = (
        "\n"
        f"{bcolors.BOLD}Docker{bcolors.ENDC} is not installed.\n"
        f"Please check out the following link to install docker: {dockerlink}"
        ""
        )
        print(msg)
        sys.exit()


def get_config():
    p = Path(Path.home(), config_file)
    if Path.exists(p):
        with open(p, 'r') as json_file:
            data = json.load(json_file)
            install_dir = data['install-dir']
            auth_url = data['auth-url']
            alias= data['alias']


def create_os_launcher():
    p = Path(install_dir, tools_dir)
    p.mkdir(parents=True, exist_ok=True)
    script_locn = f"{p}/{ccloud_launcher}"
    with open(script_locn, 'w') as fh:
        fh.write(script_text)
\s    os.chmod(script_locn, stat.S_IRWXU | stat.S_IRGRP | stat.S_IWGRP)
    return p


def update_alias(filename, alias, regex):
    tmp_file = f"{filename}.tmp"
    match = False
    with open(filename, 'rt') as fin:
        with open(tmp_file, 'wt') as fout:
            for line in fin:
                if regex.match(line):
                    line = regex.sub(alias, line)
                    match = True
                fout.write(line)
            if not match:
                line = alias
                fout.write(line)
    shutil.move(tmp_file, filename)


# def update_path(filename, regex, path_entry):

#     if not regex.match(os.environ['PATH']):
#         with open(filename, 'a') as fout:
#             line = f"export PATH=$PATH:{path_entry}"
#             fout.write(line)

def notify_user(alias):
    msg = f"{bcolors.OKGREEN} The alias {alias} was added to your .bashrc file.{bcolors.ENDC} \n"
    print(msg)

    msg = f'''{bcolors.OKGREEN} Please run \n source ${{HOME}}/.bashrc \n
              to make {alias} available from the command line.
              {bcolors.ENDC}'''
    print(msg)

if __name__ == '__main__':

    check_docker_exists()
    get_config()
    script_path = create_os_launcher()

    alias_regex = re.compile(f"^alias {alias}.*$")
    full_alias = f"alias {alias}='{script_path}/{ccloud_launcher}'\n"
    path_regex = re.compile(str(script_path))

    fp = Path(Path.home(), '.bashrc')

    if Path.exists(fp):
       update_alias(fp, full_alias, alias_regex)
    #    update_path(fp, path_regex, script_path)

    notify_user(alias)
