# encoding: utf-8
import logging

from six.moves.urllib.parse import urlparse
from flask import Blueprint, make_response
import six
from six import text_type
from dateutil.tz import tzutc
from feedgen.feed import FeedGenerator
from ckan.common import _, config, g, request
import ckan.lib.helpers as h
import ckan.lib.base as base
import ckan.model as model
import ckan.logic as logic
import ckan.plugins as plugins
import json

log = logging.getLogger(__name__)

drupal_feeds = Blueprint(u'drupal_feeds', __name__, url_prefix=u'/drupal_feeds')

ITEMS_LIMIT = config.get(u'ckan.feeds.limit', 20)
BASE_URL = config.get(u'ckanext.datasetsnippets.datenportal_url')
SITE_TITLE = config.get(u'ckanext.datasetsnippets.datenportal_title', u'Berlin Open Data')


def _package_search(data_dict):
    """
    Helper method that wraps the package_search action.

     * unless overridden, sorts results by metadata_modified date
     * unless overridden, sets a default item limit
    """
    context = {
        u'model': model,
        u'session': model.Session,
        u'user': g.user,
        u'auth_user_obj': g.userobj
    }

    if u'sort' not in data_dict or not data_dict['sort']:
        data_dict['sort'] = u'metadata_modified desc'

    if u'rows' not in data_dict or not data_dict['rows']:
        data_dict['rows'] = ITEMS_LIMIT

    # package_search action modifies the data_dict, so keep our copy intact.
    query = logic.get_action(u'package_search')(context, data_dict.copy())

    return query['count'], query['results']


def _enclosure(pkg):
    url = config.get(u'ckan.url', u'').strip() + '/datensaetze/' + pkg['name']
    enc = Enclosure(url)
    enc.type = u'application/json'
    enc.length = text_type(len(json.dumps(pkg)))
    return enc


def _set_extras(**kw):
    extras = []
    for key, value in six.iteritems(kw):
        extras.append({key: value})
    return extras


class Enclosure(text_type):
    def __init__(self, url):
        self.url = url
        self.length = u'0'
        self.mime_type = u'application/json'


class DrupalCKANFeed(FeedGenerator):
    def __init__(
        self,
        feed_title,
        feed_link,
        feed_description,
        language,
        author_name,
        feed_guid,
        feed_url,
        previous_page,
        next_page,
        first_page,
        last_page,
    ):
        super(DrupalCKANFeed, self).__init__()

        self.title(feed_title)
        self.link(href=feed_link, rel=u"alternate")
        self.description(feed_description)
        self.language(language)
        self.author({u"name": author_name})
        self.id(feed_guid)
        self.link(href=feed_url, rel=u"self")
        links = (
            (u"prev", previous_page),
            (u"next", next_page),
            (u"first", first_page),
            (u"last", last_page),
        )
        for rel, href in links:
            if not href:
                continue
            self.link(href=href, rel=rel)

    def writeString(self, encoding):
        return self.rss_str(pretty=True).decode(encoding)

    def add_item(self, **kwargs):
        entry = self.add_entry()
        for key, value in kwargs.items():
            if key in {u"published", u"updated"} and not value.tzinfo:
                value = value.replace(tzinfo=tzutc())
            elif key == u'unique_id':
                key = u'id'
            elif key == u'categories':
                key = u'category'
                value = [{u'term': t} for t in value]
            elif key == u'link':
                value = {u'href': value}
            elif key == u'author_name':
                key = u'author'
                value = {u'name': value}
            elif key == u'author_email':
                key = u'author'
                value = {u'email': value}

            key = key.replace(u"field_", u"")
            getattr(entry, key)(value)


