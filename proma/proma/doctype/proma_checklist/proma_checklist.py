# Copyright (c) 2022, phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, throw


class ProMaChecklist(Document):
    @frappe.whitelist()
    def process_check_list(self, checklist):
        frappe.throw("{}".format(self))
