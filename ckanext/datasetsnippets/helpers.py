# coding: utf-8

import os
import re
import json
import logging
import ckan.lib.helpers as h
from ckan.lib.helpers import literal
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, c, config, request
from urllib.parse import urlencode

log = logging.getLogger(__name__)

get_action = logic.get_action
NotAuthorized = logic.NotAuthorized

def url_with_params(url, params):
    '''Helper function to convert a base-URL (or path) and a dictionary with 
       parameters to an URL string. Takes care of encoding issues in the 
       parameter values, such that e.g. "köln" is encoded as "k%C3%B6ln".
    '''
    if not params:
        return url
    return url + u'?' + encode_params(params)

def encode_params(params):
    params = [(k, v.encode('utf-8') if isinstance(v, str) else str(v))
              for k, v in params.items()]
    return urlencode(params)
   
def dataset_path():
  return config.get('datasetsnippets.path', 'dataset')

def unlink_email(email):
  return email.replace("@", " AT ")


def dateformat():
  return "%d.%m.%Y"


def render_datetime(datetime):
  return h.render_datetime(datetime, date_format=dateformat())


def recent_packages(package_type="dataset", sort_by='metadata_created desc', limit=5):
  from ckan.lib.search import SearchError, SearchQueryError

  context = {'model': model, 'user': c.user,
             'auth_user_obj': c.userobj}
  data_dict = {
    'fq': ' +dataset_type:{type}'.format(type=package_type),
    'rows': limit,
    'sort': sort_by,
    'include_private': False,
  }
  try:
    query = get_action('package_search')(context, data_dict)
    return query['results']
  except SearchQueryError as se: # pragma: no cover
    # User's search parameters are invalid, in such a way that is not
    # achievable with the web interface, so return a proper error to
    # discourage spiders which are the main cause of this.
    log.info('Dataset search query rejected: %r', se.args)  # pragma: no cover
    abort(400, _('Invalid search query: {error_message}')  # pragma: no cover
          .format(error_message=str(se)))  # pragma: no cover
  except SearchError as se:  # pragma: no cover
    # May be bad input from the user, but may also be more serious like
    # bad code causing a SOLR syntax error, or a problem connecting to
    # SOLR
    log.error('Dataset search error: %r', se.args)  # pragma: no cover
    c.query_error = True  # pragma: no cover
    c.search_facets = {}  # pragma: no cover
    c.page = h.Page(collection=[])  # pragma: no cover
  except NotAuthorized:  # pragma: no cover
    abort(403, _('Not authorized to see this page'))  # pragma: no cover

def resource_label(resource):
  label = "Unbekannt"

  if resource['name']:
    name = resource['name']
  else:
    url = resource['url']
    name = url[url.rfind("/") + 1:].split('?')[0]

  if len(name) > 0:
    label = name

  return label

def get_facet_id_prefix(name):
    '''Helper function to generate the markup id-prefix for a facet
       selection box.
    '''
    return "dp_facet_" + name

def facet_plural_mapping():
    return {
        'groups': u'Kategorien',
        'author_string': u'Quellen',
        'geographical_coverage': u'Geografische Abdeckungen',
        'geographical_granularity': u'Geografische Granularitäten',
        'temporal_granularity': u'Zeitliche Granularitäten',
        'res_format': u'Formate',
        'license_id': u'Lizenzen',
        'tags': u'Tags',
        'berlin_type': u'Typen',
        'organization': u'Organisationen',  
    }


def active_item_count(items):
    '''Helper function that returns the number of active items from a list of
       facet items.'''
    return len(active_items(items))

def active_items(items):
    '''Helper function that returns the list of all active items from 
       a list of facet items.
    '''
    return [item for item in items if item['active']]

def active_items_total():
    '''Helper function that returns the total of active (selected) facet items across
       all facets.'''
    
    # CKAN behaviour is that _every_ URL parameter is interpreted as as the name of a 
    # search facet, even if such a facet doesn't exist. Non-existing search facets will 
    # lead to 0 search results.
    # Therefore, there is no need to filter the URL parameters for ones that are actually
    # search facets. Just count the number of URL parameters. In any successful search,
    # they will be equal to the number of selected search parameters.

    return len(list(request.args.items(multi=True)))

def active_item_labels(items):
    '''Helper function that returns a comma-separated string with the labels of
       all active items from a list of facet items.
    '''
    return ', '.join([item['display_name'] for item in items if item['active']])

def label_for_sorting(sortings, sorting):
    '''Helper function to retrieve the label for a search sorting from a list of sortings.'''
    flipped = { value: key for key,value in dict(sortings).items() }
    return flipped.get(sorting, None)
