# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Purchase Customization',
    'version': '1.2',
    'category': 'Inventory/Purchase',
    'sequence': 35,
    'summary': 'Purchase orders, tenders and agreements',
    'depends': ['purchase','hr'],
    'data': [
        'security/groups_view.xml',
        'security/ir.model.access.csv',
        'views/cancel_reason_view.xml',
         'views/purchase_order_view.xml',
        'views/employees_view.xml',
        'wizard/purchase_cancel_reason_wizard_view.xml',
         'reports/report_inheritance.xml',


    ],
    'demo': [
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
