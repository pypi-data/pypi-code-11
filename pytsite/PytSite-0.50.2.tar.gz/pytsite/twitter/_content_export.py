"""Content Export Twitter Driver.
"""
from frozendict import frozendict as _frozendict
from twython import Twython as _Twython, TwythonError as _TwythonError
from pytsite import content as _content, content_export as _content_export, logger as _logger, reg as _reg, \
    form as _form, router as _router
from ._widget import Auth as _TwitterAuthWidget

__author__ = 'Alexander Shepetko'
__email__ = 'a@shepetko.com'
__license__ = 'MIT'


class Driver(_content_export.AbstractDriver):
    """Content Export Driver.
    """
    def get_name(self) -> str:
        """Get system name of the driver.
        """
        return 'twitter'

    def get_description(self) -> str:
        """Get human readable description of the driver.
        """
        return 'pytsite.twitter@twitter'

    def get_options_description(self, driver_options: _frozendict) -> str:
        """Get human readable driver options.
        """
        return driver_options.get('screen_name')

    def build_settings_form(self, frm: _form.Form, driver_options: _frozendict):
        """Add widgets to the settings form of the driver.
        """
        inp = _router.request().inp
        callback_uri_q = {}
        for k, v in inp.items():
            if not k.startswith('__'):
                callback_uri_q[k] = v

        if '__form_step' in inp:
            callback_uri_q['__form_step'] = inp['__form_step']

        frm.add_widget(_TwitterAuthWidget(
            uid='driver_opts',
            oauth_token=driver_options.get('oauth_token'),
            oauth_token_secret=driver_options.get('oauth_token_secret'),
            user_id=driver_options.get('user_id'),
            screen_name=driver_options.get('screen_name'),
            callback_uri=_router.current_url(add_query=callback_uri_q)
        ))

    def export(self, entity: _content.model.Content, exporter=_content_export.model.ContentExport):
        """Export data.
        """
        _logger.info("Export started. '{}'".format(entity.title), __name__)

        opts = exporter.driver_opts  # type: _frozendict

        try:
            app_key = _reg.get('twitter.app_key')
            app_sec = _reg.get('twitter.app_secret')
            tw = _Twython(app_key, app_sec, opts['oauth_token'], opts['oauth_token_secret'])
            media_ids = []
            if entity.images:
                img = entity.images[0]
                with open(img.abs_path, 'rb') as f:
                    r = tw.upload_media(media=f)
                    media_ids.append(r['media_id'])
        except _TwythonError as e:
            raise _content_export.error.ExportError(str(e))

        tags = ['#' + t for t in exporter.add_tags if ' ' not in t]
        tags += ['#' + t.title for t in entity.tags if ' ' not in t.title]

        attempts = 20
        status = '{} {} {}'.format(entity.title, entity.url, ' '.join(tags))
        while attempts:
            try:
                tw.update_status(status=status, media_ids=media_ids)
                break
            except _TwythonError as e:
                # Cut one word from the right
                status = ' '.join(status.split(' ')[:-1])
                attempts -= 1
                if not attempts:
                    raise _content_export.error.ExportError(str(e))

        _logger.info("Export finished. '{}'".format(entity.title), __name__)