def output_feed(results, feed_title, feed_description, feed_link, feed_url,
                navigation_urls, feed_guid):
    author_name = config.get(u'ckan.feeds.author_name', u'').strip() or \
        config.get(u'ckan.site_id', u'').strip()

    # TODO: language
    feed_class = DrupalCKANFeed
    for plugin in plugins.PluginImplementations(plugins.IFeed):
        if hasattr(plugin, u'get_feed_class'):
            feed_class = plugin.get_feed_class()

    feed = feed_class(
        feed_title,
        feed_link,
        feed_description,
        language=u'en',
        author_name=author_name,
        feed_guid=feed_guid,
        feed_url=feed_url,
        previous_page=navigation_urls[u'previous'],
        next_page=navigation_urls[u'next'],
        first_page=navigation_urls[u'first'],
        last_page=navigation_urls[u'last'], )

    revert_results = results[::-1]

    for pkg in revert_results:
        additional_fields = {}

        for plugin in plugins.PluginImplementations(plugins.IFeed):
            if hasattr(plugin, u'get_item_additional_fields'):
                additional_fields = plugin.get_item_additional_fields(pkg)

        feed.add_item(
            title=pkg.get(u'title', u''),
            link = config.get(u'ckanext.datasetsnippets.datenportal_url', u'').strip() + '/datensaetze/' + pkg['name'],
            description=pkg.get(u'notes', u''),
            updated=h.date_str_to_datetime(pkg.get(u'metadata_modified')),
            published=h.date_str_to_datetime(pkg.get(u'metadata_created')),
            unique_id=_create_rss_id(u'/dataset/%s' % pkg['id']),
            author_name=pkg.get(u'author', u''),
            author_email=pkg.get(u'author_email', u''),
            categories=[t[u'name'] for t in pkg.get(u'tags', [])],
            **additional_fields)

    resp = make_response(feed.writeString(u'utf-8'), 200)
    resp.headers['Content-Type'] = u'application/rss+xml'
    return resp


def group(id):
    try:
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj
        }
        group_dict = logic.get_action(u'group_show')(context, {u'id': id})
    except logic.NotFound:
        base.abort(404, _(u'Group not found'))
    except logic.NotAuthorized:
        base.abort(403, _(u'Not authorized to see this page'))

    return group_or_organization(group_dict, is_org=False)


def organization(id):
    try:
        context = {
            u'model': model,
            u'session': model.Session,
            u'user': g.user,
            u'auth_user_obj': g.userobj
        }
        group_dict = logic.get_action(u'organization_show')(context, {
            u'id': id
        })
    except logic.NotFound:
        base.abort(404, _(u'Organization not found'))
    except logic.NotAuthorized:
        base.abort(403, _(u'Not authorized to see this page'))

    return group_or_organization(group_dict, is_org=True)


def tag(id):
    data_dict, params = _parse_url_params()
    data_dict['fq'] = u'tags: "%s"' % id

    item_count, results = _package_search(data_dict)

    navigation_urls = _navigation_urls(
        params,
        item_count=item_count,
        limit=data_dict['rows'],
        controller=u'feeds',
        action=u'tag',
        id=id)

    feed_url = _feed_url(params, controller=u'feeds', action=u'tag', id=id)

    alternate_url = _alternate_url(params, tags=id)

    title = u'%s - Tag: "%s"' % (SITE_TITLE, id)
    desc = u'Recently created or updated datasets on %s by tag: "%s"' % \
           (SITE_TITLE, id)
    guid = _create_rss_id(u'/drupal_feeds/tag/%s.rss' % id)

    return output_feed(
        results,
        feed_title=title,
        feed_description=desc,
        feed_link=alternate_url,
        feed_guid=guid,
        feed_url=feed_url,
        navigation_urls=navigation_urls)


