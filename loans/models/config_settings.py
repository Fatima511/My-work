from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    prepayment_journal = fields.Many2one('account.journal',config_parameter='loans.prepayment_journal')
    prepayment_account = fields.Many2one('account.account',config_parameter='loans.prepayment_account')
    prepayment_product = fields.Many2one('product.product',config_parameter='loans.prepayment_product')
