# -*- coding: utf-8 -*-
{
    'name': "RealStateX Complaint Management Module",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "Muhammad Nouman",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['base','website','l10n_din5008'],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/mail_template_data.xml',
        'views/rex_complaint_view.xml',
        'views/rex_addresses.xml',
        'views/menu_items.xml',
        'views/templates.xml',
        'report/work_order.xml',
        'report/ir_actions_report.xml',
    ],
'assets': {
        'web.assets_frontend': [
            'rex_complaint_mgmt/static/src/js/rex_complaint_form.js',
        ]
    },
}

