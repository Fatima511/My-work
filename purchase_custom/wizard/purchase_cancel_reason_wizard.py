from odoo import api, fields, models,_



class PurchaseCancelReasonWizard(models.TransientModel):
    _name = 'purchase.cancel.reason.wizard'


    purchase_order_id = fields.Many2one('purchase.order')
    predefined_reason= fields.Boolean(string="Predefined Reason")
    custom_reason = fields.Text(string="Custom Reason")
    reason_id = fields.Many2one('purchase.cancel.reasons', string="Reason")

    def action_submit(self):
        self.ensure_one()
        reason = self.custom_reason or self.reason_id.reason
        self.purchase_order_id.cancel_reason=reason
        self.purchase_order_id.message_post(
                author_id=self.env.user.partner_id.id,
                body=reason,
                email_layout_xmlid='mail.mail_notification_light',
                message_type='comment',
                subject="The purchase order had been canceled due",
            )

        self.purchase_order_id.button_cancel()
        return {'type': 'ir.actions.act_window_close'}
