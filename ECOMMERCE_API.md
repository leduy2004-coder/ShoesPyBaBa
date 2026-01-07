# E-commerce API Documentation - Stripe Only

## Cấu hình Stripe

Thêm các biến môi trường sau vào file `.env`:

```env
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
```

**Lưu ý:** Sử dụng test keys từ Stripe Dashboard để test. Không commit keys vào git!

---

## Luồng thanh toán

### ✅ Luồng 1: Mua trực tiếp từ sản phẩm (Buy Now)

```
1. User chọn sản phẩm và click "Buy Now"
2. Frontend tạo payment intent: POST /api/payments/create-intent
3. Frontend hiển thị Stripe payment form
4. User hoàn tất thanh toán trên Stripe
5. Frontend confirm: POST /api/payments/confirm-from-products
6. Đơn hàng được tạo với payment_status = "completed"
```

### ✅ Luồng 2: Mua từ giỏ hàng (Cart)

```
1. User thêm sản phẩm vào giỏ: POST /api/cart/items
2. User xem giỏ hàng: GET /api/cart
3. User proceed to checkout
4. Frontend tạo payment intent: POST /api/payments/create-intent
5. Frontend hiển thị Stripe payment form
6. User hoàn tất thanh toán trên Stripe
7. Frontend confirm: POST /api/payments/confirm-from-cart
8. Đơn hàng được tạo, giỏ hàng được xóa
```

---

## API Endpoints

### 1. Giỏ hàng (Cart)

#### 1.1. Lấy giỏ hàng hiện tại
```http
GET /api/cart
Authorization: Bearer {token}
```

**Response:**
```json
{
  "id": 1,
  "user_id": 123,
  "items": [
    {
      "id": 1,
      "product_id": 456,
      "product_name": "Nike Air Max",
      "product_image": "https://...",
      "quantity": 2,
      "size": 42,
      "color": "black",
      "current_price": 150.00,
      "subtotal": 300.00
    }
  ],
  "total_items": 1,
  "total_amount": 300.00
}
```

#### 1.2. Thêm sản phẩm vào giỏ
```http
POST /api/cart/items
Authorization: Bearer {token}
Content-Type: application/json

{
  "product_id": 456,
  "quantity": 2,
  "size": 42,
  "color": "black"
}
```

#### 1.3. Cập nhật số lượng
```http
PUT /api/cart/items/{item_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "quantity": 3
}
```

#### 1.4. Xóa sản phẩm
```http
DELETE /api/cart/items/{item_id}
Authorization: Bearer {token}
```

#### 1.5. Xóa toàn bộ giỏ
```http
DELETE /api/cart
Authorization: Bearer {token}
```

---

### 2. Thanh toán (Payments)

#### 2.1. Tạo Payment Intent
```http
POST /api/payments/create-intent
Authorization: Bearer {token}
Content-Type: application/json

{
  "amount": 300.00,
  "currency": "usd",
  "description": "Order payment"
}
```

**Response:**
```json
{
  "payment_intent_id": "pi_xxx",
  "client_secret": "pi_xxx_secret_yyy",
  "amount": 300.00,
  "currency": "usd",
  "status": "requires_payment_method"
}
```

#### 2.2. Confirm Payment từ Giỏ Hàng
```http
POST /api/payments/confirm-from-cart
Authorization: Bearer {token}
Content-Type: application/json

{
  "payment_intent_id": "pi_xxx",
  "delivery_address": {
    "street_address": "123 Nguyen Hue",
    "ward": "Ben Nghe",
    "province_city": "Ho Chi Minh",
    "recipient_name": "Nguyen Van A",
    "recipient_phone": "0901234567"
  }
}
```

**Response:** Trả về đơn hàng đã tạo

**Lưu ý:**
- Verify payment với Stripe
- Tạo đơn hàng từ giỏ hàng
- Xóa giỏ hàng sau khi tạo đơn thành công

#### 2.3. Confirm Payment từ Sản Phẩm (Buy Now)
```http
POST /api/payments/confirm-from-products
Authorization: Bearer {token}
Content-Type: application/json

{
  "payment_intent_id": "pi_xxx",
  "items": [
    {
      "product_id": 456,
      "quantity": 1,
      "size": 42,
      "color": "black"
    }
  ],
  "delivery_address": {
    "street_address": "123 Nguyen Hue",
    "ward": "Ben Nghe",
    "province_city": "Ho Chi Minh",
    "recipient_name": "Nguyen Van A",
    "recipient_phone": "0901234567"
  }
}
```

**Response:** Trả về đơn hàng đã tạo

