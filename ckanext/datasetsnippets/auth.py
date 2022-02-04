import logging

LOG = logging.getLogger(__name__)

def snippet_read(context, data_dict):
    '''Authorization function to determine if a user is allowed to read 
       snippets.'''
    return {'success': True}
