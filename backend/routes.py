import json
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import Query
from database import get_db_ctx
from auth import hash_password, verify_password, create_access_token, get_current_user, get_admin_user
from models import (
    User, UserCreate, UserLogin, UserUpdate, Token,
    Category, CategoryCreate,
    Product, ProductCreate, ProductUpdate,
    CartItem, CartItemCreate,
    Order, OrderCreate, OrderItem,
    PaginatedResponse,
)
from typing import Optional

router = APIRouter(prefix="/api")


# ─── Auth ─────────────────────────────────────────────────────────────────────

@router.post("/auth/register", response_model=Token)
def register(data: UserCreate):
    with get_db_ctx() as conn:
        exists = conn.execute("SELECT id FROM users WHERE email = ?", (data.email,)).fetchone()
        if exists:
            raise HTTPException(status_code=400, detail="Email já cadastrado")
        hashed = hash_password(data.password)
        cur = conn.execute(
            "INSERT INTO users (email, name, password_hash, role) VALUES (?, ?, ?, 'client')",
            (data.email, data.name, hashed),
        )
        token = create_access_token({"sub": data.email, "role": "client", "user_id": cur.lastrowid})
        return Token(access_token=token)


@router.post("/auth/login", response_model=Token)
def login(data: UserLogin):
    with get_db_ctx() as conn:
        row = conn.execute(
            "SELECT id, email, name, password_hash, role FROM users WHERE email = ?", (data.email,)
        ).fetchone()
        if not row or not verify_password(data.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="Email ou senha incorretos")
        token = create_access_token({"sub": data.email, "role": row["role"], "user_id": row["id"]})
        return Token(access_token=token)