def group_or_organization(obj_dict, is_org):
    data_dict, params = _parse_url_params()
    if is_org:
        key = u'owner_org'
        value = obj_dict['id']
        group_type = u'organization'
    else:
        key = u'groups'
        value = obj_dict['name']
        group_type = u'group'

    data_dict['fq'] = u'{0}: "{1}"'.format(key, value)
    item_count, results = _package_search(data_dict)

    navigation_urls = _navigation_urls(
        params,
        item_count=item_count,
        limit=data_dict['rows'],
        controller=u'feeds',
        action=group_type,
        id=obj_dict['name'])
    feed_url = _feed_url(
        params, controller=u'feeds', action=group_type, id=obj_dict['name'])
    # site_title = SITE_TITLE
    if is_org:
        guid = _create_rss_id(
            u'drupal_feeds/organization/%s.rss' % obj_dict['name'])
        alternate_url = _alternate_url(params, organization=obj_dict['name'])
        desc = u'Recently created or updated datasets on %s '\
               'by organization: "%s"' % (SITE_TITLE, obj_dict['title'])
        title = u'%s - Organization: "%s"' % (SITE_TITLE, obj_dict['title'])

    else:
        guid = _create_rss_id(u'drupal_feeds/group/%s.rss' % obj_dict['name'])
        alternate_url = _alternate_url(params, groups=obj_dict['name'])
        desc = u'Recently created or updated datasets on %s '\
               'by group: "%s"' % (SITE_TITLE, obj_dict['title'])
        title = u'%s - Group: "%s"' % (SITE_TITLE, obj_dict['title'])

    return output_feed(
        results,
        feed_title=title,
        feed_description=desc,
        feed_link=alternate_url,
        feed_guid=guid,
        feed_url=feed_url,
        navigation_urls=navigation_urls)


def _parse_url_params():
    """
    Constructs a search-query dict from the URL query parameters.

    Returns the constructed search-query dict, and the valid URL
    query parameters.
    """
    page = h.get_page_number(request.params)

    limit = ITEMS_LIMIT
    data_dict = {u'start': (page - 1) * limit, u'rows': limit}

    # Filter ignored query parameters
    valid_params = ['page']
    params = dict((p, request.params.get(p)) for p in valid_params
                  if p in request.params)
    return data_dict, params


def general():
    '''
        All Datasets of the portal
    '''
    data_dict, params = _parse_url_params()
    data_dict['q'] = u'*:*'

    item_count, results = _package_search(data_dict)

    navigation_urls = _navigation_urls(
        params,
        item_count=item_count,
        limit=data_dict['rows'],
        controller=u'feeds',
        action=u'general')

    feed_url = _feed_url(params, controller=u'feeds', action=u'general')

    alternate_url = _alternate_url(params)

    guid = _create_rss_id(u'/drupal_feeds/dataset.rss')

    desc = u'Recently created or updated datasets on %s' % SITE_TITLE

    return output_feed(
        results,
        feed_title=SITE_TITLE,
        feed_description=desc,
        feed_link=alternate_url,
        feed_guid=guid,
        feed_url=feed_url,
        navigation_urls=navigation_urls)


def custom():
    """
    Custom rss feed

    """
    q = request.params.get(u'q', u'')
    fields = request.params.get(u'fields', u'')
    fq = u''
    search_params = {}
    for (param, value) in request.params.items():
        if param not in [u'q', u'page', u'sort'] \
                and len(value) and not param.startswith(u'_'):
            search_params[param] = value
            fq += u'%s:%s' % (param, value)

    page = h.get_page_number(request.params)

    limit = ITEMS_LIMIT
    data_dict = {
        u'q': q,
        u'fq': fq,
        u'start': (page - 1) * limit,
        u'rows': limit,
        u'sort': request.params.get(u'sort', None)
    }

    item_count, results = _package_search(data_dict)

    navigation_urls = _navigation_urls(
        request.params,
        item_count=item_count,
        limit=data_dict['rows'],
        controller=u'feeds',
        action=u'custom')

    feed_url = _feed_url(request.params, controller=u'feeds', action=u'custom')

    rss_url = h._url_with_params(u'/drupal_feeds/custom.rss', search_params.items())

    alternate_url = _alternate_url(request.params)

    return output_feed(
        results,
        feed_title=u'%s - Datasets' % SITE_TITLE,
        feed_description=u'Recently created or updated'
        ' datasets on %s. Custom query: \'%s\'' % (SITE_TITLE, q),
        feed_link=alternate_url,
        feed_guid=_create_rss_id(rss_url),
        feed_url=feed_url,
        navigation_urls=navigation_urls)


