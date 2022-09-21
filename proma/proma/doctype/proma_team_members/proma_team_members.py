# Copyright (c) 2022, phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ProMaTeamMembers(Document):
    def before_save(self):
        if self.create_userid:
            user_id = frappe.get_doc({"doctype": "ProMa User ID", "email_id": self.email_id})
            user_id.save()

            if user_id.name:
                self.create_userid = 0

