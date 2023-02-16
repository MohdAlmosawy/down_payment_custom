from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    line_ref_custom = fields.Many2one('sale.order.line', string="Line Ref")

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    def calc_custom_amount_due(self):
        for rec in self:
            if rec.invoice_ids:
                for record in rec.invoice_ids:
                    if record.invoice_origin==rec.name:
                        print("ddsssssssssss",record.amount_residual,record,rec)
                        rec.amount_due = record.amount_residual
            else:
                rec.amount_due=rec.amount_total
    amount_due = fields.Monetary(compute='calc_custom_amount_due', string='Amount Due')
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        down_payment_product=self.env['res.config.settings'].search([])
        down_payment_product_obj= next((item for item in down_payment_product if down_payment_product.deposit_default_product_id!=None), None)
        down_payment_product_val=down_payment_product_obj.deposit_default_product_id
        invoice_lines = []
        for line in self.order_line:
            print(line)
            analytic_tag_ids = []
            for lined in self.order_line:
                analytic_tag_ids = [(4, analytic_tag.id, None) for analytic_tag in lined.analytic_tag_ids]
            so_values = {
                'name': line.name,
                'price_unit': line.price_unit*line.product_uom_qty,
                'product_uom_qty': 0.0,
                'order_id': self.id,
                'discount': 0.0,
                'product_uom': down_payment_product_val.uom_id.id,
                'product_id': down_payment_product_val.id,
                'analytic_tag_ids': analytic_tag_ids,
                'is_downpayment': True,
                'line_ref_custom':line.id
            }
            print(so_values)
            sale_order_line = self.env['sale.order.line'].create(so_values)
            vals={
                'name': sale_order_line.name,
                'price_unit': sale_order_line.price_unit,
                'quantity': 1.0,
                'product_id': sale_order_line.product_id.id,
                'product_uom_id': sale_order_line.product_uom.id,
                'tax_ids': [(6, 0, sale_order_line.tax_id.ids)],
                'sale_line_ids': [(6, 0, [sale_order_line.id])],
                'analytic_tag_ids': [(6, 0, sale_order_line.analytic_tag_ids.ids)],
                'analytic_account_id': self.analytic_account_id.id if not sale_order_line.display_type and self.analytic_account_id.id else False,
            }
            invoice_lines.append((0, 0, vals))
        invoice_vals = {
            'ref': self.client_order_ref,
            'move_type': 'out_invoice',
            'invoice_origin': self.name,
            'invoice_user_id': self.user_id.id,
            'narration': self.note,
            'partner_id': self.partner_invoice_id.id,
            'fiscal_position_id': (self.fiscal_position_id or self.fiscal_position_id.get_fiscal_position(
                self.partner_id.id)).id,
            'partner_shipping_id': self.partner_shipping_id.id,
            'currency_id': self.pricelist_id.currency_id.id,
            'payment_reference': self.reference,
            'invoice_payment_term_id': self.payment_term_id.id,
            'partner_bank_id': self.company_id.partner_id.bank_ids[:1].id,
            'team_id': self.team_id.id,
            'campaign_id': self.campaign_id.id,
            'medium_id': self.medium_id.id,
            'source_id': self.source_id.id,
            'invoice_line_ids': invoice_lines,
        }
        self.env['account.move'].create(invoice_vals)
        return res


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def write(self, data):
        res = super(StockPicking, self).write(data)

        if self.state=='done':
            sale_order = self.env['sale.order'].search([('id', '=', self.sale_id.id)])
            print(sale_order)
            so_context = {
                'active_model': 'sale.order',
                'active_ids': [sale_order.id],
                'active_id': sale_order.id,
            }
            regular_invoice_obj = self.env['sale.advance.payment.inv'].with_context(so_context)

            regular_invoice = regular_invoice_obj.create({
                'advance_payment_method': 'delivered',
            })
            regular_invoice.create_invoices()

        return res

    # def button_validate(self):
    #     res = super(StockPicking, self).button_validate()
    #     self.update({'state':'done'})
    #     sale_order=self.env['sale.order'].search([('id','=',self.sale_id.id)])
    #     print(sale_order)
    #     so_context = {
    #         'active_model': 'sale.order',
    #         'active_ids': [sale_order.id],
    #         'active_id': sale_order.id,
    #     }
    #     regular_invoice_obj = self.env['sale.advance.payment.inv'].with_context(so_context)
    # 
    #     regular_invoice=regular_invoice_obj.create({
    #         'advance_payment_method': 'delivered',
    #     })
    #     regular_invoice.create_invoices()
    # 
    #     return res