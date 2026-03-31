from typing import Any

import requests


def get_access_token(credentials: dict[str, Any]) -> str:
    auth_method = (credentials.get("auth_method") or "").strip()
    shop_domain = (credentials.get("shop_domain") or "").strip()

    if auth_method == "access_token":
        token = (credentials.get("admin_api_access_token") or "").strip()
        if not token:
            raise ValueError("admin_api_access_token is required")
        return token

    if auth_method == "client_credentials":
        client_id = (credentials.get("client_id") or "").strip()
        client_secret = (credentials.get("client_secret") or "").strip()

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


def parse_tags(raw_tags: Any) -> list[str]:
    if raw_tags is None:
        return []

    if isinstance(raw_tags, list):
        parts = raw_tags
    else:
        parts = str(raw_tags).split(",")

    tags: list[str] = []
    for part in parts:
        tag = str(part).strip()
        if tag and tag not in tags:
            tags.append(tag)

    return tags


def graphql_request(
    credentials: dict[str, Any], query: str, variables: dict[str, Any]
) -> dict[str, Any]:
    shop_domain = (credentials.get("shop_domain") or "").strip()
    api_version = (credentials.get("api_version") or "").strip()

    if not shop_domain or not api_version:
        raise ValueError("missing_provider_credentials")

    access_token = get_access_token(credentials)
    url = f"https://{shop_domain}/admin/api/{api_version}/graphql.json"
    response = requests.post(
        url,
        headers={
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
        },
        json={
            "query": query,
            "variables": variables,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()
