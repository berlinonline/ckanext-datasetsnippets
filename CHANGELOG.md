# Changelog

## Development

- Fix response to requesting deleted or private datasets: this now results in a 404 response, not a 500.
- Set env variables for database and Solr index in scripts for running unit tests locally.
- Move `_is_true()` to helpers.
- Add required `author_uri` to test data.
- Fix failing Github CI (install curl).

## [0.1.12](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.12)

_(2025-04-29)_

- Fix facetted search UX problem (form always open on mobile).
- Add a link back to the Datenregister for dataset views.

## [0.1.11](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.11)

_(2024-12-17)_

- Add [publiccode.yml](publiccode.yml) file.
- Fix failing CI/CD.
- Update README.

## [0.1.10](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.10)

_(2024-09-02)_

- Sanitize user input & handle author_string/author.

## [0.1.9](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.9)

_(2024-08-29)_

- Fix RSS Feeds.

## [0.1.8](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.8)

_(2024-08-29)_

- Add dataset RSS feeds.

## [0.1.7](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.7)

_(2024-07-04)_

- Even if the requesting user has permission, private and deleted datasets are not returned in the search results.
- Even if the requesting user has permission, requests for private and deleted datasets return a 404.

## [0.1.6](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.6)

_(2024-05-29)_

- The root element of the breadcrumb in the returned snippets can now be configured, either via a `root_breadcrumb`-URL parameter, or via the newly introduced config `datasetsnippets.default_root_breadcrumb`.
- When setting config values in `plugin.py`, don't overwrite values that might have been set elsewhere.
- Add help text for tags in facet list.
- Change "Stichwort" to "Schlagwort" for tags.

## [0.1.5](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.5)

_(2024-04-25)_

- If a dataset has no preview image, show a dummy preview image.
- Mark external organizations.
- Add new metadata field `hvd_category` (to link to the category of high-value datasets as defined by the [EU commission implementing regulation 2023/138](https://eur-lex.europa.eu/eli/reg_impl/2023/138/oj?uri=CELEX:32023R0138)).
- Add new metadata field `sample_record` (to link to the matching "Musterdatensatz", see https://www.dcat-ap.de/def/dcatde/2.0/implRules/#verwendung-des-musterdatenkatalogs-fur-kommunen).

## [0.1.4](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.4)

_(2024-03-22)_

- Use the new field `preview_image` (see [ckanext-berlin_dataset_schema](https://github.com/berlinonline/ckanext-berlin_dataset_schema)). Markup is based on the [Text Image](https://styleguide.berlin.de/patterns/11-vertical_assetservice-page-modul-textbild/11-vertical_assetservice-page-modul-textbild.html) module.
- Change Solr image reference in github CI ([test.yml](.github/workflows/test.yml)) to the new naming scheme according to https://github.com/ckan/ckan-solr.

## [0.1.3](https://github.com/berlinonline/ckanext-datasetsnippets/releases/tag/0.1.3)

_(2023-11-22)_

- Implement the [vertical "Asset Service"](http://styleguide.berlin.de/patterns/11-vertical_assetservice-page-startseite/11-vertical_assetservice-page-startseite.html) of the current berlin.de design system. This affects all templates.
- Group various format strings (`CSV`, `.csv`, `zip:csv`) into abstract formats (`CSV`). Group formats (`CSV`, `XLSX`) into more general resource classes (`tabular data`).
- Introduce a new setting `datasetsnippets.datasets_per_page` that's equivalent to [ckan.datasets_per_page](https://docs.ckan.org/en/2.9/maintaining/configuration.html#ckan-datasets-per-page), but only applies to the snippets and leaves the regular CKAN UI untouched.

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

