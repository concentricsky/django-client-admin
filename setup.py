# Copyright 2013 Concentric Sky, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages
import client_admin
import os


def find_package_data(**packages):
    package_data = {}
    for package_directory,top_dirs in packages.items():
        outfiles = []
        package_data[package_directory] = []
        for top_dir in top_dirs:
            for dirpath, dirnames, filenames in os.walk(os.path.join(package_directory,top_dir)):
                for filename in filenames:
                    path = os.path.join(dirpath, filename)[len(package_directory)+1:]
                    package_data[package_directory].append(path)
    return package_data


setup(
    name='django-client-admin',
    version=client_admin.VERSION,
    packages = find_packages(),
    package_data = find_package_data(client_admin=['static', 'templates']),

    author = 'Concentric Sky',
    author_email = 'django@concentricsky.com',
    description = 'Concentric Sky\'s client admin interface app',
)
