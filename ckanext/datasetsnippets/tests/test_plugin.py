"""Tests for plugin.py."""

import json
import logging
import pytest

from flask import Flask

import ckan.model as model
from ckan.plugins.toolkit import config, url_for
import ckan.tests.factories as factories
import ckan.tests.helpers as test_helpers

from ckan.model.package import Package


LOG = logging.getLogger(__name__)
SCHEMA_PLUGIN = 'berlin_dataset_schema'
THEME_PLUGIN = 'berlintheme'
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

@pytest.fixture
def lotsa_datasets():
    '''Fixture to create lots of datasets.'''
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
    dataset_dicts = []
    for i in range(100):
        dataset_dicts.append({
            "name": f"testing-{i}",
            "title": f"Testing {i}",
            "berlin_source": "test",
            "berlin_type": "datensatz",
            "date_released": "2018-06-25",
            "date_updated": "2019-01-01",
            "temporal_coverage_from": "2011-09-01",
            "temporal_coverage_to": "2018-12-31",
            "maintainer_email": "opendata@berlin.de",
            "author": "BerlinOnline Stadtportal GmbH & Co. KG",
            "license_id": "cc-by",
            "notes": f"Ein Testdatensatz, nämlich der {i}.",
            "groups": [
                {"name": group['name']}
            ]
        })

    for dataset_dict in dataset_dicts:
        test_helpers.call_action(
            "package_create",
            context={"user": sysadminuser.id},
            **dataset_dict
        )

    return dataset_dicts

