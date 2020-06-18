{
    'name'        : 'Access Control System',
    'version'     : '1.0',
    'summary'     : 'HTTP controllers for PERCo integration',
    'description' : """Set of controllers for establishment of the connection between PERCo MySQL database and odoo web
                    server""",
    'category'    : 'HTTP Controller',
    'author'      : 'UBtrNvME',
    'website'     : 'https://www.qzhub.com',
    'license'     : 'AGPL-3',
    'depends'     : ['hr_attendance', "mysql_connector"],
    'data'        : ["security/ir.model.access.csv",
                     "views/acs_reader_view.xml",
                     "views/acs_controller_view.xml",
                     "views/acs_zone_view.xml",
                     "views/work_type_view.xml",
                     "views/menu_items.xml",],
    'demo'        : [],
    'installable' : True,
    'auto_install': False,
    'application' : False
}
