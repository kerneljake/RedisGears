#!/usr/bin/env python

import os
import sys
import platform
import paella

os.environ["PYTHONWARNINGS"] = "ignore"

bb()
dist = platform.linux_distribution()
distname = dist[0].lower()
distver = dist[1]

#----------------------------------------------------------------------------------------------

def eprint(*args, **kwargs):
	print >> sys.stderr, ' '.join(map(lambda x: "%s" % x, args))

#----------------------------------------------------------------------------------------------

def run(cmd):
    rc = os.system(cmd)
    if rc > 0:
        eprint("failed to install " + cmd)
        sys.exit(1)

def has_command(cmd):
    return os.system("command -v " + cmd + " > /dev/null") == 0

#----------------------------------------------------------------------------------------------

def apt_install(packs):
    run("apt install -q -y " + packs)

def yum_install(packs, group=False):
    if not group:
        run("yum install -q -y " + packs)
    else:
        run("yum groupinstall -y " + packs)

def dnf_install(packs, group=False):
    if not group:
        run("dnf install -y " + packs)
    else:
        run("dnf groupinstall -y " + packs)

def zypper_install(packs):
    run("zipper --non-interactive install " + packs)

def pacman_install(packs):
    run("pacman --noconfirm -S " + packs)

def install(packs):
    if platform.system() == 'Linux':
        if distname == 'fedora':
            dnf_install(packs)
        elif distname == 'ubuntu' or distname == 'debian':
            apt_install(packs)
        elif distname == 'centos linux':
            yum_install(packs)
        elif distname == 'suse linux':
            zypper_install(packs)
        elif distname == 'arch':
            pacman_install(packs)
        else:
            Assert(False), "Cannot determine installer"
    elif platform.system() == 'Darwin':
        run('brew install -y ' + cmd)
    else:
        Assert(False), "Cannot determine installer"

#----------------------------------------------------------------------------------------------

def pip_install(cmd):
    run("pip install " + cmd)

def pip3_install(cmd):
    run("pip3 install " + cmd)

def install_pip():
    if not has_command("pip"):
        install("curl")
        get_pip = "set -e; cd /tmp; curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py"
        run(get_pip + "; python2 get-pip.py")
    if not has_command("pip3") and has_command("python3"):
        run(get_pip + "; python3 get-pip.py")

#----------------------------------------------------------------------------------------------

install_pip()
pip_install("wheel")
pip_install("setuptools --upgrade")

#----------------------------------------------------------------------------------------------

bb()
if platform.system() == 'Linux':
    if distname == 'fedora':
        dnf_install("'Development Tools'", group=True)
        dnf_install("autoconf automake libtool")
        dnf_install("zlib-devel openssl-devel readline-devel")
        # dnf_install("python3-pip")
        run("pip3 install pipenv")

    elif distname == 'ubuntu' or distname == 'debian':
        run("apt-get update -y")
        apt_install("build-essential autotools-dev autoconf libtool")
        apt_install("zlib1g-dev libssl-dev libreadline-dev")
        apt_install("lsb-release")
        apt_install("zip unzip")
        # apt_install("python3-pip")
        bb()
        pip3_install("pipenv")

    elif distname == 'centos linux':
        yum_install("'Development Tools'", group=True)
        yum_install("autoconf automake libtool")
        yum_install("zlib-devel openssl-devel readline-devel")
        yum_install("redhat-lsb-core")
        yum_install("vim-common") # for xxd
        yum_install("zip unzip")
        yum_install("python2-psutil") # otherwise subsequent python package installations fail
        # yum_install("python36-pip");
        # install("pip3.6 install --upgrade pip");
        pip_install("pipenv")

elif platform.system() == 'Darwin':
    pass

bb()
if not has_command("ramp"):
    pip_install("git+https://github.com/RedisLabs/RAMP --upgrade")
if not has_command("RLTest"):
    pip_install("git+https://github.com/RedisLabsModules/RLTest.git@master")
pip_install("redis-py-cluster")

