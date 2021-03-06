import os
import shutil
import sys
from time import strftime, gmtime

# in Python 2.x this is SocketServer
import socketserver

from fabric.api import *
from pelican.server import ComplexHTTPRequestHandler

# Local path configuration (can be absolute or relative to fabfile)
env.deploy_path = 'output'
env.theme_path = 'themes'
OUTPUT_PATH = env.deploy_path
THEME_PATH = env.theme_path

# Github Pages configuration
GH_USER_PAGE_URL = "sollago.github.io"
GH_USER_PAGE_PATH = "../{}".format(GH_USER_PAGE_URL)
GH_USER_PAGE_REPO = "https://github.com/sollago/{}.git".format(GH_USER_PAGE_URL)

# Port for `serve`
PORT = 8000


def clean():
    """Remove generated files"""
    if os.path.isdir(OUTPUT_PATH):
        shutil.rmtree(OUTPUT_PATH)
        os.makedirs(OUTPUT_PATH)


def build(config="pelicanconf"):
    """Build local version of site"""
    local('pelican -s {0}.py'.format(config))


def rebuild(config="pelicanconf"):
    """`clean` then `build`"""
    clean()
    build(config)


def regenerate():
    """Automatically regenerate site upon file modification"""
    local('pelican -r -s pelicanconf.py')


def serve():
    """Serve site at http://localhost:8000/"""
    os.chdir(env.deploy_path)

    class AddressReuseTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    server = AddressReuseTCPServer(('', PORT), ComplexHTTPRequestHandler)

    sys.stderr.write('Serving on port {0} ...\n'.format(PORT))
    server.serve_forever()


def reserve():
    """`build`, then `serve`"""
    build()
    serve()


def preview():
    """Build production version of site"""
    local('pelican -s publishconf.py')


def publish():
    rebuild(config="publishconf")
    current_dir = os.getcwd()
    if not os.path.isdir(GH_USER_PAGE_PATH):
        local('git clone {0} {1}'.format(
            GH_USER_PAGE_REPO, GH_USER_PAGE_PATH))
    os.chdir(GH_USER_PAGE_PATH)
    local('git checkout master')
    local('git pull origin master')
    local('rsync -a --delete {}/* .'.format(os.path.join(current_dir, OUTPUT_PATH)))
    local('git add .')
    commit_msg = "Publishing on " + strftime('%F %R:%S %Z', gmtime())
    local('git commit -m "{}"'.format(commit_msg))
    local("git push origin master")
    os.chdir(current_dir)
