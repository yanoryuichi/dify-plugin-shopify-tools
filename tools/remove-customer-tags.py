from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage

from tools._shopify_tags import graphql_request, parse_tags


class RemoveCustomerTagsTool(Tool):
    def _invoke(self, tool_parameters: dict[str, Any]) -> Generator[ToolInvokeMessage]:
        customer_id = (tool_parameters.get("customer_id") or "").strip()
        tags = parse_tags(tool_parameters.get("tags"))

        if not customer_id:
            yield self.create_json_message(
                {"ok": False, "error": "customer_id_is_required"}
            )
            return

        if not tags:
            yield self.create_json_message({"ok": False, "error": "tags_are_required"})
            return

        mutation = """
        mutation RemoveCustomerTags($id: ID!, $tags: [String!]!) {
          tagsRemove(id: $id, tags: $tags) {
            node {
              ... on Customer {
                id
                legacyResourceId
                displayName
                email
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
                {"id": f"gid://shopify/Customer/{customer_id}", "tags": tags},
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

            customer = payload.get("node")
            yield self.create_json_message(
                {
                    "ok": True,
                    "action": "remove",
                    "resource_type": "customer",
                    "customer": {
                        "id": customer.get("legacyResourceId"),
                        "gid": customer.get("id"),
                        "display_name": customer.get("displayName"),
                        "email": customer.get("email"),
                        "tags": customer.get("tags", []),
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
