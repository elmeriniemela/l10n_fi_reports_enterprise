# -*- coding: utf-8 -*-
##############################################################################
#
#    ODOO Open Source Management Solution
#
#    ODOO Addon module by Sprintit Ltd
#    Copyright (C) 2016 Sprintit Ltd (<http://sprintit.fi>).
#
#
##############################################################################

from odoo import api, fields, models, _



class EUVatReport(models.AbstractModel):
    _name = "account.eu_vat_report"
    _description = "EU VAT Summary report (Finnish standart)"
    _inherit = "account.report"

    # https://www.youtube.com/watch?v=Vz76XPhLqhU   29:40
    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_year'}

    # https://www.youtube.com/watch?v=Vz76XPhLqhU   15:00
    @api.model
    def _get_lines(self, options, line_id=None):
        tables, where_clause, where_params = self.env['account.move.line'].with_context(strict_range=True)._query_get()


        # Create SELECT statement
        sql_select = """ select ai.partner_id, 
                sum(sales_material_EU) as sales_material_EU,
                sum(sales_service_EU) as sales_service_EU,
                sum(triangulation_sales) as triangulation_sales 
                """

        sql_from = """ from (
            select  invoice_id, account_move_line.date as aml_date, 0 as sales_material_EU, (account_move_line.credit - account_move_line.debit) as sales_service_EU, 0 as triangulation_sales ,  account_move_line.company_id
                    from %s
                    join account_move_line_account_tax_rel as amlatr on amlatr.account_move_line_id = account_move_line.id
                    left join  account_tax_account_tag as atat on  amlatr.account_tax_id = atat.account_tax_id
                left join account_account_tag as aat on atat.account_account_tag_id = aat.id
                where aat.name like '312%%' and %s
            union all
            select  invoice_id, account_move_line.date as aml_date, (account_move_line.credit - account_move_line.debit) as sales_material_EU, 0 as sales_service_EU, 0 as triangulation_sales , account_move_line.company_id
                    from %s 
                    join account_move_line_account_tax_rel as amlatr on amlatr.account_move_line_id = account_move_line.id
                    left join  account_tax_account_tag as atat on  amlatr.account_tax_id = atat.account_tax_id
                left join account_account_tag as aat on atat.account_account_tag_id = aat.id
                where aat.name like '311%%' and %s
            union all
            select  invoice_id, account_move_line.date as aml_date, 0 as sales_material_EU, 0 as sales_service_EU, (account_move_line.credit - account_move_line.debit) as triangulation_sales , account_move_line.company_id
                    from %s 
                    join account_move_line_account_tax_rel as amlatr on amlatr.account_move_line_id = account_move_line.id
                    left join  account_tax_account_tag as atat on  amlatr.account_tax_id = atat.account_tax_id
                left join account_account_tag as aat on atat.account_account_tag_id = aat.id
                where aat.name like '333%%' and %s) 
            as result join account_invoice ai on ai.id = result.invoice_id """


        # Create GROUP BY statement
        sql_group_by = " group by partner_id  "

        sql = sql_select + sql_from + sql_group_by

        if line_id != None:
            unfold_sql = sql_select + ", result.invoice_id" + sql_from + sql_group_by + ", invoice_id"
            where_clause = where_clause + 'AND partner_id = %s '
            where_params = where_params + [line_id]


        query = sql % ((tables, where_clause) * 3)

        # Preparing quert for parameter substitution: ... like '311%' ... should not be substituted
        query = query.replace("%'", "%%'")

        self.env.cr.execute(query, where_params * 3)
        results = self.env.cr.dictfetchall()

        lines = []
        idx = 0
        for line in results:
            partner = self.env['res.partner'].search([('id', '=', line['partner_id'])])


            columns = [partner.vat[:2] if partner.vat else " ", partner.vat[2:] if partner.vat else " ",
                       line['sales_material_eu'], line['sales_service_eu'], line['triangulation_sales']]

            vals = {
                'id': line['partner_id'],
                'name': partner.name,
                'columns': [{'name': v} for v in columns],
                'unfoldable': True,
                'unfolded': line_id == line['partner_id'] and True or False,
            }
            lines.append(vals)

        # Unfolding line
        if line_id:
            unfold_query = unfold_sql % ((tables, where_clause) * 3)

            # Preparing quert for parameter substitution: ... like '311%' ... should not be substituted
            unfold_query = unfold_query.replace("%'", "%%'")

            self.env.cr.execute(unfold_query, where_params * 3)
            results = self.env.cr.dictfetchall()



            for child_line in results:

                invoice = self.env['account.invoice'].search([('id', '=', child_line['invoice_id'])])

                columns = [" ",  " ",
                           child_line['sales_material_eu'], child_line['sales_service_eu'], child_line['triangulation_sales']]

                lines.append({
                    'id': invoice.move_id.line_ids[0].id,
                    'invoice_id': invoice.id,
                    'name': invoice.number,
                    'parent_id': line['partner_id'],
                    'columns': [{'name': v} for v in columns],
                    'caret_options': 'account.invoice.out',

                })


        return lines

    def _get_report_name(self):
        return _('EU VAT report')

    # https://www.youtube.com/watch?v=Vz76XPhLqhU   13:00
    def _get_columns_name(self, options):
        return [
            {'name': 'Partner', 'style': 'text-align:left'},
            {'name': 'Country Code'},
            {'name': 'VAT-number', 'style': 'text-align:right'},
            {'name': 'EU material sales', 'style': 'text-align:right'},
            {'name': 'EU service sales', 'style': 'text-align:right'},
            {'name': 'Triangulation sales', 'style': 'text-align:right'},
        ]
