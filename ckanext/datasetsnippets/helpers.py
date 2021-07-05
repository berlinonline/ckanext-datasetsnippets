# coding: utf-8

import os
import re
import json
import logging
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
from ckan.common import _, c, config, response, request
from urllib import urlencode
from webhelpers.html import literal

log = logging.getLogger(__name__)

get_action = logic.get_action
NotAuthorized = logic.NotAuthorized

_facet_mapping = {}

_path_patterns = {
  "home" : [ "/nutzungsbedingungen", "/impressum" , "/faq" , "/contact", "/user/.*", "/dashboard(/.*)?", "/" ] ,
  "dataset": [ "/dataset(/.*)?" ] ,
  "apps": [ "/anwendungen" ] ,
  "contributors": [ "/datenbereitsteller" ] ,
  "interaktion": [ "/interaktion" ] ,
  "admin": [ "/ckan-admin(/.*)?" ] ,
  "organization": [ "/organization(/.*)?" ] ,
  "group": [ "/group(/.*)?" ] ,
  "user-list": [ "/user" ] ,
  "harvest": [ "/harvest(/.*)?" ],
}

def url_with_params(url, params):
    if not params:
        return url
    params = [(k, v.encode('utf-8') if isinstance(v, basestring) else str(v))
              for k, v in params.items()]
    return url + u'?' + urlencode(params)

def dataset_path():
  return config.get('datasetsnippets.path', 'dataset')

def breadcrumb_length():
  return config.get("berlintheme.breadcrumb_length", 35)

def read_facet_mapping():
  path = os.path.abspath(__file__)
  dir_path = os.path.dirname(path)
  with open(os.path.join(dir_path, "config", "facet_name_mapping.json")) as json_data:
    global _facet_mapping
    _facet_mapping = json.load(json_data)


def facet_mapping(item, facet):
  global _facet_mapping
  name = item['display_name']
  # log.debug("{}:{}".format(name.encode('utf-8'), facet.encode('utf-8')))
  if facet in _facet_mapping:
    if name in _facet_mapping[facet]:
      return _facet_mapping[facet][name]
  return name


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
  except SearchQueryError, se:
    # User's search parameters are invalid, in such a way that is not
    # achievable with the web interface, so return a proper error to
    # discourage spiders which are the main cause of this.
    log.info('Dataset search query rejected: %r', se.args)
    abort(400, _('Invalid search query: {error_message}')
          .format(error_message=str(se)))
  except SearchError, se:
    # May be bad input from the user, but may also be more serious like
    # bad code causing a SOLR syntax error, or a problem connecting to
    # SOLR
    log.error('Dataset search error: %r', se.args)
    c.query_error = True
    c.search_facets = {}
    c.page = h.Page(collection=[])
  except NotAuthorized:
    abort(403, _('Not authorized to see this page'))

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

def user_object(user_name):
  log.info("user_name: {}".format(user_name))
  user_name = unicode(user_name)
  user = model.User.get(user_name)
  if not user:
    return None
  else:
    return user


def http_status_code_mapping(status):
  mapping = {
    "400 Bad Request": "Bad Request",
    "401 Unauthorized": "Unauthorized",
    "402 Payment Required": "Payment Required",
    "403 Forbidden": "Forbidden",
    "404 Not Found": "Not Found",
    "405 Method Not Allowed": "Method Not Allowed",
    "406 Not Acceptable": "Not Acceptable",
    "407 Proxy Authentication Required": "Proxy Authentication Required",
    "408 Request Timeout": "Request Timeout",
    "409 Conflict": "Conflict",
    "410 Gone": "Gone",
    "411 Length Required": "Length Required",
    "412 Precondition Failed": "Precondition Failed",
    "413 Payload Too Large": "Payload Too Large",
    "414 Request-URI Too Long": "Request-URI Too Long",
    "415 Unsupported Media Type": "Unsupported Media Type",
    "416 Requested Range Not Satisfiable": "Requested Range Not Satisfiable",
    "417 Expectation Failed": "Expectation Failed",
    "418 I'm a teapot": "I'm a teapot",
    "421 Misdirected Request": "Misdirected Request",
    "422 Unprocessable Entity": "Unprocessable Entity",
    "423 Locked": "Locked",
    "424 Failed Dependency": "Failed Dependency",
    "426 Upgrade Required": "Upgrade Required",
    "428 Precondition Required": "Precondition Required",
    "429 Too Many Requests": "Too Many Requests",
    "431 Request Header Fields Too Large": "Request Header Fields Too Large",
    "444 Connection Closed Without Response": "Connection Closed Without Response",
    "451 Unavailable For Legal Reasons": "Unavailable For Legal Reasons",
    "499 Client Closed Request": "Client Closed Request",
    "500 Internal Server Error": "Internal Server Error",
    "501 Not Implemented": "Not Implemented",
    "502 Bad Gateway": "Bad Gateway",
    "503 Service Unavailable": "Service Unavailable",
    "504 Gateway Timeout": "Gateway Timeout",
    "505 HTTP Version Not Supported": "HTTP Version Not Supported",
    "506 Variant Also Negotiates": "Variant Also Negotiates",
    "507 Insufficient Storage": "Insufficient Storage",
    "508 Loop Detected": "Loop Detected",
    "510 Not Extended": "Not Extended",
    "511 Network Authentication Required": "Network Authentication Required",
    "599 Network Connect Timeout Error": "Network Connect Timeout Error",
  }
  return mapping[status]


