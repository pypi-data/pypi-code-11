#- Converted from:
#- http://svn.apache.org/repos/asf/httpd/httpd/trunk/docs/conf/mime.types
#- (excluding vnd. tree types)

# NOTE:
# For some reason, this file raises a syntax error when used with Python 2.6 on Linux.
# 2.7 os OK, though.

__author__      = "Graham Klyne (GK@ACM.ORG)"
__copyright__   = "Copyright 2011-2013, University of Oxford"
__license__     = "MIT (http://opensource.org/licenses/MIT)"

FileMimeTypes = (
    { ("application/andrew-inset",              ("ez",))
    , ("application/applixware",                ("aw",))
    , ("application/atom+xml",                  ("atom",))
    , ("application/atomcat+xml",               ("atomcat",))
    , ("application/atomsvc+xml",               ("atomsvc",))
    , ("application/ccxml+xml",                 ("ccxml",))
    , ("application/cdmi-capability",           ("cdmia",))
    , ("application/cdmi-container",            ("cdmic",))
    , ("application/cdmi-domain",               ("cdmid",))
    , ("application/cdmi-object",               ("cdmio",))
    , ("application/cdmi-queue",                ("cdmiq",))
    , ("application/cu-seeme",                  ("cu",))
    , ("application/davmount+xml",              ("davmount",))
    , ("application/docbook+xml",               ("dbk",))
    , ("application/dssc+der",                  ("dssc",))
    , ("application/dssc+xml",                  ("xdssc",))
    , ("application/ecmascript",                ("ecma",))
    , ("application/emma+xml",                  ("emma",))
    , ("application/epub+zip",                  ("epub",))
    , ("application/exi",                       ("exi",))
    , ("application/font-tdpfr",                ("pfr",))
    , ("application/gml+xml",                   ("gml",))
    , ("application/gpx+xml",                   ("gpx",))
    , ("application/gxf",                       ("gxf",))
    , ("application/hyperstudio",               ("stk",))
    , ("application/inkml+xml",                 ("ink","inkml",))
    , ("application/ipfix",                     ("ipfix",))
    , ("application/java-archive",              ("jar",))
    , ("application/java-serialized-object",    ("ser",))
    , ("application/java-vm",                   ("class",))
    , ("application/javascript",                ("js",))
    , ("application/json",                      ("json",))
    , ("application/jsonml+json",               ("jsonml",))
    , ("application/lost+xml",                  ("lostxml",))
    , ("application/mac-binhex40",              ("hqx",))
    , ("application/mac-compactpro",            ("cpt",))
    , ("application/mads+xml",                  ("mads",))
    , ("application/marc",                      ("mrc",))
    , ("application/marcxml+xml",               ("mrcx",))
    , ("application/mathematica",               ("ma","nb","mb",))
    , ("application/mathml+xml",                ("mathml",))
    , ("application/mbox",                      ("mbox",))
    , ("application/mediaservercontrol+xml",    ("mscml",))
    , ("application/metalink+xml",              ("metalink",))
    , ("application/metalink4+xml",             ("meta4",))
    , ("application/mets+xml",                  ("mets",))
    , ("application/mods+xml",                  ("mods",))
    , ("application/mp21",                      ("m21","mp21",))
    , ("application/mp4",                       ("mp4s",))
    , ("application/msword",                    ("doc","dot",))
    , ("application/mxf",                       ("mxf",))
    , ("application/octet-stream",              ("bin","dms","lrf","mar","so","dist","distz","pkg","bpk","dump","elc","deploy",))
    , ("application/oda",                       ("oda",))
    , ("application/oebps-package+xml",         ("opf",))
    , ("application/ogg",                       ("ogx",))
    , ("application/omdoc+xml",                 ("omdoc",))
    , ("application/onenote",                   ("onetoc","onetoc2","onetmp","onepkg",))
    , ("application/oxps",                      ("oxps",))
    , ("application/patch-ops-error+xml",       ("xer",))
    , ("application/pdf",                       ("pdf",))
    , ("application/pgp-encrypted",             ("pgp",))
    , ("application/pgp-signature",             ("asc","sig",))
    , ("application/pics-rules",                ("prf",))
    , ("application/pkcs10",                    ("p10",))
    , ("application/pkcs7-mime",                ("p7m","p7c",))
    , ("application/pkcs7-signature",           ("p7s",))
    , ("application/pkcs8",                     ("p8",))
    , ("application/pkix-attr-cert",            ("ac",))
    , ("application/pkix-cert",                 ("cer",))
    , ("application/pkix-crl",                  ("crl",))
    , ("application/pkix-pkipath",              ("pkipath",))
    , ("application/pkixcmp",                   ("pki",))
    , ("application/pls+xml",                   ("pls",))
    , ("application/postscript",                ("ai","eps","ps",))
    , ("application/prs.cww",                   ("cww",))
    , ("application/pskc+xml",                  ("pskcxml",))
    , ("application/rdf+xml",                   ("rdf",))
    , ("application/reginfo+xml",               ("rif",))
    , ("application/relax-ng-compact-syntax",   ("rnc",))
    , ("application/resource-lists+xml",        ("rl",))
    , ("application/resource-lists-diff+xml",   ("rld",))
    , ("application/rls-services+xml",          ("rs",))
    , ("application/rpki-ghostbusters",         ("gbr",))
    , ("application/rpki-manifest",             ("mft",))
    , ("application/rpki-roa",                  ("roa",))
    , ("application/rsd+xml",                   ("rsd",))
    , ("application/rss+xml",                   ("rss",))
    , ("application/rtf",                       ("rtf",))
    , ("application/sbml+xml",                  ("sbml",))
    , ("application/scvp-cv-request",           ("scq",))
    , ("application/scvp-cv-response",          ("scs",))
    , ("application/scvp-vp-request",           ("spq",))
    , ("application/scvp-vp-response",          ("spp",))
    , ("application/sdp",                       ("sdp",))
    , ("application/set-payment-initiation",    ("setpay",))
    , ("application/set-registration-initiation", ("setreg",))
    , ("application/shf+xml",                   ("shf",))
    , ("application/smil+xml",                  ("smi","smil",))
    , ("application/sparql-query",              ("rq",))
    , ("application/sparql-results+xml",        ("srx",))
    , ("application/srgs",                      ("gram",))
    , ("application/srgs+xml",                  ("grxml",))
    , ("application/sru+xml",                   ("sru",))
    , ("application/ssdl+xml",                  ("ssdl",))
    , ("application/ssml+xml",                  ("ssml",))
    , ("application/tei+xml",                   ("tei","teicorpus",))
    , ("application/thraud+xml",                ("tfi",))
    , ("application/timestamped-data",          ("tsd",))
    , ("application/voicexml+xml",              ("vxml",))
    , ("application/widget",                    ("wgt",))
    , ("application/winhlp",                    ("hlp",))
    , ("application/wsdl+xml",                  ("wsdl",))
    , ("application/wspolicy+xml",              ("wspolicy",))
    , ("application/x-7z-compressed",           ("7z",))
    , ("application/x-abiword",                 ("abw",))
    , ("application/x-ace-compressed",          ("ace",))
    , ("application/x-apple-diskimage",         ("dmg",))
    , ("application/x-authorware-bin",          ("aab","x32","u32","vox",))
    , ("application/x-authorware-map",          ("aam",))
    , ("application/x-authorware-seg",          ("aas",))
    , ("application/x-bcpio",                   ("bcpio",))
    , ("application/x-bittorrent",              ("torrent",))
    , ("application/x-blorb",                   ("blb","blorb",))
    , ("application/x-bzip",                    ("bz",))
    , ("application/x-bzip2",                   ("bz2","boz",))
    , ("application/x-cbr",                     ("cbr","cba","cbt","cbz","cb7",))
    , ("application/x-cdlink",                  ("vcd",))
    , ("application/x-cfs-compressed",          ("cfs",))
    , ("application/x-chat",                    ("chat",))
    , ("application/x-chess-pgn",               ("pgn",))
    , ("application/x-conference",              ("nsc",))
    , ("application/x-cpio",                    ("cpio",))
    , ("application/x-csh",                     ("csh",))
    , ("application/x-debian-package",          ("deb","udeb",))
    , ("application/x-dgc-compressed",          ("dgc",))
    , ("application/x-director",                ("dir","dcr","dxr","cst","cct","cxt","w3d","fgd","swa",))
    , ("application/x-doom",                    ("wad",))
    , ("application/x-dtbncx+xml",              ("ncx",))
    , ("application/x-dtbook+xml",              ("dtb",))
    , ("application/x-dtbresource+xml",         ("res",))
    , ("application/x-dvi",                     ("dvi",))
    , ("application/x-envoy",                   ("evy",))
    , ("application/x-eva",                     ("eva",))
    , ("application/x-font-bdf",                ("bdf",))
    , ("application/x-font-ghostscript",        ("gsf",))
    , ("application/x-font-linux-psf",          ("psf",))
    , ("application/x-font-otf",                ("otf",))
    , ("application/x-font-pcf",                ("pcf",))
    , ("application/x-font-snf",                ("snf",))
    , ("application/x-font-ttf",                ("ttf","ttc",))
    , ("application/x-font-type1",              ("pfa","pfb","pfm","afm",))
    , ("application/font-woff",                 ("woff",))
    , ("application/x-freearc",                 ("arc",))
    , ("application/x-futuresplash",            ("spl",))
    , ("application/x-gca-compressed",          ("gca",))
    , ("application/x-glulx",                   ("ulx",))
    , ("application/x-gnumeric",                ("gnumeric",))
    , ("application/x-gramps-xml",              ("gramps",))
    , ("application/x-gtar",                    ("gtar",))
    , ("application/x-hdf",                     ("hdf",))
    , ("application/x-install-instructions",    ("install",))
    , ("application/x-iso9660-image",           ("iso",))
    , ("application/x-java-jnlp-file",          ("jnlp",))
    , ("application/x-latex",                   ("latex",))
    , ("application/x-lzh-compressed",          ("lzh","lha",))
    , ("application/x-mie",                     ("mie",))
    , ("application/x-mobipocket-ebook",        ("prc","mobi",))
    , ("application/x-ms-application",          ("application",))
    , ("application/x-ms-shortcut",             ("lnk",))
    , ("application/x-ms-wmd",                  ("wmd",))
    , ("application/x-ms-wmz",                  ("wmz",))
    , ("application/x-ms-xbap",                 ("xbap",))
    , ("application/x-msaccess",                ("mdb",))
    , ("application/x-msbinder",                ("obd",))
    , ("application/x-mscardfile",              ("crd",))
    , ("application/x-msclip",                  ("clp",))
    , ("application/x-msdownload",              ("exe","dll","com","bat","msi",))
    , ("application/x-msmediaview",             ("mvb","m13","m14",))
    , ("application/x-msmetafile",              ("wmf","wmz","emf","emz",))
    , ("application/x-msmoney",                 ("mny",))
    , ("application/x-mspublisher",             ("pub",))
    , ("application/x-msschedule",              ("scd",))
    , ("application/x-msterminal",              ("trm",))
    , ("application/x-mswrite",                 ("wri",))
    , ("application/x-netcdf",                  ("nc","cdf",))
    , ("application/x-nzb",                     ("nzb",))
    , ("application/x-pkcs12",                  ("p12","pfx",))
    , ("application/x-pkcs7-certificates",      ("p7b","spc",))
    , ("application/x-pkcs7-certreqresp",       ("p7r",))
    , ("application/x-rar-compressed",          ("rar",))
    , ("application/x-research-info-systems",   ("ris",))
    , ("application/x-sh",                      ("sh",))
    , ("application/x-shar",                    ("shar",))
    , ("application/x-shockwave-flash",         ("swf",))
    , ("application/x-silverlight-app",         ("xap",))
    , ("application/x-sql",                     ("sql",))
    , ("application/x-stuffit",                 ("sit",))
    , ("application/x-stuffitx",                ("sitx",))
    , ("application/x-subrip",                  ("srt",))
    , ("application/x-sv4cpio",                 ("sv4cpio",))
    , ("application/x-sv4crc",                  ("sv4crc",))
    , ("application/x-t3vm-image",              ("t3",))
    , ("application/x-tads",                    ("gam",))
    , ("application/x-tar",                     ("tar",))
    , ("application/x-tcl",                     ("tcl",))
    , ("application/x-tex",                     ("tex",))
    , ("application/x-tex-tfm",                 ("tfm",))
    , ("application/x-texinfo",                 ("texinfo","texi",))
    , ("application/x-tgif",                    ("obj",))
    , ("application/x-ustar",                   ("ustar",))
    , ("application/x-wais-source",             ("src",))
    , ("application/x-x509-ca-cert",            ("der","crt",))
    , ("application/x-xfig",                    ("fig",))
    , ("application/x-xliff+xml",               ("xlf",))
    , ("application/x-xpinstall",               ("xpi",))
    , ("application/x-xz",                      ("xz",))
    , ("application/x-zmachine",                ("z1","z2","z3","z4","z5","z6","z7","z8",))
    , ("application/xaml+xml",                  ("xaml",))
    , ("application/xcap-diff+xml",             ("xdf",))
    , ("application/xenc+xml",                  ("xenc",))
    , ("application/xhtml+xml",                 ("xhtml","xht",))
    , ("application/xml",                       ("xml","xsl",))
    , ("application/xml-dtd",                   ("dtd",))
    , ("application/xop+xml",                   ("xop",))
    , ("application/xproc+xml",                 ("xpl",))
    , ("application/xslt+xml",                  ("xslt",))
    , ("application/xspf+xml",                  ("xspf",))
    , ("application/xv+xml",                    ("mxml","xhvml","xvml","xvm",))
    , ("application/yang",                      ("yang",))
    , ("application/yin+xml",                   ("yin",))
    , ("application/zip",                       ("zip",))
    , ("audio/adpcm",                           ("adp",))
    , ("audio/basic",                           ("au","snd",))
    , ("audio/midi",                            ("mid","midi","kar","rmi",))
    , ("audio/mp4",                             ("mp4a",))
    , ("audio/mpeg",                            ("mpga","mp2","mp2a","mp3","m2a","m3a",))
    , ("audio/ogg",                             ("oga","ogg","spx",))
    , ("audio/s3m",                             ("s3m",))
    , ("audio/silk",                            ("sil",))
    , ("audio/vnd.dece.audio",                  ("uva","uvva",))
    , ("audio/vnd.digital-winds",               ("eol",))
    , ("audio/vnd.dra",                         ("dra",))
    , ("audio/vnd.dts",                         ("dts",))
    , ("audio/vnd.dts.hd",                      ("dtshd",))
    , ("audio/vnd.lucent.voice",                ("lvp",))
    , ("audio/vnd.ms-playready.media.pya",      ("pya",))
    , ("audio/vnd.nuera.ecelp4800",             ("ecelp4800",))
    , ("audio/vnd.nuera.ecelp7470",             ("ecelp7470",))
    , ("audio/vnd.nuera.ecelp9600",             ("ecelp9600",))
    , ("audio/vnd.rip",                         ("rip",))
    , ("audio/webm",                            ("weba",))
    , ("audio/x-aac",                           ("aac",))
    , ("audio/x-aiff",                          ("aif","aiff","aifc",))
    , ("audio/x-caf",                           ("caf",))
    , ("audio/x-flac",                          ("flac",))
    , ("audio/x-matroska",                      ("mka",))
    , ("audio/x-mpegurl",                       ("m3u",))
    , ("audio/x-ms-wax",                        ("wax",))
    , ("audio/x-ms-wma",                        ("wma",))
    , ("audio/x-pn-realaudio",                  ("ram","ra",))
    , ("audio/x-pn-realaudio-plugin",           ("rmp",))
    , ("audio/x-wav",                           ("wav",))
    , ("audio/xm",                              ("xm",))
    , ("chemical/x-cdx",                        ("cdx",))
    , ("chemical/x-cif",                        ("cif",))
    , ("chemical/x-cmdf",                       ("cmdf",))
    , ("chemical/x-cml",                        ("cml",))
    , ("chemical/x-csml",                       ("csml",))
    , ("chemical/x-xyz",                        ("xyz",))
    , ("image/bmp",                             ("bmp",))
    , ("image/cgm",                             ("cgm",))
    , ("image/g3fax",                           ("g3",))
    , ("image/gif",                             ("gif",))
    , ("image/ief",                             ("ief",))
    , ("image/jpeg",                            ("jpeg","jpg","jpe",))
    , ("image/ktx",                             ("ktx",))
    , ("image/png",                             ("png",))
    , ("image/prs.btif",                        ("btif",))
    , ("image/sgi",                             ("sgi",))
    , ("image/svg+xml",                         ("svg","svgz",))
    , ("image/tiff",                            ("tiff","tif",))
    , ("image/webp",                            ("webp",))
    , ("image/x-3ds",                           ("3ds",))
    , ("image/x-cmu-raster",                    ("ras",))
    , ("image/x-cmx",                           ("cmx",))
    , ("image/x-freehand",                      ("fh","fhc","fh4","fh5","fh7",))
    , ("image/x-icon",                          ("ico",))
    , ("image/x-mrsid-image",                   ("sid",))
    , ("image/x-pcx",                           ("pcx",))
    , ("image/x-pict",                          ("pic","pct",))
    , ("image/x-portable-anymap",               ("pnm",))
    , ("image/x-portable-bitmap",               ("pbm",))
    , ("image/x-portable-graymap",              ("pgm",))
    , ("image/x-portable-pixmap",               ("ppm",))
    , ("image/x-rgb",                           ("rgb",))
    , ("image/x-tga",                           ("tga",))
    , ("image/x-xbitmap",                       ("xbm",))
    , ("image/x-xpixmap",                       ("xpm",))
    , ("image/x-xwindowdump",                   ("xwd",))
    , ("message/rfc822",                        ("eml","mime",))
    , ("model/iges",                            ("igs","iges",))
    , ("model/mesh",                            ("msh","mesh","silo",))
    , ("model/vrml",                            ("wrl","vrml",))
    , ("model/x3d+binary",                      ("x3db","x3dbz",))
    , ("model/x3d+vrml",                        ("x3dv","x3dvz",))
    , ("model/x3d+xml",                         ("x3d","x3dz",))
    , ("text/cache-manifest",                   ("appcache",))
    , ("text/calendar",                         ("ics","ifb",))
    , ("text/css",                              ("css",))
    , ("text/csv",                              ("csv",))
    , ("text/html",                             ("html","htm",))
    , ("text/n3",                               ("n3",))
    , ("text/plain",                            ("txt","text","conf","def","list","log","in",))
    , ("text/prs.lines.tag",                    ("dsc",))
    , ("text/richtext",                         ("rtx",))
    , ("text/sgml",                             ("sgml","sgm",))
    , ("text/tab-separated-values",             ("tsv",))
    , ("text/troff",                            ("t","tr","roff","man","me","ms",))
    , ("text/turtle",                           ("ttl",))
    , ("text/uri-list",                         ("uri","uris","urls",))
    , ("text/vcard",                            ("vcard",))
    , ("text/x-asm",                            ("s","asm",))
    , ("text/x-c",                              ("c","cc","cxx","cpp","h","hh","dic",))
    , ("text/x-fortran",                        ("f","for","f77","f90",))
    , ("text/x-java-source",                    ("java",))
    , ("text/x-opml",                           ("opml",))
    , ("text/x-pascal",                         ("p","pas",))
    , ("text/x-nfo",                            ("nfo",))
    , ("text/x-setext",                         ("etx",))
    , ("text/x-sfv",                            ("sfv",))
    , ("text/x-uuencode",                       ("uu",))
    , ("text/x-vcalendar",                      ("vcs",))
    , ("text/x-vcard",                          ("vcf",))
    , ("video/3gpp",                            ("3gp",))
    , ("video/3gpp2",                           ("3g2",))
    , ("video/h261",                            ("h261",))
    , ("video/h263",                            ("h263",))
    , ("video/h264",                            ("h264",))
    , ("video/jpeg",                            ("jpgv",))
    , ("video/jpm",                             ("jpm","jpgm",))
    , ("video/mj2",                             ("mj2","mjp2",))
    , ("video/mp4",                             ("mp4","mp4v","mpg4",))
    , ("video/mpeg",                            ("mpeg","mpg","mpe","m1v","m2v",))
    , ("video/ogg",                             ("ogv",))
    , ("video/quicktime",                       ("qt","mov",))
    , ("video/webm",                            ("webm",))
    , ("video/x-f4v",                           ("f4v",))
    , ("video/x-fli",                           ("fli",))
    , ("video/x-flv",                           ("flv",))
    , ("video/x-m4v",                           ("m4v",))
    , ("video/x-matroska",                      ("mkv","mk3d","mks",))
    , ("video/x-mng",                           ("mng",))
    , ("video/x-ms-asf",                        ("asf","asx",))
    , ("video/x-ms-vob",                        ("vob",))
    , ("video/x-ms-wm",                         ("wm",))
    , ("video/x-ms-wmv",                        ("wmv",))
    , ("video/x-ms-wmx",                        ("wmx",))
    , ("video/x-ms-wvx",                        ("wvx",))
    , ("video/x-msvideo",                       ("avi",))
    , ("video/x-sgi-movie",                     ("movie",))
    , ("video/x-smv",                           ("smv",))
    , ("x-conference/x-cooltalk",               ("ice",))
    })
