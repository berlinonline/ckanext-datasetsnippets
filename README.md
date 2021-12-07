# ckanext-datasetsnippets

[![Tests](https://github.com/berlinonline/ckanext-datasetsnippets/workflows/Tests/badge.svg?branch=master)](https://github.com/berlinonline/ckanext-datasetsnippets/actions)

This plugin belongs to a set of plugins for the _Datenregister_ – the non-public [CKAN](https://ckan.org) instance that is part of Berlin's open data portal [daten.berlin.de](https://daten.berlin.de).
_ckanext-datasetsnippets_ provides markup snippets for dataset pages and dataset search.
These snippets can be loaded from the data portals public CMS to handle all requests for datasets.

The plugin implements the following CKAN interfaces:

- [IRoutes](http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IRoutes)
- [ITemplateHelpers](http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.ITemplateHelpers)

## Requirements

This plugin has been tested with CKAN 2.9.4 (which requires Python 3).

## License

This material is copyright © [BerlinOnline Stadtportal GmbH & Co. KG](https://www.berlinonline.net/).

This extension is open and licensed under the GNU Affero General Public License (AGPL) v3.0.
Its full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
