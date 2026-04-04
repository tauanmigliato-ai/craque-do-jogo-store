import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useCart } from '@/hooks/useCart'
import { api, getToken } from '@/lib/api'
import { CheckCircle, QrCode, Copy, Clock } from 'lucide-react'

const UFS = ['AC','AL','AP','AM','BA','CE','DF','ES','GO','MA','MT','MS','MG','PA','PB','PR','PE','PI','RJ','RN','RS','RO','RR','SC','SP','SE','TO']

export default function Checkout() {
  const { items, total } = useCart()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    customer_name: '', customer_email: '', customer_phone: '',
    shipping_address: '', shipping_city: '', shipping_state: '', shipping_zip: '',
  })
  const [step, setStep] = useState<'form' | 'pix' | 'success'>('form')
  const [pixData, setPixData] = useState<{ qr_code: string; qr_code_url: string; amount: number } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!getToken()) { navigate('/login'); return }
    setLoading(true)
    setError('')
    try {
      const order = await api.createOrder({ ...form, items: [] })
      const pix = await api.payOrder(order.id)
      setPixData(pix)
      setStep('pix')
    } catch (err: any) {
      setError(err.message || 'Erro ao criar pedido')
    } finally {
      setLoading(false)
    }
  }

  const handleCopy = () => {
    if (pixData?.qr_code) navigator.clipboard.writeText(pixData.qr_code)
  }

  if (items.length === 0 && step !== 'success') {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center">
        <p className="text-xl font-bold text-gray-400 mb-4">Carrinho vazio</p>
        <button onClick={() => navigate('/catalogo')} className="bg-[#E74C3C] text-white font-bold px-8 py-3 rounded-full">Ver Catálogo</button>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-extrabold mb-6">Finalizar Pedido</h1>

      {/* Progress */}
      <div className="flex items-center gap-4 mb-8 text-sm font-bold">
        <span className={step === 'form' ? 'text-[#E74C3C]' : 'text-green-600'}>1. Dados</span>
        <span className="text-gray-300">→</span>
        <span className={step === 'pix' ? 'text-[#E74C3C]' : step === 'success' ? 'text-green-600' : 'text-gray-400'}>2. Pagamento PIX</span>
        <span className="text-gray-300">→</span>
        <span className={step === 'success' ? 'text-green-600' : 'text-gray-400'}>3. Confirmado!</span>
      </div>

      {step === 'form' && (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Client Info */}
          <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="font-bold text-lg">Dados do Cliente</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <input name="customer_name" placeholder="Nome completo" value={form.customer_name} onChange={handleChange} required
                className="border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
              <input name="customer_email" placeholder="Email" type="email" value={form.customer_email} onChange={handleChange} required
                className="border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
              <input name="customer_phone" placeholder="WhatsApp" type="tel" value={form.customer_phone} onChange={handleChange} required
                className="border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C] md:col-span-2" />
            </div>
          </div>

          {/* Shipping */}
          <div className="bg-white rounded-xl shadow-sm p-6 space-y-4">
            <h2 className="font-bold text-lg">Endereço de Entrega</h2>
            <input name="shipping_address" placeholder="Endereço (rua, número, complemento)" value={form.shipping_address} onChange={handleChange} required
              className="w-full border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <input name="shipping_city" placeholder="Cidade" value={form.shipping_city} onChange={handleChange} required
                className="border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C] md:col-span-2" />
              <select name="shipping_state" value={form.shipping_state} onChange={handleChange} required
                className="border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]">
                <option value="">UF</option>
                {UFS.map(u => <option key={u} value={u}>{u}</option>)}
              </select>
              <input name="shipping_zip" placeholder="CEP" value={form.shipping_zip} onChange={handleChange} required
                className="border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            </div>
          </div>

          {/* Summary */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="font-bold mb-4">Resumo do Pedido</h2>
            <div className="space-y-2 mb-4">
              {items.map(item => (
                <div key={`${item.id}-${item.size}`} className="flex justify-between text-sm">
                  <span>{item.name} ({item.size}) x{item.quantity}</span>
                  <span className="font-semibold">R$ {item.subtotal.toFixed(2).replace('.', ',')}</span>
                </div>
              ))}
            </div>
            <div className="flex justify-between items-center border-t pt-4">
              <span className="font-bold">Total a pagar</span>
              <span className="text-2xl font-extrabold text-[#E74C3C]">R$ {total.toFixed(2).replace('.', ',')}</span>
            </div>
            <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800 mt-3">
              <Clock className="inline w-4 h-4 mr-1" />
              PAGAMENTO VIA PIX — QR Code será gerado na próxima etapa.
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button type="submit" disabled={loading}
            className="w-full bg-[#E74C3C] text-white font-bold py-4 rounded-xl text-lg hover:bg-[#C0392B] disabled:opacity-50 transition">
            {loading ? 'Gerando PIX...' : 'Continuar para Pagamento'}
          </button>
        </form>
      )}

      {step === 'pix' && pixData && (
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm p-6 text-center">
            <h2 className="font-bold text-xl mb-4">Pagar com PIX</h2>
            <div className="bg-white border-2 border-dashed border-gray-300 rounded-xl p-6 inline-block">
              <QrCode className="w-48 h-48 text-gray-800 mx-auto" />
              <p className="text-xs text-gray-500 mt-2">QR Code PIX</p>
            </div>
            <p className="mt-4 font-bold text-lg">Valor: <span className="text-[#E74C3C]">R$ {pixData.amount.toFixed(2).replace('.', ',')}</span></p>
            <button onClick={handleCopy} className="mt-3 flex items-center gap-2 mx-auto text-sm text-[#E74C3C] font-bold hover:underline">
              <Copy className="w-4 h-4" /> Copiar código PIX
            </button>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-center">
            <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <p className="font-bold text-green-800">Pedido criado! Aguarde a confirmação do PIX.</p>
            <p className="text-sm text-green-700 mt-1">A confirmação é automática e leva poucos minutos.</p>
          </div>

          <button onClick={() => navigate('/pedidos')} className="w-full border-2 border-[#E74C3C] text-[#E74C3C] font-bold py-4 rounded-xl text-lg hover:bg-[#E74C3C] hover:text-white transition">
            Ver Meus Pedidos
          </button>
        </div>
      )}
    </div>
  )
}