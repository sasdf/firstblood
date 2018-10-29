import json
from .patch import patch, needFlush


@needFlush
def addMethods():
    patch(dict, 'json', property(json.dumps))
    patch(int, 'json', property(json.dumps))
    patch(list, 'json', property(json.dumps))
    patch(set, 'json', property(json.dumps))
    patch(str, 'json', property(json.dumps))


@needFlush
def patchMethods():
    pass


@needFlush
def patchAll():
    addMethods()
    patchMethods()


if __name__ == '__main__':
    from IPython import embed
    patchAll()
    embed()
