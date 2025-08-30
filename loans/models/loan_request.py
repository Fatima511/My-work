from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import datetime
from dateutil.relativedelta import relativedelta



class LoanRequest(models.Model):
    _name = 'loan.request'
    _inherit = ['mail.thread']
    _description = 'Loan Request'


    name = fields.Char(
        string="loan Reference",
        required=True, copy=False, readonly=False,
        default=lambda self: _('New'))

    company_id = fields.Many2one('res.company',string='Company',
                                 readonly=True, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency',required=True,
                                  default=lambda self: self.env.company.currency_id)
    loan_type_id = fields.Many2one('loan.type', required=True,string='Loan Type')
    amount = fields.Integer('Loan Amount')
    tenure = fields.Integer(
    string="Tenure in Months",
    default=1,
    help="Amortization period, usually in months or years depending on configuration.")
    processing_fees= fields.Integer('Processing Fee')
    disbursal_amount = fields.Float(string='Disbursal Amount',help="Net amount disbursed to the customer after deducting processing fee.",
                                   )
    document_ids = fields.Many2many('loan.document')
    date = fields.Date('Loan Date', default=lambda self: fields.Date.context_today(self))
    partner_id = fields.Many2one('res.partner', 'Partner', required=True)
    attachment_ids = fields.Many2many('ir.attachment')
    journal_id = fields.Many2one('account.journal', string='Account Journal')
    debit_account_id = fields.Many2one('account.account', string='Debit Account')
    credit_account_id = fields.Many2one('account.account', string='Credit Account')
    rejection_reason = fields.Text('Rejection Reason')
    request = fields.Boolean(string="Request")
    prepayment_lines = fields.One2many('loan.prepayment.line','loan_id')
    state = fields.Selection(string='State',
                selection=[('draft', 'Draft'), ('confirmed', 'Confirmed'),
                   ('waiting', 'Waiting For Approval'),
                   ('approved', 'Approved'), ('disbursed', 'Disbursed'),
                   ('rejected', 'Rejected'), ('closed', 'Closed')],
        copy=False, tracking=True, default='draft')


    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            loan_count = self.env['loan.request'].search([
                ('partner_id', '=', vals.get('partner_id')),
                ('state', 'not in', ('draft', 'rejected', 'closed'))
            ])
            if loan_count:
                raise UserError(_('The partner has already an ongoing loan.'))

            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('loan.request')

        res = super().create(vals_list)
        return res


    @api.onchange('loan_type_id')
    def onchange_loan_type(self):
        self.amount = self.loan_type_id.amount
        self.tenure = self.loan_type_id.tenure
        self.processing_fees = self.loan_type_id.processing_fees
        self.disbursal_amount = self.loan_type_id.disbursal_amount
        self.document_ids = self.loan_type_id.document_ids


    def action_confirm(self):
        self.write({'state': "confirmed"})
        mail =self.env['mail.mail'].sudo().create({
                'subject':'Loan Confirmed',
                'author_id': self.env.user.partner_id.id,
                'body_html': (f"Your loan{self.name} had been submitted"),
                'email_from': self.company_id.email,
                'email_to': self.partner_id.email,

            })
        mail.send()

    def action_waiting_approval(self):
      self.write({'state': "waiting"})

    def action_approved(self):
        self.write({'state': "approved"})

    def action_reject(self):
        return {
            'name': 'Reject Loan',
            'type': 'ir.actions.act_window',
            'res_model': 'reject.loan.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'active_id': self.id},
        }

    def action_disbursed(self):
        self.write({'state': "disbursed"})


        for loan in self:
            move_vals = {
            'ref': loan.name,
            'journal_id': loan.journal_id.id,
            'date': loan.date,
            }
            move = loan.env['account.move'].create(move_vals)
            move_lines = [
                (0, 0, {
                    'name':loan.partner_id.name,
                    'account_id': loan.debit_account_id.id,
                    'debit': loan.disbursal_amount,
                    'credit': 0.0,
                    'date':loan.date,
                    'partner_id': loan.partner_id.id,
                }),
                (0, 0, {
                'name':loan.partner_id.name,
                'account_id': loan.credit_account_id.id,
                'debit': 0.0,
                 'date':loan.date,
                'credit': loan.disbursal_amount,
                'partner_id': loan.partner_id.id,
            })
            ]

            move.line_ids = move_lines
            move.action_post()

    def action_do_prepayment(self):
        self.request = True
        for loan in self:
            loan.prepayment_lines.unlink()
            date_start = datetime.strptime(str(loan.date),'%Y-%m-%d') + relativedelta(months=1)
            amount = loan.amount
            partner = self.partner_id
            prepayment_account_id = self.env['ir.config_parameter'].sudo().get_param('loans.prepayment_account')
            journal_id = self.env['ir.config_parameter'].sudo().get_param('loans.prepayment_journal')
            if not prepayment_account_id or not journal_id:
                raise UserError("Prepayment account or journal ID is not set in the configuration.")


            for lo in range(1, loan.tenure + 1):
                self.env['loan.prepayment.line'].create({
                    'name': f"{loan.name}/{lo}",
                    'partner_id': partner.id,
                    'date': date_start,
                    'amount': amount/loan.tenure,
                    'prepayment_account':prepayment_account_id,
                    'journal_id':journal_id,
                    'loan_id': loan.id})
                date_start += relativedelta(months=1)
        return True


    def action_close_loan(self):
        for check in self.prepayment_lines:
            if check.state == 'unpaid':
                raise ValidationError('There are unpaid loans')

        self.write({'state': "closed"})
