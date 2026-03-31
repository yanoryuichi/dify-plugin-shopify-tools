from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class SearchProductsTool(Tool):
    def _get_access_token(self) -> str:
        auth_method = (self.runtime.credentials.get("auth_method") or "").strip()
        shop_domain = (self.runtime.credentials.get("shop_domain") or "").strip()

        if auth_method == "access_token":
            token = (
                self.runtime.credentials.get("admin_api_access_token") or ""
            ).strip()
            if not token:
                raise ValueError("admin_api_access_token is required")
            return token

        if auth_method == "client_credentials":
            client_id = (self.runtime.credentials.get("client_id") or "").strip()
            client_secret = (
                self.runtime.credentials.get("client_secret") or ""
            ).strip()

            if not client_id or not client_secret:
                raise ValueError("client_id and client_secret are required")

            token_url = f"https://{shop_domain}/admin/oauth/access_token"
            response = requests.post(
                token_url,
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                },
                data={
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "grant_type": "client_credentials",
                },
                timeout=30,
            )
            response.raise_for_status()
            data = response.json()

            access_token = (data.get("access_token") or "").strip()
            if not access_token:
                raise ValueError("failed to get access_token by client_credentials")

            return access_token

        raise ValueError("unsupported auth_method")

    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        query = (tool_parameters.get("query") or "").strip()
        raw_limit = tool_parameters.get("limit", 5)

        if not query:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "query_is_required",
                }
            )
            return

        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "limit_must_be_an_integer",
                }
            )
            return

        if limit < 1 or limit > 20:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "limit_must_be_between_1_and_20",
                }
            )
            return

        shop_domain = (self.runtime.credentials.get("shop_domain") or "").strip()
        api_version = (self.runtime.credentials.get("api_version") or "").strip()

        if not shop_domain or not api_version:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "missing_provider_credentials",
                }
            )
            return

        try:
            access_token = self._get_access_token()
        except Exception as e:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "authentication_error",
                    "message": str(e),
                }
            )
            return

        url = f"https://{shop_domain}/admin/api/{api_version}/graphql.json"
        query_text = """
        query SearchProducts($first: Int!, $query: String!) {
          products(first: $first, query: $query) {
            nodes {
              id
              legacyResourceId
              title
              handle
              status
              totalInventory
              featuredMedia {
                preview {
                  image {
                    url
                  }
                }
              }
              variants(first: 5) {
                nodes {
                  id
                  legacyResourceId
                  title
                  sku
                  price
                  inventoryQuantity
                }
              }
            }
          }
        }
        """

        payload = {
            "query": query_text,
            "variables": {
                "first": limit,
                "query": query,
            },
        }
        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("errors"):
                yield self.create_json_message(
                    {
                        "ok": False,
                        "error": "graphql_error",
                        "details": data["errors"],
                    }
                )
                return

            products = data.get("data", {}).get("products", {}).get("nodes", [])
            formatted_products = []

            for product in products:
                variants = product.get("variants", {}).get("nodes", [])
                first_variant = variants[0] if variants else None
                image_url = (
                    product.get("featuredMedia", {})
                    .get("preview", {})
                    .get("image", {})
                    .get("url")
                )

                formatted_products.append(
                    {
                        "id": product.get("legacyResourceId"),
                        "gid": product.get("id"),
                        "title": product.get("title"),
                        "handle": product.get("handle"),
                        "status": product.get("status"),
                        "image_url": image_url,
                        "total_inventory": product.get("totalInventory"),
                        "price": first_variant.get("price") if first_variant else None,
                        "sku": first_variant.get("sku") if first_variant else None,
                        "variant_title": (
                            first_variant.get("title") if first_variant else None
                        ),
                        "variants": variants,
                    }
                )

            yield self.create_json_message(
                {
                    "ok": True,
                    "query": query,
                    "count": len(formatted_products),
                    "products": formatted_products,
                }
            )

        except requests.HTTPError as e:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "http_error",
                    "message": str(e),
                    "response_text": response.text if "response" in locals() else None,
                }
            )
        except Exception as e:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "unexpected_error",
                    "message": str(e),
                }
            )
