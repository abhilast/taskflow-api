# tests/unit/test_models.py
from django.test import TestCase
from django.contrib.auth.models import User
from tasks.models import Task


class TaskModelTest(TestCase):
    """Test Task model"""

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", password="testpass123"
        )

    def test_create_task(self):
        """Test creating a task"""
        task = Task.objects.create(
            title="Test Task",
            description="Test Description",
            created_by=self.user,
            status="TODO",
            priority="HIGH",
        )

        self.assertEqual(task.title, "Test Task")
        self.assertEqual(task.status, "TODO")
        self.assertEqual(task.priority, "HIGH")
        self.assertEqual(task.created_by, self.user)

    def test_task_str(self):
        """Test task string representation"""
        task = Task.objects.create(
            title="My Task", created_by=self.user, status="IN_PROGRESS"
        )

        self.assertEqual(str(task), "My Task (IN_PROGRESS)")
