from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetCustomerTool(Tool):
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
        customer_id = (tool_parameters.get("customer_id") or "").strip()
        email = (tool_parameters.get("email") or "").strip()

        if not customer_id and not email:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "customer_id_or_email_is_required",
                }
            )
            return

        if customer_id and email:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "specify_only_one_of_customer_id_or_email",
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
        customer_fields = """
          id
          legacyResourceId
          displayName
          firstName
          lastName
          email
          phone
          state
          createdAt
          numberOfOrders
          amountSpent {
            amount
            currencyCode
          }
          tags
        """

        if customer_id:
            query = f"""
            query GetCustomerById($id: ID!) {{
              customer(id: $id) {{
                {customer_fields}
              }}
            }}
            """
            variables = {
                "id": f"gid://shopify/Customer/{customer_id}",
            }
        else:
            query = f"""
            query GetCustomerByEmail($first: Int!, $query: String!) {{
              customers(first: $first, query: $query) {{
                nodes {{
                  {customer_fields}
                }}
              }}
            }}
            """
            variables = {
                "first": 1,
                "query": f'email:"{email}"',
            }

        headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "variables": variables,
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

            if customer_id:
                customer = data.get("data", {}).get("customer")
            else:
                customer = next(
                    iter(data.get("data", {}).get("customers", {}).get("nodes", [])),
                    None,
                )

            if not customer:
                yield self.create_json_message(
                    {
                        "ok": False,
                        "error": "customer_not_found",
                        "customer_id": customer_id or None,
                        "email": email or None,
                    }
                )
                return

            amount_spent = customer.get("amountSpent", {})
            formatted_customer = {
                "id": customer.get("legacyResourceId"),
                "gid": customer.get("id"),
                "display_name": customer.get("displayName"),
                "first_name": customer.get("firstName"),
                "last_name": customer.get("lastName"),
                "email": customer.get("email"),
                "phone": customer.get("phone"),
                "state": customer.get("state"),
                "created_at": customer.get("createdAt"),
                "number_of_orders": customer.get("numberOfOrders"),
                "amount_spent": amount_spent.get("amount"),
                "currency": amount_spent.get("currencyCode"),
                "tags": customer.get("tags"),
            }

            yield self.create_json_message(
                {
                    "ok": True,
                    "customer": formatted_customer,
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
