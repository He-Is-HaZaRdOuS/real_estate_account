from odoo import fields, models


class EstatePropertyInherited(models.Model):
    _inherit = "estate.property"

    def action_sell(self):
        result = super().action_sell()

        for property in self:
            # Calculate 6% of the selling price
            six_percent = property.selling_price * 0.06
            admin_fee = 100.00

            # Prepare the invoice lines
            invoice_line_vals = [
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

            # Prepare the move (invoice) values
            move_vals = {
                'partner_id': property.buyer.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [(0, 0, line) for line in invoice_line_vals],
            }

            # Create the invoice
            self.env['account.move'].sudo().create(move_vals)

        return result
