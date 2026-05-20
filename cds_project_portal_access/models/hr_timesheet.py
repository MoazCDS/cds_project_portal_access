from odoo import models
from odoo.fields import Domain


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    def _timesheet_get_portal_domain(self):
        domain = super()._timesheet_get_portal_domain()
        if not self.env.user.has_group('hr_timesheet.group_hr_timesheet_user'):
            if employee := self.env.user.employee_id:
                domain = Domain(domain) & Domain('employee_id', '=', employee.id)
            else:
                domain = Domain.FALSE
        return domain
