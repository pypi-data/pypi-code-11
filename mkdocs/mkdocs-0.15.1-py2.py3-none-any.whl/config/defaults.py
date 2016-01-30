from __future__ import unicode_literals

from mkdocs import utils
from mkdocs.config import config_options

# NOTE: The order here is important. During validation some config options
# depend on others. So, if config option A depends on B, then A should be
# listed higher in the schema.

# Once we drop Python 2.6 support, this could be an OrderedDict, however, it
# isn't really needed either as we always sequentially process the schema other
# than at initialisation when we grab the full set of keys for convenience.

DEFAULT_SCHEMA = (

    # Reserved for internal use, stores the mkdocs.yml config file.
    ('config_file_path', config_options.Type(utils.string_types)),

    # The title to use for the documentation
    ('site_name', config_options.Type(utils.string_types, required=True)),

    # Defines the structure of the navigation and which markdown files are
    # included in the build.
    ('pages', config_options.Pages()),

    # The full URL to where the documentation will be hosted
    ('site_url', config_options.URL()),

    # A description for the documentation project that will be added to the
    # HTML meta tags.
    ('site_description', config_options.Type(utils.string_types)),
    # The name of the author to add to the HTML meta tags
    ('site_author', config_options.Type(utils.string_types)),

    # The path to the favicon for a site
    ('site_favicon', config_options.Type(utils.string_types)),

    # The MkDocs theme for the documentation.
    ('theme', config_options.Theme(default='mkdocs')),

    # The directory containing the documentation markdown.
    ('docs_dir', config_options.Dir(default='docs', exists=True)),

    # The directory where the site will be built to
    ('site_dir', config_options.SiteDir(default='site')),

    # The directory of a theme to use if not using one of the builtin MkDocs
    # themes.
    ('theme_dir', config_options.ThemeDir(exists=True)),

    # A copyright notice to add to the footer of documentation.
    ('copyright', config_options.Type(utils.string_types)),

    # set of values for Google analytics containing the account IO and domain,
    # this should look like, ['UA-27795084-5', 'mkdocs.org']
    ('google_analytics', config_options.Type(list, length=2)),

    # The address on which to serve the live reloading docs server.
    ('dev_addr', config_options.Type(
        utils.string_types, default='127.0.0.1:8000')),

    # If `True`, use `<page_name>/index.hmtl` style files with hyperlinks to
    # the directory.If `False`, use `<page_name>.html style file with
    # hyperlinks to the file.
    # True generates nicer URLs, but False is useful if browsing the output on
    # a filesystem.
    ('use_directory_urls', config_options.Type(bool, default=True)),

    # Specify a link to the project source repo to be included
    # in the documentation pages.
    ('repo_url', config_options.RepoURL()),

    # A name to use for the link to the project source repo.
    # Default, If repo_url is unset then None, otherwise
    # "GitHub" or "Bitbucket" for known url or Hostname for unknown urls.
    ('repo_name', config_options.Type(utils.string_types)),

    # Specify which css or javascript files from the docs directory should be
    # additionally included in the site. Default, List of all .css and .js
    # files in the docs dir.
    ('extra_css', config_options.Extras(file_match=utils.is_css_file)),
    ('extra_javascript', config_options.Extras(
        file_match=utils.is_javascript_file)),

    # Similar to the above, but each template (HTML or XML) will be build with
    # Jinja2 and the global context.
    ('extra_templates', config_options.Extras()),

    # Determine if the site should include the nav and next/prev elements.
    # Default, True if the site has more than one page, False otherwise.
    ('include_nav', config_options.NumPages()),
    ('include_next_prev', config_options.NumPages()),

    # PyMarkdown extension names.
    ('markdown_extensions', config_options.MarkdownExtensions(
        builtins=['meta', 'toc', 'tables', 'fenced_code'],
        configkey='mdx_configs', default=[])),

    # PyMarkdown Extension Configs. For internal use only.
    ('mdx_configs', config_options.Private()),

    # enabling strict mode causes MkDocs to stop the build when a problem is
    # encountered rather than display an error.
    ('strict', config_options.Type(bool, default=False)),

    # the remote branch to commit to when using gh-deploy
    ('remote_branch', config_options.Type(
        utils.string_types, default='gh-pages')),

    # the remote name to push to when using gh-deploy
    ('remote_name', config_options.Type(utils.string_types, default='origin')),

    # extra is a mapping/dictionary of data that is passed to the template.
    # This allows template authors to require extra configuration that not
    # relevant to all themes and doesn't need to be explicitly supported by
    # MkDocs itself. A good example here would be including the current
    # project version.
    ('extra', config_options.SubConfig()),
)
