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

以下の手順は、Shopify 側の画面や名称は変更されることがあるため、最新の表示と異なる場合があります。  
特に protected customer data に関する設定や利用可否は、Shopify の仕様、ストアプラン、アプリ種別に依存します。

### Admin API access token を使う方法

この手順で取得した `shop_domain`, `api_version`, `auth_method=access_token`, `admin_api_access_token` を Dify プラグイン設定に入力します。

1. Shopify ストア管理画面で、`設定` -> `アプリ` を開き、`アプリを開発する` を押します。
2. ストア用のアプリを作成し、適当なアプリ名を入力して作成します。
3. アプリ作成後、`概要` タブで `Admin API スコープを設定する` を押します。
4. 次のスコープを選択して保存します。  
   `write_orders`, `read_orders`, `write_products`, `read_products`, `write_customers`, `read_customers`
5. 必要に応じて、`設定` タブで protected customer data に関する追加設定を確認します。
6. `アプリをインストール` を押します。
7. `API 資格情報` タブで `Admin API access token` を表示し、控えておきます。

選択するスコープの例:

- 商品の取得・検索・タグ更新: `read_products`, `write_products`
- 注文の取得・検索・タグ更新: `read_orders`, `write_orders`
- 顧客の取得・検索・タグ更新: `read_customers`, `write_customers`

### Client ID / Client secret を使う方法

この手順で取得した `shop_domain`, `api_version`, `auth_method=client_credentials`, `client_id`, `client_secret` を Dify プラグイン設定に入力します。

1. Shopify ストア管理画面で、`設定` -> `アプリ` を開き、`アプリを開発する` を押します。
2. `Dev Dashboard でアプリを開発` を押します。
3. Dev Dashboard で `アプリを作成` を押します。
4. 適当なアプリ名を入力して作成します。
5. アプリ作成後、バージョン画面で `アクセス` の `スコープを選択` を押します。
6. 次のスコープを選択します。  
   `write_orders`, `read_orders`, `write_products`, `read_products`, `write_customers`, `read_customers`
7. スコープ設定後、`リリース` を押してアプリバージョンを公開します。
8. Dev Dashboard 右上の組織メニューから `Partner Dashboard` を開きます。
9. `アプリ配布` から作成したアプリを選択します。
10. `API アクセス要求` を開き、protected customer data に関する `アクセス権をリクエスト` を押します。
11. 必要事項を入力して保存します。
12. `配布` で `カスタム配布` を選び、対象ストアドメインを入力してインストールリンクを生成します。
13. 生成したリンクを開き、対象ストアでアプリをインストールします。
14. Dev Dashboard の `設定` で `Client ID` と `Client secret` を確認し、控えておきます。

補足:

- アクセススコープを変更する場合は、Dev Dashboard でアプリの新しいバージョンを作成し、そのバージョンでスコープを変更してからリリースしてください。

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

## Shopify の検索クエリについて

`search-products`, `search-orders`, `search-customers` の `query` には、Shopify Admin GraphQL の検索構文を指定します。

- `search-products`: https://shopify.dev/docs/api/admin-graphql/latest/queries/products
- `search-orders`: https://shopify.dev/docs/api/admin-graphql/latest/queries/orders
- `search-customers`: https://shopify.dev/docs/api/admin-graphql/latest/queries/customers

## 注意

- `shop_domain` は `your-store.myshopify.com` の形式で入力してください。
- `https://` は含めないでください。
- このプラグインで使う `product_id`, `order_id`, `customer_id` は Shopify の数値 ID です。例: `1234567890123`

## Author

ryuichi
