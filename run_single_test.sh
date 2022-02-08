#! /bin/bash

export CKAN_INI="/usr/lib/ckan/default/src/ckan/test-core.ini"

# delete .pyc-files to prevent the "import file mismatch" errors
find -name "*.pyc" -delete
coverage run --source=ckanext.datasetsnippets -m pytest -vv --log-cli-level=10 ckanext/datasetsnippets/tests -k "$1" && coverage html
