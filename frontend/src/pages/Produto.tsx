import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '@/lib/api'
import { useCart } from '@/hooks/useCart'
import type { Product } from '@/lib/api'
import { ShoppingCart, Check } from 'lucide-react'

const SIZES = ['P', 'M', 'G', 'GG', 'XG', 'EXG']

export default function Produto() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { addItem } = useCart()
  const [product, setProduct] = useState<Product | null>(null)
  const [selectedSize, setSelectedSize] = useState('')
  const [quantity, setQuantity] = useState(1)
  const [loading, setLoading] = useState(true)
  const [added, setAdded] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!id) return
    api.getProduct(Number(id)).then(setProduct).catch(() => setError('Produto não encontrado')).finally(() => setLoading(false))
  }, [id])

  const handleAdd = async () => {
    if (!selectedSize) { setError('Selecione um tamanho'); return }
    if (!product) return
    try {
      await addItem(product.id, selectedSize, quantity)
      setAdded(true)
      setTimeout(() => setAdded(false), 2000)
    } catch { setError('Erro ao adicionar ao carrinho') }
  }

  if (loading) return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <div className="grid md:grid-cols-2 gap-8">
        <div className="aspect-square bg-gray-200 rounded-2xl animate-pulse" />
        <div className="space-y-4"><div className="h-8 bg-gray-200 rounded animate-pulse" /><div className="h-4 bg-gray-200 rounded animate-pulse w-2/3" /></div>
      </div>
    </div>
  )

  if (error && !product) return (
    <div className="max-w-5xl mx-auto px-4 py-16 text-center">
      <p className="text-xl font-bold text-gray-400">{error}</p>
      <button onClick={() => navigate('/catalogo')} className="mt-4 bg-[#E74C3C] text-white font-bold px-6 py-3 rounded-full">Ver Catálogo</button>
    </div>
  )

  if (!product) return null

  const availableSizes = SIZES.filter(s => product.sizes.includes(s))

  return (
    <div className="max-w-5xl mx-auto px-4 py-8">
      <button onClick={() => navigate(-1)} className="text-sm text-gray-500 hover:text-[#E74C3C] mb-4">← Voltar</button>
      <div className="grid md:grid-cols-2 gap-8">
        {/* Image */}
        <div className="aspect-square bg-gray-100 rounded-2xl overflow-hidden">
          {product.image_url ? (
            <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
          ) : (
            <div className="w-full h-full flex items-center justify-center text-gray-300 text-7xl font-bold">{product.name[0]}</div>
          )}
        </div>

        {/* Details */}
        <div className="space-y-5">
          {product.team && <span className="text-sm font-semibold text-gray-500 bg-gray-100 px-3 py-1 rounded-full">{product.team}</span>}
          <h1 className="text-3xl font-extrabold leading-tight">{product.name}</h1>
          {product.year && <p className="text-sm text-gray-500">Temporada {product.year}</p>}

          <div className="flex items-baseline gap-3">
            <span className="text-4xl font-extrabold text-[#E74C3C]">R$ {product.price.toFixed(2).replace('.', ',')}</span>
            {product.compare_price && product.compare_price > product.price && (
              <span className="text-xl text-gray-400 line-through">R$ {product.compare_price.toFixed(2).replace('.', ',')}</span>
            )}
          </div>

          {product.description && <p className="text-gray-600 leading-relaxed">{product.description}</p>}

          {/* Size */}
          <div>
            <p className="font-bold mb-2 text-sm">Selecione o tamanho:</p>
            <div className="flex gap-2 flex-wrap">
              {availableSizes.map(s => (
                <button key={s}
                  onClick={() => setSelectedSize(s)}
                  className={`w-12 h-12 rounded-lg font-bold text-sm border-2 transition ${selectedSize === s ? 'border-[#E74C3C] bg-[#E74C3C] text-white' : 'border-gray-200 hover:border-[#E74C3C]'}`}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>

          {/* Quantity */}
          <div>
            <p className="font-bold mb-2 text-sm">Quantidade:</p>
            <div className="flex items-center gap-3">
              <button onClick={() => setQuantity(q => Math.max(1, q - 1))} className="w-10 h-10 rounded-lg border font-bold text-lg hover:bg-gray-100">-</button>
              <span className="font-bold text-xl w-8 text-center">{quantity}</span>
              <button onClick={() => setQuantity(q => Math.min(10, q + 1))} className="w-10 h-10 rounded-lg border font-bold text-lg hover:bg-gray-100">+</button>
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button
            onClick={handleAdd}
            className={`w-full py-4 rounded-xl font-bold text-lg flex items-center justify-center gap-2 transition ${added ? 'bg-green-500 text-white' : 'bg-[#E74C3C] text-white hover:bg-[#C0392B]'}`}
          >
            {added ? <><Check className="w-5 h-5" /> Adicionado ao carrinho!</> : <><ShoppingCart className="w-5 h-5" /> Adicionar ao Carrinho</>}
          </button>

          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 text-sm text-yellow-800">
            <strong>Pagamento:</strong> PIX em até 15 min. O pedido é enviado após confirmação do pagamento.
          </div>
        </div>
      </div>
    </div>
  )
}