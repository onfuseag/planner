// Copyright (c) 2024, ONFUSE AG and contributors
// For license information, please see license.txt

frappe.ui.form.on("Project Checklist", {
    refresh(frm) {
		frm.add_custom_button(__('Email'), function(){
            const args = {
    			doc: frm.doc,
    			frm: frm,
    			recipients: frm.doc.customer_mail,
    			is_a_reply: false,
    			title: null,
    			last_email: null,
    			subject: null,
    			reply_all: false,
    			attach_document_print: 1
    		};
    		new frappe.views.CommunicationComposer(args);
            
        });
	}
});
