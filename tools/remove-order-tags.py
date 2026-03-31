from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._shopify_tags import graphql_request, parse_tags


class RemoveOrderTagsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        order_id = (tool_parameters.get("order_id") or "").strip()
        tags = parse_tags(tool_parameters.get("tags"))

        if not order_id:
            yield self.create_json_message({"ok": False, "error": "order_id_is_required"})
            return

        if not tags:
            yield self.create_json_message({"ok": False, "error": "tags_are_required"})
            return

        mutation = """
        mutation RemoveOrderTags($id: ID!, $tags: [String!]!) {
          tagsRemove(id: $id, tags: $tags) {
            node {
              ... on Order {
                id
                legacyResourceId
                name
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
                {"id": f"gid://shopify/Order/{order_id}", "tags": tags},
            )

            if data.get("errors"):
                yield self.create_json_message(
                    {"ok": False, "error": "graphql_error", "details": data["errors"]}
                )
                return

            payload = data.get("data", {}).get("tagsRemove", {})
            if payload.get("userErrors"):
                yield self.create_json_message(
                    {
                        "ok": False,
                        "error": "user_error",
                        "details": payload["userErrors"],
                    }
                )
                return

            order = payload.get("node")
            yield self.create_json_message(
                {
                    "ok": True,
                    "action": "remove",
                    "resource_type": "order",
                    "order": {
                        "id": order.get("legacyResourceId"),
                        "gid": order.get("id"),
                        "name": order.get("name"),
                        "tags": order.get("tags", []),
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
