import re
import json
import functools as fn
from pathlib import Path


root = Path('cpython-dbg')
includeFix = ['Python/pyfpe.c', 'Modules/rotatingtree.c', 'Modules/tkappinit.c']


pat = re.compile(r'^[\w][\w\ \*]*[\n ]\*?(\w+)\([,\w\*\ \n\(\)]*(?:\.\.\.)?\)[\n ]?{', re.M)
longspace = re.compile(r'\s+')


def replace(p, g):
    p = p.relative_to(root)
    raw = g.group(0)
    func = g.group(1)
    sig = longspace.sub(' ', func)
    msg = f'[DBG] {sig} @ {p}'
    msg = 'if(getenv("DEBUG")!=(void*)0){puts(' + json.dumps(msg) + ');}'
    func = raw + msg
    return func


def main():
    print(f'[*] Listing all files')
    files = list(root.glob('**/*.c'))
    for i, p in enumerate(files):
        print(f'[*] Patching ({i+1} / {len(files)}): {p}')
        with p.open() as f:
            content = pat.sub(fn.partial(replace, p), f.read())
        with p.open('w') as f:
            f.write(content)
    print('')

    print(f'[*] Fixing includes')
    for i, p in enumerate(includeFix):
        print(f'[*] Patching ({i+1} / {len(includeFix)}): {root / p}')
        with open(root / p, 'r') as f:
            content = f.read()
        with open(root / p, 'w') as f:
            f.write('#include <stdio.h>\n#include <stdlib.h>\n' + content)


main()