@pytest.mark.ckan_config('ckan.plugins', f"{SCHEMA_PLUGIN} {THEME_PLUGIN} {SNIPPET_PLUGIN}")
@pytest.mark.ckan_config('search.facets', 'organization groups tags res_format license_id foo')
@pytest.mark.usefixtures('clean_db', 'clean_index', 'with_plugins')
class TestPlugin(object):

    # # Tests for the dataset page route and snippets
    # def test_dataset_route(self, app, datasets, user):
    #     '''Test that the routing for dataset page snippets works.'''
    #     dataset = datasets[0]
    #     dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_snippet_url,
    #         status=200  # this is a magic assert for the status (happens in CKANTestClient.open())
    #     )
    #     data = json.loads(str(response.body))
    #     assert dataset['title'] == data['title']
    #     assert dataset['title'] in data['content']

    # def test_dataset_not_found(self, app, datasets, user):
    #     '''Test that the dataset route returns with 404 if the dataset is not found.'''
    #     dataset_snippet_url = url_for("snippetapi.read_dataset", id="unknown dataset")
    #     app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_snippet_url,
    #         status=404  # this is a magic assert for the status (happens in CKANTestClient.open())
    #     )

    def test_private_dataset_not_found(self, app, datasets):
        '''Test that requests for a private dataset result in a 404.'''
        user = factories.Sysadmin(name='theadmin')

        # make the dataset private
        dataset = datasets[0]
        dataset_obj = Package.by_name(dataset['name'])
        dataset_obj.private = True
        model.Session.commit()
        
        # check it cannot be accessed directly
        dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
        response = app.get(
            headers=[("Authorization", user['apikey'])],
            url=dataset_snippet_url,
            status=404
        )

        # check it's not in the search results
        dataset_search_url = "/snippet/dataset?sort=title_string+asc"
        response = app.get(
            headers=[("Authorization", user['apikey'])],
            url=dataset_search_url,
            status=200
        )
        data = json.loads(str(response.body))
        assert "Index" == data['title']
        assert datasets[0]['title'] not in data['content']

    # def test_deleted_dataset_not_found(self, app, datasets):
    #     '''Test that requests for a deleted dataset result in a 404.'''
    #     user = factories.Sysadmin(name='theadmin')

    #     # delete the dataset
    #     dataset = datasets[0]
    #     dataset_obj = Package.by_name(dataset['name'])
    #     dataset_obj.delete()

    #     # check it cannot be accessed directly
    #     dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
    #     response = app.get(
    #         headers=[("Authorization", user['apikey'])],
    #         url=dataset_snippet_url,
    #         status=404
    #     )

    #     # check it's not in the search results
    #     dataset_search_url = "/snippet/dataset?sort=title_string+asc"
    #     response = app.get(
    #         headers=[("Authorization", user['apikey'])],
    #         url=dataset_search_url,
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert "Index" == data['title']
    #     assert datasets[0]['title'] not in data['content']


    # @pytest.mark.parametrize("url", [
    #     "/snippet/dataset",
    #     "/snippet/dataset/foo",
    #     "/snippet/latest_datasets"
    # ])
    # def test_not_authorized_for_anonymous(self, app, url):
    #     '''Test that snippet reading is not authorized for anonymous users.'''
    #     app.get(
    #         url=url,
    #         status=403  # this is a magic assert for the status (happens in CKANTestClient.open())
    #     )

    # def test_complete_dataset(self, app, datasets, user):
    #     '''Test rendering of a dataset with extensive metadata.'''
    #     dataset = datasets[0]
    #     dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_snippet_url,
    #         status=200  # this is a magic assert for the status (happens in CKANTestClient.open())
    #     )
    #     data = json.loads(str(response.body))
    #     assert "Zeitlicher Bezug" in data['content']
    #     assert "01.09.2011" in data['content']
    #     assert "bis zum" in data['content']
    #     assert "31.12.2018" in data['content']

    # # Tests for the dataset search route and snippets
    # def test_dataset_search_route(self, app, datasets, user):
    #     '''Test that the routing for dataset search snippets works.'''
    #     dataset_search_url = "/snippet/dataset?sort=title_string+asc"
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_search_url,
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert "Index" == data['title']
    #     assert datasets[0]['title'] in data['content']

    # # Tests for the latest datasets route and snippets
    # def test_latest_datasets_route(self, app, datasets, user):
    #     '''Test that the routing for the "Latest Datasets" snippet works.'''
    #     latest_datasets_url = url_for("snippetapi.show_latest_datasets")
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=latest_datasets_url,
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert "Latest Datasets" == data['title']
    #     assert datasets[0]['title'] in data['content']


    # def test_value_error(self, app, user):
    #     '''Test that we get a 400 if we provide an non-integer as a limit parameter.'''
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url="/snippet/dataset?_groups_limit=x",
    #         status=400
    #     )

    # def test_pager(self, app, user, lotsa_datasets):
    #     '''Sanity test to check if pagination works.'''
    #     dataset_search_url = url_for("snippetapi.search_dataset")
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_search_url,
    #         query_string={"sort": "title_string asc"},
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert "Index" == data['title']
    #     assert lotsa_datasets[0]['title'] in data['content']
    #     print(data['content'])
    #     assert 'page=1' in data['content']
    #     assert 'page=2' in data['content']
    #     assert 'class="pagination"' in data['content']

    # def test_filter_pills(self, app, user, lotsa_datasets):
    #     '''Sanity test to check if filter pills show up when tags are used for search.'''
    #     dataset_search_url = url_for("snippetapi.search_dataset")
    #     tag_1 = "d089d7bc"
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_search_url,
    #         query_string={"tags": tag_1},
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert tag_1 in data['content']
    #     assert 'dp-filter-list' in data['content']
    #     assert '"pill' in data['content']

    # @pytest.mark.parametrize("breadcrumb", [
    #     "Startseite", "Berlin Open Data", "Berlin Open Data-Dev", "X"
    # ])
    # def test_valid_root_breadcrumbs(self, app, user, datasets, breadcrumb):
    #     '''
    #     Test some valid root_breadcrumb parameter values and check that they
    #     show up in the returned snippets.
    #     '''
    #     dataset = datasets[0]
    #     dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_snippet_url,
    #         query_string={"root_breadcrumb": breadcrumb},
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert breadcrumb in data['content']

    #     dataset_search_url = url_for("snippetapi.search_dataset")
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_search_url,
    #         query_string={"root_breadcrumb": breadcrumb},
    #         status=200
    #     )
    #     data = json.loads(str(response.body))
    #     assert breadcrumb in data['content']
    #     assert "Index" == data['title']
    #     assert datasets[0]['title'] in data['content']

    # @pytest.mark.parametrize("breadcrumb", [
    #     "", " ", "-", "<a href='http://spam.com'>Startseite</a>", "Berlin Open Data Berlin Open Data", "Berlin Open Data-Dev!"
    # ])
    # def test_invalid_root_breadcrumbs(self, app, user, datasets, breadcrumb):
    #     '''
    #     Test some invalid root_breadcrumb parameter values and check that we
    #     get an invalid response.
    #     '''
    #     dataset = datasets[0]
    #     dataset_snippet_url = url_for("snippetapi.read_dataset", id=dataset['name'])
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_snippet_url,
    #         query_string={"root_breadcrumb": breadcrumb},
    #         status=400
    #     )

    #     dataset_search_url = url_for("snippetapi.search_dataset")
    #     response = app.get(
    #         headers=[("Authorization", user.apikey)],
    #         url=dataset_search_url,
    #         query_string={"root_breadcrumb": breadcrumb},
    #         status=400
    #     )
