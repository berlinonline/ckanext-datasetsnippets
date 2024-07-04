# """Tests for resource_mappings.py."""

# import json
# import logging
# import pytest

# from flask import Flask

# import ckan.model as model
# from ckan.plugins.toolkit import config, url_for
# import ckan.tests.factories as factories
# import ckan.tests.helpers as test_helpers

# from ckanext.datasetsnippets.resource_mappings import ResourceMapping, MappingsError


# LOG = logging.getLogger(__name__)
# SNIPPET_PLUGIN = 'datasetsnippets'

# @pytest.mark.ckan_config('ckan.plugins', SNIPPET_PLUGIN)
# @pytest.mark.usefixtures('with_plugins')
# class TestResourceMappings(object):

#     @pytest.mark.parametrize("data", [
#         { "format_string": "zip:csv", "format": "CSV" },
#         { "format_string": ".csv", "format": "CSV" },
#         { "format_string": "XLSX", "format": "XLSX" },
#         { "format_string": "webseite", "format": "HTML" },
#         { "format_string": "GeoJSON", "format": "GEOJSON" },
#     ])
#     def test_reverse_format_mapping(self, data):
#         '''Sanity test that the mapping from concrete format strings to abstract formats
#            works.'''
#         mapping = ResourceMapping().format_string_format_mapping()
#         assert mapping[data['format_string']] == data['format']

#     @pytest.mark.parametrize("data", [
#         { "format_string": "zip:csv", "category": "Tabular Data" },
#         { "format_string": ".csv", "category": "Tabular Data" },
#         { "format_string": "XLSX", "category": "Tabular Data" },
#         { "format_string": "webseite", "category": "Website" },
#         { "format_string": "GeoJSON", "category": "GIS Data" },
#     ])
#     def test_reverse_category_mapping(self, data):
#         '''Sanity test that the mapping from concrete format strings to abstract categories
#            works.'''
#         mapping = ResourceMapping().format_string_category_mapping()
#         assert mapping[data['format_string']] == data['category']

# @pytest.mark.ckan_config('ckan.plugins', SNIPPET_PLUGIN)
# @pytest.mark.usefixtures('with_plugins')
# class TestResourceMappingErrors(object):

#     def test_unloaded_mapping_error_category_mapping(self):
#         '''Test that MappingsErrors are raised once the mapping has been unloaded.'''
#         ResourceMapping().unload_mappings()
#         with pytest.raises(MappingsError):
#             ResourceMapping().category_mapping()

#     def test_unloaded_mapping_error_format_string_format_mapping(self):
#         '''Test that MappingsErrors are raised once the mapping has been unloaded.'''
#         ResourceMapping().unload_mappings()
#         with pytest.raises(MappingsError):
#             ResourceMapping().format_string_format_mapping()

#     def test_unloaded_mapping_error_format_string_category_mapping(self):
#         '''Test that MappingsErrors are raised once the mapping has been unloaded.'''
#         ResourceMapping().unload_mappings()
#         with pytest.raises(MappingsError):
#             ResourceMapping().format_string_category_mapping()

#     def test_cannot_load_file(self):
#         '''Test that a MappingsError is raised if the mapping file cannot be loaded.'''
#         with pytest.raises(MappingsError):
#             ResourceMapping().load_mappings('non_existant_file.orc')