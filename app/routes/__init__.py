try:
    from secret import dumb_decryption
except:
    import json
    print('Score decrypter not found, will not be able to parse scores')
    dumb_decryption = lambda x: json.loads(x)

from . import api, main, static

