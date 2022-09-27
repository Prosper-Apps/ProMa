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


def get_translation(source_text):
    if source_text:
        lst = frappe.db.get_list('Translation', filters={'source_text': source_text},
                                 fields=['language', 'translated_text'])
        trans = {}
        if lst:
            for item in lst:
                trans.setdefault(str(item.language), str(item.translated_text))

            if trans:
                if not trans.get("en"):
                    trans.setdefault("en", source_text)
                if not trans.get("es"):
                    trans.setdefault("es", source_text)
                if not trans.get("zh"):
                    trans.setdefault("zh", source_text)
                if not trans.get("de"):
                    trans.setdefault("de", source_text)
            return trans
        else:
            return {
                "de": source_text,
                "en": source_text,
                "es": source_text,
                "zh": source_text
            }
    else:
        return {
            "de": None,
            "en": None,
            "es": None,
            "zh": None
        }


def get_item_values(items_values, id, position, item_type, item_name, hint, item_values=None, parent_id=None):
    return_dict = {}
    for itm_key, itm_value in items_values.items():
        if itm_key == "options":
            if isinstance(itm_value, list):
                opt_list = []
                for opt in itm_value:
                    opt_itm = {}
                    for key, value in opt.items():
                        if key != "__islocal":
                            opt_itm[key] = value
                        if key == "label":
                            opt_itm[key] = get_translation(value)

                    opt_itm.pop("idx")
                    opt_itm.pop("name")

                    opt_list.append(opt_itm)
                return_dict.update({"options": opt_list})

        elif isinstance(itm_value, list) and itm_key != "options":
            list_itm = []
            for itm in itm_value:
                dct_itm = {}
                for key, value in itm.items():
                    if key == "idx":
                        dct_itm["position"] = value - 1
                    if key != "__islocal":
                        dct_itm[key] = value
                dct_itm.pop("idx")
                list_itm.append(dct_itm)
            return_dict.update({str(itm_key): list_itm})
        elif itm_key == "values":
            if not item_values:
                values = [itm_value]
                return_dict["values"] = values
        elif itm_key == "dataType":
            return_dict["dataType"] = itm_value
        else:
            props = {}
            props.setdefault("hint", get_translation(hint))
            if isinstance(itm_value, int):
                props.update({str(itm_key): bool(int(itm_value))})
            else:
                props.update({str(itm_key): itm_value})

            return_dict.update({"props": props})

    return_dict["id"] = str(id)
    return_dict["values"] = item_values
    return_dict["position"] = int(position) - 1
    return_dict["type"] = item_type.lower()
    return_dict["name"] = get_translation(item_name)
    if parent_id != "":
        return_dict["parentId"] = str(parent_id)
    else:
        return_dict["parentId"] = None
    if not return_dict.get("values"):
        return_dict["values"] = None

    return return_dict


def get_extension_items(items_values, id, position, item_type, item_name, hint, item_value=None, parent_id=None):
    return_dict = {"dataType": None, "values": item_value, "type": item_type.lower(),
                   "name": get_translation(item_name), "extensionItems": None, "template": [],
                   "hint": get_translation(hint), "position": int(position) - 1, "id": str(id), "parentId": parent_id
                   }
    for itm_key, itm_value in items_values.items():
        extension_itm = {}
        pi = []
        if itm_key == "order":
            extension_itm["order"] = itm_value
        if itm_key == "id":
            extension_itm["id"] = itm_value
            pchklist_itm = frappe.db.get_list('ProMa Checklist Template Items',
                                              fields=["item_type", "item_name",
                                                      "hint", "proma_item_template_values", "idx"],
                                              filters={"docstatus": 1, "parent": itm_value},
                                              order_by="idx")
            page_id = ""
            grp_id = ""
            for b in pchklist_itm:
                pos = int(b.idx) + 1
                if b.item_type == "Page":
                    page_id = b.idx
                    pi.append(get_item_values(json.loads(b.proma_item_template_values), b.idx,
                                              pos, b.item_type, b.item_name, b.hint, ""))
                if b.item_type == "Group":
                    grp_id = b.idx
                    pi.append(get_item_values(json.loads(b.proma_item_template_values),
                                              b.idx, pos, b.item_type, b.item_name, b.hint, "", page_id))
                if b.item_type == "Item":
                    pi.append(get_item_values(json.loads(b.proma_item_template_values),
                                              b.idx, pos, b.item_type, b.item_name, b.hint, "", grp_id))
            extension_itm["items"] = pi
            return_dict.update({"extensionItems": extension_itm})
            return_dict.update({"template": pi})

    return return_dict


@frappe.whitelist()
def proma_checklist(checklist):
    cl_item = frappe.get_doc("ProMa Checklist", checklist)
    camera_setting = frappe._dict()
    template_names = get_translation(cl_item.template_names)
    checklist_name = get_translation(cl_item.chk_name)
    checklist_description = get_translation(cl_item.description)
    file_names = get_translation(cl_item.file_url_name)
    file_urls = get_translation(cl_item.file_url)
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
    page_id = ""
    grp_id = ""
    for b in cl_item.items:
        if b.item_type == "Page":
            page_id = b.idx
            proma_items.append(get_item_values(json.loads(b.proma_item_template_values), b.idx,
                                               b.idx, b.item_type, b.item_name, b.hint, b.values))
        if b.item_type == "Group":
            grp_id = b.idx
            proma_items.append(get_item_values(json.loads(b.proma_item_template_values),
                                               b.idx, b.idx, b.item_type, b.item_name, b.hint, b.values, page_id))
        if b.item_type == "Item":
            proma_items.append(get_item_values(json.loads(b.proma_item_template_values),
                                               b.idx, b.idx, b.item_type, b.item_name, b.hint, b.values, grp_id))
        if b.item_type == "Extension":
            proma_items.append(get_extension_items(json.loads(b.proma_item_template_values),
                                                   b.idx, b.idx, b.item_type, b.item_name, b.hint, b.values, grp_id))
    
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
