# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import copy
import ast
import re

from odoo import models, fields, api, _

class AccountFinancialReportLine(models.Model):
    _inherit = "account.financial.html.report.line"

    belongs_to_financial_report_id = fields.Many2one('account.financial.html.report', 'Belongs to Financial Report', compute='_get_root_financial_report', store=True)

    @api.depends('parent_id')
    def _get_root_financial_report(self):
        for line in self:
            parent_ids = line.parent_path.split("/")
            if len(parent_ids)>0:
                    root_line = self.env['account.financial.html.report.line'].browse(int(parent_ids[0]))
                    line.belongs_to_financial_report_id = root_line.financial_report_id
            else:
                line.belongs_to_financial_report_id = False

    def write(self, vals):
        if vals.get('domain', False):
            vals['domain'] = self.resolve_external_ids(vals.get('domain'))
        return super(AccountFinancialReportLine, self).write(vals)

    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('domain', False):
                vals['domain'] = self.resolve_external_ids(vals.get('domain'))
        return super(AccountFinancialReportLine, self).create(vals_list)



    def resolve_external_ids(self, arch_fs):
        def replacer(m):
            xmlid = m.group('xmlid')

            return m.group('prefix') + str(self.env['ir.model.data'].xmlid_to_res_id(xmlid))

        if re.findall(r'(?P<prefix>[^%])%\((?P<xmlid>.*?)\)[ds]', str(arch_fs)):
            return re.sub(r'(?P<prefix>[^%])%\((?P<xmlid>.*?)\)[ds]', replacer, arch_fs)
        else:
            return arch_fs

