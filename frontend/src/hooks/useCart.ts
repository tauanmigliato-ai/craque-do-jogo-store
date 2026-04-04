import { useState, useEffect, useCallback } from 'react'
import { api, getToken } from '@/lib/api'
import type { CartItem } from '@/lib/api'

export function useCart() {
  const [items, setItems] = useState<CartItem[]>([])
  const [loading, setLoading] = useState(false)

  const count = items.reduce((acc, i) => acc + i.quantity, 0)

  const refresh = useCallback(async () => {
    if (!getToken()) return // não carrega se não logado
    try {
      setLoading(true)
      const data = await api.getCart()
      setItems(data.items)
    } catch { /* ignore */ }
    finally { setLoading(false) }
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const addItem = async (product_id: number, size: string, quantity = 1) => {
    await api.addToCart({ product_id, size, quantity })
    await refresh()
  }

  const removeItem = async (id: number) => {
    await api.removeFromCart(id)
    await refresh()
  }

  const updateItem = async (id: number, product_id: number, size: string, quantity: number) => {
    await api.updateCart(id, { product_id, size, quantity })
    await refresh()
  }

  const clear = async () => {
    await api.clearCart()
    setItems([])
  }

  const total = items.reduce((acc, i) => acc + i.subtotal, 0)

  return { items, count, total, loading, refresh, addItem, removeItem, updateItem, clear }
}