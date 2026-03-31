from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._shopify_tags import graphql_request, parse_tags


class AddProductTagsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        product_id = (tool_parameters.get("product_id") or "").strip()
        tags = parse_tags(tool_parameters.get("tags"))

        if not product_id:
            yield self.create_json_message(
                {"ok": False, "error": "product_id_is_required"}
            )
            return

        if not tags:
            yield self.create_json_message({"ok": False, "error": "tags_are_required"})
            return

        mutation = """
        mutation AddProductTags($id: ID!, $tags: [String!]!) {
          tagsAdd(id: $id, tags: $tags) {
            node {
              ... on Product {
                id
                legacyResourceId
                title
                handle
                tags
              }
            }
            userErrors {
              field
              message
            }
          }
        }
        """

        try:
            data = graphql_request(
                self.runtime.credentials,
                mutation,
                {"id": f"gid://shopify/Product/{product_id}", "tags": tags},
            )

            if data.get("errors"):
                yield self.create_json_message(
                    {"ok": False, "error": "graphql_error", "details": data["errors"]}
                )
                return

            payload = data.get("data", {}).get("tagsAdd", {})
            if payload.get("userErrors"):
                yield self.create_json_message(
                    {
                        "ok": False,
                        "error": "user_error",
                        "details": payload["userErrors"],
                    }
                )
                return

            product = payload.get("node")
            yield self.create_json_message(
                {
                    "ok": True,
                    "action": "add",
                    "resource_type": "product",
                    "product": {
                        "id": product.get("legacyResourceId"),
                        "gid": product.get("id"),
                        "title": product.get("title"),
                        "handle": product.get("handle"),
                        "tags": product.get("tags", []),
                    },
                    "requested_tags": tags,
                }
            )
        except ValueError as e:
            yield self.create_json_message(
                {"ok": False, "error": str(e), "message": str(e)}
            )
        except requests.HTTPError as e:
            yield self.create_json_message(
                {"ok": False, "error": "http_error", "message": str(e)}
            )
        except Exception as e:
            yield self.create_json_message(
                {"ok": False, "error": "unexpected_error", "message": str(e)}
            )
