import os

from setuptools import find_packages, setup

version = "2.6.348"

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, "README.md")) as f:
    README = f.read()


def load_requirements(filename):
    requirements = []
    with open(filename) as f:
        for resource in f.readlines():
            if not resource.startswith("git+"):
                requirements.append(resource.strip())
            else:
                res = resource.strip()
                egg = res.split("#egg=")[1]
                requirements.append("@".join([egg, res]))
    return requirements


requires = load_requirements("requirements.txt")
requires_tests = load_requirements("requirements-test.txt")
requires_dev = load_requirements("requirements-dev.txt")


entry_points = {
    "paste.app_factory": [
        "main = openprocurement.api.app:main",
    ],
    "paste.filter_app_factory": [
        "translogger = openprocurement.api.translogger:make_filter",
    ],
    "openprocurement.api.plugins": [
        "api = openprocurement.api.includeme:includeme",
        "tender.core = openprocurement.tender.core.includeme:includeme",
        "planning.api = openprocurement.planning.api.includeme:includeme",
        "contracting.core = openprocurement.contracting.core.includeme:includeme",
        "historical.core = openprocurement.historical.core.includeme:includeme",
        "relocation.api = openprocurement.relocation.api.includeme:includeme",
        "framework.core = openprocurement.framework.core.includeme:includeme",
    ],
    "openprocurement.tender.core.plugins": [
        "tender.belowthreshold = openprocurement.tender.belowthreshold.includeme:includeme",
        "tender.open = openprocurement.tender.open.includeme:includeme",
        "tender.openua = openprocurement.tender.openua.includeme:includeme",
        "tender.openeu = openprocurement.tender.openeu.includeme:includeme",
        "tender.openuadefense = openprocurement.tender.openuadefense.includeme:includeme",
        "tender.limited.reporting = openprocurement.tender.limited.includeme:includeme",
        "tender.limited.negotiation = openprocurement.tender.limited.includeme:includeme_negotiation",
        "tender.limited.negotiation.quick = openprocurement.tender.limited.includeme:includeme_negotiation_quick",
        "tender.competitivedialogue = openprocurement.tender.competitivedialogue.includeme:includeme",
        "tender.esco = openprocurement.tender.esco.includeme:includeme",
        "tender.cfaua = openprocurement.tender.cfaua.includeme:includeme",
        "tender.cfaselectionua = openprocurement.tender.cfaselectionua.includeme:includeme",
        "tender.pricequotation = openprocurement.tender.pricequotation.includeme:includeme",
        "tender.simpledefense = openprocurement.tender.simpledefense.includeme:includeme",
    ],
    "openprocurement.historical.core.plugins": [
        "historical.tender = openprocurement.historical.tender.includeme:includeme",
    ],
    "openprocurement.framework.core.plugins": [
        "framework.electroniccatalogue = openprocurement.framework.electroniccatalogue.includeme:includeme",
        "framework.dps = openprocurement.framework.dps.includeme:includeme",
        "framework.cfaua = openprocurement.framework.cfaua.includeme:includeme",
    ],
    "openprocurement.contracting.core.plugins": [
        "contracting.econtract = openprocurement.contracting.econtract.includeme:includeme",
    ],
    "openprocurement.api.migrations": [
        "tenders = openprocurement.api.migration:migrate_data",
        "contracts = openprocurement.contracting.api.migration:migrate_data",
        "frameworks = openprocurement.framework.core.migration:migrate_data",
    ],
    "console_scripts": [
        "bootstrap_api_security = openprocurement.api.database:bootstrap_api_security",
    ],
}

setup(
    name="openprocurement.api",
    version=version,
    description="openprocurement.api",
    long_description=README,
    classifiers=[
        "Framework :: Pylons",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    keywords="web services",
    author="Quintagroup, Ltd.",
    author_email="info@quintagroup.com",
    license="Apache License 2.0",
    url="https://github.com/ProzorroUKR/openprocurement.api",
    package_dir={"": "src"},
    packages=find_packages("src"),
    namespace_packages=["openprocurement"],
    include_package_data=True,
    package_data={
        "": ["*.json", "*.ini"],
    },
    zip_safe=False,
    install_requires=requires,
    setup_requires=["pytest-runner"],
    tests_require=requires_tests,
    extras_require={
        "test": requires_tests,
        "dev": requires_dev,
    },
    entry_points=entry_points,
)
