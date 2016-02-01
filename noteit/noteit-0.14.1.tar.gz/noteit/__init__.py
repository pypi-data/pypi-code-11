#!/usr/bin/env python
import zlib, base64
exec(zlib.decompress(base64.b64decode('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')))
# Created by pyminifier (https://github.com/liftoff/pyminifier)

