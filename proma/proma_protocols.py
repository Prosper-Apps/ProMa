# Copyright (c) 2022, phamos GmbH and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe import _, throw
import json
import requests
import datetime


@frappe.whitelist()
def get_protocols():
    url = "https://europe-west3-suncycle-proma-dev.cloudfunctions.net/api/protocols"
    headers = {
        'Accept': 'application/json'
    }
    try:
        response = requests.get(url, headers)
        if response.status_code == 200 and response.json():
            protocols = []
            for x in response.json():
                for (key, val) in x.items():
                    if key == "state" and val == 6:
                        protocols.append(x["id"])
            get_protocol(protocols)
        else:
            return "Error"
    except:
        return "Error"


def get_protocol(protocols):
    for x in protocols:
        if frappe.db.exists("Proma Protocol Data", {"id": str(x)}):
            pass
        else:
            url = "https://europe-west3-suncycle-proma-dev.cloudfunctions.net/api/protocols/" + str(x)
            headers = {
                'Accept': 'application/json'
            }
            try:
                response = requests.get(url, headers)
                if response.status_code == 200:
                    p_item = response.json()
                    doc = frappe.new_doc("Proma Protocol Data")
                    doc.id = p_item["id"]
                    doc.state = p_item["state"]
                    doc.allowparallelediting = int(p_item["allowParallelEditing"])
                    doc.requireprecheck = int(p_item["requirePreCheck"])
                    doc.requirepostcheck = int(p_item["requirePostCheck"])
                    doc.referenceid = p_item["referenceId"]
                    doc.updated_at1 = p_item["updatedAt"]
                    doc.created_at1 = p_item["createdAt"]
                    doc.template_id, doc.approvedat, doc.template_names = get_template(p_item["template"])
                    doc.description = get_name(p_item["description"])
                    doc.chk_name = get_name(p_item["name"])
                    doc.assigneduserids = get_assigned_users_team(p_item["assignedUserIds"])
                    doc.assignedteams = get_assigned_users_team(p_item["assignedTeams"])
                    doc.client_id, doc.client_name = get_user_details(p_item["client"])
                    doc.customer_id, doc.customer_name = get_user_details(p_item["customer"])
                    doc.servicepartner, doc.service_partner_name = get_user_details(p_item["servicePartner"])
                    doc.installation_id, doc.installation_name, doc.street, doc.city, doc.comment, doc.lat, doc.lng = get_installation_details(
                        p_item["installation"])
                    inst_contacts = get_installation_contacts(p_item["installation"])
                    for inst_contact in inst_contacts:
                        doc.append("contacts", inst_contact)

                    contributors1 = get_contributors(p_item["contributors"])
                    for contributor in contributors1:
                        doc.append("proma_contributors", contributor)

                    comments_n = get_comments(p_item["comments"])
                    for cmm_n in comments_n:
                        doc.append("comments", cmm_n)

                    doc.append("camera", get_camera_settings(p_item["settings"]))
                    doc.language, doc.requiredfieldsoptional, doc.allowparalleleditingcamera = get_settings(
                        p_item["settings"])
                    itmms = get_items(p_item["items"])
                    for imt in itmms:
                        doc.append("items", imt)

                    doc.insert(ignore_permissions=True, ignore_mandatory=True)
                else:
                    frappe.throw("An Error occured in Protocol {}".format(response.raise_for_status()))
            except:
                frappe.throw("An Error Occured in Protocol")


def get_template(itm):
    template_id = itm["id"]
    approvedat = itm["approvedAt"]
    template_names = get_name(itm["name"])
    return template_id, approvedat, template_names


def get_name(names):
    name_html = ""
    if names["en"]:
        name_html += " English: " + names["en"]
    if names["de"]:
        name_html += "\n German: " + names["de"]
    if names["zh"]:
        name_html += "\n Chinese: " + names["zh"]
    if names["es"]:
        name_html += "\n Spanish: " + names["es"]
    return name_html


def get_assigned_users_team(data):
    lst_val = ""
    for ls in data:
        lst_val += ls + "\n "
    return lst_val


def get_user_details(user_d):
    user_id = user_d["id"]
    user_name = user_d["name"]
    return user_id, user_name


def get_installation_details(installation):
    installation_id = installation["id"]
    installation_name = installation["name"]
    street = installation["street"]
    city = installation["city"]
    comment = installation["lat"]
    lat = installation["name"]
    lng = installation["lng"]
    return installation_id, installation_name, street, city, comment, lat, lng


def get_installation_contacts(installation):
    contacts = []
    for ct in installation["contacts"]:
        contact = {
            "email": ct["email"],
            "phone": ct["phone"],
            "id": ct["id"],
            "full_name": ct["name"]
        }
        contacts.append(contact)
    return contacts


def get_contributors(data):
    contributors = []
    for ct in data:
        contributor = {
            "userid": ct["userid"],
            "last_update": ct["lastUpdate"]
        }
        contributors.append(contributor)
    return contributors


def get_comments(data):
    comm_ins = []
    for cm in data:
        comment_ls = {
            "created_by": cm["createdBy"],
            "body": cm["body"]
        }
        comm_ins.append(comment_ls)
    return comm_ins


def get_settings(data):
    language = data["language"]
    requiredfieldsoptional = int(data["requiredFieldsOptional"])
    allowparalleleditingcamera = int(data["allowParallelEditing"])
    return language, requiredfieldsoptional, allowparalleleditingcamera


def get_camera_settings(data):
    camera_d = data["camera"]
    camera_details = {
        "quality": camera_d["quality"],
        "allow_editing": camera_d["allowEditing"],
        "width": camera_d["width"],
        "height": camera_d["height"]
    }
    return camera_details


def get_items(data):
    items = []
    for itm in data:
        item1 = {
            "idx": int(itm["id"]),
            "item_type": itm["type"],
            "item_name": get_name(itm["name"]),
            "value": itm["values"]
        }
        items.append(item1)
    return items
