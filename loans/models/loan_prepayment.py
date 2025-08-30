from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError



class LoanPrepaymentLine(models.Model):
    _name = 'loan.prepayment.line'


    name = fields.Char(
        string="loan Prepayment", readonly=False,
        default=lambda self: _('New'))

    company_id = fields.Many2one('res.company',string='Company',
                                 readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',required=True,
                                  default=lambda self: self.env.company.currency_id)
    loan_id = fields.Many2one('loan.request', string='Loan Ref', readonly= True)
    amount = fields.Integer('Amount', required=True)
    date = fields.Date('Payment Date',readonly=True, default=lambda self: fields.Date.context_today(self))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    journal_id = fields.Many2one('account.journal', string='Account Journal')
    invoice = fields.Boolean('Invoice')
    prepayment_account = fields.Many2one('account.account', 'Prepayment Account')
    state = fields.Selection(string='State',selection=[('unpaid', 'Unpaid'), ('invoiced', 'Invoiced'),('paid', 'Paid')],
        copy=False, tracking=True, default='unpaid')

    def action_pay(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('loans.prepayment_product')
        prepayment_account_id = self.env['ir.config_parameter'].sudo().get_param('loans.prepayment_account')
        if not prepayment_account_id or not product_id:
            raise UserError("Prepayment account or product ID is not set in the configuration.")
        invoice = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'invoice_date': self.date,
            'partner_id': self.partner_id.id,
            'currency_id': self.loan_id.currency_id.id,
            'payment_reference': self.name,
            'invoice_line_ids': [
                (0, 0, {
                    'price_unit': self.amount,
                    'product_id': product_id,
                    'name': 'Repayment',
                    'account_id': prepayment_account_id,
                    'quantity': 1,
                }),

            ],
        })
        if invoice:
            invoice.action_post()
            self.invoice=True
            self.write({'state':'invoiced'})
        return {
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }
    def view_invoice(self):
        invoice = self.env['account.move'].search([
            ('payment_reference', '=', self.name)
        ])
        self.invoice = True

        return {
            'name': 'Invoice',
            'res_model': 'account.move',
            'res_id': invoice.id,
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
        }


    class AccountPaymentRegister(models.TransientModel):
        _inherit = 'account.payment.register'

        def _post_payments(self, to_process, edit_mode=False):
            res = super()._post_payments(to_process, edit_mode=False)
            for record in self:
                loan_line_id = self.env['loan.prepayment.line'].search([
                    ('name', 'ilike', record.communication)])
                loan_line_id.write({'state': 'paid'})
            return res



