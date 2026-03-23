"""
Accounts models: User, Role, Team.

Custom User extends AbstractBaseUser for enterprise SSO compatibility.
Role-based access control is modelled as first-class domain objects.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, password, **extra_fields)


class Role(models.Model):
    """Named role with a set of platform permissions."""

    class RoleType(models.TextChoices):
        DEVELOPER = "developer", "Developer"
        REVIEWER = "reviewer", "Reviewer"
        TEAM_LEAD = "team_lead", "Team Lead"
        ADMIN = "admin", "Platform Admin"
        READ_ONLY = "read_only", "Read Only"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    role_type = models.CharField(max_length=50, choices=RoleType.choices)
    description = models.TextField(blank=True)

    # Capabilities granted to this role
    can_create_workflow = models.BooleanField(default=False)
    can_approve_plan = models.BooleanField(default=False)
    can_approve_pr = models.BooleanField(default=False)
    can_approve_deployment = models.BooleanField(default=False)
    can_publish_flow = models.BooleanField(default=False)
    can_manage_capabilities = models.BooleanField(default=False)
    can_view_audit = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Team(models.Model):
    """Organizational team grouping users."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)

    # Jira / GitHub integration references
    jira_project_keys = models.JSONField(default=list, blank=True)
    github_orgs = models.JSONField(default=list, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class User(AbstractBaseUser, PermissionsMixin):
    """
    Platform user. Supports local auth and enterprise SSO.
    Email is the unique identifier.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=300)
    display_name = models.CharField(max_length=100, blank=True)

    # Platform role
    role = models.ForeignKey(
        Role, on_delete=models.PROTECT, null=True, blank=True, related_name="users"
    )
    teams = models.ManyToManyField(Team, blank=True, related_name="members")

    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # SSO
    sso_provider = models.CharField(max_length=100, blank=True)
    sso_subject = models.CharField(max_length=500, blank=True)

    # Preferences
    preferences = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login_at = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = UserManager()

    class Meta:
        ordering = ["email"]

    def __str__(self):
        return self.email

    @property
    def effective_display_name(self) -> str:
        return self.display_name or self.full_name or self.email
