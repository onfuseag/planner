from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch

import frappe

from planner.api.tasks import get_users_with_tasks


class TestTaskUserVisibility(TestCase):
	def test_users_with_only_unreadable_tasks_are_excluded(self):
		candidates = [
			self._row("TASK-HIDDEN-1", "alice@example.com", "Alice"),
			self._row("TASK-VISIBLE-1", "bob@example.com", "Bob"),
			self._row("TASK-VISIBLE-2", "bob@example.com", "Bob"),
			self._row("TASK-HIDDEN-2", "charlie@example.com", "Charlie"),
			self._row("TASK-VISIBLE-3", "charlie@example.com", "Charlie"),
		]
		database = SimpleNamespace(sql=Mock(return_value=candidates))

		with (
			patch("planner.api.tasks.check_planner_access"),
			patch.object(frappe, "db", database),
			patch.object(
				frappe,
				"get_list",
				return_value=["TASK-VISIBLE-1", "TASK-VISIBLE-2", "TASK-VISIBLE-3"],
			) as get_list,
		):
			users = get_users_with_tasks("2026-11-01", "2026-11-30")

		self.assertEqual(
			users,
			[
				self._user("bob@example.com", "Bob"),
				self._user("charlie@example.com", "Charlie"),
			],
		)
		self.assertEqual(get_list.call_args.args, ("Task",))
		self.assertEqual(get_list.call_args.kwargs["pluck"], "name")
		self.assertEqual(get_list.call_args.kwargs["limit_page_length"], 0)

	def test_no_candidates_returns_empty_without_permission_query(self):
		database = SimpleNamespace(sql=Mock(return_value=[]))
		with (
			patch("planner.api.tasks.check_planner_access"),
			patch.object(frappe, "db", database),
			patch.object(frappe, "get_list") as get_list,
		):
			self.assertEqual(get_users_with_tasks("2026-11-01", "2026-11-30"), [])
		get_list.assert_not_called()

	@staticmethod
	def _row(task_name, email, full_name):
		return {"task_name": task_name, **TestTaskUserVisibility._user(email, full_name)}

	@staticmethod
	def _user(email, full_name):
		return {"name": email, "full_name": full_name, "image": None, "email": email}
