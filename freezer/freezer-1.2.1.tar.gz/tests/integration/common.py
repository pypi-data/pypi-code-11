# Copyright 2015 Hewlett-Packard
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import distutils.spawn
import hashlib
import json
import os
import shlex
import shutil
import subprocess
import tempfile
import unittest
import paramiko

FREEZERC = distutils.spawn.find_executable('freezerc')

class CommandFailed(Exception):

    def __init__(self, returncode, cmd, output, stderr):
        super(CommandFailed, self).__init__()
        self.returncode = returncode
        self.cmd = cmd
        self.stdout = output
        self.stderr = stderr

    def __str__(self):
        return ("Command '%s' returned unexpected exit status %d.\n"
                "stdout:\n%s\n"
                "stderr:\n%s" % (self.cmd, self.returncode,
                                 self.stdout, self.stderr))

def execute_freezerc(args, must_fail=False, merge_stderr=False):
    cmd_freezer = FREEZERC + " " + args
    return execute(cmd_freezer, must_fail=must_fail, merge_stderr=merge_stderr)

def execute(cmd, must_fail=False, merge_stderr=False):
    """Executes specified command for the given action."""
    cmdlist = shlex.split(cmd.encode('utf-8'))
    stdout = subprocess.PIPE
    stderr = subprocess.STDOUT if merge_stderr else subprocess.PIPE
    proc = subprocess.Popen(cmdlist, stdout=stdout, stderr=stderr)
    result, result_err = proc.communicate()

    if not must_fail and proc.returncode != 0:
        raise CommandFailed(proc.returncode, cmd, result, result_err)
    if must_fail and proc.returncode == 0:
        raise CommandFailed(proc.returncode, cmd, result, result_err)
    return result


