from odoo import fields, models, api
from odoo.exceptions import UserError


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    saleperson = fields.Many2one('res.users', string="Saleperson")
    state = fields.Selection(selection_add=[('approval', 'For Management Approval')])
    responsible_user = fields.Many2one('res.users', string="Responsible User")
    printing_counter = fields.Integer()
    cancel_reason = fields.Text(tracked=True)
    '''
     Add Total Units Counter to Purchase Orders
    '''
    total_quantity= fields.Integer(store=True, readonly=True, compute='_quantity_all')

    @api.depends('order_line.product_id')
    def _quantity_all(self):
        total_quantity = sum(line.product_qty for line in self.order_line)
        self.total_quantity=total_quantity


    def button_approve(self, force=False):
        currency = self.env.user.company_id.currency_id
        if (self.state != 'approval'):
            if (self.amount_total < self.currency_id._convert(
                self.company_id.secondary_amount,
                self.currency_id,
                self.company_id,
                self.date_order or fields.Date.today()) or
                self.env.user._has_group('purchase_custom.group_purchase_head')):
                return super(PurchaseOrder, self).button_approve(force=force)
            else:
                self.write({'state': 'approval'})
        else:
            super(PurchaseOrder, self).button_approve(force=force)
        return {}

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):

        if self.company_id.default_terms:
            self.notes= self.company_id.default_terms
        return super(PurchaseOrder, self).onchange_partner_id()

    def add_count(self):
         self.printing_counter += 1



class PurchaseOrderLine(models.Model):
    _inherit='purchase.order.line'

    sequence_number  = fields.Integer('#',default=0, compute="_line_sequence_number")
    last_purchase_price = fields.Monetary(string='Last Price', compute="_compute_last_purchase_price", readonly=True)
    # Display Product Images in Purchase Orders
    image_128 = fields.Image("Image", related="product_id.image_1920", store=True)



    @api.depends('order_id')
    def _line_sequence_number(self):
        quantity=0
        for order in self.mapped('order_id'):
            sequence_id = 1
            for line in order.order_line:
                if line.product_id:
                    line.sequence_number = sequence_id
                    sequence_id += 1
                else:
                    line.sequence_number = sequence_id



    def copy_line(self):
        self.copy(default={'order_id': self.order_id.id})



    @api.depends('product_id')
    def _compute_last_purchase_price(self):
        for record in self:
            last_record = self.env['purchase.order.line'].search([
                ('product_id', '=', record.product_id.id),
                ('order_id', '!=', record.order_id.id)
            ], order='id desc', limit=1)
            record.last_purchase_price = last_record.price_subtotal if last_record else 0.0

