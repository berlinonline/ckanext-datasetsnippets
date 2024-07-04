# encoding: utf-8

from collections import OrderedDict
from flask import Blueprint, make_response, request
import logging
import re
from urllib.parse import urlencode

from ckan.common import asbool
import ckan.lib.base as base
import ckan.lib.helpers as h
import ckan.logic as logic
import ckan.model as model
import ckan.plugins as plugins
from ckan.plugins import toolkit
from ckan.common import _, c, request, config

LOG = logging.getLogger(__name__)
ROOT_BREADCRUMB_MIN_LENGTH = 1
ROOT_BREADCRUMB_MAX_LENGTH = 25

NotAuthorized = logic.NotAuthorized
check_access = logic.check_access

def _is_breadcrumb_valid(breadcrumb: str) -> bool:
    '''
    `breadcrumb` length < ROOT_BREADCRUMB_MAX_LENGTH and > ROOT_BREADCRUMB_MIN_LENGTH,
    and only contain alphanumeric characters, space or dash.
    If `breadcrumb` length is 1, it must only contain alphanumeric characters.
    '''
    if len(breadcrumb) < ROOT_BREADCRUMB_MAX_LENGTH and len(breadcrumb) >= ROOT_BREADCRUMB_MIN_LENGTH:
      disallowed = re.compile(r'[^A-Za-z0-9- ]').search
      if len(breadcrumb) == 1:
          disallowed = re.compile(r'[^A-Za-z0-9]').search
      return not bool(disallowed(breadcrumb))
    else:
        return False

def _encode_params(params):
    return [(k, v.encode('utf-8') if isinstance(v, str) else str(v))
            for k, v in params]

def _finish(status_int, response_data=None):
    '''When a controller method has completed, call this method
    to prepare the response.
    @return response message - return this value from the controller
                                method
                e.g. return self._finish(404, 'Package not found')

    Shortened version of from ckan/controllers/api._finish()
    '''
    assert(isinstance(status_int, int))
    response_msg = ''
    response_headers = {}
    if response_data is not None:
        response_headers['Content-Type'] = 'application/json;charset=utf-8'
        response_msg = h.json.dumps(
            response_data,
            for_json=True)  # handle objects with for_json methods
    return make_response(response_msg, status_int, response_headers)

def show_latest_datasets():
    try:
        context = {'model': model, 'user': c.user,
                   'auth_user_obj': c.userobj}
        check_access('snippet_read', context)
    except NotAuthorized:
        toolkit.abort(403, _('Not authorized to see this page'))

    template = "datasetsnippets/snippets/recent_packages.html"
    output = base.render(template)

    data = {
        "title": "Latest Datasets",
        "content": output
    }

    return _finish(200, data)

def read_dataset(id):
    context = {
        'model': model,
        'session': model.Session,
        'user': c.user,
        'for_view': True,
        'auth_user_obj': c.userobj,
    }
    try:
        context = {'model': model, 'user': c.user,
                   'auth_user_obj': c.userobj}
        check_access('snippet_read', context)
    except NotAuthorized:
        toolkit.abort(403, _('Not authorized to see this page'))

    try:
        c.pkg_dict = toolkit.get_action('package_show')(context, {'id': id})
    except toolkit.ObjectNotFound:
        toolkit.abort(404)

    print(f"private: {c.pkg_dict['private']}")
    print(f"state: {c.pkg_dict['state']}")
    print(c.pkg_dict)
    assert(False)
    # even if the requesting user/token has permission, don't ever return
    # deleted or private datasets
    if c.pkg_dict['state'] == 'deleted' or c.pkg_dict['private']:
        toolkit.abort(404)

    if 'root_breadcrumb' in request.args:
        root_breadcrumb = request.args.get('root_breadcrumb')
        if not _is_breadcrumb_valid(root_breadcrumb):
          data = {
              "success": False,
              "message": f"Parameter 'root_breadcrumb' is invalid (must be longer than {ROOT_BREADCRUMB_MIN_LENGTH} and no longer than {ROOT_BREADCRUMB_MAX_LENGTH} and match /A-Za-z0-9- /)."
          }
          return _finish(400, data)
    else:
        root_breadcrumb = config.get(
        'datasetsnippets.default_root_breadcrumb', 'Homepage')

    template = "datasetsnippets/dataset.html"
    output = base.render(template, extra_vars={"root_breadcrumb": root_breadcrumb})

    data = {
        "title": c.pkg_dict['title'],
        "content": output
    }

    return _finish(200, data)

