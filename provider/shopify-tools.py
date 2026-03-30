from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ShopifyToolsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            shop_domain = (credentials.get("shop_domain") or "").strip()
            auth_method = (credentials.get("auth_method") or "").strip()
            admin_api_access_token = (
                credentials.get("admin_api_access_token") or ""
            ).strip()
            client_id = (credentials.get("client_id") or "").strip()
            client_secret = (credentials.get("client_secret") or "").strip()
            api_version = (credentials.get("api_version") or "").strip()

            if not shop_domain:
                raise ValueError("shop_domain is required")

            if "." not in shop_domain:
                raise ValueError("shop_domain must look like your-store.myshopify.com")

            if not auth_method:
                raise ValueError("auth_method is required")

            if auth_method not in {"access_token", "client_credentials"}:
                raise ValueError(
                    "auth_method must be access_token or client_credentials"
                )

            if not api_version:
                raise ValueError("api_version is required")

            if auth_method == "access_token":
                if not admin_api_access_token:
                    raise ValueError(
                        "admin_api_access_token is required when auth_method=access_token"
                    )

            if auth_method == "client_credentials":
                if not client_id:
                    raise ValueError(
                        "client_id is required when auth_method=client_credentials"
                    )
                if not client_secret:
                    raise ValueError(
                        "client_secret is required when auth_method=client_credentials"
                    )

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