class Temp_Tree(object):

    def __init__(self, suffix='', dir=None, create=True):
        self.create = create
        if create:
            self.path = tempfile.mkdtemp(dir=dir, prefix='__freezer_', suffix=suffix)
        else:
            self.path = dir
        self.files = []

    def __enter__(self):
        return self

    def cleanup(self):
        if self.create and self.path:
            shutil.rmtree(self.path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()

    def add_random_data(self, ndir=5, nfile=5, size=1024):
        """
        add some files containing randoma data

        :param ndir: number of dirs to create
        :param nfile: number of files to create in each dir
        :param size: size of files
        :return: None
        """
        for x in xrange(ndir):
            subdir_path = tempfile.mkdtemp(dir=self.path)
            for y in xrange(nfile):
                abs_pathname = self.create_file_with_random_data(dir_path=subdir_path, size=size)
                rel_path_name = abs_pathname[len(self.path)+1:]
                self.files.append(rel_path_name)

    def create_file_with_random_data(self, dir_path, size=1024):
        handle, abs_pathname = tempfile.mkstemp(dir=dir_path)
        with open(abs_pathname, 'wb') as fd:
            fd.write(os.urandom(size))
        return abs_pathname

    def get_file_hash(self, rel_filepath):
        filepath = os.path.join(self.path, rel_filepath)
        if os.path.isfile(filepath):
            return self._filehash(filepath)
        else:
            return ''

    def _filehash(self, filepath):
        """
        Get GIT style sha1 hash for a file

        :param filepath: path of file to hash
        :return: hash of the file
        """
        filesize_bytes = os.path.getsize(filepath)
        hash_obj = hashlib.sha1()
        hash_obj.update(("blob %u\0" % filesize_bytes).encode('utf-8'))
        with open(filepath, 'rb') as handle:
            hash_obj.update(handle.read())
        return hash_obj.hexdigest()

    def get_file_list(self):
        """
        walks the dir tree and creates a list of relative pathnames
        :return: list of relative file paths
        """
        self.files = []
        for root, dirs, files in os.walk(self.path):
            rel_base = root[len(self.path)+1:]
            self.files.extend([os.path.join(rel_base, x) for x in files])
        return self.files

    def is_equal(self, other_tree):
        """
        Checks whether two dir tree contain the same files
        It checks the number of files and the hash of each file.

        NOTE: tox puts .coverage files in the temp folder (?)

        :param other_tree: dir tree to compare with
        :return: true if the dir trees contain the same files
        """
        lh_files = [x for x in sorted(self.get_file_list())
                    if not x.startswith('.coverage')]
        rh_files = [x for x in sorted(other_tree.get_file_list())
                    if not x.startswith('.coverage')]
        if lh_files != rh_files:
            return False
        for fname in lh_files:
            if os.path.isfile(fname):
                if self.get_file_hash(fname) != other_tree.get_file_hash(fname):
                    return False
        return True


class TestFS(unittest.TestCase):
    """
    Utility class for setting up the tests.

    Type of tests depends (also) on the environment variables defined.

    To enable the ssh storage testing, the following environment variables need to be defined:
     - FREEZER_TEST_SSH_KEY
     - FREEZER_TEST_SSH_USERNAME
     - FREEZER_TEST_SSH_HOST
     - FREEZER_TEST_CONTAINER

    To enable the swift storage testing, the following environment variables need to be defined:
     - FREEZER_TEST_OS_TENANT_NAME
     - FREEZER_TEST_OS_USERNAME
     - FREEZER_TEST_OS_REGION_NAME
     - FREEZER_TEST_OS_PASSWORD
     - FREEZER_TEST_OS_AUTH_URL

    Tests involving LVM snapshots are evoided if:
     - user is not root
     - FREEZER_TEST_NO_LVM is set
    """

    ssh_key = os.environ.get('FREEZER_TEST_SSH_KEY')
    ssh_username = os.environ.get('FREEZER_TEST_SSH_USERNAME')
    ssh_host = os.environ.get('FREEZER_TEST_SSH_HOST')
    container = os.environ.get('FREEZER_TEST_CONTAINER')
    use_ssh = ssh_key and ssh_username and ssh_host and container

    os_tenant_name = os.environ.get('FREEZER_TEST_OS_TENANT_NAME')
    os_user_name = os.environ.get('FREEZER_TEST_OS_USERNAME')
    os_region = os.environ.get('FREEZER_TEST_OS_REGION_NAME')
    os_password = os.environ.get('FREEZER_TEST_OS_PASSWORD')
    os_auth_url = os.environ.get('FREEZER_TEST_OS_AUTH_URL')
    use_os = (os_tenant_name and os_user_name and os_region
              and os_password and os_auth_url)
    if use_os:
        os.environ['OS_USERNAME'] = os_user_name
        os.environ['OS_TENANT_NAME'] = os_tenant_name
        os.environ['OS_AUTH_URL'] = os_auth_url
        os.environ['OS_PASSWORD'] = os_password
        os.environ['OS_REGION_NAME'] = os_region
        os.environ['OS_TENANT_ID'] = ''

    openstack_executable = distutils.spawn.find_executable('openstack')
    swift_executable = distutils.spawn.find_executable('swift')

    use_lvm = (os.getuid() == 0 and 'FREEZER_TEST_NO_LVM' not in os.environ)
    ssh_executable = distutils.spawn.find_executable('ssh')

    def setUp(self):
        self.source_tree = Temp_Tree()
        self.dest_tree = Temp_Tree()
        if TestFS.use_ssh:
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.ssh_client.connect(TestFS.ssh_host,
                                    username=TestFS.ssh_username,
                                    key_filename=TestFS.ssh_key)

    def tearDown(self):
        self.source_tree.cleanup()
        self.dest_tree.cleanup()

    def assertTreesMatch(self):
        self.assertTrue(self.source_tree.is_equal(self.dest_tree))

    def assertTreesMatchNot(self):
        self.assertFalse(self.source_tree.is_equal(self.dest_tree))

    def dict_to_args(self, d):
        arg_string = ''
        for k, v in d.iteritems():
            arg_string += ' --{0} {1}'.format(k.replace('_', '-'), v)
        return arg_string

    def get_file_list_ssh(self, sub_path=''):
        ftp = self.ssh_client.open_sftp()
        path = '{0}/{1}'.format(self.container, sub_path)
        return ftp.listdir(path)

    def remove_ssh_directory(self, sub_path=''):
        cmd = 'rm -rf {0}/{1}'.format(self.container, sub_path)
        self.ssh_client.exec_command(cmd)

    def get_file_list_openstack(self, container):
        if self.openstack_executable:
            cmd = '{0} object list {1} -f json'.format(
                self.openstack_executable, container)
            json_result = execute(cmd)
            result = json.loads(json_result)
            return [x['Name'] for x in result]
        if self.swift_executable:
            cmd = '{0} list {1}'.format(self.swift_executable, container)
            result = execute(cmd)
            return result.split()
        raise Exception("Unable to get container list using openstackclient/swiftclient")

    def remove_swift_container(self, container):
        if self.openstack_executable:
            execute('{0} container delete {1}'.format(self.openstack_executable,
                                                      container))
            execute('{0} container delete {1}_segments'.format(self.openstack_executable,
                                                               container))
        elif self.swift_executable:
            execute('{0} delete {1}'.format(self.swift_executable,
                                            container))
            execute('{0} delete {1}_segments'.format(self.swift_executable,
                                                     container))
        return True

    def do_backup_and_restore_with_check(self, backup_args, restore_args):
        self.source_tree.add_random_data()
        self.assertTreesMatchNot()
        result = execute_freezerc(self.dict_to_args(backup_args))
        self.assertIsNotNone(result)
        result = execute_freezerc(self.dict_to_args(restore_args))
        self.assertIsNotNone(result)
        self.assertTreesMatch()
        return True