def search_dataset():
    from ckan.lib.search import SearchError, SearchQueryError

    package_type = "dataset"

    try:
        context = {'model': model, 'user': c.user,
                    'auth_user_obj': c.userobj}
        check_access('snippet_read', context)
    except NotAuthorized:
        toolkit.abort(403, _('Not authorized to see this page'))

    if 'root_breadcrumb' in request.args:
        root_breadcrumb = request.args.get('root_breadcrumb')
        if not _is_breadcrumb_valid(root_breadcrumb):
            data = {
                "success": False,
                "message": f"Parameter 'root_breadcrumb' is invalid (must be longer than {ROOT_BREADCRUMB_MIN_LENGTH} and no longer than {ROOT_BREADCRUMB_MAX_LENGTH} and match /A-Za-z0-9- /)."
            }
            return _finish(400, data)
    else:
        root_breadcrumb = config.get(
        'datasetsnippets.default_root_breadcrumb', 'Homepage')

    # remove the root_breadcrumb parameter if present (will confuse search)
    params_nobreadcrumb = [(k, v) for k, v in request.params.items()
                        if k != 'root_breadcrumb']

    # unicode format (decoded from utf8)
    q = c.q = request.params.get('q', u'')
    c.query_error = False
    page = h.get_page_number(request.params)

    limit = int(config.get('datasetsnippets.datasets_per_page', 20))

    # most search operations should reset the page counter:
    params_nopage = [(k, v) for k, v in params_nobreadcrumb
                        if k != 'page']

    def remove_field(key, value=None, replace=None):
        return h.remove_url_param(key, value=value, replace=replace,
                                    controller='package', action='search',
                                    alternative_url="/datensaetze")

    c.remove_field = remove_field

    sort_by = request.params.get('sort', None)
    params_nosort = [(k, v) for k, v in params_nopage if k != 'sort']

    if not sort_by:
        c.sort_by_fields = []
    else:
        c.sort_by_fields = [field.split()[0]
                            for field in sort_by.split(',')]

    c.search_url_params = urlencode(_encode_params(params_nopage))

    try:
        c.fields = []
        # c.fields_grouped will contain a dict of params containing
        # a list of values eg {'tags':['tag1', 'tag2']}
        c.fields_grouped = {}
        search_extras = {}
        fq = ''
        for (param, value) in request.args.items(multi=True):
            # remove the root_breadcrumb parameter if present (will confuse search)
            if param not in ['q', 'page', 'sort', 'root_breadcrumb'] \
                    and len(value) and not param.startswith('_'):
                c.fields.append((param, value))
                fq += f' {param}:"{value}"'
                c.fields_grouped.setdefault(param, [])
                c.fields_grouped[param].append(value)

        context = {'model': model, 'session': model.Session,
                    'user': c.user, 'for_view': True,
                    'auth_user_obj': c.userobj}

        # Unless changed via config options, don't show non standard
        # dataset types on the default search page
        if not asbool(
                config.get('ckan.search.show_all_types', 'False')):
            fq += ' +dataset_type:dataset'

        facets = OrderedDict()

        default_facet_titles = {
            'organization': _('Organizations'),
            'groups': _('Groups'),
            'tags': _('Tags'),
            'res_format': _('Formats'),
            'license_id': _('Licenses'),
            }

        for facet in h.facets():
            if facet in default_facet_titles:
                facets[facet] = default_facet_titles[facet]
            else:
                facets[facet] = facet

        # Facet titles
        for plugin in plugins.PluginImplementations(plugins.IFacets):
            # we currently don't use an IFacets implementation, so this does not need
            # to be tested
            facets = plugin.dataset_facets(facets, package_type)  # pragma: no cover

        c.facet_titles = facets

        data_dict = {
            'q': q,
            'fq': fq.strip(),
            'facet.field': list(facets.keys()),
            'rows': limit,
            'start': (page - 1) * limit,
            'sort': sort_by,
            'extras': search_extras,
            'include_drafts': False,
            'include_private': False,
        }

        query = toolkit.get_action('package_search')(context, data_dict)
        c.sort_by_selected = query['sort']

        c.page = h.Page(
            collection=query['results'],
            page=page,
            item_count=query['count'],
            items_per_page=limit
        )
        c.search_facets = query['search_facets']
        c.page.items = query['results']
    except SearchQueryError as se:  # pragma: no cover
        # User's search parameters are invalid, in such a way that is not
        # achievable with the web interface, so return a proper error to
        # discourage spiders which are the main cause of this.
        LOG.info(f'Dataset search query rejected: {se.args}')  # pragma: no cover
        toolkit.abort(400, _(f'Invalid search query: {str(se)}'))  # pragma: no cover
    except SearchError as se:  # pragma: no cover
        # May be bad input from the user, but may also be more serious like
        # bad code causing a SOLR syntax error, or a problem connecting to
        # SOLR
        LOG.error(f'Dataset search error: {se.args}')  # pragma: no cover
        c.query_error = True  # pragma: no cover
        c.search_facets = {}  # pragma: no cover
        c.page = h.Page(collection=[])  # pragma: no cover
    except NotAuthorized:  # pragma: no cover
        toolkit.abort(403, _('Not authorized to see this page'))  # pragma: no cover

    c.search_facets_limits = {}
    for facet in c.search_facets.keys():
        try:
            limit = int(request.params.get(f'_{facet}_limit',
                        int(config.get('search.facets.default', 10))))
        except ValueError:
            toolkit.abort(400, _('Parameter "_{facet}_limit" is not an integer'))
        c.search_facets_limits[facet] = limit

    template = "datasetsnippets/search.html"
    output = base.render(template, extra_vars={"root_breadcrumb": root_breadcrumb})

    data = {
        "title": u'Index' ,
        "content": output
    }

    return _finish(200, data)


snippetapi = Blueprint('snippetapi', __name__)
snippetapi.add_url_rule(u'/snippet/dataset/<id>',
                        methods=[u'GET'], view_func=read_dataset)
snippetapi.add_url_rule(u'/snippet/dataset',
                        methods=[u'GET'], view_func=search_dataset)
snippetapi.add_url_rule(u'/snippet/latest_datasets',
                        methods=[u'GET'], view_func=show_latest_datasets)

