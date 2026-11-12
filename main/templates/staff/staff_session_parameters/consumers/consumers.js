show_edit_parameter_set_consumer: function show_edit_parameter_set_consumer(id) {
    if (app.session.started || app.working || app.reconnecting) return;
    app.current_parameter_set_consumer = Object.assign({}, app.parameter_set.parameter_set_consumers[id]);
    app.consumer_errors = {};
    app.consumer_message = "";
    app.edit_parameterset_consumer_modal.show();
},

send_parameter_set_consumer_change: function send_parameter_set_consumer_change(message_type) {
    app.consumer_errors = {};
    app.consumer_message = "";
    app.working = true;
    app.send_message(message_type, {
        session_id: app.session.id,
        parameterset_consumer_id: app.current_parameter_set_consumer.id,
        form_data: app.current_parameter_set_consumer,
    });
},
