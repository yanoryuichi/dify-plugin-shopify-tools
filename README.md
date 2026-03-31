# Shopify Tools for Dify

A Dify tool plugin for reading and updating Shopify products, orders, and customers.

## Overview

This plugin provides Shopify tools for:

- Getting a single product, order, or customer
- Searching products, orders, or customers
- Adding or removing tags on products, orders, or customers

Supported authentication methods:

- Admin API access token
- Client credentials (`client_id` / `client_secret`)

## Tools

### Products

- `get-product`
  - Input: `product_id` or `handle`
  - Output: title, description, handle, image URL, inventory, variants
- `search-products`
  - Input: `query`, `limit`
  - Output: matched product list
- `add-product-tags`
  - Input: `product_id`, `tags`
  - Output: updated product tags
- `remove-product-tags`
  - Input: `product_id`, `tags`
  - Output: updated product tags

### Orders

- `get-order`
  - Input: `order_id` or `name`
  - Output: order summary, statuses, totals, customer summary, line items
- `search-orders`
  - Input: `query`, `limit`
  - Output: matched order list
- `add-order-tags`
  - Input: `order_id`, `tags`
  - Output: updated order tags
- `remove-order-tags`
  - Input: `order_id`, `tags`
  - Output: updated order tags

### Customers

- `get-customer`
  - Input: `customer_id` or `email`
  - Output: customer summary, contact information, tags
- `search-customers`
  - Input: `query`, `limit`
  - Output: matched customer list
- `add-customer-tags`
  - Input: `customer_id`, `tags`
  - Output: updated customer tags
- `remove-customer-tags`
  - Input: `customer_id`, `tags`
  - Output: updated customer tags

## Required Shopify scopes

If you want to use all tools in this plugin, enable these Admin API scopes:

- `read_products`
- `write_products`
- `read_orders`
- `write_orders`
- `read_customers`
- `write_customers`

Scope examples by feature:

- Product read/search/tag update: `read_products`, `write_products`
- Order read/search/tag update: `read_orders`, `write_orders`
- Customer read/search/tag update: `read_customers`, `write_customers`

## Protected customer data

- Product-related tools usually do not require additional protected customer data settings.
- Order-related and customer-related tools are related to protected customer data.
- Especially when using the Admin API access token method, handling customer identifiers such as `email` or `phone` may require additional settings or review.
- Available fields and settings can vary depending on Shopify plan and app type.
- Check Shopify protected customer data settings and app permissions for details. This plugin does not guarantee the availability of features related to protected customer data in your Shopify configuration.

## Authentication methods

### Option 1: Admin API access token

Use this method if you want to configure the plugin with:

- `shop_domain`
- `api_version`
- `auth_method=access_token`
- `admin_api_access_token`

General steps:

1. In your Shopify admin, open `Settings` -> `Apps and sales channels`.
2. Open app development and create an app for your store.
3. Configure Admin API scopes for the resources you want to use.
4. Install the app to the store.
5. Copy the Admin API access token.

Note:

- Depending on your store plan and app type, some customer-related fields may need additional Shopify settings.

### Option 2: Client ID / Client secret

Use this method if you want to configure the plugin with:

- `shop_domain`
- `api_version`
- `auth_method=client_credentials`
- `client_id`
- `client_secret`

General steps:

1. Create a custom app from the Shopify developer dashboard.
2. Configure the required API scopes.
3. Release the app version.
4. Install the app to your store.
5. Copy the Client ID and Client secret.

Note:

- Depending on your Shopify configuration, customer-related access may still require additional setup.

## Dify plugin settings

### Common settings

- `shop_domain`: for example `your-store.myshopify.com`
- `api_version`: for example `2025-10`

### If using Admin API access token

- `auth_method`: `access_token`
- `admin_api_access_token`: your Shopify Admin API access token

### If using Client credentials

- `auth_method`: `client_credentials`
- `client_id`: your Shopify Client ID
- `client_secret`: your Shopify Client secret

## Notes

- `shop_domain` must be your Shopify domain such as `your-store.myshopify.com`
- Do not include `https://`
- Resource IDs used by this plugin are Shopify numeric IDs such as `1234567890123`

## Author

ryuichi
