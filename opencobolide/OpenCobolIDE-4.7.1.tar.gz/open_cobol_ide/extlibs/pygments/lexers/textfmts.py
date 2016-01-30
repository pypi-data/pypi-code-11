# -*- coding: utf-8 -*-
"""
    pygments.lexers.textfmts
    ~~~~~~~~~~~~~~~~~~~~~~~~

    Lexers for various text formats.

    :copyright: Copyright 2006-2015 by the Pygments team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

import re

from pygments.lexer import RegexLexer, bygroups
from pygments.token import Text, Comment, Operator, Keyword, Name, String, \
    Number, Generic, Literal
from pygments.util import ClassNotFound

__all__ = ['IrcLogsLexer', 'TodotxtLexer', 'HttpLexer', 'GettextLexer']


class IrcLogsLexer(RegexLexer):
    """
    Lexer for IRC logs in *irssi*, *xchat* or *weechat* style.
    """

    name = 'IRC logs'
    aliases = ['irc']
    filenames = ['*.weechatlog']
    mimetypes = ['text/x-irclog']

    flags = re.VERBOSE | re.MULTILINE
    timestamp = r"""
        (
          # irssi / xchat and others
          (?: \[|\()?                  # Opening bracket or paren for the timestamp
            (?:                        # Timestamp
                (?: (?:\d{1,4} [-/])*  # Date as - or /-separated groups of digits
                    (?:\d{1,4})
                 [T ])?                # Date/time separator: T or space
                (?: \d?\d [:.])*       # Time as :/.-separated groups of 1 or 2 digits
                    (?: \d?\d)
            )
          (?: \]|\))?\s+               # Closing bracket or paren for the timestamp
        |
          # weechat
          \d{4}\s\w{3}\s\d{2}\s        # Date
          \d{2}:\d{2}:\d{2}\s+         # Time + Whitespace
        |
          # xchat
          \w{3}\s\d{2}\s               # Date
          \d{2}:\d{2}:\d{2}\s+         # Time + Whitespace
        )?
    """
    tokens = {
        'root': [
            # log start/end
            (r'^\*\*\*\*(.*)\*\*\*\*$', Comment),
            # hack
            ("^" + timestamp + r'(\s*<[^>]*>\s*)$', bygroups(Comment.Preproc, Name.Tag)),
            # normal msgs
            ("^" + timestamp + r"""
                (\s*<.*?>\s*)          # Nick """,
             bygroups(Comment.Preproc, Name.Tag), 'msg'),
            # /me msgs
            ("^" + timestamp + r"""
                (\s*[*]\s+)            # Star
                (\S+\s+.*?\n)          # Nick + rest of message """,
             bygroups(Comment.Preproc, Keyword, Generic.Inserted)),
            # join/part msgs
            ("^" + timestamp + r"""
                (\s*(?:\*{3}|<?-[!@=P]?->?)\s*)  # Star(s) or symbols
                (\S+\s+)                     # Nick + Space
                (.*?\n)                         # Rest of message """,
             bygroups(Comment.Preproc, Keyword, String, Comment)),
            (r"^.*?\n", Text),
        ],
        'msg': [
            (r"\S+:(?!//)", Name.Attribute),  # Prefix
            (r".*\n", Text, '#pop'),
        ],
    }


class GettextLexer(RegexLexer):
    """
    Lexer for Gettext catalog files.

    .. versionadded:: 0.9
    """
    name = 'Gettext Catalog'
    aliases = ['pot', 'po']
    filenames = ['*.pot', '*.po']
    mimetypes = ['application/x-gettext', 'text/x-gettext', 'text/gettext']

    tokens = {
        'root': [
            (r'^#,\s.*?$', Keyword.Type),
            (r'^#:\s.*?$', Keyword.Declaration),
            # (r'^#$', Comment),
            (r'^(#|#\.\s|#\|\s|#~\s|#\s).*$', Comment.Single),
            (r'^(")([A-Za-z-]+:)(.*")$',
             bygroups(String, Name.Property, String)),
            (r'^".*"$', String),
            (r'^(msgid|msgid_plural|msgstr|msgctxt)(\s+)(".*")$',
             bygroups(Name.Variable, Text, String)),
            (r'^(msgstr\[)(\d)(\])(\s+)(".*")$',
             bygroups(Name.Variable, Number.Integer, Name.Variable, Text, String)),
        ]
    }


