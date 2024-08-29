# ckanext-datasetsnippets

[![Tests](https://github.com/berlinonline/ckanext-datasetsnippets/workflows/Tests/badge.svg?branch=master)](https://github.com/berlinonline/ckanext-datasetsnippets/actions)
[![Code Coverage](http://codecov.io/github/berlinonline/ckanext-datasetsnippets/coverage.svg?branch=master)](http://codecov.io/github/berlinonline/ckanext-datasetsnippets?branch=master)

This plugin belongs to a set of plugins for the _Datenregister_ – the non-public [CKAN](https://ckan.org) instance that is part of Berlin's open data portal [daten.berlin.de](https://daten.berlin.de).
_ckanext-datasetsnippets_ provides markup snippets for dataset pages and dataset search.
These snippets can be loaded from the data portal's public CMS to handle all requests for datasets.

The plugin implements the following CKAN interfaces:

- [ITemplateHelpers](http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.ITemplateHelpers)
- [IBlueprint](http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IBlueprint)
- [IAuthFunctions](http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IAuthFunctions)

## Requirements

This plugin has been tested with CKAN 2.9.9 (which requires Python 3).

## API

The Snippet API has the following two endpoints:

### `/snippet/dataset`

This is the search endpoint of the snippet API, which is equivalent to `/dataset` in the regular CKAN UI.
Without additional parameters, this returns markup for the paginated list of all datasets.
Parameters (search facets, ordering etc.) can be use to restrict the result.
The parameters are identical to the regular CKAN search parameters.

### `/snippet/dataset/<id>`

This is the dataset detail endpoint of the snippet API, which is equivalent to `/dataset/<id>` in the regular CKAN UI. 
`<id>` is the name or id of a dataset.

### Parameters

Both endpoints allow a `root_breadcrumb` parameter to set the root element of the breadcrumb returned in the snippets.
The `root_breadcrumb`-URL-parameter takes precedence over the `datasetsnippets.default_root_breadcrumb` config (see below).

## Configuration

The plugin introduces the following configuration options:

### datasetsnippets.path

Defines the path component that is prefixed to links that the snippets contain.
In the regular CKAN UI, this would be `dataset`, but the site calling the snippet API might require a different path.

```ini
datasetsnippets.path = 'datensaetze'
```

### datasetsnippets.datasets_per_page

Defines how many datasets are shown per result page in pagination.
The option is equivalent to [ckan.datasets_per_page](https://docs.ckan.org/en/2.9/maintaining/configuration.html#ckan-datasets-per-page), but only applies to the snippets and leaves the regular CKAN UI untouched.

```ini
datasetsnippets.datasets_per_page = 10
```

### datasetsnippets.default_root_breadcrumb

Defines the string that is used as the root element for the breadcrumb that is part of the returned snippets.

```ini
datasetsnippets.default_root_breadcrumb = 'Berlin Open Data'
```

### datasetsnippets.datenportal_url

Defines the url to the datenportal. The url will then be used for generating the feeds using the provided url.

```ini
datasetsnippets.datenportal_url = link_to_portal
```

### datasetsnippets.datenportal_title

Defines a string that will be used as a title in the feeds.

```ini
datasetsnippets.datenportal_title = 'Berlin Open Data'
```

## License

This material is copyright © [BerlinOnline Stadtportal GmbH](https://www.berlinonline.net/).

This extension is open and licensed under the GNU Affero General Public License (AGPL) v3.0.
Its full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
