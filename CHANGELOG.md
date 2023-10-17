# Changelog

## Development

- Implement the [vertical "Asset Service"](http://styleguide.berlin.de/patterns/11-vertical_assetservice-page-startseite/11-vertical_assetservice-page-startseite.html) of the current berlin.de design system.
- Group various format strings (`CSV`, `.csv`, `zip:csv`) into abstract formats (`CSV`). Group formats (`CSV`, `XLSX`) into more general resource classes (`tabular data`).

## [0.1.2](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.2)

_(2023-05-22)_

- Remove reference to IRoutes interface from readme.
- Remove some unused folders.
- Define extension's version string in [VERSION](ckanext/datasetsnippets/VERSION), make it available as `ckanext.datasetsnippets.__version__` and in [setup.py](setup.py).
- Fix broken test.
- More f-strings.


## [0.1.1](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.1)

_(2022-02-22)_

- Fix codecov configuration and add badge.

## [0.1.0](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.0)

_(2022-02-22)_

- First public version, targetting Python 3 / CKAN >= 2.9.

