"""Tests for plugin.py."""

import json
import logging
import pytest

from flask import Flask

import ckan.model as model
from ckan.plugins.toolkit import url_for
import ckan.tests.factories as factories
import ckan.tests.helpers as test_helpers


LOG = logging.getLogger(__name__)
SCHEMA_PLUGIN = 'berlin_dataset_schema'
SNIPPET_PLUGIN = 'datasetsnippets'


@pytest.fixture
def user():
    '''Fixture to create a logged-in user.'''
    user = model.User(name="vera_musterer", password=u"testtest")
    model.Session.add(user)
    model.Session.commit()
    return user

@pytest.fixture
def datasets():
    '''Fixture to create some datasets.'''
    sysadminuser = model.User(name="admin", password=u'test', sysadmin=True)
    model.Session.add(sysadminuser)
    model.Session.commit()
    group = factories.Group()
    data = {
        "id": group['id'],
        "username": sysadminuser.name,
        "role": "editor"
    }
    result = test_helpers.call_action("group_member_create", **data)

    dataset_dicts = [
        {
            "name": "zugriffsstatistik-daten-berlin-de",
            "title": "Zugriffsstatistik daten.berlin.de",
            "berlin_source": "test",
            "berlin_type": "datensatz",
            "date_released": "2018-06-25",
            "date_updated": "2019-01-01",
            "temporal_coverage_from": "2011-09-01",
            "temporal_coverage_to": "2018-12-31",
            "maintainer_email": "opendata@berlin.de",
            "author": "BerlinOnline Stadtportal GmbH & Co. KG",
            "license_id": "cc-by",
            "notes": "Zugriffsstatistik des Berliner Datenportals"
            "(daten.berlin.de). Enthalten sind die Gesamtzugriffe"
            "auf die Domain daten.berlin.de('impressions' und"
            "'visits') für jeden Monat, sowie die Zugriffszahlen"
            "('impressions' und 'visits') für alle Datensätze für"
            "jeden Monat.\r\n\r\nDer Datensatz wird monatlich erneuert.",
            "groups": [
                {"name": group['name']}
            ]
        }
    ]

    for dataset_dict in dataset_dicts:
        test_helpers.call_action(
            "package_create",
            context={"user": sysadminuser.id},
            **dataset_dict
        )

    return dataset_dicts


@pytest.mark.ckan_config('ckan.plugins', f"{SCHEMA_PLUGIN} {SNIPPET_PLUGIN}")
@pytest.mark.usefixtures('with_plugins', 'clean_db')
class TestPlugin(object):

    # Tests for the dataset page route and snippets
    def test_dataset_route(self, app, datasets, user):
        '''Test that the routing for dataset page snippets works.'''
        dataset = datasets[0]
        dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
        response = app.get(
            headers=[("Authorization", user.apikey)],
            url=dataset_snippet_url,
            status=200  # this is a magic assert for the status (happens in CKANTestClient.open())
        )
        data = json.loads(str(response.body))
        assert dataset['title'] == data['title']
        assert dataset['title'] in data['content']

    def test_dataset_not_found(self, app, datasets, user):
        '''Test that the dataset route returns with 404 if the dataset is not found.'''
        dataset_snippet_url = url_for("snippetapi.read_dataset", id="unknown dataset")
        app.get(
            headers=[("Authorization", user.apikey)],
            url=dataset_snippet_url,
            status=404  # this is a magic assert for the status (happens in CKANTestClient.open())
        )

    @pytest.mark.parametrize("url", [
        "/snippet/dataset",
        "/snippet/dataset/foo",
        "/snippet/latest_datasets"
    ])
    def test_not_authorized_for_anonymous(self, app, url):
        '''Test that snippet reading is not authorized for anonymous users.'''
        app.get(
            url=url,
            status=403  # this is a magic assert for the status (happens in CKANTestClient.open())
        )

    def test_complete_dataset(self, app, datasets, user):
        '''Test rendering of a dataset with extensive metadata.'''
        dataset = datasets[0]
        dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
        response = app.get(
            headers=[("Authorization", user.apikey)],
            url=dataset_snippet_url,
            status=200  # this is a magic assert for the status (happens in CKANTestClient.open())
        )
        data = json.loads(str(response.body))
        assert "Zeitlicher Bezug" in data['content']
        assert "01.09.2011" in data['content']
        assert "bis zum" in data['content']
        assert "31.12.2018" in data['content']

    # Tests for the dataset search route and snippets
    def test_dataset_search_route(self, app, datasets, user):
        '''Test that the routing for dataset search snippets works.'''
        dataset_search_url = url_for("snippetapi.search_dataset")
        response = app.get(
            headers=[("Authorization", user.apikey)],
            url=dataset_search_url,
            status=200
        )
        data = json.loads(str(response.body))
        assert "Index" == data['title']
        assert datasets[0]['title'] in data['content']

    # Tests for the latest datasets route and snippets
    def test_latest_datasets_route(self, app, datasets, user):
        '''Test that the routing for the "Latest Datasets" snippet works.'''
        latest_datasets_url = url_for("snippetapi.show_latest_datasets")
        response = app.get(
            headers=[("Authorization", user.apikey)],
            url=latest_datasets_url,
            status=200
        )
        data = json.loads(str(response.body))
        assert "Latest Datasets" == data['title']
        assert datasets[0]['title'] in data['content']

    @pytest.mark.parametrize("data", [
        {
            "url": "/snippet/dataset",
            "expected": 0
        },
        {
            "url": "/snippet/dataset?foo=bar",
            "expected": 1
        },
        {
            "url": "/snippet/dataset?license_id=cc-by",
            "expected": 1
        },
        {
            "url": "/snippet/dataset?license_id=cc-by&foo=bar",
            "expected": 2
        },
        {
            "url": "/snippet/dataset?license_id=cc-by&foo=bar&foo=baz",
            "expected": 3
        },
    ])
    def test_active_items_total(self, app, data, user):
        response = app.get(
            headers=[("Authorization", user.apikey)],
            url=data['url'],
            status=200
        )
        body = json.loads(str(response.body))
        if data['expected'] == 0:
            assert "<div class=\"badge dp-activefacets\">" not in body[
                'content']
        else:
            assert f"<div class=\"badge dp-activefacets\">{data['expected']}</div>" in body[
                'content']
