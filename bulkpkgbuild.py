#!/usr/bin/python3

import os
import sys
import csv
import subprocess
import numpy as np

class Packages:

    git_dir = ''
    pkg_dir = ''
    pkg_urls = []
    pkg_names = []

    def __init__(self, pkgs_file_path):
        self.pkg_names, self.pkg_urls = self._process_csv(pkgs_file_path)

    def build_packages(self):
        self._download()
        self._build()
        self._collect_packages()

    def _download(self):
        self.git_dir = os.path.join(os.getcwd(), 'pkgbuild-repos')
        os.mkdir(self.git_dir)
        i = 0
        self.p = []
        for i, url in enumerate(self.pkg_urls):
            self.p.append(subprocess.Popen(args=['git', 'clone', url], cwd=self.git_dir))
            print(self.p[i].args)

    def _build(self):
        for i, pkg in enumerate(self.pkg_names):
            self.p[i].wait()
            self.p[i] = subprocess.Popen(args=['makepkg'], cwd=os.path.join(self.git_dir,pkg))
            print(self.p[i].args)

    def _collect_packages(self):
        self.pkg_dir = os.path.join(os.getcwd(), 'built-packages')
        os.mkdir(self.pkg_dir)
        failed_builds_error = []
        for i, pkg in enumerate(self.pkg_names):
            self.p[i].wait()
            if self.p[i].returncode > 0:
                failed_builds_error.append(pkg + ' build failed. Error code ' + self.p[i].returncode)
            self.p[i] = subprocess.Popen(args=['cp *.pkg.tar.zst ' + self.pkg_dir + '/'], shell=True, cwd=os.path.join(self.git_dir,pkg))
            print(self.p[i].args)
        print('Failed packages:')
        for failed_pkg in failed_builds_error:
            print(' ', failed_pkg)

    def _process_csv(self, pkgs_file_path):
        pkgs_file = open(pkgs_file_path)
        content = pkgs_file.read()
        pkg_names = []
        pkg_urls = []
        word = ''
        i = 0
        while i < len(content):
            if content[i] == ',':
                pkg_name = str(word)
                word = ''
                i += 1
                continue
            if content[i] == '\n':
                pkg_url = str(word)
                if pkg_url == 'AUR':
                    pkg_url = 'https://aur.archlinux.org/' + pkg_name + '.git'
                pkg_names.append(pkg_name)
                pkg_urls.append(pkg_url)
                word = ''
                i += 1
                continue
            word += content[i]
            i += 1
        return pkg_names, pkg_urls


def print_usage():
    print('Bulk Package Builder')
    print('usage: bulkpkgbuild PKGSFILEPATH')
    print('  -h, --help         print usage')

def handle_arguments():
    n = len(sys.argv)
    if n < 2:
        print_usage()
    if not os.path.exists(sys.argv[1]):
        print('File path ', sys.argv[1], ' does not exist. Aborting.')
        exit()
    return sys.argv[1]

if __name__=="__main__":
    pkgs_file_path = handle_arguments()
    pkg_obj = Packages(pkgs_file_path)
    pkg_obj.build_packages()
