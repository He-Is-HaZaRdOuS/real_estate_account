from odoo import fields, models

class AccountMove(models.Model):
    _inherit = "account.move"
    property_id = fields.Many2one('estate.property', string="Property")

class EstatePropertyInherited(models.Model):
    _inherit = "estate.property"
    invoice_ids = fields.One2many('account.move', 'property_id', string="Invoices")

    def action_sell(self):
        self.check_access_rights('write')

        for prop in self:
            prop.check_access_rule('write')

            # Calculate 6% of the selling price
            six_percent = prop.selling_price * 0.06
            admin_fee = 100.00

            # Prepare the invoice lines
            invoice_line_vals = [
                {
                    'name': 'Property Selling Price',
                    'quantity': 1,
                    'price_unit': prop.selling_price,
                },
                {
                    'name': '6% of Selling Price',
                    'quantity': 1,
                    'price_unit': six_percent,
                },
                {
                    'name': 'Administrative Fees',
                    'quantity': 1,
                    'price_unit': admin_fee,
                }
            ]

            journal = self.env['account.journal'].search([('type', '=', 'sale')], limit=1)

            payment = self.env['account.payment'].search([
                ('partner_id', '=', prop.buyer.id),
                ('amount', '=', six_percent + admin_fee),  # Match the payment amount with the invoice total
                ('state', '=', 'posted')  # Ensure the payment is posted
            ], limit=1)

            if payment:
                payment_id = payment.id
            else:
                payment_id = False

            # Prepare the move (invoice) values
            move_vals = {
                'name': False,
                'partner_id': prop.buyer.id,
                'move_type': 'out_invoice',
                'invoice_date': fields.Date.today(),
                'journal_id': journal.id,
                'payment_id': payment_id,
                'state': 'draft',
                'posted_before': False,
                'invoice_line_ids': [(0, 0, line) for line in invoice_line_vals],
                'property_id': prop.id,  # Link the invoice to the property
            }

            # Create the invoice
            invoice = self.env['account.move'].sudo().create(move_vals)
            invoice.action_post()

            # Link the invoice back to the property
            prop.write({'invoice_ids': [(4, invoice.id)]})

        return super().action_sell()
