import importlib
from types import SimpleNamespace

from django.apps import apps
from django.test import TestCase

from main.forms import ParameterSetForm
from main.models import HelpDocs, Session


class RemoveCollectibleTokensTests(TestCase):
    fixtures = ["auth_user.json", "main.json"]

    def setUp(self):
        self.session = Session.objects.get(title="Sample")
        self.parameter_set = self.session.parameter_set

    def test_form_and_serialized_parameters_exclude_removed_field(self):
        self.assertNotIn("tokens_per_period", ParameterSetForm().fields)
        parameters = self.parameter_set.json(update_required=True)
        self.assertNotIn("tokens_per_period", parameters)
        self.assertIn("token_cents_value", parameters)

    def test_legacy_parameter_import_ignores_removed_field(self):
        parameters = self.parameter_set.json(update_required=True).copy()
        parameters["tokens_per_period"] = 12

        self.assertEqual(self.parameter_set.from_dict(parameters)["status"], "success")
        self.assertNotIn("tokens_per_period", self.parameter_set.json())

    def test_new_world_has_inventory_without_collectibles_or_grass(self):
        self.parameter_set.parameter_set_grounds.all().delete()
        self.session.start_experiment()

        self.assertNotIn("tokens", self.session.world_state)
        self.assertTrue(self.session.world_state["session_players"])
        for player in self.session.world_state["session_players"].values():
            self.assertEqual(
                player["inventory"],
                {str(period_id): 0 for period_id in self.session.world_state["session_periods_order"]},
            )

    def test_migration_removes_only_obsolete_cached_key(self):
        self.parameter_set.json_for_session = {
            "tokens_per_period": 42,
            "token_cents_value": "2.00",
            "period_count": 3,
        }
        self.parameter_set.save(update_fields=["json_for_session"])
        migration = importlib.import_module("main.migrations.0083_remove_parameterset_tokens_per_period")
        migration.remove_cached_tokens_per_period(apps, SimpleNamespace(connection=SimpleNamespace(alias="default")))

        self.parameter_set.refresh_from_db()
        self.assertEqual(self.parameter_set.json_for_session, {
            "token_cents_value": "2.00",
            "period_count": 3,
        })

    def test_migration_updates_bundled_help(self):
        help_doc = HelpDocs.objects.get(title="Staff Parameters General")
        help_doc.text = (
            "Existing help.<br><br><strong>Tokens per Period</strong>: "
            "The number of cherries available each period."
            "<p><strong>Token Value (&cent;)</strong>: The value of a cherry in cents.</p>"
        )
        help_doc.save(update_fields=["text"])
        migration = importlib.import_module("main.migrations.0083_remove_parameterset_tokens_per_period")
        migration.update_general_settings_help(apps, SimpleNamespace(connection=SimpleNamespace(alias="default")))

        help_doc.refresh_from_db()
        text = help_doc.text
        self.assertNotIn("Tokens per Period", text)
        self.assertIn("Inventory Unit Value (&cent;)", text)
        self.assertIn("Existing help.", text)
