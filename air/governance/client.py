"""Top-level governance client that aggregates all governance sub-clients."""

from air import BASE_URL
from air.auth.token_provider import TokenProvider
from air.governance.api_keys import APIKeysClient, AsyncAPIKeysClient
from air.governance.memberships import AsyncMembershipsClient, MembershipsClient
from air.governance.models import AsyncModelsClient, ModelsClient
from air.governance.organizations import AsyncOrganizationsClient, OrganizationsClient
from air.governance.projects import AsyncProjectsClient, ProjectsClient
from air.governance.users import AsyncUsersClient, UsersClient
from air.governance.workspaces import AsyncWorkspacesClient, WorkspacesClient


class AsyncGovernanceClient:  # pylint: disable=too-few-public-methods
    """Asynchronous governance client.

    Provides access to governance sub-clients for managing organizations,
    users, memberships, workspaces, projects, and API keys.

    Sub-clients:
        organizations: Organization CRUD.
        users: User CRUD and lookup.
        memberships: Membership management and role updates.
        workspaces: Workspace CRUD.
        projects: Project listing.
        models: Private model creation, listing, and deletion.
        api_keys: API key create / validate / inspect / revoke.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        self.organizations = AsyncOrganizationsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.users = AsyncUsersClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.memberships = AsyncMembershipsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.workspaces = AsyncWorkspacesClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.projects = AsyncProjectsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.models = AsyncModelsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.api_keys = AsyncAPIKeysClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )


class GovernanceClient:  # pylint: disable=too-few-public-methods
    """Synchronous governance client.

    Provides access to governance sub-clients for managing organizations,
    users, memberships, workspaces, projects, models, and API keys.

    Sub-clients:
        organizations: Organization CRUD.
        users: User CRUD and lookup.
        memberships: Membership management and role updates.
        workspaces: Workspace CRUD.
        projects: Project listing.
        models: Private model creation, listing, and deletion.
        api_keys: API key create / validate / inspect / revoke.
    """

    def __init__(
        self,
        api_key: str | TokenProvider,
        *,
        base_url: str = BASE_URL,
        default_headers: dict[str, str] | None = None,
    ):
        self.organizations = OrganizationsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.users = UsersClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.memberships = MembershipsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.workspaces = WorkspacesClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.projects = ProjectsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.models = ModelsClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
        self.api_keys = APIKeysClient(
            api_key,
            base_url=base_url,
            default_headers=default_headers,
        )
