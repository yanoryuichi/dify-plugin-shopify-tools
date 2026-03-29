from typing import Any

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError


class ShopifyToolsProvider(ToolProvider):
    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            shop_domain = (credentials.get("shop_domain") or "").strip()
            admin_api_access_token = (credentials.get("admin_api_access_token") or "").strip()
            api_version = (credentials.get("api_version") or "").strip()

            if not shop_domain:
                raise ValueError("shop_domain is required")

            if not admin_api_access_token:
                raise ValueError("admin_api_access_token is required")

            if not api_version:
                raise ValueError("api_version is required")

            if "." not in shop_domain:
                raise ValueError("shop_domain must look like your-store.myshopify.com")

        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e))
