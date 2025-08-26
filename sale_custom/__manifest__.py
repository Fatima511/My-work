# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Sales Customization',
    'version': '1.2',
    'category': 'Sales/Sales',
    'sequence': 35,
    'summary': 'Sale orders, tenders and agreements',
    'depends': ['sale'],
    'data': [
        'views/res_partner_view.xml',
        'report/order_extension.xml'


    ],
    'demo': [
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
