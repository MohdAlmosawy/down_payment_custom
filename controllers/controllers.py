# -*- coding: utf-8 -*-
# from odoo import http


# class DownPaymentCustom(http.Controller):
#     @http.route('/down_payment_custom/down_payment_custom', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/down_payment_custom/down_payment_custom/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('down_payment_custom.listing', {
#             'root': '/down_payment_custom/down_payment_custom',
#             'objects': http.request.env['down_payment_custom.down_payment_custom'].search([]),
#         })

#     @http.route('/down_payment_custom/down_payment_custom/objects/<model("down_payment_custom.down_payment_custom"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('down_payment_custom.object', {
#             'object': obj
#         })
