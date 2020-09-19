import argparse
import logging
import os
import sys
from contextlib import contextmanager

import docker
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


DEFAULT_FILE='mgnt'
LOG_FILE=f'{DEFAULT_FILE}.log'
LOG_FORMAT = '%(asctime)-15s %(message)s'

logging.basicConfig(filename=LOG_FILE, filemode="a+", format=LOG_FORMAT)
PROG_NAME='docker-deployer'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
parser = argparse.ArgumentParser(
    # prog=PROG_NAME,
    description='Deploy docker stacks with docker comppose.')

parser.add_argument('-f', '--file', default=DEFAULT_FILE,
                    help=f'file for configuration search for {DEFAULT_FILE}.{{yml, yaml, json}}')

parser.add_argument('action', action='store', choices=['up', 'down', 'restart', 'stop'], metavar='action', help="wihi")

args = parser.parse_args()

action = args.action
if action == 'up':
    action = 'up -d'

input_path = args.file
if args.file==DEFAULT_FILE:
    inf = args.file
    if os.path.exists(f"{inf}.yml"):
        input_path = f"{inf}.yml"
    elif os.path.exists(f"{inf}.yaml"):
        input_path = f"{inf}.yaml"
    elif os.path.exists(f"{inf}.json"):
        input_path = f"{inf}.json"
    else:
        eprint("""ERROR: Can't find a suitable configuration file in this directory.
        Are you in the right directory?
        Supported filenames: mgnt.yml, mgnt.yaml, mgnt.json""")
        sys.exit(1)
    
elif not os.path.exists(input_path):
    eprint('ERROR: No such file : ', input_path)
    sys.exit(1)


config = yaml.load(open(input_path), Loader=Loader)
networks = []
client = docker.from_env()
nets = client.networks.list()

netsName = []
for net in nets:
    netsName.append(net.name)

for net in config.get('networks', []):
    if net['name'] not in netsName:
        logging.info('NETWORK Creating : ' + network.name)
        network = client.networks.create(**net)
        logging.info('NETWORK Created : ' +  network.name)


@contextmanager
def cd(directory):
    owd = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(owd)


for stack in config.get('stacks', []):
    if os.path.exists(stack['dir']):
        with cd(stack['dir']):
            logging.info("Starting : " + stack['dir'])
            print("Starting :", stack['dir'])
            cmd = "docker-compose "
            if 'file' in stack:
                cmd += f" -f {stack['file']}"

            if 'name' in stack:
                cmd += f" -p {stack['name']}"
            cmd += " " + action
            stream = os.popen(cmd)
            output = stream.read()
            print(output)
            logging.info(output)
            logging.info("Finished : ", stack['dir'])
    else:
        eprint("ERROR: No such directory :"+ stack['dir'])
        logging.error("No such directory : %s", stack['dir'])
