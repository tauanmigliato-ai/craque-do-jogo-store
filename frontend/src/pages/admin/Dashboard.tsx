import { useState, useEffect } from 'react'
import { api, type Order, type Stats } from '@/lib/api'
import { Package, Users, ShoppingCart, DollarSign } from 'lucide-react'

const STATUS_COLORS: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  paid: 'bg-green-100 text-green-800',
  shipped: 'bg-blue-100 text-blue-800',
  delivered: 'bg-gray-100 text-gray-800',
  cancelled: 'bg-red-100 text-red-800',
}

const STATUS_LABELS: Record<string, string> = {
  pending: 'Aguardando PIX',
  paid: 'Pago',
  shipped: 'Enviado',
  delivered: 'Entregue',
  cancelled: 'Cancelado',
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<Stats | null>(null)
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    Promise.all([api.getStats(), api.getAdminOrders({ per_page: 20 })])
      .then(([s, o]) => { setStats(s); setOrders(o.items) })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleStatus = async (id: number, status: string) => {
    await api.updateOrderStatus(id, status)
    setOrders(prev => prev.map(o => o.id === id ? { ...o, status } : o))
  }

  if (loading) return <div className="p-6 text-gray-400">Carregando...</div>

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-extrabold">Painel Admin</h1>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Produtos', value: stats?.total_products ?? 0, icon: Package, color: 'text-blue-500' },
          { label: 'Pedidos', value: stats?.total_orders ?? 0, icon: ShoppingCart, color: 'text-[#E74C3C]' },
          { label: 'Clientes', value: stats?.total_clients ?? 0, icon: Users, color: 'text-green-500' },
          { label: 'Receita', value: `R$ ${(stats?.revenue ?? 0).toFixed(2).replace('.', ',')}`, icon: DollarSign, color: 'text-yellow-500' },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="bg-white rounded-xl shadow-sm p-5">
            <div className={`${color} mb-2`}><Icon className="w-6 h-6" /></div>
            <p className="text-2xl font-extrabold">{value}</p>
            <p className="text-sm text-gray-500">{label}</p>
          </div>
        ))}
      </div>

      {/* Pending Orders */}
      {stats && stats.pending_orders > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-4 flex items-center gap-3">
          <ShoppingCart className="w-6 h-6 text-yellow-600" />
          <span className="font-bold text-yellow-800">{stats.pending_orders} pedido(s) aguardando pagamento PIX</span>
        </div>
      )}

      {/* Orders Table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="p-4 border-b font-bold">Últimos Pedidos</div>
        {orders.length === 0 ? (
          <p className="text-center py-8 text-gray-400">Nenhum pedido ainda.</p>
        ) : (
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-4 font-bold">Pedido</th>
                <th className="text-left p-4 font-bold">Cliente</th>
                <th className="text-left p-4 font-bold">Total</th>
                <th className="text-left p-4 font-bold">Status</th>
                <th className="text-left p-4 font-bold">Ações</th>
              </tr>
            </thead>
            <tbody>
              {orders.map(o => (
                <tr key={o.id} className="border-b hover:bg-gray-50">
                  <td className="p-4">#{o.id} <span className="text-xs text-gray-400 block">{new Date(o.created_at).toLocaleDateString('pt-BR')}</span></td>
                  <td className="p-4">
                    <div className="font-semibold">{o.customer_name}</div>
                    <div className="text-xs text-gray-500">{o.customer_email}</div>
                  </td>
                  <td className="p-4 font-bold text-[#E74C3C]">R$ {o.total.toFixed(2).replace('.', ',')}</td>
                  <td className="p-4">
                    <span className={`text-xs font-bold px-2 py-1 rounded ${STATUS_COLORS[o.status] || ''}`}>{STATUS_LABELS[o.status] || o.status}</span>
                  </td>
                  <td className="p-4">
                    <select value={o.status}
                      onChange={e => handleStatus(o.id, e.target.value)}
                      className="border rounded px-2 py-1 text-xs">
                      {Object.keys(STATUS_LABELS).map(s => <option key={s} value={s}>{STATUS_LABELS[s]}</option>)}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  )
}