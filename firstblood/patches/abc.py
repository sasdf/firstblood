def getAllSubclasses(abc, blacklist):
    res = []
    blacklist = dict.fromkeys(blacklist)
    for klass in object.__subclasses__():
        if issubclass(klass, abc) and klass.__module__ not in blacklist:
            res.append(klass)
    return set(res)


if __name__ == '__main__':
    from collections.abc import Iterable
    its = getAllSubclasses(Iterable)
    print(its)
    from IPython import embed
    embed()
