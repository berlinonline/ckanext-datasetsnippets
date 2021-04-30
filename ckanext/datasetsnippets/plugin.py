import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.plugins.toolkit import config

import ckanext.datasetsnippets.helpers as theme_helpers


class DatasetsnippetsPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IRoutes, inherit=True)
    plugins.implements(plugins.ITemplateHelpers)

    # IConfigurer

    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetsnippets')
        config['datasetsnippets.path'] = "datensaetze"

    # IRoutes

    def before_map(self, _map):

        controller = 'ckanext.datasetsnippets.controller:SnippetController'

        _map.connect('snippet_dataset', '/snippet/dataset/{_id}',
                     controller=controller, action='read_dataset')

        _map.connect('snippet_search', '/snippet/dataset',
                     controller=controller, action='search_dataset')

        _map.connect('snippet_latest_datasets', '/snippet/latest_datasets',
                     controller=controller, action='show_latest_datasets')

        return _map

    # -------------------------------------------------------------------
    # Implementation ITemplateHelpers
    # -------------------------------------------------------------------

    def get_helpers(self):
        return {
            'berlintheme_facet_mapping': theme_helpers.facet_mapping ,
            'berlin_unlink_email': theme_helpers.unlink_email ,
            'berlin_render_datetime': theme_helpers.render_datetime ,
            'berlin_recent_packages': theme_helpers.recent_packages ,
            'berlin_resource_label': theme_helpers.resource_label ,
            'berlin_breadcrumb_length': theme_helpers.breadcrumb_length ,
            'berlin_build_menu_item': theme_helpers.build_menu_item ,
            'berlin_http_status_codes': theme_helpers.http_status_code_mapping ,
            'berlin_user_object': theme_helpers.user_object ,
            'berlin_log_this': theme_helpers.log_this ,
            'berlin_dataset_type_mapping': theme_helpers.dataset_type_mapping ,
            'berlin_type_mapping_select_options': theme_helpers.type_mapping_select_options ,
            'berlin_temporal_granularity_select_options': theme_helpers.temporal_granularity_select_options ,
            'berlin_geo_granularity_select_options': theme_helpers.geo_granularity_select_options ,
            'berlin_geo_coverage_select_options':
                theme_helpers.geo_coverage_select_options ,
            'berlin_state_mapping': theme_helpers.state_mapping ,
            'berlin_user_orgs': theme_helpers.organizations_for_user ,
            'berlin_is_sysadmin': theme_helpers.is_sysadmin ,
            'berlin_dataset_path': theme_helpers.dataset_path ,
            'berlin_url_with_params': theme_helpers.url_with_params ,
            'berlin_facet_prefix': theme_helpers.get_facet_id_prefix ,
            'berlin_facet_has_active_item': theme_helpers.has_active_item ,
            'berlin_facet_active_items': theme_helpers.active_items ,
            'berlin_facet_active_item_labels': theme_helpers.active_item_labels ,
            'berlin_label_for_sorting': theme_helpers.label_for_sorting ,
        }
