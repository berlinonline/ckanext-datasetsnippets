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

# [item['display_name'] for item in items if item['active']]
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
