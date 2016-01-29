from mock import patch
from mock import DEFAULT
from pytest import raises
import os

from ..testing.utils import apply_fs
from .config import ConfigError
from .config import InvalidConfig
from .config import load
from .config import BuildConfig
from .config import ProjectConfig
from .config import TYPE_REQUIRED
from .config import NAME_REQUIRED
from .config import NAME_INVALID
from .config import PYTHON_INVALID
from .validation import INVALID_BOOL
from .validation import INVALID_CHOICE
from .validation import INVALID_DIRECTORY
from .validation import INVALID_PATH
from .validation import INVALID_STRING


env_config = {
    'output_base': '/tmp'
}


minimal_config = {
    'name': 'docs',
    'type': 'sphinx',
}


minimal_config_dir = {
    'readthedocs.yml': '''\
name: docs
type: sphinx
'''
}


multiple_config_dir = {
    'readthedocs.yml': '''
name: first
type: sphinx
---
name: second
type: sphinx
    ''',
    'nested': minimal_config_dir,
}


def get_build_config(config, env_config=None, source_file='readthedocs.yml',
                     source_position=0):
    return BuildConfig(
        env_config or {},
        config,
        source_file=source_file,
        source_position=source_position)


def test_load_no_config_file(tmpdir):
    base = str(tmpdir)
    with raises(ConfigError):
        load(base, env_config)


def test_load_empty_config_file(tmpdir):
    apply_fs(tmpdir, {
        'readthedocs.yml': ''
    })
    base = str(tmpdir)
    with raises(ConfigError):
        load(base, env_config)


def test_minimal_config(tmpdir):
    apply_fs(tmpdir, minimal_config_dir)
    base = str(tmpdir)
    config = load(base, env_config)
    assert isinstance(config, ProjectConfig)
    assert len(config) == 1
    build = config[0]
    assert isinstance(build, BuildConfig)


def test_build_config_has_source_file(tmpdir):
    base = str(apply_fs(tmpdir, minimal_config_dir))
    build = load(base, env_config)[0]
    assert build.source_file == os.path.join(base, 'readthedocs.yml')
    assert build.source_position == 0


def test_build_config_has_source_position(tmpdir):
    base = str(apply_fs(tmpdir, multiple_config_dir))
    builds = load(base, env_config)
    assert len(builds) == 3
    first, second = filter(
        lambda b: not b.source_file.endswith('nested/readthedocs.yml'),
        builds)
    third, = filter(
        lambda b: b.source_file.endswith('nested/readthedocs.yml'),
        builds)
    assert first.source_position == 0
    assert second.source_position == 1
    assert third.source_position == 0


