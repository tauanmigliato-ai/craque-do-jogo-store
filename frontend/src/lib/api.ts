const API_BASE = (() => {
  if (import.meta.env.DEV) return 'http://localhost:5051'
  // Em produção no mesmo servidor, usa relative path
  return window.location.origin
})()

let token: string | null = localStorage.getItem('token')

export function setToken(t: string) {
  token = t
  if (t) localStorage.setItem('token', t)
  else localStorage.removeItem('token')
}

export function getToken() {
  return token
}

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string> || {}),
  }
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers,
  })

  if (res.status === 401) {
    setToken('')
    if (window.location.pathname !== '/login') { window.location.href = '/login' }
    throw new Error('Unauthorized')
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Erro desconhecido' }))
    throw new Error(err.detail || 'Erro na requisição')
  }

  return res.json()
}

export const api = {
  // Auth
  register: (data: { email: string; name: string; password: string }) =>
    request<{ access_token: string }>('/api/auth/register', { method: 'POST', body: JSON.stringify(data) }),
  login: (data: { email: string; password: string }) =>
    request<{ access_token: string }>('/api/auth/login', { method: 'POST', body: JSON.stringify(data) }),
  me: () => request<User>('/api/auth/me'),

  // Categories
  getCategories: () => request<Category[]>('/api/categories'),
  createCategory: (data: CategoryInput) =>
    request<Category>('/api/categories', { method: 'POST', body: JSON.stringify(data) }),

  // Products
  getProducts: (params?: Record<string, string | number | boolean>) => {
    const qs = params ? '?' + new URLSearchParams(params as any).toString() : ''
    return request<PaginatedProducts>(`/api/products${qs}`)
  },
  getFeatured: (limit = 8) => request<Product[]>(`/api/products/featured?limit=${limit}`),
  getProduct: (id: number) => request<Product>(`/api/products/${id}`),
  createProduct: (data: ProductInput) =>
    request<Product>('/api/products', { method: 'POST', body: JSON.stringify(data) }),
  updateProduct: (id: number, data: Partial<ProductInput>) =>
    request<Product>(`/api/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
  deleteProduct: (id: number) =>
    request<{ ok: boolean }>(`/api/products/${id}`, { method: 'DELETE' }),

  // Cart
  getCart: () => request<CartResponse>('/api/cart'),
  addToCart: (data: { product_id: number; size: string; quantity: number }) =>
    request('/api/cart', { method: 'POST', body: JSON.stringify(data) }),
  updateCart: (id: number, data: { product_id: number; size: string; quantity: number }) =>
    request('/api/cart/' + id, { method: 'PUT', body: JSON.stringify(data) }),
  removeFromCart: (id: number) =>
    request('/api/cart/' + id, { method: 'DELETE' }),
  clearCart: () => request('/api/cart', { method: 'DELETE' }),

  // Orders
  createOrder: (data: OrderInput) =>
    request<Order>('/api/orders', { method: 'POST', body: JSON.stringify(data) }),
  getMyOrders: () => request<Order[]>('/api/orders/my'),
  getOrder: (id: number) => request<Order>(`/api/orders/${id}`),
  payOrder: (id: number) => request<{ qr_code: string; qr_code_url: string; amount: number }>(`/api/orders/${id}/pay`, { method: 'POST' }),

  // Admin
  getAdminOrders: (params?: Record<string, string | number>) => {
    const qs = params ? '?' + new URLSearchParams(params as any).toString() : ''
    return request<PaginatedOrders>(`/api/admin/orders${qs}`)
  },
  updateOrderStatus: (id: number, status: string) =>
    request('/api/admin/orders/' + id + '/status', { method: 'PATCH', body: JSON.stringify({ status }) }),
  getStats: () => request<Stats>('/api/admin/stats'),
  deleteCategory: (id: number) => request('/api/categories/' + id, { method: 'DELETE' }),
  updateCategory: (id: number, data: CategoryInput) =>
    request<Category>('/api/categories/' + id, { method: 'PUT', body: JSON.stringify(data) }),
}

// Types
export interface User { id: number; email: string; name: string; role: 'admin' | 'client'; created_at: string }
export interface Category { id: number; name: string; slug: string; description?: string; image_url?: string; created_at: string }
export type CategoryInput = Omit<Category, 'id' | 'created_at'>
export interface Product {
  id: number; name: string; slug: string; description?: string; price: number
  compare_price?: number; image_url?: string; images: string[]; sizes: string[]
  category_id?: number; category_name?: string; team?: string; league?: string
  year?: string; type?: string; stock: number; featured: boolean; active: boolean
  created_at: string; updated_at: string
}
export type ProductInput = Omit<Product, 'id' | 'created_at' | 'updated_at' | 'category_name'>
export interface CartItem { id: number; product_id: number; name: string; price: number; image_url?: string; size: string; quantity: number; stock: number; sizes: string[]; subtotal: number }
export interface CartResponse { items: CartItem[]; total: number }
export type OrderInput = { items: any[]; shipping_address: string; shipping_city: string; shipping_state: string; shipping_zip: string; customer_name: string; customer_email: string; customer_phone: string }
export interface OrderItem { id: number; product_id: number; size: string; quantity: number; unit_price: number }
export interface Order { id: number; user_id?: number; status: string; total: number; shipping_address: string; shipping_city: string; shipping_state: string; shipping_zip: string; customer_name: string; customer_email: string; customer_phone: string; items: OrderItem[]; created_at: string; updated_at: string }
export interface PaginatedProducts { items: Product[]; total: number; page: number; per_page: number; pages: number }
export interface PaginatedOrders { items: Order[]; total: number; page: number; per_page: number; pages: number }
export interface Stats { total_products: number; total_orders: number; total_clients: number; revenue: number; pending_orders: number }