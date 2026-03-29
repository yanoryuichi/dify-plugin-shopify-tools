from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class ShopifyToolsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        product_id = (tool_parameters.get("product_id") or "").strip()
        if not product_id:
            yield self.create_text_message("product_id is required")
            return

        shop_domain = (self.runtime.credentials.get("shop_domain") or "").strip()
        admin_api_access_token = (self.runtime.credentials.get("admin_api_access_token") or "").strip()
        api_version = (self.runtime.credentials.get("api_version") or "").strip()

        if not shop_domain or not admin_api_access_token or not api_version:
            yield self.create_json_message({
                "ok": False,
                "error": "missing_provider_credentials",
            })
            return

        product_gid = f"gid://shopify/Product/{product_id}"
        url = f"https://{shop_domain}/admin/api/{api_version}/graphql.json"

        query = """
        query GetProduct($id: ID!) {
          product(id: $id) {
            id
            legacyResourceId
            title
            handle
            status
            description
            onlineStoreUrl
            totalInventory
            featuredMedia {
              preview {
                image {
                  url
                }
              }
            }
            variants(first: 20) {
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
        """

        headers = {
            "X-Shopify-Access-Token": admin_api_access_token,
            "Content-Type": "application/json",
        }

        payload = {
            "query": query,
            "variables": {
                "id": product_gid,
            },
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("errors"):
                yield self.create_json_message({
                    "ok": False,
                    "error": "graphql_error",
                    "details": data["errors"],
                })
                return

            product = data.get("data", {}).get("product")
            if not product:
                yield self.create_json_message({
                    "ok": False,
                    "error": "product_not_found",
                    "product_id": product_id,
                })
                return

            yield self.create_json_message({
                "ok": True,
                "product": product,
            })

        except requests.HTTPError as e:
            yield self.create_json_message({
                "ok": False,
                "error": "http_error",
                "message": str(e),
                "response_text": response.text if "response" in locals() else None,
            })
        except Exception as e:
            yield self.create_json_message({
                "ok": False,
                "error": "unexpected_error",
                "message": str(e),
            })
