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

    @pytest.mark.parametrize('data', [
        {
            # this is what a WFS usually looks like: several resources, one of which has `'format': 'WFS'` and
            # `'internal_function': 'ap_endpoint'`
            'dataset_dict': {
                "resources": [
                    {
                        "format": "WFS",
                        "internal_function": "api_description",
                        "name": "Endpunkt-Beschreibung des WFS-Service",
                        "url": "https://gdi.berlin.de/services/wfs/baumbestand?REQUEST=GetCapabilities&SERVICE=wfs",
                    },
                    {
                        "format": "HTML",
                        "internal_function": "documentation",
                        "name": "Inhaltliche Beschreibung",
                        "url": "https://fbinter.stadt-berlin.de/fb_daten/beschreibung/sachdaten/baumbestand.html",
                    },
                    {
                        "format": "WFS",
                        "internal_function": "api_endpoint",
                        "name": "API-Endpunkt des WFS-Service",
                        "url": "https://gdi.berlin.de/services/wfs/baumbestand",
                    },
                    {
                        "format": "PDF",
                        "internal_function": "documentation",
                        "name": "Technische Beschreibung",
                        "url": "https://fbinter.stadt-berlin.de/fb_daten/beschreibung/datenformatbeschreibung/Datenformatbeschreibung_Baeume.pdf",
                    }
                ]
            } ,
            'expected': 'https://gdi.berlin.de/services/wfs/baumbestand'
        } ,
        {
            # a WMS is not a WFS
            'dataset_dict': {
                'resources': [
                    {
                        'format': 'wms',
                        'internal_function': 'api_endpoint',
                        'url': 'https://gdi.berlin.de/services/wms/ua_einwohnerdichte_2023'
                    }
                ]
            } ,
            'expected': None
        } ,
        {
            # it's a WFS, but doesn't seem to have an endpoint
            'dataset_dict': {
                'resources': [
                    {
                        'format': 'wfs',
                        "name": "Endpunkt-Beschreibung des WFS-Service",
                        'internal_function': 'api_description',
                        "url": "https://gdi.berlin.de/services/wfs/baumbestand?REQUEST=GetCapabilities&SERVICE=wfs",
                    }
                ]
            } ,
            'expected': None
        } ,
        {
            # just one WFS resource
            'dataset_dict': {
                "resources": [
                    {
                        "format": "wfs",
                        "internal_function": "api_endpoint",
                        "name": "API-Endpunkt des WFS-Service",
                        "url": "https://gdi.berlin.de/services/wfs/parkraumbewirtschaftung",
                    },
                ]
            } ,
            'expected': 'https://gdi.berlin.de/services/wfs/parkraumbewirtschaftung'
        } ,
        {
            # no resources, so not a WFS
            'dataset_dict': {
                'resources': [
                ]
            } ,
            'expected': None
        } ,
    ])
    def test_wfs_endpoint_for_dataset(self, data: dict):
        '''Test to see if the correct values is returned.'''
        assert dshelpers.wfs_endpoint_for_dataset(data['dataset_dict']) == data['expected']

    @pytest.mark.parametrize('data', [
        {
            # a typical orgchart dataset: tag `_organigramm` and a JSON resource
            'dataset_dict': {
                'tags': [
                    {'name': 'organigramm'},
                    {'name': '_organigramm'},
                ],
                'resources': [
                    {
                        'format': 'PDF',
                        'name': 'Beschreibung',
                        'url': 'https://example.org/orgchart.pdf',
                    },
                    {
                        'format': 'JSON',
                        'name': 'Organigramm-Daten',
                        'url': 'https://example.org/orgchart.json',
                    },
                ],
            },
            'expected': 'https://example.org/orgchart.json',
        },
        {
            # tag `_organigramm` missing, even though there is a JSON resource
            'dataset_dict': {
                'tags': [
                    {'name': 'organigramm'},
                ],
                'resources': [
                    {
                        'format': 'JSON',
                        'name': 'Organigramm-Daten',
                        'url': 'https://example.org/orgchart.json',
                    },
                ],
            },
            'expected': None,
        },
        {
            # tag `_organigramm` is present, but no JSON resource
            'dataset_dict': {
                'tags': [
                    {'name': '_organigramm'},
                ],
                'resources': [
                    {
                        'format': 'PDF',
                        'name': 'Beschreibung',
                        'url': 'https://example.org/orgchart.pdf',
                    },
                ],
            },
            'expected': None,
        },
        {
            # tag `_organigramm` is present, JSON resource is present but
            # has no URL
            'dataset_dict': {
                'tags': [
                    {'name': '_organigramm'},
                ],
                'resources': [
                    {
                        'format': 'JSON',
                        'name': 'Organigramm-Daten',
                    },
                ],
            },
            'expected': None,
        },
        {
            # lowercase `json` should still match
            'dataset_dict': {
                'tags': [
                    {'name': '_organigramm'},
                ],
                'resources': [
                    {
                        'format': 'json',
                        'name': 'Organigramm-Daten',
                        'url': 'https://example.org/orgchart.json',
                    },
                ],
            },
            'expected': 'https://example.org/orgchart.json',
        },
        {
            # no tags at all, no resources
            'dataset_dict': {
                'tags': [],
                'resources': [],
            },
            'expected': None,
        },
    ])
    def test_orgchart_endpoint_for_dataset(self, data: dict):
        '''Test to see if the correct values is returned for orgchart datasets.'''
        assert dshelpers.orgchart_endpoint_for_dataset(data['dataset_dict']) == data['expected']
