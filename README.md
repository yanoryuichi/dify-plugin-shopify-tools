# Shopify Tools for Dify

A Dify tool plugin that provides Shopify tools for workflows and agents.

## Features

- Get a product by `product_id`
- Get a product by `handle`
- Supports:
  - Admin API access token
  - Client credentials (`client_id` / `client_secret`)

## Tool

### `get-product`

Input:

- `product_id` or `handle`

Output:

- product title
- description
- handle
- image URL
- price
- inventory
- variants

## Provider Settings

Required:

- `shop_domain`
- `api_version`
- `auth_method`

If `auth_method = access_token`:

- `admin_api_access_token`

If `auth_method = client_credentials`:

- `client_id`
- `client_secret`

## Notes

- `shop_domain` should be like `your-store.myshopify.com`
- Do not include `https://`

## Author

ryuichi