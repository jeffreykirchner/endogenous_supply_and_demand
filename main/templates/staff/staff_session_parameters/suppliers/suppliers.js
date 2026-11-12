show_edit_parameter_set_supplier: function show_edit_parameter_set_supplier(id) {
    if (app.session.started || app.working || app.reconnecting) return;
    app.current_parameter_set_supplier = Object.assign({}, app.parameter_set.parameter_set_suppliers[id]);
    app.supplier_errors = {};
    app.supplier_message = "";
    app.edit_parameterset_supplier_modal.show();
},

send_parameter_set_supplier_change: function send_parameter_set_supplier_change(message_type) {
    app.supplier_errors = {};
    app.supplier_message = "";
    app.working = true;
    app.send_message(message_type, {
        session_id: app.session.id,
        parameterset_supplier_id: app.current_parameter_set_supplier.id,
        form_data: app.current_parameter_set_supplier,
    });
},
