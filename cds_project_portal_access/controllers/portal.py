from werkzeug.exceptions import NotFound

from odoo import fields, http
from odoo.fields import Domain
from odoo.http import request

from odoo.addons.portal.controllers.portal_thread import PortalChatter, get_portal_partner
from odoo.addons.portal.controllers.portal import CustomerPortal


class CdsPortalChatter(PortalChatter):

    def _is_lognotes_enabled_for_task(self):
        return request.env.user.has_group(
            'cds_project_portal_access.group_cds_portal_trainees'
        )

    @http.route('/mail/chatter_fetch', type='jsonrpc', auth='public', website=True)
    def portal_message_fetch(self, thread_model, thread_id, fetch_params=None, **kw):
        model = request.env[thread_model]
        field = model._fields['website_message_ids']
        domain = (
            Domain(self._setup_portal_message_fetch_extra_domain(kw))
            & Domain(field.get_comodel_domain(model))
            & Domain("res_id", "=", thread_id)
            & self._get_non_empty_message_domain()
        )

        include_lognotes = (
            thread_model == 'project.task'
            and self._is_lognotes_enabled_for_task()
        )
        if include_lognotes:
            subtype_ids = [
                request.env.ref("mail.mt_comment").id,
                request.env.ref("mail.mt_note").id,
            ]
        else:
            subtype_ids = [request.env.ref("mail.mt_comment").id]
        domain &= Domain("subtype_id", "in", subtype_ids)

        Message = request.env['mail.message']
        if kw.get('token'):
            thread = self._get_thread_with_access(
                thread_model, thread_id, token=kw.get("token"),
            )
            if not thread:
                raise NotFound()
            if portal_partner := get_portal_partner(
                thread, _hash=None, pid=None, token=kw.get("token"),
            ):
                request.update_context(
                    portal_data={"portal_partner": portal_partner, "portal_thread": thread}
                )
            if not request.env.user._is_internal():
                if not include_lognotes:
                    domain = Message._get_search_domain_share() & domain
            Message = request.env["mail.message"].sudo()
        res = Message._message_fetch(domain, **(fetch_params or {}))
        messages = res.pop("messages")
        return {
            **res,
            "data": {"mail.message": messages.portal_message_format(options=kw)},
            "messages": messages.ids,
        }


class CdsProjectPortal(CustomerPortal):

    def _has_trainees_group(self):
        return request.env.user.has_group(
            'cds_project_portal_access.group_cds_portal_trainees'
        )

    def _task_get_page_view_values(self, task, access_token, **kwargs):
        values = super()._task_get_page_view_values(task, access_token, **kwargs)
        is_trainee = self._has_trainees_group()
        if is_trainee and task.project_id:
            values['stages'] = task.project_id.type_ids.sorted(lambda s: (s.sequence, s.id))
        values['can_change_stage'] = is_trainee
        values['today'] = fields.Date.today()
        return values

    @http.route(['/my/tasks/<int:task_id>/change_stage'], type='http', auth='public',
                website=True, methods=['POST'])
    def change_task_stage(self, task_id, stage_id=None, access_token=None, **kw):
        try:
            task_sudo = self._document_check_access('project.task', task_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')
        if not self._has_trainees_group():
            return request.redirect('/my')
        if not stage_id:
            return request.redirect(f'/my/tasks/{task_id}')
        stage = request.env['project.task.type'].browse(int(stage_id)).exists()
        if not stage or stage not in task_sudo.project_id.type_ids:
            return request.redirect(f'/my/tasks/{task_id}')
        task_sudo.write({'stage_id': int(stage_id)})
        return request.redirect(f'/my/tasks/{task_id}')
