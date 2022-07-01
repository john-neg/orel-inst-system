from setuptools import setup

setup(
    name='apeks-vuz-extension',
    version='1.0b0',
    long_description=__doc__,
    packages=['apeks-vuz-extension'],
    # package_data={
    #     'apeks-vuz-extension': ['requirements.txt'],
    # },
    include_package_data=True,
    zip_safe=False,
    install_requires=['Flask'],
)
