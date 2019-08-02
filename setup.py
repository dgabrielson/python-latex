from setuptools import find_packages, setup


def read_requirements(filename="requirements.txt"):
    "Read the requirements"
    with open(filename) as f:
        return [line.strip() for line in f \
                if line.strip() and \
                line[0].strip() != '#' and \
                not line.startswith('-e ')]


def get_version(filename='latex/version.py', name='VERSION'):
    "Get the version"
    with open(filename) as f:
        s = f.read()
        d = {}
        exec(s, d)
        return d[name]



setup(
    name='python-latex',
    version='0.7.1',
    author='Dave Gabrielson',
    author_email='Dave@Gabrielson.CA',
    description='Some python code for dealing with LaTeX',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[],
)
