from django.db import migrations


def remove_cached_tokens_per_period(apps, schema_editor):
    parameter_set = apps.get_model("main", "ParameterSet")
    db = schema_editor.connection.alias
    for item in parameter_set.objects.using(db).exclude(json_for_session=None).iterator():
        if isinstance(item.json_for_session, dict) and "tokens_per_period" in item.json_for_session:
            del item.json_for_session["tokens_per_period"]
            parameter_set.objects.using(db).filter(pk=item.pk).update(json_for_session=item.json_for_session)


def update_general_settings_help(apps, schema_editor):
    help_docs = apps.get_model("main", "HelpDocs")
    db = schema_editor.connection.alias
    for item in help_docs.objects.using(db).filter(title="Staff Parameters General").iterator():
        text = item.text.replace(
            "<br><br><strong>Tokens per Period</strong>: The number of cherries available each period.",
            "",
        ).replace("Token Value (&cent;)", "Inventory Unit Value (&cent;)")
        if text != item.text:
            help_docs.objects.using(db).filter(pk=item.pk).update(text=text)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0082_instruction_script"),
    ]

    operations = [
        migrations.RunPython(remove_cached_tokens_per_period, migrations.RunPython.noop),
        migrations.RunPython(update_general_settings_help, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="parameterset",
            name="tokens_per_period",
        ),
    ]
