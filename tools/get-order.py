from collections.abc import Generator
from typing import Any

import requests
from dify_plugin import Tool
from dify_plugin.entities.tool import ToolInvokeMessage


class GetOrderTool(Tool):
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
        order_id = (tool_parameters.get("order_id") or "").strip()
        name = (tool_parameters.get("name") or "").strip()

        if not order_id and not name:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "order_id_or_name_is_required",
                }
            )
            return

        if order_id and name:
            yield self.create_json_message(
                {
                    "ok": False,
                    "error": "specify_only_one_of_order_id_or_name",
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
        order_fields = """
          id
          legacyResourceId
          name
          createdAt
          cancelledAt
          closedAt
          displayFinancialStatus
          displayFulfillmentStatus
          totalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          currentSubtotalPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          totalShippingPriceSet {
            shopMoney {
              amount
              currencyCode
            }
          }
          customer {
            id
            displayName
            email
          }
          lineItems(first: 20) {
            nodes {
              id
              name
              sku
              quantity
              currentQuantity
              variant {
                product {
                  handle
                }
              }
              discountedTotalSet {
                shopMoney {
                  amount
                  currencyCode
                }
              }
            }
          }
        """

        if order_id:
            query = f"""
            query GetOrderById($id: ID!) {{
              order(id: $id) {{
                {order_fields}
              }}
            }}
            """
            variables = {
                "id": f"gid://shopify/Order/{order_id}",
            }
            data_path = ("order",)
        else:
            query = f"""
            query GetOrderByName($first: Int!, $query: String!) {{
              orders(first: $first, query: $query, sortKey: CREATED_AT, reverse: true) {{
                nodes {{
                  {order_fields}
                }}
              }}
            }}
            """
            search_name = name if name.startswith("#") else f"#{name}"
            variables = {
                "first": 1,
                "query": f'name:"{search_name}"',
            }
            data_path = ("orders", "nodes")

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

            if order_id:
                order = data.get("data", {}).get(data_path[0])
            else:
                order = next(
                    iter(
                        data.get("data", {})
                        .get(data_path[0], {})
                        .get(data_path[1], [])
                    ),
                    None,
                )

            if not order:
                yield self.create_json_message(
                    {
                        "ok": False,
                        "error": "order_not_found",
                        "order_id": order_id or None,
                        "name": name or None,
                    }
                )
                return

            total_price = (
                order.get("totalPriceSet", {})
                .get("shopMoney", {})
            )
            subtotal_price = (
                order.get("currentSubtotalPriceSet", {})
                .get("shopMoney", {})
            )
            shipping_price = (
                order.get("totalShippingPriceSet", {})
                .get("shopMoney", {})
            )
            customer = order.get("customer") or {}
            line_items = order.get("lineItems", {}).get("nodes", [])

            formatted_line_items = []
            for item in line_items:
                line_total = (
                    item.get("discountedTotalSet", {})
                    .get("shopMoney", {})
                )
                handle = (
                    item.get("variant", {})
                    .get("product", {})
                    .get("handle")
                )
                formatted_line_items.append(
                    {
                        "id": item.get("id"),
                        "name": item.get("name"),
                        "handle": handle,
                        "sku": item.get("sku"),
                        "quantity": item.get("quantity"),
                        "current_quantity": item.get("currentQuantity"),
                        "line_total": line_total.get("amount"),
                        "currency": line_total.get("currencyCode"),
                    }
                )

            formatted_order = {
                "id": order.get("legacyResourceId"),
                "gid": order.get("id"),
                "name": order.get("name"),
                "created_at": order.get("createdAt"),
                "cancelled_at": order.get("cancelledAt"),
                "closed_at": order.get("closedAt"),
                "display_financial_status": order.get("displayFinancialStatus"),
                "display_fulfillment_status": order.get("displayFulfillmentStatus"),
                "total_price": total_price.get("amount"),
                "subtotal_price": subtotal_price.get("amount"),
                "shipping_price": shipping_price.get("amount"),
                "currency": total_price.get("currencyCode"),
                "customer": {
                    "id": customer.get("id"),
                    "display_name": customer.get("displayName"),
                    "email": customer.get("email"),
                }
                if customer
                else None,
                "line_items": formatted_line_items,
            }

            yield self.create_json_message(
                {
                    "ok": True,
                    "order": formatted_order,
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