def compile_path_patterns():
  for menu, patterns in _path_patterns.iteritems():
    patterns =[re.compile("^{}$".format(pattern)) for pattern in patterns]
    _path_patterns[menu] = patterns


def _is_active(item):
  for pattern in _path_patterns[item[0]]:
    if pattern.match(request.path):
      return True
  return False


def build_menu_item(item):
  link = u"<a href='{}'>{}</a>".format(item[2], item[1])
  list_classes = []
  submenu = ""
  if len(item) > 3:
    sub_items = []
    for sub_item in item[3]:
      sub_items.append(build_menu_item(sub_item))
    submenu = "<ul class='nav'>{}</ul>".format("".join(sub_items))
    list_classes.append("has-submenu")

  is_active = _is_active(item)
  if is_active:
    list_classes.append("active")
  if len(list_classes) > 0:
    list_classes = " class='{}'".format(" ".join(list_classes))
  else:
    list_classes = ""
  return literal(u"<li{}>{}{}</li>".format(list_classes, link, submenu))


def log_this(_object):
  log.info(_object.__class__)
  log.info(_object)


def dataset_type_mapping():
    return {
        'datensatz': 'Datensatz',
        'dokument': 'Dokument',
        'app': 'Anwendung'
    }


def geo_coverage_select_options():
    return [
        {u'id': u'Adlershof', u'label': u'Adlershof'},
        {u'id': u'Alt-Hohenschönhausen', u'label': u'Alt-Hohenschönhausen'},
        {u'id': u'Alt-Treptow', u'label': u'Alt-Treptow'},
        {u'id': u'Altglienicke', u'label': u'Altglienicke'},
        {u'id': u'Baumschulenweg', u'label': u'Baumschulenweg'},
        {u'id': u'Berlin', u'label': u'Berlin'},
        {u'id': u'Biesdorf', u'label': u'Biesdorf'},
        {u'id': u'Blankenburg', u'label': u'Blankenburg'},
        {u'id': u'Blankenfelde', u'label': u'Blankenfelde'},
        {u'id': u'Bohnsdorf', u'label': u'Bohnsdorf'},
        {u'id': u'Britz', u'label': u'Britz'},
        {u'id': u'Buch', u'label': u'Buch'},
        {u'id': u'Buckow', u'label': u'Buckow'},
        {u'id': u'Charlottenburg', u'label': u'Charlottenburg'},
        {u'id': u'Charlottenburg-Nord', u'label': u'Charlottenburg-Nord'},
        {u'id': u'Charlottenburg-Wilmersdorf', u'label': u'Charlottenburg-Wilmersdorf'},
        {u'id': u'Dahlem', u'label': u'Dahlem'},
        {u'id': u'Deutschland', u'label': u'Deutschland'},
        {u'id': u'Friedenau', u'label': u'Friedenau'},
        {u'id': u'Friedrichsfelde', u'label': u'Friedrichsfelde'},
        {u'id': u'Friedrichshagen', u'label': u'Friedrichshagen'},
        {u'id': u'Friedrichshain', u'label': u'Friedrichshain'},
        {u'id': u'Friedrichshain-Kreuzberg', u'label': u'Friedrichshain-Kreuzberg'},
        {u'id': u'Frohnau', u'label': u'Frohnau'},
        {u'id': u'Gatow', u'label': u'Gatow'},
        {u'id': u'Gesundbrunnen', u'label': u'Gesundbrunnen'},
        {u'id': u'Gropiusstadt', u'label': u'Gropiusstadt'},
        {u'id': u'Grunewald', u'label': u'Grunewald'},
        {u'id': u'Grünau', u'label': u'Grünau'},
        {u'id': u'Hakenfelde', u'label': u'Hakenfelde'},
        {u'id': u'Halensee', u'label': u'Halensee'},
        {u'id': u'Hansaviertel', u'label': u'Hansaviertel'},
        {u'id': u'Haselhorst', u'label': u'Haselhorst'},
        {u'id': u'Heiligensee', u'label': u'Heiligensee'},
        {u'id': u'Heinersdorf', u'label': u'Heinersdorf'},
        {u'id': u'Hellersdorf', u'label': u'Hellersdorf'},
        {u'id': u'Hermsdorf', u'label': u'Hermsdorf'},
        {u'id': u'Hohenschönhausen', u'label': u'Hohenschönhausen'},
        {u'id': u'Johannisthal', u'label': u'Johannisthal'},
        {u'id': u'Karlshorst', u'label': u'Karlshorst'},
        {u'id': u'Karow', u'label': u'Karow'},
        {u'id': u'Kaulsdorf', u'label': u'Kaulsdorf'},
        {u'id': u'Kladow', u'label': u'Kladow'},
        {u'id': u'Kreuzberg', u'label': u'Kreuzberg'},
        {u'id': u'Lichtenberg', u'label': u'Lichtenberg'},
        {u'id': u'Lichtenrade', u'label': u'Lichtenrade'},
        {u'id': u'Lichterfelde', u'label': u'Lichterfelde'},
        {u'id': u'Lübars', u'label': u'Lübars'},
        {u'id': u'Mahlsdorf', u'label': u'Mahlsdorf'},
        {u'id': u'Malchow', u'label': u'Malchow'},
        {u'id': u'Mariendorf', u'label': u'Mariendorf'},
        {u'id': u'Marienfelde', u'label': u'Marienfelde'},
        {u'id': u'Marzahn', u'label': u'Marzahn'},
        {u'id': u'Marzahn-Hellersdorf', u'label': u'Marzahn-Hellersdorf'},
        {u'id': u'Mitte', u'label': u'Mitte'},
        {u'id': u'Moabit', u'label': u'Moabit'},
        {u'id': u'Märkisches Viertel', u'label': u'Märkisches Viertel'},
        {u'id': u'Müggelheim', u'label': u'Müggelheim'},
        {u'id': u'Neu-Hohenschönhausen', u'label': u'Neu-Hohenschönhausen'},
        {u'id': u'Neukölln', u'label': u'Neukölln'},
        {u'id': u'Niederschöneweide', u'label': u'Niederschöneweide'},
        {u'id': u'Niederschönhausen', u'label': u'Niederschönhausen'},
        {u'id': u'Nikolassee', u'label': u'Nikolassee'},
        {u'id': u'Oberschöneweide', u'label': u'Oberschöneweide'},
        {u'id': u'Pankow', u'label': u'Pankow'},
        {u'id': u'Plänterwald', u'label': u'Plänterwald'},
        {u'id': u'Prenzlauer Berg', u'label': u'Prenzlauer Berg'},
        {u'id': u'Rahnsdorf', u'label': u'Rahnsdorf'},
        {u'id': u'Reinickendorf', u'label': u'Reinickendorf'},
        {u'id': u'Schmöckwitz', u'label': u'Schmöckwitz'},
        {u'id': u'Schöneberg', u'label': u'Schöneberg'},
        {u'id': u'Siemensstadt', u'label': u'Siemensstadt'},
        {u'id': u'Spandau', u'label': u'Spandau'},
        {u'id': u'Staaken', u'label': u'Staaken'},
        {u'id': u'Stadtrandsiedlung Malchow', u'label': u'Stadtrandsiedlung Malchow'},
        {u'id': u'Steglitz', u'label': u'Steglitz'},
        {u'id': u'Steglitz-Zehlendorf', u'label': u'Steglitz-Zehlendorf'},
        {u'id': u'Tegel', u'label': u'Tegel'},
        {u'id': u'Tempelhof', u'label': u'Tempelhof'},
        {u'id': u'Tempelhof-Schöneberg', u'label': u'Tempelhof-Schöneberg'},
        {u'id': u'Tiergarten', u'label': u'Tiergarten'},
        {u'id': u'Treptow-Köpenick', u'label': u'Treptow-Köpenick'},
        {u'id': u'Waidmannslust', u'label': u'Waidmannslust'},
        {u'id': u'Wannsee', u'label': u'Wannsee'},
        {u'id': u'Wartenberg', u'label': u'Wartenberg'},
        {u'id': u'Wedding', u'label': u'Wedding'},
        {u'id': u'Weißensee', u'label': u'Weißensee'},
        {u'id': u'Westend', u'label': u'Westend'},
        {u'id': u'Wilhelmsruh', u'label': u'Wilhelmsruh'},
        {u'id': u'Wilhelmstadt', u'label': u'Wilhelmstadt'},
        {u'id': u'Wilmersdorf', u'label': u'Wilmersdorf'},
        {u'id': u'Wittenau', u'label': u'Wittenau'},
        {u'id': u'Zehlendorf', u'label': u'Zehlendorf'},
    ]


