# -*- coding: utf-8 -*-
from __future__ import with_statement

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.urlresolvers import resolve, Resolver404, reverse
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.context import RequestContext
from django.template.response import TemplateResponse
from django.utils.http import urlquote
from django.utils.translation import get_language

from cms.apphook_pool import apphook_pool
from cms.appresolver import get_app_urls
from cms.cache.page import set_page_cache, get_page_cache
from cms.models import Page
from cms.utils import get_template_from_request, get_language_code
from cms.utils import get_language_from_request
from cms.utils import get_cms_setting
from cms.utils.i18n import get_fallback_languages
from cms.utils.i18n import force_language
from cms.utils.i18n import get_public_languages
from cms.utils.i18n import get_redirect_on_fallback
from cms.utils.i18n import get_language_list
from cms.utils.i18n import is_language_prefix_patterns_used
from cms.utils.page_resolver import get_page_from_request


def _handle_no_page(request, slug):
    if not slug and settings.DEBUG:
        return TemplateResponse(request, "cms/welcome.html", RequestContext(request))
    try:
        #add a $ to the end of the url (does not match on the cms anymore)
        resolve('%s$' % request.path)
    except Resolver404 as e:
        # raise a django http 404 page
        exc = Http404(dict(path=request.path, tried=e.args[0]['tried']))
        raise exc
    raise Http404('CMS Page not found: %s' % request.path)


