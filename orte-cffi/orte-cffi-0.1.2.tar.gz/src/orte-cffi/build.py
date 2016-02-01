import subprocess
import os
from cffi import FFI

def ompi_info_path(key):

    cmd = ['ompi_info', '--path', key, '--parseable']

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr= p.communicate()

    if p.returncode != 0:
        raise Exception(stderr)

    p_str, l_str, path = stdout.split(':')
    if p_str.strip() != 'path':
        raise Exception('Parse error')
    if l_str.strip() != key:
        raise Exception('Parse error')

    path = path.strip()

    if not os.path.isdir(path):
        raise Exception('Path "%s" is not an existing directory' % path)
    
    return path


def get_pkgconfig_dir():

    libdir = ompi_info_path('libdir')

    pkgdir = os.path.join(libdir, 'pkgconfig')
    if not os.path.isdir(pkgdir):
        raise Exception('Path "%s" is not an existing directory' % pkgdir)
    
    return pkgdir


def pkgconfig(libname, variables=None):

    cmd = ['pkg-config', '--cflags-only-I', '--libs-only-L',  libname]

    if variables:
        for k,v in variables.iteritems():
            cmd.append('--define-variable=%s=%s' % (k, v))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr= p.communicate()

    if p.returncode != 0:
        raise Exception(stderr)

    include_dirs = []
    library_dirs = []

    for item in stdout.split():
        if item.startswith("-L"):
            library_dirs.append(item[2:])
        elif item.startswith("-I"):
            include_dirs.append(item[2:])

    return {'include_dirs': include_dirs,
            'library_dirs': library_dirs}


# Get the pkgconfigdir from orte_info and export to environment
pkgconfig_dir = get_pkgconfig_dir()
os.environ['PKG_CONFIG_PATH'] = pkgconfig_dir

# Get the pkgincludedir from ompi_info
pkgincludedir = ompi_info_path('pkgincludedir')
pkgcfg = pkgconfig('orte', variables={'pkgincludedir': pkgincludedir})

include_dirs = pkgcfg['include_dirs']
library_dirs = pkgcfg['library_dirs']

ffi = FFI()

ffi.set_source("orte_cffi", """

#include "orte/orted/orted_submit.h"

""",
    libraries=["open-rte"],
    include_dirs=include_dirs,
    library_dirs=library_dirs
)

ffi.cdef("""

/* Types */
typedef ... orte_job_t;
typedef void (*orte_submit_cbfunc_t)(int index, orte_job_t *jdata, int ret, void *cbdata);

/* Functions */
int orte_submit_init(int argc, char *argv[]);
int orte_submit_job(char *cmd[],
                    orte_submit_cbfunc_t launch_cb, void *launch_cbdata,
                    orte_submit_cbfunc_t complete_cb, void *complete_cbdata);
void orte_submit_finalize(void);

/* Callbacks */
extern "Python" void launch_cb(int, orte_job_t *, int, void *);
extern "Python" void finish_cb(int, orte_job_t *, int, void *);

""")

if __name__ == "__main__":
    ffi.compile()