def type_mapping_select_options():
    options = []
    for machine, human in dataset_type_mapping().items():
        options.append({'text': human, 'value': machine})
    return options


# eventually, these values should come from a JSON API
# ids should be URIs, not just the label string
def temporal_granularity_select_options():
    return [
        {u'id': u'Keine', u'label': u'Keine'},
        {u'id': u'5 Jahre', u'label': u'5 Jahre'},
        {u'id': u'Jahr', u'label': u'Jahr'},
        {u'id': u'Quartal', u'label': u'Quartal'},
        {u'id': u'Monat', u'label': u'Monat'},
        {u'id': u'Woche', u'label': u'Woche'},
        {u'id': u'Tag', u'label': u'Tag'},
        {u'id': u'Stunde', u'label': u'Stunde'},
        {u'id': u'Minute', u'label': u'Minute'},
        {u'id': u'Sekunde', u'label': u'Sekunde'},
    ]


# eventually, these values should come from a JSON API
# ids should be URIs, not just the label string
def geo_granularity_select_options():
    return [
        {u'id': u'Deutschland', u'label': u'Deutschland'},
        {u'id': u'Berlin', u'label': u'Berlin'},
        {u'id': u'Bezirk', u'label': u'Bezirk'},
        {u'id': u'Ortsteil', u'label': u'Ortsteil'},
        {u'id': u'Prognoseraum', u'label': u'Prognoseraum'},
        {u'id': u'Bezirksregion', u'label': u'Bezirksregion'},
        {u'id': u'Planungsraum', u'label': u'Planungsraum'},
        {u'id': u'Block', u'label': u'Block'},
        {u'id': u'Einschulbereich', u'label': u'Einschulbereich'},
        {u'id': u'Kontaktbereich', u'label': u'Kontaktbereich'},
        {u'id': u'PLZ', u'label': u'PLZ'},
        {u'id': u'Stimmbezirk', u'label': u'Stimmbezirk'},
        {u'id': u'Quartiersmanagement', u'label': u'Quartiersmanagement'},
        {u'id': u'Wohnanlage', u'label': u'Wohnanlage'},
        {u'id': u'Wahlkreis', u'label': u'Wahlkreis'},
        {u'id': u'Adresse', u'label': u'Adresse'},
    ]


