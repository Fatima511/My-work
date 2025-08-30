from odoo import fields, models, api
from odoo.exceptions import UserError


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    purchase_order_count = fields.Integer(store=False, readonly=True, compute='_qet_orders')

    def _qet_orders(self):
        for employee in self:
            if employee.user_id:
                employee.purchase_order_count = self.env['purchase.order'].search_count([
                    ('responsible_user', '=', employee.user_id.id)
                ])
            else:
                employee.purchase_order_count = 0



    def get_purchase_orders(self):
        return {
                'type': 'ir.actions.act_window',
                'name': 'Related purchase order',
                'view_type': 'list',
                'view_mode': 'list',
                'res_model': 'purchase.order',
                'domain': [
                    ('responsible_user', '=', self.user_id.id),
                    ('responsible_user', '!=', False)
                ],

            }


