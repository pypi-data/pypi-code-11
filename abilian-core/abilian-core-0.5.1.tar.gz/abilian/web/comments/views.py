# coding=utf-8
"""
"""
from __future__ import absolute_import, print_function, division

from datetime import datetime

import sqlalchemy as sa
from werkzeug.exceptions import BadRequest
from flask_login import current_user

from abilian.i18n import _, _l
from abilian.core.entities import Entity
from abilian.core.models.comment import Comment, is_commentable
from abilian.core.util import utc_dt
from abilian.web import url_for, nav
from abilian.web.blueprints import Blueprint
from abilian.web.action import actions, ButtonAction
from abilian.web.views.object import (
  ObjectEdit, ObjectCreate, ObjectDelete, CANCEL_BUTTON,
)
from .forms import CommentForm

bp = Blueprint('comments', __name__, url_prefix='/comments')

def _default_comment_view(obj, obj_type, obj_id, **kwargs):
  entity = obj.entity
  return url_for(entity, _anchor='comment-{}'.format(obj.id))


@bp.record_once
def register_default_view(state):
  state.app.default_view.register(Comment, _default_comment_view)

COMMENT_BUTTON = ButtonAction('form', 'edit', btn_class='primary',
                              title=_l(u'Post'))


class BaseCommentView(object):
  Model = Comment
  Form = CommentForm

  #: commented entity
  entity = None

  def init_object(self, args, kwargs):
    args, kwargs = super(BaseCommentView, self).init_object(args, kwargs)
    entity_id = kwargs.pop('entity_id', None)
    if entity_id is not None:
      self.entity = Entity.query.get(entity_id)

    if self.entity is None:
      raise BadRequest('No entity to comment')

    if not is_commentable(self.entity):
      raise BadRequest('This entity is not commentable')

    actions.context['object'] = self.entity
    return args, kwargs

  def view_url(self):
    kw = {}
    if self.obj and self.obj.id:
      kw['_anchor'] = 'comment-{}'.format(self.obj.id)
    return url_for(self.entity, **kw)

  def index_url(self):
    return self.view_url()

  @property
  def activity_target(self):
    return self.entity


class CommentEditView(BaseCommentView, ObjectEdit):
  """
  """
  _message_success = _l(u'Comment edited')

  def breadcrumb(self):
    label = _(u'Edit comment on "{title}"').format(title=self.entity.name)
    return nav.BreadcrumbItem(label=label)

  def get_form_buttons(self, *args, **kwargs):
    return [COMMENT_BUTTON, CANCEL_BUTTON]

  def after_populate_obj(self):
    obj_meta = self.obj.meta.setdefault('abilian.core.models.comment', {})
    history = obj_meta.setdefault('history', [])
    history.append(dict(user_id=current_user.id,
                        user=unicode(current_user),
                        date=utc_dt(datetime.utcnow()).isoformat(),))
    self.obj.meta.changed()


edit_view = CommentEditView.as_view('edit')
bp.route('/<int:entity_id>/<int:object_id>/edit')(edit_view)


class CommentCreateView(BaseCommentView, ObjectCreate):
  """
  """
  _message_success = _l(u"Comment added")

  def __init__(self, *args, **kwargs):
    super(CommentCreateView, self).__init__(*args, **kwargs)

  def init_object(self, args, kwargs):
    args, kwargs = super(CommentCreateView, self).init_object(args, kwargs)
    self.obj.entity = self.entity
    session = sa.orm.object_session(self.entity)

    if session:
      sa.orm.session.make_transient(self.obj)

    return args, kwargs

  def breadcrumb(self):
    label = _(u'New comment on "{title}"').format(title=self.entity.name)
    return nav.BreadcrumbItem(label=label)

  def get_form_buttons(self, *args, **kwargs):
    return [COMMENT_BUTTON, CANCEL_BUTTON]


create_view = CommentCreateView.as_view('create')
bp.route('/<int:entity_id>/create')(create_view)


class CommentDeleteView(BaseCommentView, ObjectDelete):
  """
  """
  _message_success = _l(u"Comment deleted")


delete_view = CommentDeleteView.as_view('delete')
bp.route('/<int:entity_id>/<int:object_id>/delete')(delete_view)
