"""
Main module for ckanext-datasetsnippets
"""

import os

import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import config

import ckanext.datasetsnippets.helpers as theme_helpers
from ckanext.datasetsnippets import snippet_blueprint
import ckanext.datasetsnippets.auth as snippet_auth
from ckanext.datasetsnippets.resource_mappings import ResourceMapping

class DatasetsnippetsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IAuthFunctions)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetsnippets')
        config['datasetsnippets.path'] = "datensaetze"
        # we introduce a new config setting here to be able to have
        # different behaviour in snippets and regular CKAN UI
        config['datasetsnippets.datasets_per_page'] = 10

        path = os.path.abspath(__file__)
        dir_path = os.path.dirname(path)
        resource_mappings_path = os.path.join(dir_path, "mappings", "resource_format_mappings.json")
        self.resource_mappings = ResourceMapping()
        self.resource_mappings.load_mappings(resource_mappings_path)

    # IBlueprint

    def get_blueprint(self):
        return snippet_blueprint.snippetapi


    # ITemplateHelpers

    def get_helpers(self):
        return {
            'berlin_unlink_email': theme_helpers.unlink_email ,
            'berlin_render_datetime': theme_helpers.render_datetime ,
            'berlin_recent_packages': theme_helpers.recent_packages ,
            'berlin_resource_label': theme_helpers.resource_label ,
            'berlin_dataset_path': theme_helpers.dataset_path ,
            'berlin_url_with_params': theme_helpers.url_with_params ,
            'berlin_encode_params': theme_helpers.encode_params ,
            'berlin_facet_prefix': theme_helpers.get_facet_id_prefix ,
            'berlin_facet_active_items': theme_helpers.active_items ,
            'berlin_facet_active_item_count': theme_helpers.active_item_count ,
            'berlin_facet_active_item_labels': theme_helpers.active_item_labels ,
            'berlin_facet_plural_mapping': theme_helpers.facet_plural_mapping ,
            'berlin_description_for_facet': theme_helpers.description_for_facet ,
            'berlin_css_class_for_format_string': theme_helpers.css_class_for_format_string ,
            'berlin_pagination_cells': theme_helpers.pagination_cells ,
            'berlin_pagination_url_for_page': theme_helpers.pagination_url_for_page ,
        }

    # IAuthFunctions
    # http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IAuthFunctions

    def get_auth_functions(self):
        '''Implementation of http://docs.ckan.org/en/latest/extensions/plugin-interfaces.html#ckan.plugins.interfaces.IAuthFunctions.get_auth_functions'''
        return {
            'snippet_read': snippet_auth.snippet_read
        }