**Lưu ý:**
- Verify payment với Stripe
- Tạo đơn hàng trực tiếp từ danh sách sản phẩm
- Không liên quan đến giỏ hàng

#### 2.4. Kiểm tra trạng thái thanh toán
```http
GET /api/payments/status/{payment_intent_id}
Authorization: Bearer {token}
```

---

### 3. Đơn hàng (Orders)

#### 3.1. Lấy lịch sử đơn hàng
```http
GET /api/orders?page=1&limit=10
Authorization: Bearer {token}
```

**Response:**
```json
{
  "orders": [...],
  "total": 25,
  "page": 1,
  "limit": 10,
  "total_pages": 3
}
```

#### 3.2. Xem chi tiết đơn hàng
```http
GET /api/orders/{order_id}
Authorization: Bearer {token}
```

#### 3.3. Tìm kiếm đơn hàng
```http
GET /api/orders/search/all?status=completed&payment_status=completed&page=1&limit=10
Authorization: Bearer {token}
```

**Query Parameters:**
- `status`: pending, processing, shipped, delivered, cancelled
- `payment_status`: pending, completed, failed, refunded
- `start_date`: ISO datetime
- `end_date`: ISO datetime
- `page`: số trang (default: 1)
- `limit`: số items per page (default: 10, max: 100)

---

### 4. Admin - Quản lý đơn hàng

**Lưu ý:** Tất cả endpoints admin yêu cầu role = "admin"

#### 4.1. Xem đơn hàng theo user
```http
GET /api/orders/admin/by-user/{user_id}?page=1&limit=10
Authorization: Bearer {admin_token}
```

#### 4.2. Xem đơn hàng theo sản phẩm
```http
GET /api/orders/admin/by-product/{product_id}?page=1&limit=10
Authorization: Bearer {admin_token}
```

#### 4.3. Cập nhật trạng thái đơn hàng
```http
PUT /api/orders/admin/{order_id}/status
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "processing"
}
```

---

## Ví dụ sử dụng

### Ví dụ 1: Mua trực tiếp (Buy Now)

```bash
# 1. Tạo payment intent
curl -X POST http://localhost:8000/api/payments/create-intent \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 150.00,
    "currency": "usd"
  }'

# Response: {"payment_intent_id": "pi_xxx", "client_secret": "pi_xxx_secret_yyy", ...}

# 2. User thanh toán trên frontend với Stripe.js

# 3. Confirm payment và tạo đơn
curl -X POST http://localhost:8000/api/payments/confirm-from-products \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_xxx",
    "items": [
      {"product_id": 1, "quantity": 1, "size": 42, "color": "black"}
    ],
    "delivery_address": {
      "street_address": "123 Test St",
      "province_city": "Test City",
      "recipient_name": "Test User",
      "recipient_phone": "0123456789"
    }
  }'
```

### Ví dụ 2: Mua từ giỏ hàng

```bash
# 1. Thêm vào giỏ
curl -X POST http://localhost:8000/api/cart/items \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "quantity": 2, "size": 42}'

# 2. Xem giỏ
curl -X GET http://localhost:8000/api/cart \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. Tạo payment intent
curl -X POST http://localhost:8000/api/payments/create-intent \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": 300.00, "currency": "usd"}'

# 4. User thanh toán trên frontend với Stripe.js

# 5. Confirm payment và tạo đơn từ giỏ
curl -X POST http://localhost:8000/api/payments/confirm-from-cart \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "payment_intent_id": "pi_xxx",
    "delivery_address": {
      "street_address": "123 Test St",
      "province_city": "Test City",
      "recipient_name": "Test User",
      "recipient_phone": "0123456789"
    }
  }'
```

---

## Lưu ý quan trọng

### Về giá sản phẩm
- **Giỏ hàng:** Luôn hiển thị giá hiện tại (có thể thay đổi)
- **Đơn hàng:** Lưu giá tại thời điểm đặt hàng (`price_at_purchase`)

### Về thanh toán
- **Chỉ hỗ trợ Stripe** - Không có COD
- Payment được verify trực tiếp khi confirm
- Sử dụng test cards của Stripe:
  - Success: `4242 4242 4242 4242`
  - Decline: `4000 0000 0000 0002`

### Về bảo mật
- Tất cả endpoints yêu cầu authentication
- Admin endpoints kiểm tra role = "admin"
- User chỉ xem được đơn hàng của mình

### Về luồng
- **Buy Now:** Không lưu vào cart, tạo đơn trực tiếp
- **Cart:** Lưu vào cart, có thể chỉnh sửa trước khi checkout
- Cả hai đều phải qua Stripe payment