def details(request, slug):
    """
    The main view of the Django-CMS! Takes a request and a slug, renders the
    page.
    """

    if get_cms_setting("PAGE_CACHE") and (
        not hasattr(request, 'toolbar') or (
            not request.toolbar.edit_mode and
            not request.toolbar.show_toolbar and
            not request.user.is_authenticated()
        )
    ):
        cache_content = get_page_cache(request)
        if cache_content is not None:
            content, headers = cache_content
            response = HttpResponse(content)
            response._headers = headers
            return response

    # Get a Page model object from the request
    page = get_page_from_request(request, use_path=slug)
    if not page:
        return _handle_no_page(request, slug)
    current_language = request.GET.get('language', None)
    if not current_language:
        current_language = request.POST.get('language', None)
    if current_language:
        current_language = get_language_code(current_language)
        if current_language not in get_language_list(page.site_id):
            current_language = None
    if current_language is None:
        current_language = get_language_code(getattr(request, 'LANGUAGE_CODE', None))
        if current_language:
            current_language = get_language_code(current_language)
            if current_language not in get_language_list(page.site_id):
                current_language = None
    if current_language is None:
        current_language = get_language_code(get_language())
    # Check that the current page is available in the desired (current) language
    available_languages = []
    # this will return all languages in draft mode, and published only in live mode
    page_languages = list(page.get_published_languages())
    if hasattr(request, 'user') and request.user.is_staff:
        user_languages = get_language_list()
    else:
        user_languages = get_public_languages()
    for frontend_lang in user_languages:
        if frontend_lang in page_languages:
            available_languages.append(frontend_lang)
    # Check that the language is in FRONTEND_LANGUAGES:
    own_urls = [
        'http%s://%s%s' % ('s' if request.is_secure() else '', request.get_host(), request.path),
        '/%s' % request.path,
        request.path,
    ]
    if not current_language in user_languages:
        #are we on root?
        if not slug:
            #redirect to supported language
            languages = []
            for language in available_languages:
                languages.append((language, language))
            if languages:
                # get supported language
                new_language = get_language_from_request(request)
                if new_language in get_public_languages():
                    with force_language(new_language):
                        pages_root = reverse('pages-root')
                        if hasattr(request, 'toolbar') and request.user.is_staff and request.toolbar.edit_mode:
                            request.toolbar.redirect_url = pages_root
                        elif pages_root not in own_urls:
                            return HttpResponseRedirect(pages_root)
            elif not hasattr(request, 'toolbar') or not request.toolbar.redirect_url:
                _handle_no_page(request, slug)
        else:
            return _handle_no_page(request, slug)
    if current_language not in available_languages:
        # If we didn't find the required page in the requested (current)
        # language, let's try to find a fallback
        found = False
        for alt_lang in get_fallback_languages(current_language):
            if alt_lang in available_languages:
                if get_redirect_on_fallback(current_language) or slug == "":
                    with force_language(alt_lang):
                        path = page.get_absolute_url(language=alt_lang, fallback=True)
                        # In the case where the page is not available in the
                    # preferred language, *redirect* to the fallback page. This
                    # is a design decision (instead of rendering in place)).
                    if hasattr(request, 'toolbar') and request.user.is_staff and request.toolbar.edit_mode:
                        request.toolbar.redirect_url = path
                    elif path not in own_urls:
                        return HttpResponseRedirect(path)
                else:
                    found = True
        if not found and (not hasattr(request, 'toolbar') or not request.toolbar.redirect_url):
            # There is a page object we can't find a proper language to render it
            _handle_no_page(request, slug)

    if apphook_pool.get_apphooks():
        # There are apphooks in the pool. Let's see if there is one for the
        # current page
        # since we always have a page at this point, applications_page_check is
        # pointless
        # page = applications_page_check(request, page, slug)
        # Check for apphooks! This time for real!
        app_urls = page.get_application_urls(current_language, False)
        skip_app = False
        if not page.is_published(current_language) and hasattr(request, 'toolbar') and request.toolbar.edit_mode:
            skip_app = True
        if app_urls and not skip_app:
            app = apphook_pool.get_apphook(app_urls)
            pattern_list = []
            for urlpatterns in get_app_urls(app.urls):
                pattern_list += urlpatterns
            try:
                view, args, kwargs = resolve('/', tuple(pattern_list))
                return view(request, *args, **kwargs)
            except Resolver404:
                pass
                # Check if the page has a redirect url defined for this language.
    redirect_url = page.get_redirect(language=current_language)
    if redirect_url:
        if (is_language_prefix_patterns_used() and redirect_url[0] == "/" and not redirect_url.startswith(
                    '/%s/' % current_language)):
            # add language prefix to url
            redirect_url = "/%s/%s" % (current_language, redirect_url.lstrip("/"))
            # prevent redirect to self

        if hasattr(request, 'toolbar') and request.user.is_staff and request.toolbar.edit_mode:
            request.toolbar.redirect_url = redirect_url
        elif redirect_url not in own_urls:
            return HttpResponseRedirect(redirect_url)

    # permission checks
    if page.login_required and not request.user.is_authenticated():
        return redirect_to_login(urlquote(request.get_full_path()), settings.LOGIN_URL)
    if hasattr(request, 'toolbar'):
        request.toolbar.set_object(page)

    template_name = get_template_from_request(request, page, no_current_page=True)
    # fill the context
    context = RequestContext(request)
    context['lang'] = current_language
    context['current_page'] = page
    context['has_change_permissions'] = page.has_change_permission(request)
    context['has_view_permissions'] = page.has_view_permission(request)

    if not context['has_view_permissions']:
        return _handle_no_page(request, slug)

    response = TemplateResponse(request, template_name, context)

    response.add_post_render_callback(set_page_cache)

    # Add headers for X Frame Options - this really should be changed upon moving to class based views
    xframe_options = page.get_xframe_options()
    # xframe_options can be None if there's no xframe information on the page
    # (eg. a top-level page which has xframe options set to "inherit")
    if xframe_options == Page.X_FRAME_OPTIONS_INHERIT or xframe_options is None:
        # This is when we defer to django's own clickjacking handling
        return response

    # We want to prevent django setting this in their middlewear
    response.xframe_options_exempt = True

    if xframe_options == Page.X_FRAME_OPTIONS_ALLOW:
        # Do nothing, allowed is no header.
        return response
    elif xframe_options == Page.X_FRAME_OPTIONS_SAMEORIGIN:
        response['X-Frame-Options'] = 'SAMEORIGIN'
    elif xframe_options == Page.X_FRAME_OPTIONS_DENY:
        response['X-Frame-Options'] = 'DENY'

    return response
