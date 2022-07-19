import frappe
from frappe import _, throw
import json
import requests
import datetime


def send_to_proma_api(data):
    url = "https://europe-west3-suncycle-proma-dev.cloudfunctions.net/api/protocols"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    try:
        response = requests.request("POST", url, headers=headers, data=json.dumps(data))
        if response.status_code == 200:
            return response.text
        else:
            return response.text
    except:
        print("exception occurred")


def get_multi_language_items(return_dict, list_item):
    for tdt in list_item:
        return_dict.setdefault("de", tdt.de),
        return_dict.setdefault("en", tdt.en),
        return_dict.setdefault("es", tdt.es),
        return_dict.setdefault("zh", tdt.zh)
        break
    return return_dict


@frappe.whitelist()
def proma_checklist(checklist):
    cl_item = frappe.get_doc("ProMa Checklist", checklist)

    template_names = checklist_name = checklist_description = file_urls = file_names = camera_setting = frappe._dict()
    template_names = get_multi_language_items(template_names, cl_item.template_name)
    checklist_name = get_multi_language_items(checklist_name, cl_item.checklist_name)
    checklist_description = get_multi_language_items(checklist_description, cl_item.checklist_description)
    file_names = get_multi_language_items(file_names, cl_item.file_url_name)
    file_urls = get_multi_language_items(file_urls, cl_item.file_url)

    contacts_list = []
    for c_list in cl_item.contacts:
        lst = {
            "id": c_list.id,
            "name": c_list.full_name,
            "phone": c_list.phone,
            "email": c_list.email
        }
        contacts_list.append(lst)

    contributors_list = []
    for c_lst in cl_item.proma_contributors:
        c_list = {
            "userid": c_lst.userid,
            "lastUpdate": str(c_lst.modified)
        }
        contributors_list.append(c_list)

    comments_list = []
    for c_itm in cl_item.comments:
        cmt = {
            "position": c_itm.idx,
            "body": c_itm.body,
            "createdBy": c_itm.created_by,
            "createdAt": str(c_itm.creation)
        }
        comments_list.append(cmt)

    for c_setting in cl_item.camera:
        camera_setting.setdefault("quality", c_setting.quality),
        camera_setting.setdefault("allowEditing", bool(int(c_setting.allow_editing))),
        camera_setting.setdefault("width", c_setting.width),
        camera_setting.setdefault("height", c_setting.height)
        break

    assigned_uids = []
    for au_id in cl_item.assigneduserids:
        assigned_uids.append(au_id.proma_user_id)

    assignedteams = []
    for a_team in cl_item.assignedteams:
        assignedteams.append(a_team.team)

    proma_items = []
    for b in cl_item.items:
        proma_items.append(b.proma_item_template_values)

    data = {
        "referenceId": cl_item.referenceid,
        "createdAt": str(cl_item.creation),
        "updatedAt": str(cl_item.modified),
        "template": {
            "id": cl_item.template_id,
            "name": template_names,
            "approvedAt": str(cl_item.approvedat)
        },
        "allowParallelEditing": bool(int(cl_item.allowparallelediting)),
        "requirePreCheck": bool(int(cl_item.requireprecheck)),
        "requirePostCheck": bool(int(cl_item.requirepostcheck)),
        "assignedUserIds": assigned_uids,
        "assignedTeams": assignedteams,
        "client": {
            "id": cl_item.client_id,
            "name": cl_item.client_name
        },
        "customer": {
            "id": cl_item.customer_id,
            "name": cl_item.customer_name
        },
        "state": int(cl_item.protocol_state),
        "name": checklist_name,
        "description": checklist_description,
        "installation": {
            "id": cl_item.installation_id,
            "name": cl_item.installation_name,
            "street": cl_item.street,
            "city": cl_item.city,
            "comment": cl_item.comment,
            "lat": cl_item.lat,
            "lng": cl_item.lng,
            "contacts": contacts_list
        },
        "servicePartner": {
            "id": cl_item.servicepartner,
            "name": cl_item.service_partner_name
        },
        "fileUrls": [
            {
                "id": cl_item.file_url_id,
                "url": file_urls,
                "name": file_names,
                "onDemand": bool(int(cl_item.on_demand)),
                "context": cl_item.context
            }
        ],
        "comments": comments_list,
        "settings": {
            "language": cl_item.language,
            "requiredFieldsOptional": bool(int(cl_item.requiredfieldsoptional)),
            "camera": camera_setting,
            "allowParallelEditing": bool(int(cl_item.allowparalleleditingcamera))
        },
        "contributors": contributors_list,
        "items": proma_items
    }
    res = send_to_proma_api(data)
    return res
