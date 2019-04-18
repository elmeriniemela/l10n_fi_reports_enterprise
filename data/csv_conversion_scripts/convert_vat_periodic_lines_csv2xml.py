import os
import re

import csv_converter

CSV_FILE = os.path.dirname(__file__) + '/../csv_sources/vat_periodical_report_lines.csv'
XML_FILE = os.path.dirname(__file__) + '/../vat_periodical_report_lines.xml'
XML_ID_PREFIX = 'sprintit_vat_periodical'
MAIN_REPORT_ID = 'sprintit_vat_periodical_report'

DOMAIN_FORMATTING_STRING_ACCT_TYPE = "[(%s, 'in', [%s])]"

tag_id2xml_id = {
    "4": "l10n_fi.301-sales24",
    "5": "l10n_fi.302-sales14",
    "6": "l10n_fi.303-sales10",
    "7": "l10n_fi.305-purchases-material-eu",
    "8": "l10n_fi.306-purchases-service-eu",
    "9": "l10n_fi.307-purchases",
    "10": "l10n_fi.318-purchases-construct",
    "11": "l10n_fi.304-sales0",
    "12": "l10n_fi.311-sales-material-eu",
    "13": "l10n_fi.312-sales-service-eu",
    "14": "l10n_fi.319-sales-construct",
    "15": "l10n_fi.330-triangulation-purchase",
    "16": "l10n_fi.333-triangulation-eu",
    "17": "l10n_fi.340-import-payable",
}

tax_id2xml_id = {
    "41": "l10n_fi.aland0",
    "42": "l10n_fi.purchase14euservice2",
    "43": "l10n_fi.purchase14euservice",
    "44": "l10n_fi.purchase14eugoods",
    "45": "l10n_fi.purchase14eugoods2",
    "46": "l10n_fi.purchase24eugoods",
    "47": "l10n_fi.vat10service",
    "48": "l10n_fi.purchase10eugoods2",
    "49": "l10n_fi.purchase10euservice2",
    "50": "l10n_fi.purchase24service",
    "51": "l10n_fi.purchase24eugoods2",
    "52": "l10n_fi.purchase14service",
    "53": "l10n_fi.purchase24euservice2",
    "54": "l10n_fi.vat0eugoods",
    "55": "l10n_fi.purchase10service",
    "56": "l10n_fi.purchase24construct",
    "57": "l10n_fi.purchase24construct2",
    "58": "l10n_fi.construct0",
    "59": "l10n_fi.purchase10eugoods",
    "60": "l10n_fi.purchase10euservice",
    "61": "l10n_fi.purchase24",
    "62": "l10n_fi.purchase24euservice",
    "63": "l10n_fi.vat0euservice",
    "64": "l10n_fi.vat14service",
    "65": "l10n_fi.purchase24brutto",
    "66": "l10n_fi.purchase14brutto",
    "67": "l10n_fi.purchase10",
    "68": "l10n_fi.prepay24",
    "69": "l10n_fi.purchase14",
    "70": "l10n_fi.purchase0",
    "71": "l10n_fi.sales24",
    "72": "l10n_fi.sales14",
    "73": "l10n_fi.sales10",
    "74": "l10n_fi.sales0",
    "75": "l10n_fi.purchase10brutto",
    "76": "l10n_fi.vat24service",
    "77": "l10n_fi.vat0triangulation",
    "78": "l10n_fi.triangulation_purchase",
    "79": "l10n_fi.purchase24construct3",
    "80": "l10n_fi.vat0export",
    "81": "l10n_fi.import_pay24",
    "82": "l10n_fi.import_deduct24"
}


class CsvBalanceSheetConverter(csv_converter.CsvConverter):

    def convert_domain(self, domain):

        first_domain_element = re.findall(r'\(.*\)', domain)[0][1:-1].split(',')[0]
        domain_ids = re.split(r'\D+', domain)[1:-1]

        account_tag_xml_ids = []


        for id in domain_ids:
            if first_domain_element == "'tax_ids'":
                xml_id = tax_id2xml_id.get(id, False)
            elif first_domain_element == "'tax_line_id.tag_ids'":
                xml_id = tag_id2xml_id.get(id, False)
            else:
                print("unknown first domain element %s" % first_domain_element)
                quit()

            if not xml_id:
                print("cannot find xmlid: %s %s" % (first_domain_element, id))
                quit()


            account_tag_xml_ids.append("ref('" + xml_id + "')")
        domain_formatting_string_parameter = ','.join(account_tag_xml_ids)
        return DOMAIN_FORMATTING_STRING_ACCT_TYPE % (first_domain_element, domain_formatting_string_parameter)


if __name__ == '__main__':
    # service.py executed as script
    # do something
    csv_balance_sheet_converter = CsvBalanceSheetConverter()
    csv_balance_sheet_converter.convert_csv2xml(csv_file = CSV_FILE, xml_file = XML_FILE,
                                                main_report_id = MAIN_REPORT_ID,
                                                xml_id_prefix = XML_ID_PREFIX)