// Copyright (c) 2022, Chris and contributors
// For license information, please see license.txt
function open_template_values_editor(template, current_values = {}) {
	return new Promise(resolve => {
		frappe.model.with_doc("Proma Item Template", template).then((doc) => {
			let d = new frappe.ui.Dialog({
				size:"large",
				title: __("Configure Values"),
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

				// start capturing fields in current_table till the next table break
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

frappe.ui.form.on('Proma Check List Template', {
	// refresh: function(frm) {

	// }
    	onload: function(frm) {
		frm.set_query('proma_item_template', 'proma_check_list_template', function() {
			return {
				filters: {
					"type": ['in', ['Item', 'Group','Page']]
				}
			};
		});
	},
});

frappe.ui.form.on("ProMa Checklist Template Items", {
	edit_values(frm, cdt, cdn) {
		let row = frm.selected_doc;
		let values = JSON.parse(row.proma_item_template_values || "{}");
		open_template_values_editor(row.proma_item_template, values)
			.then(new_values => {
				frappe.model.set_value(cdt, cdn, "proma_item_template_values", JSON.stringify(new_values));
			});
	},
});
