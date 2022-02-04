"""
Main module for ckanext-datasetsnippets
"""
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import config

import ckanext.datasetsnippets.helpers as theme_helpers
from ckanext.datasetsnippets import snippet_blueprint

class DatasetsnippetsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetsnippets')
        config['datasetsnippets.path'] = "datensaetze"

    # IBlueprint

    def get_blueprint(self):
        return snippet_blueprint.snippetapi


    # -------------------------------------------------------------------
    # Implementation ITemplateHelpers
    # -------------------------------------------------------------------

    def get_helpers(self):
        return {
            'berlin_unlink_email': theme_helpers.unlink_email ,
            'berlin_render_datetime': theme_helpers.render_datetime ,
            'berlin_recent_packages': theme_helpers.recent_packages ,
            'berlin_resource_label': theme_helpers.resource_label ,
            'berlin_dataset_path': theme_helpers.dataset_path ,
            'berlin_url_with_params': theme_helpers.url_with_params ,
            'berlin_facet_prefix': theme_helpers.get_facet_id_prefix ,
            'berlin_facet_active_items': theme_helpers.active_items ,
            'berlin_facet_active_item_count': theme_helpers.active_item_count ,
            'berlin_facet_active_items_total': theme_helpers.active_items_total ,
            'berlin_facet_active_item_labels': theme_helpers.active_item_labels ,
            'berlin_label_for_sorting': theme_helpers.label_for_sorting ,
            'berlin_facet_plural_mapping': theme_helpers.facet_plural_mapping ,
        }
