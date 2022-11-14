import frappe
from frappe import _
import erpnext
import urllib.parse


@frappe.whitelist(allow_guest=True)
def custom(random_string=""):
    data = frappe.request.data
    doc = frappe.new_doc("API Test")
    doc.response_data = data
    doc.insert()