def _alternate_url(params, **kwargs):
    search_params = params.copy()
    search_params.update(kwargs)

    # Can't count on the page sizes being the same on the search results
    # view.  So provide an alternate link to the first page, regardless
    # of the page we're looking at in the feed.
    search_params.pop(u'page', None)
    return _feed_url(search_params, controller=u'dataset', action=u'search')


def _feed_url(query, controller, action, **kwargs):
    """
    Constructs the url for the given action.  Encoding the query
    parameters.
    """
    for item in six.iteritems(query):
        kwargs['query'] = item
    return h.url_for(controller=controller, action=action, **kwargs)


def _navigation_urls(query, controller, action, item_count, limit, **kwargs):
    """
    Constructs and returns first, last, prev and next links for paging
    """

    urls = dict((rel, None) for rel in u'previous next first last'.split())

    page = int(query.get(u'page', 1))

    # first: remove any page parameter
    first_query = query.copy()
    first_query.pop(u'page', None)
    urls['first'] = _feed_url(first_query, controller,
                              action, **kwargs)

    # last: add last page parameter
    last_page = (item_count / limit) + min(1, item_count % limit)
    last_query = query.copy()
    last_query['page'] = last_page
    urls['last'] = _feed_url(last_query, controller,
                             action, **kwargs)

    # previous
    if page > 1:
        previous_query = query.copy()
        previous_query['page'] = page - 1
        urls['previous'] = _feed_url(previous_query, controller,
                                     action, **kwargs)
    else:
        urls['previous'] = None

    # next
    if page < last_page:
        next_query = query.copy()
        next_query['page'] = page + 1
        urls['next'] = _feed_url(next_query, controller,
                                 action, **kwargs)
    else:
        urls['next'] = None

    return urls


def _create_rss_id(resource_path, authority_name=None, date_string=None):
    """
    Helper method that creates an rss id for a feed or entry.

    resource_path
        The resource path that uniquely identifies the feed or element.  This
        mustn't be something that changes over time for a given entry or feed.
        And does not necessarily need to be resolvable.

        e.g. ``"/group/933f3857-79fd-4beb-a835-c0349e31ce76"`` could represent
        the feed of datasets belonging to the identified group.

    authority_name
        The domain name or email address of the publisher of the feed.  See [3]
        for more details.  If ``None`` then the domain name is taken from the
        config file.  First trying ``ckan.feeds.authority_name``, and failing
        that, it uses ``ckan.site_url``.  Again, this should not change over
        time.
    """
    if authority_name is None:
        authority_name = config.get('ckan.feeds.authority_name', '').strip()
        if not authority_name:
            site_url = config.get(u'ckanext.datasetsnippets.datenportal_url', u'').strip()
            authority_name = urlparse(site_url).netloc

    if not authority_name:
        log.warning('No authority_name available for feed generation. '
                    'Generated feed might be invalid.')

    # Construct the GUID as a full URL
    if authority_name:
        return f"http://{authority_name}{resource_path}"
    else:
        # Fallback to just the resource path if authority_name is not available
        return resource_path


# Routing
drupal_feeds.add_url_rule(u'/dataset.rss', methods=[u'GET'], view_func=general)
drupal_feeds.add_url_rule(u'/custom.rss', methods=[u'GET'], view_func=custom)
drupal_feeds.add_url_rule(u'/tag/<string:id>.rss', methods=[u'GET'], view_func=tag)
drupal_feeds.add_url_rule(
    u'/group/<string:id>.rss', methods=[u'GET'], view_func=group)
drupal_feeds.add_url_rule(
    u'/organization/<string:id>.rss',
    methods=[u'GET'],
    view_func=organization)