class HttpLexer(RegexLexer):
    """
    Lexer for HTTP sessions.

    .. versionadded:: 1.5
    """

    name = 'HTTP'
    aliases = ['http']

    flags = re.DOTALL

    def header_callback(self, match):
        if match.group(1).lower() == 'content-type':
            content_type = match.group(5).strip()
            if ';' in content_type:
                content_type = content_type[:content_type.find(';')].strip()
            self.content_type = content_type
        yield match.start(1), Name.Attribute, match.group(1)
        yield match.start(2), Text, match.group(2)
        yield match.start(3), Operator, match.group(3)
        yield match.start(4), Text, match.group(4)
        yield match.start(5), Literal, match.group(5)
        yield match.start(6), Text, match.group(6)

    def continuous_header_callback(self, match):
        yield match.start(1), Text, match.group(1)
        yield match.start(2), Literal, match.group(2)
        yield match.start(3), Text, match.group(3)

    def content_callback(self, match):
        content_type = getattr(self, 'content_type', None)
        content = match.group()
        offset = match.start()
        if content_type:
            from pygments.lexers import get_lexer_for_mimetype
            possible_lexer_mimetypes = [content_type]
            if '+' in content_type:
                # application/calendar+xml can be treated as application/xml
                # if there's not a better match.
                general_type = re.sub(r'^(.*)/.*\+(.*)$', r'\1/\2',
                                      content_type)
                possible_lexer_mimetypes.append(general_type)

            for i in possible_lexer_mimetypes:
                try:
                    lexer = get_lexer_for_mimetype(i)
                except ClassNotFound:
                    pass
                else:
                    for idx, token, value in lexer.get_tokens_unprocessed(content):
                        yield offset + idx, token, value
                    return
        yield offset, Text, content

    tokens = {
        'root': [
            (r'(GET|POST|PUT|DELETE|HEAD|OPTIONS|TRACE|PATCH)( +)([^ ]+)( +)'
             r'(HTTP)(/)(1\.[01])(\r?\n|\Z)',
             bygroups(Name.Function, Text, Name.Namespace, Text,
                      Keyword.Reserved, Operator, Number, Text),
             'headers'),
            (r'(HTTP)(/)(1\.[01])( +)(\d{3})( +)([^\r\n]+)(\r?\n|\Z)',
             bygroups(Keyword.Reserved, Operator, Number, Text, Number,
                      Text, Name.Exception, Text),
             'headers'),
        ],
        'headers': [
            (r'([^\s:]+)( *)(:)( *)([^\r\n]+)(\r?\n|\Z)', header_callback),
            (r'([\t ]+)([^\r\n]+)(\r?\n|\Z)', continuous_header_callback),
            (r'\r?\n', Text, 'content')
        ],
        'content': [
            (r'.+', content_callback)
        ]
    }

    def analyse_text(text):
        return text.startswith(('GET /', 'POST /', 'PUT /', 'DELETE /', 'HEAD /',
                                'OPTIONS /', 'TRACE /', 'PATCH /'))


class TodotxtLexer(RegexLexer):
    """
    Lexer for `Todo.txt <http://todotxt.com/>`_ todo list format.

    .. versionadded:: 2.0
    """

    name = 'Todotxt'
    aliases = ['todotxt']
    # *.todotxt is not a standard extension for Todo.txt files; including it
    # makes testing easier, and also makes autodetecting file type easier.
    filenames = ['todo.txt', '*.todotxt']
    mimetypes = ['text/x-todo']

    # Aliases mapping standard token types of Todo.txt format concepts
    CompleteTaskText = Operator  # Chosen to de-emphasize complete tasks
    IncompleteTaskText = Text    # Incomplete tasks should look like plain text

    # Priority should have most emphasis to indicate importance of tasks
    Priority = Generic.Heading
    # Dates should have next most emphasis because time is important
    Date = Generic.Subheading

    # Project and context should have equal weight, and be in different colors
    Project = Generic.Error
    Context = String

    # If tag functionality is added, it should have the same weight as Project
    # and Context, and a different color. Generic.Traceback would work well.

    # Regex patterns for building up rules; dates, priorities, projects, and
    # contexts are all atomic
    # TODO: Make date regex more ISO 8601 compliant
    date_regex = r'\d{4,}-\d{2}-\d{2}'
    priority_regex = r'\([A-Z]\)'
    project_regex = r'\+\S+'
    context_regex = r'@\S+'

    # Compound regex expressions
    complete_one_date_regex = r'(x )(' + date_regex + r')'
    complete_two_date_regex = (complete_one_date_regex + r'( )(' +
                               date_regex + r')')
    priority_date_regex = r'(' + priority_regex + r')( )(' + date_regex + r')'

    tokens = {
        # Should parse starting at beginning of line; each line is a task
        'root': [
            # Complete task entry points: two total:
            # 1. Complete task with two dates
            (complete_two_date_regex, bygroups(CompleteTaskText, Date,
                                               CompleteTaskText, Date),
             'complete'),
            # 2. Complete task with one date
            (complete_one_date_regex, bygroups(CompleteTaskText, Date),
             'complete'),

            # Incomplete task entry points: six total:
            # 1. Priority plus date
            (priority_date_regex, bygroups(Priority, IncompleteTaskText, Date),
             'incomplete'),
            # 2. Priority only
            (priority_regex, Priority, 'incomplete'),
            # 3. Leading date
            (date_regex, Date, 'incomplete'),
            # 4. Leading context
            (context_regex, Context, 'incomplete'),
            # 5. Leading project
            (project_regex, Project, 'incomplete'),
            # 6. Non-whitespace catch-all
            ('\S+', IncompleteTaskText, 'incomplete'),
        ],

        # Parse a complete task
        'complete': [
            # Newline indicates end of task, should return to root
            (r'\s*\n', CompleteTaskText, '#pop'),
            # Tokenize contexts and projects
            (context_regex, Context),
            (project_regex, Project),
            # Tokenize non-whitespace text
            ('\S+', CompleteTaskText),
            # Tokenize whitespace not containing a newline
            ('\s+', CompleteTaskText),
        ],

        # Parse an incomplete task
        'incomplete': [
            # Newline indicates end of task, should return to root
            (r'\s*\n', IncompleteTaskText, '#pop'),
            # Tokenize contexts and projects
            (context_regex, Context),
            (project_regex, Project),
            # Tokenize non-whitespace text
            ('\S+', IncompleteTaskText),
            # Tokenize whitespace not containing a newline
            ('\s+', IncompleteTaskText),
        ],
    }
