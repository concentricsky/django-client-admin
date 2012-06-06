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
