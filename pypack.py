#!/usr/bin/env python

import os
import sys
import base64
import zlib

STUB="""
#!/usr/bin/env python
import sys
import imp
import zlib
import base64

MODULES = {0}

class Importer(object):
    def find_module(self, fullname, path=None):
        if fullname in MODULES:
            return self
        return None

    def load_module(self, fullname):
        if fullname in sys.modules:
            return sys.modules[fullname]
        mod = imp.new_module(fullname)
        mod.__loader__ = self
        sys.modules[fullname] = mod
        packed_code = MODULES[fullname]
        unpacked_code = zlib.decompress(base64.b64decode(packed_code))
        mod.__file__ = "[packed module %r]" % fullname
        mod.__path__ = []
        exec unpacked_code in mod.__dict__
        return mod    

sys.meta_path = [Importer()]

# -----------------------------------------
{1}
"""

def modname(path):
    return os.path.splitext(os.path.basename(path))[0]

def slurp(path):
    return open(path).read()

def pack(scripts):
    MODULES={}
    for path in scripts[1:]:
        mod_name = modname(path)
        MODULES[mod_name] = base64.b64encode(zlib.compress(slurp(path)))
    print STUB.format(repr(MODULES), slurp(scripts[0]))
    
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Usage: pypack <script> [module-files ...]"
        print
        print "Packs a script and supporting modules into a single Python file."
        print "A combined script will be printed to standard output."
        print
        sys.exit(0)
    pack(sys.argv[1:])

