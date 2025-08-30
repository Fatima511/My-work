from odoo import models, fields, api, _

class PurchaseCancelReasons(models.Model):
    _name = 'purchase.cancel.reasons'
    _description = 'Purchase Cancel Reasons'
    _rec_name = "reason"

    reason = fields.Text('Reason')

