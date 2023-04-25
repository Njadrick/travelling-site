from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import sys

import kanisa


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


setup(
    name='kanisa',
    version=kanisa.__version__,
    description="A Django app for managing Church websites.",
    long_description=open('README.md').read(),
    author='Dominic Rodger',
    author_email='internet@dominicrodger.com',
    url='http://github.com/dominicrodger/kanisa',
    license='BSD',
    packages=find_packages(exclude=["tests", "tests.*"]),
    include_package_data=True,
    install_requires=[
        "Django==1.7.10",
        "Pillow==2.8.1",
        "django-autoslug==1.7.1",
        "django-crispy-forms==1.4.0",
        "django-haystack==1.2.7",
        "django-mptt==0.7.4",
        "django-password-reset==0.7",
        "django-recurrence==1.1.0",
        "markdown==2.6.2",
        "mutagen==1.29",
        "sorl-thumbnail==12.2",
        "Whoosh==2.4.1",
    ],
    tests_require=(
        "pytest==2.7.1",
        "pytest-cov==1.8.1",
        "pytest-django==2.8.0",
        "factory-boy==2.5.2",
        "mock==1.0.1",
    ),
    cmdclass = {'test': PyTest},
)
