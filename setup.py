from setuptools import find_packages, setup

setup(
    name="automationassets",
    version="0.0.1",
    description="Enables the development and testing of Azure Automation python runbooks in an offline experience using the built-in Automation assets (variables, credentials, connections, and certificates).",
    url="https://azure.microsoft.com/en-us/services/automation/",
    author="Eamon O'Reilly @ Microsoft",
    license="MIT",

    packages=find_packages(),
    package_data={'automationassets' : ['localassets.json']},
    include_package_data=True,

    install_requires=[
        'pyopenssl',
    ],
    zipsafe=False,
)