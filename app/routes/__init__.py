from flask import current_app, request, url_for

try:
    from secret import dumb_decryption
except:
    import json
    print('Score decrypter not found, will not be able to parse scores')
    dumb_decryption = lambda x: json.loads(x)

def build_pager(route, data, per_page=None, **kwargs):
    page = request.args.get('page', 1, type=int)
    per_page = per_page or current_app.config['ITEMS_PER_PAGE']
    pagination = data.paginate(page, per_page, False)
    return {
        'next_url': url_for(route, page=pagination.next_num, **kwargs) \
            if pagination.has_next else None,
        'prev_url': url_for(route, page=pagination.prev_num, **kwargs) \
            if pagination.has_prev else None,
        'current_url': url_for(route, page=page, **kwargs),
        'page': page,
        'items': pagination.items
    }

from . import api, main, static