def state_mapping():
    return {
        'active': u'veröffentlicht',
        'deleted': u'gelöscht'
    }


def organizations_for_user(user, permission='create_dataset'):
    '''Return a list of organizations that the given user has the specified
    permission for.
    '''
    context = {'user': user}
    data_dict = {'permission': permission}
    return logic.get_action('organization_list_for_user')(context, data_dict)


def is_sysadmin(user_name):
    user = model.User.get(unicode(user_name))
    return user.sysadmin

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


def has_active_item(items):
    '''Helper function that returns True if the list of items contains
       at least one that is active. Otherwise returns False.
    '''
    for item in items:
      if item['active']:
        return True
    return False

def active_item_count(items):
    '''Helper function that returns the number of active items from a list of
       facet items.'''
    return len(active_items(items))

def active_items(items):
    '''Helper function that returns the list of all active items from 
       a list of facet items.
    '''
    return [item for item in items if item['active']]

def active_item_labels(items):
    '''Helper function that returns a comma-separated string with the labels of
       all active items from a list of facet items.
    '''
    return ', '.join([item['display_name'] for item in items if item['active']])

def label_for_sorting(sortings, sorting):
    '''Helper function to retrieve the label for a search sorting from a list of sortings.'''
    flipped = { value: key for key,value in dict(sortings).items() }
    return flipped.get(sorting, None)
