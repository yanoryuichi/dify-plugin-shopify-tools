# Shopify Tools for Dify

A Dify tool plugin that provides Shopify tools for workflows and agents.

## Features

- Get a product by `product_id`
- Get a product by `handle`
- Get an order by `order_id`
- Get an order by `name`
- Search orders by `query`
- Search products by `query`
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

### `search-products`

Input:

- `query`
- `limit` (optional, 1-20)

Output:

- matched product list
- product ID
- handle
- title
- image URL
- price
- inventory
- variants

### `get-order`

Input:

- `order_id` or `name`

Output:

- order number
- created date
- financial status
- fulfillment status
- total price
- customer summary
- line items

### `search-orders`

Input:

- `query`
- `limit` (optional, 1-20)

Output:

- matched order list
- order ID
- order number
- created date
- financial status
- fulfillment status
- total price
- customer summary

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