def test_config_requires_name():
    build = BuildConfig({},
                        {},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_name()
    assert excinfo.value.key == 'name'
    assert excinfo.value.code == NAME_REQUIRED


def test_build_requires_valid_name():
    build = BuildConfig({},
                        {'name': 'with/slashes'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_name()
    assert excinfo.value.key == 'name'
    assert excinfo.value.code == NAME_INVALID


def test_config_requires_type():
    build = BuildConfig({},
                        {'name': 'docs'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_type()
    assert excinfo.value.key == 'type'
    assert excinfo.value.code == TYPE_REQUIRED


def test_build_requires_valid_type():
    build = BuildConfig({},
                        {'type': 'unknown'},
                        source_file=None,
                        source_position=None)
    with raises(InvalidConfig) as excinfo:
        build.validate_type()
    assert excinfo.value.key == 'type'
    assert excinfo.value.code == INVALID_CHOICE


def test_empty_python_section_is_valid():
    build = get_build_config({'python': {}})
    build.validate_python()
    assert 'python' in build


def test_python_section_must_be_dict():
    build = get_build_config({'python': 123})
    with raises(InvalidConfig) as excinfo:
        build.validate_python()
    assert excinfo.value.key == 'python'
    assert excinfo.value.code == PYTHON_INVALID


def test_use_system_site_packages_defaults_to_false():
    build = get_build_config({'python': {}})
    build.validate_python()
    # Default is False.
    assert not build['python']['use_system_site_packages']


def describe_validate_use_system_site_packages():
    def it_defaults_to_false():
        build = get_build_config({'python': {}})
        build.validate_python()
        assert build['python']['setup_py_install'] is False

    def it_validates_value():
        build = get_build_config(
            {'python': {'use_system_site_packages': 'invalid'}})
        with raises(InvalidConfig) as excinfo:
            build.validate_python()
        excinfo.value.key = 'python.use_system_site_packages'
        excinfo.value.code = INVALID_BOOL

    @patch('readthedocs_build.config.config.validate_bool')
    def it_uses_validate_bool(validate_bool):
        validate_bool.return_value = True
        build = get_build_config(
            {'python': {'use_system_site_packages': 'to-validate'}})
        build.validate_python()
        validate_bool.assert_any_call('to-validate')


def describe_validate_setup_py_install():

    def it_defaults_to_false():
        build = get_build_config({'python': {}})
        build.validate_python()
        assert build['python']['setup_py_install'] is False

    def it_validates_value():
        build = get_build_config({'python': {'setup_py_install': 'this-is-string'}})
        with raises(InvalidConfig) as excinfo:
            build.validate_python()
        assert excinfo.value.key == 'python.setup_py_install'
        assert excinfo.value.code == INVALID_BOOL

    @patch('readthedocs_build.config.config.validate_bool')
    def it_uses_validate_bool(validate_bool):
        validate_bool.return_value = True
        build = get_build_config(
            {'python': {'setup_py_install': 'to-validate'}})
        build.validate_python()
        validate_bool.assert_any_call('to-validate')


def describe_validate_formats():

    def it_defaults_to_not_being_included():
        build = get_build_config({})
        build.validate_formats()
        assert 'formats' not in build

    def it_gets_set_correctly():
        build = get_build_config({'formats': ['pdf']})
        build.validate_formats()
        assert 'pdf' in build['formats']

    def formats_can_be_empty():
        build = get_build_config({'formats': 'none'})
        build.validate_formats()
        assert build['formats'] == []


def describe_validate_setup_py_path():

    def it_defaults_to_source_file_directory(tmpdir):
        with tmpdir.as_cwd():
            source_file = tmpdir.join('subdir', 'readthedocs.yml')
            setup_py = tmpdir.join('subdir', 'setup.py')
            build = get_build_config({}, source_file=str(source_file))
            build.validate_python()
            assert build['python']['setup_py_path'] == str(setup_py)

    def it_validates_value(tmpdir):
        with tmpdir.as_cwd():
            build = get_build_config({'python': {'setup_py_path': 'this-is-string'}})
            with raises(InvalidConfig) as excinfo:
                build.validate_python()
            assert excinfo.value.key == 'python.setup_py_path'
            assert excinfo.value.code == INVALID_PATH

    def it_uses_validate_file(tmpdir):
        path = tmpdir.join('setup.py')
        path.write('content')
        path = str(path)
        patcher = patch('readthedocs_build.config.config.validate_file')
        with patcher as validate_file:
            validate_file.return_value = path
            build = get_build_config(
                {'python': {'setup_py_path': 'setup.py'}})
            build.validate_python()
            args, kwargs = validate_file.call_args
            assert args[0] == 'setup.py'


def test_valid_build_config():
    build = BuildConfig(env_config,
                        minimal_config,
                        source_file='readthedocs.yml',
                        source_position=0)
    build.validate()
    assert build['name'] == 'docs'
    assert build['type'] == 'sphinx'
    assert build['base']
    assert build['python']
    assert 'setup_py_install' in build['python']
    assert 'use_system_site_packages' in build['python']
    assert build['output_base']


def describe_validate_base():

    def it_validates_to_abspath(tmpdir):
        apply_fs(tmpdir, {'configs': minimal_config, 'docs': {}})
        with tmpdir.as_cwd():
            source_file = str(tmpdir.join('configs', 'readthedocs.yml'))
            build = BuildConfig(
                {},
                {'base': '../docs'},
                source_file=source_file,
                source_position=0)
            build.validate_base()
            assert build['base'] == str(tmpdir.join('docs'))

    @patch('readthedocs_build.config.config.validate_directory')
    def it_uses_validate_directory(validate_directory):
        validate_directory.return_value = 'path'
        build = get_build_config({'base': '../my-path'})
        build.validate_base()
        # Test for first argument to validate_directory
        args, kwargs = validate_directory.call_args
        assert args[0] == '../my-path'

    def it_fails_if_base_is_not_a_string(tmpdir):
        apply_fs(tmpdir, minimal_config)
        with tmpdir.as_cwd():
            build = BuildConfig(
                {},
                {'base': 1},
                source_file=str(tmpdir.join('readthedocs.yml')),
                source_position=0)
            with raises(InvalidConfig) as excinfo:
                build.validate_base()
            assert excinfo.value.key == 'base'
            assert excinfo.value.code == INVALID_STRING

    def it_fails_if_base_does_not_exist(tmpdir):
        apply_fs(tmpdir, minimal_config)
        build = BuildConfig(
            {},
            {'base': 'docs'},
            source_file=str(tmpdir.join('readthedocs.yml')),
            source_position=0)
        with raises(InvalidConfig) as excinfo:
            build.validate_base()
        assert excinfo.value.key == 'base'
        assert excinfo.value.code == INVALID_PATH


def test_build_validate_calls_all_subvalidators(tmpdir):
    apply_fs(tmpdir, minimal_config)
    build = BuildConfig(
        {},
        {},
        source_file=str(tmpdir.join('readthedocs.yml')),
        source_position=0)
    with patch.multiple(BuildConfig,
                        validate_base=DEFAULT,
                        validate_name=DEFAULT,
                        validate_type=DEFAULT,
                        validate_python=DEFAULT,
                        validate_output_base=DEFAULT):
        build.validate()
        BuildConfig.validate_base.assert_called_with()
        BuildConfig.validate_name.assert_called_with()
        BuildConfig.validate_type.assert_called_with()
        BuildConfig.validate_python.assert_called_with()
        BuildConfig.validate_output_base.assert_called_with()


def test_validate_project_config():
    with patch.object(BuildConfig, 'validate') as build_validate:
        project = ProjectConfig([
            BuildConfig(
                env_config,
                minimal_config,
                source_file='readthedocs.yml',
                source_position=0)
        ])
        project.validate()
        assert build_validate.call_count == 1


def test_load_calls_validate(tmpdir):
    apply_fs(tmpdir, minimal_config_dir)
    base = str(tmpdir)
    with patch.object(BuildConfig, 'validate') as build_validate:
        load(base, env_config)
        assert build_validate.call_count == 1


def test_project_set_output_base():
    project = ProjectConfig([
        BuildConfig(
            env_config,
            minimal_config,
            source_file='readthedocs.yml',
            source_position=0),
        BuildConfig(
            env_config,
            minimal_config,
            source_file='readthedocs.yml',
            source_position=1),
    ])
    project.set_output_base('random')
    for build_config in project:
        assert (
            build_config['output_base'] == os.path.join(os.getcwd(), 'random'))
