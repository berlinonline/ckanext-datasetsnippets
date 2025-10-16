"""Tests for plugin.py."""

import json
import logging
import pytest

from flask import Flask

from ckan.plugins.toolkit import url_for
import ckan.tests.factories as factories
import ckan.tests.helpers as test_helpers

import ckanext.datasetsnippets.helpers as dshelpers

LOG = logging.getLogger(__name__)
SNIPPET_PLUGIN = 'datasetsnippets'

@pytest.mark.ckan_config('ckan.plugins', f"{SNIPPET_PLUGIN}")
@pytest.mark.usefixtures('with_plugins', 'clean_db')
class TestHelpers(object):

    @pytest.mark.parametrize("data", [
        { "resource": 
            { "name": "Fancy Resource",
              "url": "http://some.domain.com/path/to/resource.json"
            },
          "label": "Fancy Resource"
        },
        { "resource":
            { "url": "http://some.domain.com/path/to/resource.json"
            },
          "label": "resource.json"
        },
        { "resource": {},
          "label": "Unbekannt"
        }
    ])
    def test_resource_label(self, data):
        '''Test that the resource labelling function works correctly based on different scenarios.'''
        user = factories.User()
        dataset = factories.Dataset(user=user)
        res_dict = test_helpers.call_action(
            "resource_create",
            context={"user": user["name"]},
            package_id=dataset["id"],
            **data['resource']
        )
        assert dshelpers.resource_label(res_dict) == data['label']

    @pytest.mark.parametrize("data", [
        {
            "base": "http://test.org/dataset",
            "params": None,
            "urlstring": "http://test.org/dataset"
        } ,
        {
            "base": "http://test.org/dataset",
            "params": {
               "name": "average_temperatures"
            },
            "urlstring": "http://test.org/dataset?name=average_temperatures"
        } ,
        {
            "base": "http://test.org/dataset",
            "params": {
               "category": "health",
               "source": "senweb"
            },
            "urlstring": "http://test.org/dataset?category=health&source=senweb"
        } ,
        {
            "base": "http://test.org/user",
            "params": {
                "name": "möller"
            },
            "urlstring": "http://test.org/user?name=m%C3%B6ller"
        } ,
    ])
    def test_url_param_helper(self, data):
        assert dshelpers.url_with_params(data['base'], data['params']) == data['urlstring']

    @pytest.mark.parametrize("data", [
        {
            'name': 'groups',
            'plural': 'Kategorien'
        },
        {
            'name': 'temporal_granularity',
            'plural': 'Zeitliche Granularitäten'
        },
    ])
    def test_plural_mapping(self, data):
        assert dshelpers.facet_plural_mapping()[data['name']] == data['plural']

    @pytest.mark.parametrize("data", [
        {
            "items": [
                {
                    "display_name": "foo",
                    "active": True
                },
                {
                    "display_name": "bar",
                    "active": False
                },
                {
                    "display_name": "baz",
                    "active": True
                },
            ],
            "expected": "foo, baz"
        },
        {
            "items": [
                {
                    "display_name": "foo",
                    "active": False
                },
                {
                    "display_name": "bar",
                    "active": False
                },
                {
                    "display_name": "baz",
                    "active": False
                },
            ],
            "expected": ""
        }
    ])
    def test_active_item_labels(self, data):
        assert dshelpers.active_item_labels(data['items']) == data['expected']

    @pytest.mark.parametrize("data", [
        {
            'resources': [
                {
                    "name": "res_1",
                    "format": "CSV"
                },
                {
                    "name": "res_2",
                    "format": ".csv"
                },
                {
                    "name": "res_3",
                    "format": "PDF"
                },
                {
                    "name": "res_4",
                    "format": "PDF"
                },
                {
                    "name": "res_5",
                    "format": "PDF"
                },
                {
                    "name": "res_6",
                    "format": "GeoJSON"
                },
                {
                    "name": "res_7",
                    "format": "XLS"
                },
            ],
            'formats': [ "CSV", "PDF", "GEOJSON", "XLSX" ]
        },
        {
            'resources': [
                {
                    "name": "res_1",
                    "format": ".foonknown"
                },
                {
                    "name": "res_2",
                    "format": "GTFS"
                },
                {
                    "name": "res_3",
                    "format": "JPEG"
                },
            ],
            'formats': [ "JPG", "GTFS", ".foonknown" ]
        },
    ])
    def test_unique_resource_formats(self, data: dict):
        '''Test that the concrete format strings in a list of resources are correctly
           boiled down to unique abstract formats.'''
        assert set(dshelpers.unique_resource_formats(data['resources'])) == set(data['formats'])

    @pytest.mark.parametrize("data", [
        { "format_string": "zip:csv", "category": "tabular" },
        { "format_string": ".csv", "category": "tabular" },
        { "format_string": "XLSX", "category": "tabular" },
        { "format_string": "webseite", "category": "website" },
        { "format_string": "GeoJSON", "category": "gis" },
    ])
    def test_format_code_for_format_string(self, data: dict):
        '''Sanity test to check that the correct category code is returned for a given
           format string.'''
        assert dshelpers.format_code_for_format_string(data['format_string']) == data['category']

    @pytest.mark.parametrize("data", [
        { "format_string": "zip:csv", "css_class": "dp-resource-tabular" },
        { "format_string": ".csv", "css_class": "dp-resource-tabular" },
        { "format_string": "XLSX", "css_class": "dp-resource-tabular" },
        { "format_string": "webseite", "css_class": "dp-resource-website" },
        { "format_string": "GeoJSON", "css_class": "dp-resource-gis" },
        { "format_string": ".foonknown", "css_class": "dp-resource-undefined" },
    ])
    def test_css_class_for_format_string(self, data: dict):
        '''Sanity test to check that the correct css class for a given format string is
           generated.'''
        assert dshelpers.css_class_for_format_string(data['format_string']) == data['css_class']

    @pytest.mark.parametrize("data", [
        { "value": "true", "expected": True },
        { "value": "True", "expected": True },
        { "value": "TRUE", "expected": True },
        { "value": "tRue", "expected": True },
        { "value": "whatever", "expected": False },
        { "value": 1, "expected": False },
        { "value": None, "expected": False },
    ])
    def test_truth_converter(self, data: dict):
        '''Test to see if values passed to is_true are correctly converted to a boolean.'''
        assert dshelpers.is_true(data['value']) is data['expected']