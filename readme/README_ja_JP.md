# Shopify Tools for Dify

Shopify の商品、注文、顧客の取得・検索・タグ更新を行う Dify ツールプラグインです。

## 概要

このプラグインでは、次の操作ができます。

- 商品、注文、顧客の単体取得
- 商品、注文、顧客の検索
- 商品、注文、顧客へのタグ追加
- 商品、注文、顧客からのタグ削除

対応している認証方式:

- Admin API access token
- Client credentials (`client_id` / `client_secret`)

## ツール

### 商品

- `get-product`
  - 入力: `product_id` または `handle`
  - 出力: 商品名、説明、handle、画像 URL、在庫、バリアント
- `search-products`
  - 入力: `query`, `limit`
  - 出力: 商品一覧
- `add-product-tags`
  - 入力: `product_id`, `tags`
  - 出力: 更新後の商品タグ
- `remove-product-tags`
  - 入力: `product_id`, `tags`
  - 出力: 更新後の商品タグ

### 注文

- `get-order`
  - 入力: `order_id` または `name`
  - 出力: 注文サマリー、ステータス、金額、顧客サマリー、明細
- `search-orders`
  - 入力: `query`, `limit`
  - 出力: 注文一覧
- `add-order-tags`
  - 入力: `order_id`, `tags`
  - 出力: 更新後の注文タグ
- `remove-order-tags`
  - 入力: `order_id`, `tags`
  - 出力: 更新後の注文タグ

### 顧客

- `get-customer`
  - 入力: `customer_id` または `email`
  - 出力: 顧客サマリー、連絡先、タグ
- `search-customers`
  - 入力: `query`, `limit`
  - 出力: 顧客一覧
- `add-customer-tags`
  - 入力: `customer_id`, `tags`
  - 出力: 更新後の顧客タグ
- `remove-customer-tags`
  - 入力: `customer_id`, `tags`
  - 出力: 更新後の顧客タグ

## 必要な Admin API スコープ

このプラグインの全機能を使う場合は、次のスコープを選択してください。

- `read_products`
- `write_products`
- `read_orders`
- `write_orders`
- `read_customers`
- `write_customers`

機能ごとの目安:

- 商品の取得・検索・タグ更新: `read_products`, `write_products`
- 注文の取得・検索・タグ更新: `read_orders`, `write_orders`
- 顧客の取得・検索・タグ更新: `read_customers`, `write_customers`

## 保護された顧客データについて

- 商品関連のツールは、通常は protected customer data への追加設定は不要です。
- 注文関連・顧客関連のツールは、protected customer data に関係します。
- 特に Admin API access token を使う方法では、`email` や `phone` などの顧客識別情報を扱う場合、追加設定や審査が必要になることがあります。
- Shopify の仕様やストアプランにより、利用できる項目や設定画面が異なる場合があります。
- 詳しくは Shopify 側の protected customer data 設定とアプリ権限を確認してください。本プラグイン側では、保護された顧客データに関連する機能の利用可否は保証できません。

## 認証情報の作成

### Admin API access token を使う方法

この手順で取得した `shop_domain`, `api_version`, `auth_method=access_token`, `admin_api_access_token` を Dify プラグイン設定に入力します。

1. Shopify ストア管理画面で、`設定` -> `アプリと販売チャネル` を開きます。
2. `アプリを開発する` を押して、ストア用のアプリを作成します。
3. Admin API スコープを設定します。
4. 必要なスコープを保存したら、アプリをストアへインストールします。
5. Admin API access token を表示し、控えておきます。

選択するスコープの例:

- 商品の取得・検索・タグ更新: `read_products`, `write_products`
- 注文の取得・検索・タグ更新: `read_orders`, `write_orders`
- 顧客の取得・検索・タグ更新: `read_customers`, `write_customers`

補足:

- Shopify の画面や名称は変更されることがあります。
- 顧客情報や注文情報の一部は、Shopify 側の追加設定が必要になる場合があります。

### Client ID / Client secret を使う方法

この手順で取得した `shop_domain`, `api_version`, `auth_method=client_credentials`, `client_id`, `client_secret` を Dify プラグイン設定に入力します。

1. Shopify の Dev Dashboard でカスタムアプリを作成します。
2. 必要な API スコープを選択します。
3. アプリのバージョンをリリースします。
4. 作成したアプリをストアへインストールします。
5. Client ID と Client secret を確認し、控えておきます。

補足:

- Shopify の設定やストアの状態によっては、顧客情報へのアクセスに追加設定が必要です。

## Dify プラグイン設定に入力する値

### 共通

- `shop_domain`: 例 `your-store.myshopify.com`
- `api_version`: 例 `2025-10`

### Admin API access token を使う場合

- `auth_method`: `access_token`
- `admin_api_access_token`: Shopify で取得した Admin API access token

### Client credentials を使う場合

- `auth_method`: `client_credentials`
- `client_id`: Shopify で取得した Client ID
- `client_secret`: Shopify で取得した Client secret

## 注意

- `shop_domain` は `your-store.myshopify.com` の形式で入力してください。
- `https://` は含めないでください。
- このプラグインで使う `product_id`, `order_id`, `customer_id` は Shopify の数値 ID です。例: `1234567890123`

## Author

ryuichi
