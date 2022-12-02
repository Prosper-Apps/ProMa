# Copyright (c) 2022, phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, throw
import json
import requests
import datetime


class PromaProtocolData(Document):
    pass


def get_protocol_ids():
    url = "https://europe-west3-suncycle-proma-dev.cloudfunctions.net/api/protocols"
    headers = {
        'Accept': 'application/json'
    }
    try:
        response = requests.get(url, headers)
        if response.status_code == 200 and response.json():
            for x in response.json():
                for (key, val) in x.items():
                    if key == "state" and val == 6:
                        get_protocol(x["id"])
                        doc = frappe.new_doc("API Test")
                        doc.response = x["id"]
                        doc.insert()
                        get_protocol(x["id"])
                        frappe.throw("An Error Occured in Protocol {}".format(x["id"]))
        else:
            return "Error"
    except:
        return "Error"


def get_protocol(protocol):
    if not frappe.db.exists("Proma Protocol Data", {"id": protocol}):
        url1 = "https://europe-west3-suncycle-proma-dev.cloudfunctions.net/api/protocols/" + protocol
        headers1 = {
            'Accept': 'application/json'
        }
        try:
            response1 = requests.get(url1, headers1)
            if response1.status_code == 200:
                p_item1 = response1.json()
                frappe.throw("{}".format(p_item1))
                # doc = frappe.new_doc({
                #     "Doctype": "Proma Protocol Data",
                #     "state": p_item["state"],
                #     "allowparallelediting": int(p_item["allowParallelEditing"]),
                #     "requireprecheck": int(p_item["requirePreCheck"]),
                #     "requirepostcheck": int(p_item["requirePostCheck"]),
                #     "referenceid": p_item["referenceId"],
                #     "id": p_item["id"],
                #     "updated_at1": p_item["updatedAt"],
                #     "created_at1": p_item["createdAt"],
                #     "language": p_item["language"]
                # })

                doc1 = frappe.new_doc("Proma Protocol Data")
                doc1.state = p_item1["state"]
                doc1.allowparallelediting = int(p_item1["allowParallelEditing"])
                doc1.requireprecheck = int(p_item1["requirePreCheck"])
                doc1.requirepostcheck = int(p_item1["requirePostCheck"])
                doc1.referenceid = p_item1["referenceId"]
                doc1.id = p_item1["id"]
                doc1.updated_at1 = p_item1["updatedAt"]
                doc1.created_at1 = p_item1["createdAt"]
                doc1.language = p_item1["language"]
                doc1.insert(ignore_permissions=True, ignore_mandatory=True)
            else:
                frappe.throw("An Error Occured in Protocol {}".format(response1.raise_for_status()))
        except:
            frappe.throw("An Error Occured in Protocol")
