// Copyright (c) 2022, phamos GmbH and contributors
// For license information, please see license.txt

var checklist_fields = ["proma_item_template","item_type","edit_values","item_name","hint","proma_item_template_values"];

function get_child_tables(frm, s_cd_name,fields,t_cd_name){
                for(var n = 0; n < s_cd_name.length; n++){
                    var item = s_cd_name[n];
                    var child = {};
                    for(var m = 0; m < fields.length; m++){
                        child[fields[m]] = item[fields[m]];
                    }

                    frm.add_child(String(t_cd_name),child);
                    frm.refresh_fields(String(t_cd_name));
                }
}

function checklist_dialog(frm) {
	let dialog = new frappe.ui.form.MultiSelectDialog({
		doctype: "Proma Check List Template",
		target: frm,
		setters: {
		},
		date_field: "creation",
		get_query() {
			return {
				filters: {  }
			};
		},
		action(selections) {
	        var name = selections[0];
	        frappe.db.get_doc("Proma Check List Template", name)
            .then(doc => {
                get_child_tables(frm,doc.proma_check_list_template,checklist_fields,"items");
            });
		}
	});
}

function open_template_values_editor(template, current_values = {}) {
	return new Promise(resolve => {
		frappe.model.with_doc("Proma Item Template", template).then((doc) => {
			let d = new frappe.ui.Dialog({
				title: __("Edit Values"),
				fields: get_fields(doc),
				primary_action(values) {
					d.hide();
					resolve(values);
				},
			});
			d.set_values(current_values);
			d.show();

			d.sections.forEach((sect) => {
				let fields_with_value = sect.fields_list.filter(
					(field) => current_values[field.df.fieldname]
				);

				if (fields_with_value.length) {
					sect.collapse(false);
				}
			});
		});
	});

	function get_fields(doc) {
		let normal_fields = [];
		let table_fields = [];

		let current_table = null;
		for (let df of doc.fields) {
			if (current_table) {
				if (df.fieldtype != 'Table Break') {
					current_table.fields.push(df);
				} else {
					table_fields.push(df);
					current_table = df;
				}
			} else if (df.fieldtype != 'Table Break') {
				normal_fields.push(df);
			} else {
				table_fields.push(df);
				current_table = df;
				current_table.fields = [];
			}
		}

		let fields = [
			...normal_fields,
			...table_fields.map(tf => {
				let data = current_values[tf.fieldname] || [];
				return {
					label: tf.label,
					fieldname: tf.fieldname,
					fieldtype: 'Table',
					fields: tf.fields.map((df, i) => ({
						...df,
						in_list_view: i <= 1,
						columns: tf.fields.length == 1 ? 10 : 5
					})),
					data,
					get_data: () => data
				};
			})
		];

		return fields;
	}
}

frappe.ui.form.on('ProMa Checklist', {
	refresh(frm) {
	    frm.add_custom_button('Item Checklist Template', function () { frm.trigger('get_items') }, __("Get Items From"));
	    if(!frm.doc.__islocal){
			frm.add_custom_button(	__('Export List'),
			() => {
			    if(frm.is_dirty()){
	                frappe.throw("Kindly save the ProMa Checklist first before proceeding");
	            }
				frappe.call({
					method: 'proma.auto_custom.proma_checklist',
					args: {
					    "checklist":frm.doc.name
					},
					freeze: true,
					callback: (res) => {

					    var x = JSON.parse(res.message)
						frappe.msgprint("Exported Successfully \n Document ID: "+x["id"])
						frm.set_value("id",x["id"]);


					}
				});

			});
	    }
	},
	get_items(frm){
	    checklist_dialog(frm);
	},
	onload: function(frm) {
		frm.set_query('proma_item_template', 'items', function() {
			return {
				filters: {
					"type": ['in', ['Item', 'Group','Page']]
				}
			};
		});
	}
});

frappe.ui.form.on("ProMa Checklist Items", {
	edit_values(frm, cdt, cdn) {
		let row = frm.selected_doc;
		let values = JSON.parse(row.proma_item_template_values || "{}");
		open_template_values_editor(row.proma_item_template, values)
			.then(new_values => {
				frappe.model.set_value(cdt, cdn, "proma_item_template_values", JSON.stringify(new_values));

			});
	},
});
