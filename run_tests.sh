#! /bin/bash

export CKAN_INI="/usr/lib/ckan/default/src/ckan/test-core.ini"

# delete .pyc-files to prevent the "import file mismatch" errors
find -name "*.pyc" -delete
coverage run --source=ckanext.datasetsnippets -m pytest ckanext/datasetsnippets/tests && coverage html