@router.get("/auth/me", response_model=User)
def me(current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        row = conn.execute(
            "SELECT id, email, name, role, created_at FROM users WHERE email = ?",
            (current_user["sub"],),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return dict(row)


# ─── Categories ───────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[Category])
def list_categories():
    with get_db_ctx() as conn:
        rows = conn.execute("SELECT * FROM categories ORDER BY name").fetchall()
        return [dict(r) for r in rows]


@router.post("/categories", response_model=Category)
def create_category(data: CategoryCreate, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        cur = conn.execute(
            "INSERT INTO categories (name, slug, description, image_url) VALUES (?, ?, ?, ?)",
            (data.name, data.slug, data.description, data.image_url),
        )
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (cur.lastrowid,)).fetchone()
        return dict(row)


@router.put("/categories/{cat_id}", response_model=Category)
def update_category(cat_id: int, data: CategoryCreate, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        conn.execute(
            "UPDATE categories SET name=?, slug=?, description=?, image_url=? WHERE id=?",
            (data.name, data.slug, data.description, data.image_url, cat_id),
        )
        row = conn.execute("SELECT * FROM categories WHERE id = ?", (cat_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Categoria não encontrada")
        return dict(row)


@router.delete("/categories/{cat_id}")
def delete_category(cat_id: int, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        cur = conn.execute("UPDATE products SET category_id=null WHERE category_id=?", (cat_id,))
        conn.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        return {"ok": True}


# ─── Products ─────────────────────────────────────────────────────────────────

def _product_from_row(row) -> dict:
    d = dict(row)
    d["images"] = json.loads(d.get("images", "[]"))
    d["sizes"] = json.loads(d.get("sizes", "[]"))
    return d


@router.get("/products", response_model=PaginatedResponse)
def list_products(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    team: Optional[str] = None,
    league: Optional[str] = None,
    featured: Optional[bool] = None,
    search: Optional[str] = None,
):
    with get_db_ctx() as conn:
        where = ["p.active = 1"]
        params = []
        if category:
            where.append("c.slug = ?")
            params.append(category)
        if team:
            where.append("p.team LIKE ?")
            params.append(f"%{team}%")
        if league:
            where.append("p.league = ?")
            params.append(league)
        if featured is not None:
            where.append("p.featured = ?")
            params.append(1 if featured else 0)
        if search:
            where.append("(p.name LIKE ? OR p.team LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])

        where_sql = " AND ".join(where)
        total = conn.execute(
            f"SELECT COUNT(*) FROM products p LEFT JOIN categories c ON p.category_id=c.id WHERE {where_sql}",
            params,
        ).fetchone()[0]

        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p LEFT JOIN categories c ON p.category_id=c.id
            WHERE {where_sql}
            ORDER BY p.featured DESC, p.created_at DESC
            LIMIT ? OFFSET ?
            """,
            params + [per_page, offset],
        ).fetchall()

        return PaginatedResponse(
            items=[_product_from_row(r) for r in rows],
            total=total,
            page=page,
            per_page=per_page,
            pages=(total + per_page - 1) // per_page,
        )


@router.get("/products/featured")
def featured_products(limit: int = Query(8, ge=1, le=40)):
    with get_db_ctx() as conn:
        rows = conn.execute(
            "SELECT * FROM products WHERE active=1 AND featured=1 ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [_product_from_row(r) for r in rows]


@router.get("/products/{product_id}")
def get_product(product_id: int):
    with get_db_ctx() as conn:
        row = conn.execute(
            "SELECT p.*, c.name as category_name, c.slug as category_slug "
            "FROM products p LEFT JOIN categories c ON p.category_id=c.id "
            "WHERE p.id = ?",
            (product_id,),
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Produto não encontrado")
        return _product_from_row(row)


@router.post("/products", response_model=Product)
def create_product(data: ProductCreate, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        cur = conn.execute(
            """INSERT INTO products
            (name, slug, description, price, compare_price, image_url, images, sizes,
             category_id, team, league, year, type, stock, featured, active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data.name, data.slug, data.description, data.price, data.compare_price,
                data.image_url, json.dumps(data.images), json.dumps(data.sizes),
                data.category_id, data.team, data.league, data.year, data.type,
                data.stock, 1 if data.featured else 0, 1 if data.active else 0,
            ),
        )
        row = conn.execute("SELECT * FROM products WHERE id = ?", (cur.lastrowid,)).fetchone()
        return _product_from_row(row)


@router.put("/products/{product_id}", response_model=Product)
def update_product(product_id: int, data: ProductUpdate, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        row = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Produto não encontrado")

        fields = {k: v for k, v in data.model_dump().items() if v is not None}
        if "images" in fields:
            fields["images"] = json.dumps(fields["images"])
        if "sizes" in fields:
            fields["sizes"] = json.dumps(fields["sizes"])
        fields["updated_at"] = "CURRENT_TIMESTAMP"

        for key in ["featured", "active"]:
            if key in fields:
                fields[key] = 1 if fields[key] else 0

        set_sql = ", ".join(f"{k}=?" for k in fields)
        conn.execute(f"UPDATE products SET {set_sql} WHERE id=?", list(fields.values()) + [product_id])
        updated = conn.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
        return _product_from_row(updated)


@router.delete("/products/{product_id}")
def delete_product(product_id: int, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        conn.execute("DELETE FROM products WHERE id = ?", (product_id,))
        return {"ok": True}


# ─── Cart ─────────────────────────────────────────────────────────────────────

@router.get("/cart")
def get_cart(current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        rows = conn.execute(
            """SELECT ci.*, p.name, p.price, p.image_url, p.stock, p.sizes
            FROM cart_items ci JOIN products p ON ci.product_id=p.id
            WHERE ci.user_id = ?""",
            (current_user["user_id"],),
        ).fetchall()
        items = []
        total = 0
        for r in rows:
            item = dict(r)
            item["sizes"] = json.loads(item["sizes"])
            item["subtotal"] = item["price"] * item["quantity"]
            total += item["subtotal"]
            items.append(item)
        return {"items": items, "total": round(total, 2)}


@router.post("/cart")
def add_to_cart(data: CartItemCreate, current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        conn.execute(
            """INSERT INTO cart_items (user_id, product_id, size, quantity)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, product_id, size) DO UPDATE SET quantity = quantity + excluded.quantity""",
            (current_user["user_id"], data.product_id, data.size, data.quantity),
        )
        return {"ok": True}


@router.put("/cart/{item_id}")
def update_cart(item_id: int, data: CartItemCreate, current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        cur = conn.execute(
            "UPDATE cart_items SET quantity=? WHERE id=? AND user_id=?",
            (data.quantity, item_id, current_user["user_id"]),
        )
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Item não encontrado")
        return {"ok": True}


@router.delete("/cart/{item_id}")
def remove_from_cart(item_id: int, current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        conn.execute("DELETE FROM cart_items WHERE id=? AND user_id=?", (item_id, current_user["user_id"]))
        return {"ok": True}


@router.delete("/cart")
def clear_cart(current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        conn.execute("DELETE FROM cart_items WHERE user_id = ?", (current_user["user_id"],))
        return {"ok": True}


# ─── Orders ───────────────────────────────────────────────────────────────────

@router.post("/orders", response_model=Order)
def create_order(data: OrderCreate, current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        # calculate total from cart
        cart_rows = conn.execute(
            """SELECT ci.*, p.price, p.stock FROM cart_items ci
            JOIN products p ON ci.product_id=p.id WHERE ci.user_id=?""",
            (current_user["user_id"],),
        ).fetchall()
        if not cart_rows:
            raise HTTPException(status_code=400, detail="Carrinho vazio")

        total = 0
        order_items = []
        for r in cart_rows:
            unit_price = r["price"]
            total += unit_price * r["quantity"]
            order_items.append((r["product_id"], r["size"], r["quantity"], unit_price))

        cur = conn.execute(
            """INSERT INTO orders
            (user_id, total, shipping_address, shipping_city, shipping_state, shipping_zip,
             customer_name, customer_email, customer_phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                current_user["user_id"], round(total, 2),
                data.shipping_address, data.shipping_city, data.shipping_state, data.shipping_zip,
                data.customer_name, data.customer_email, data.customer_phone,
            ),
        )
        order_id = cur.lastrowid
        for (pid, size, qty, price) in order_items:
            conn.execute(
                "INSERT INTO order_items (order_id, product_id, size, quantity, unit_price) VALUES (?, ?, ?, ?, ?)",
                (order_id, pid, size, qty, price),
            )
        # clear cart
        conn.execute("DELETE FROM cart_items WHERE user_id = ?", (current_user["user_id"],))

        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        items = conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
        result = dict(order)
        result["items"] = [dict(i) for i in items]
        return result


@router.get("/orders/my")
def my_orders(current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        rows = conn.execute(
            "SELECT * FROM orders WHERE user_id = ? ORDER BY created_at DESC",
            (current_user["user_id"],),
        ).fetchall()
        result = []
        for r in rows:
            order = dict(r)
            order["items"] = [
                dict(i) for i in conn.execute("SELECT * FROM order_items WHERE order_id = ?", (r["id"],)).fetchall()
            ]
            result.append(order)
        return result


@router.get("/orders/{order_id}")
def get_order(order_id: int, current_user: dict = Depends(get_current_user)):
    with get_db_ctx() as conn:
        row = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        # clients can only see their own orders
        if current_user.get("role") != "admin" and row["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Acesso negado")
        order = dict(row)
        order["items"] = [
            dict(i) for i in conn.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,)).fetchall()
        ]
        return order


# ─── Admin Orders ─────────────────────────────────────────────────────────────

@router.get("/admin/orders")
def admin_list_orders(
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    _=Depends(get_admin_user),
):
    with get_db_ctx() as conn:
        where = []
        params = []
        if status:
            where.append("o.status = ?")
            params.append(status)
        where_sql = " AND ".join(where) if where else "1=1"

        total = conn.execute(f"SELECT COUNT(*) FROM orders o WHERE {where_sql}", params).fetchone()[0]
        offset = (page - 1) * per_page
        rows = conn.execute(
            f"""SELECT o.*, u.name as user_name, u.email as user_email
            FROM orders o LEFT JOIN users u ON o.user_id=u.id
            WHERE {where_sql} ORDER BY o.created_at DESC LIMIT ? OFFSET ?""",
            params + [per_page, offset],
        ).fetchall()
        result = []
        for r in rows:
            order = dict(r)
            order["items"] = [
                dict(i) for i in conn.execute("SELECT * FROM order_items WHERE order_id = ?", (r["id"],)).fetchall()
            ]
            result.append(order)
        return {"items": result, "total": total, "page": page, "per_page": per_page,
                "pages": (total + per_page - 1) // per_page}


@router.patch("/admin/orders/{order_id}/status")
def admin_update_status(order_id: int, status: str, _=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        conn.execute("UPDATE orders SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?", (status, order_id))
        return {"ok": True}


# ─── Stats ────────────────────────────────────────────────────────────────────

@router.get("/admin/stats")
def admin_stats(_=Depends(get_admin_user)):
    with get_db_ctx() as conn:
        return {
            "total_products": conn.execute("SELECT COUNT(*) FROM products").fetchone()[0],
            "total_orders": conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
            "total_clients": conn.execute("SELECT COUNT(*) FROM users WHERE role='client'").fetchone()[0],
            "revenue": conn.execute("SELECT COALESCE(SUM(total),0) FROM orders WHERE status IN ('paid','shipped','delivered')").fetchone()[0],
            "pending_orders": conn.execute("SELECT COUNT(*) FROM orders WHERE status='pending'").fetchone()[0],
        }


# ─── Pagar.me PIX ─────────────────────────────────────────────────────────────

@router.post("/orders/{order_id}/pay")
def initiate_pix_payment(order_id: int, current_user: dict = Depends(get_current_user)):
    """Gera QR Code PIX via Pagar.me"""
    import requests
    from config import settings

    if not settings.PAGARME_API_KEY:
        raise HTTPException(status_code=503, detail="Pagamento PIX não configurado")

    with get_db_ctx() as conn:
        order = conn.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Pedido não encontrado")
        if current_user.get("role") != "admin" and order["user_id"] != current_user["user_id"]:
            raise HTTPException(status_code=403, detail="Acesso negado")

    # Pagar.me payment
    headers = {"Authorization": f"Token {settings.PAGARME_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "mode": "gateway",
        "amount": int(float(order["total"]) * 100),
        "payment_method": "pix",
        "order_id": str(order_id),
        "pix": {"expires_in": 3600},
    }

    try:
        resp = requests.post("https://api.pagar.me/core/v5/orders", json=payload, headers=headers, timeout=15)
        data = resp.json()
        qr_code = data.get("charges", [{}])[0].get("last_transaction", {}).get("qr_code", "")
        qr_code_url = data.get("charges", [{}])[0].get("last_transaction", {}).get("qr_code_url", "")
        payment_id = data.get("charges", [{}])[0].get("id", "")

        with get_db_ctx() as conn:
            conn.execute(
                "UPDATE orders SET pagarme_payment_id=?, pagarme_qr_code=?, pagarme_qr_code_url=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                (payment_id, qr_code, qr_code_url, order_id),
            )
        return {"qr_code": qr_code, "qr_code_url": qr_code_url, "amount": float(order["total"])}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar PIX: {str(e)}")


@router.post("/webhooks/pagarme")
def pagarme_webhook(payload: dict):
    """Webhook do Pagar.me para confirmar pagamento"""
    from config import settings
    if payload.get("current_status") == "paid":
        order_id = payload.get("order_id")
        if order_id:
            with get_db_ctx() as conn:
                conn.execute(
                    "UPDATE orders SET status='paid', updated_at=CURRENT_TIMESTAMP WHERE id=?",
                    (int(order_id),),
                )
    return {"ok": True}


# ─── Serve uploaded images ─────────────────────────────────────────────────────

@router.get("/uploads/{filename}")
def serve_upload(filename: str):
    from fastapi.responses import FileResponse
    import os
    path = f"/opt/craque-do-jogo/uploads/{filename}"
    if os.path.exists(path):
        return FileResponse(path)
    raise HTTPException(status_code=404, detail="Arquivo não encontrado")