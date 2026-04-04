import { Link } from 'react-router-dom'
import { useCart } from '@/hooks/useCart'
import { Trash2, Minus, Plus, ShoppingBag } from 'lucide-react'

export default function Carrinho() {
  const { items, total, removeItem, updateItem, clear } = useCart()

  if (items.length === 0) return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <ShoppingBag className="w-16 h-16 text-gray-300 mx-auto mb-4" />
      <h1 className="text-2xl font-bold text-gray-500 mb-2">Seu carrinho está vazio</h1>
      <p className="text-gray-400 mb-6">Adicione camisas ao seu carrinho!</p>
      <Link to="/catalogo" className="inline-block bg-[#E74C3C] text-white font-bold px-8 py-3 rounded-full hover:bg-[#C0392B]">Ver Catálogo</Link>
    </div>
  )

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-extrabold">Meu Carrinho</h1>
        <button onClick={clear} className="text-sm text-gray-400 hover:text-red-500">Esvaziar</button>
      </div>

      <div className="space-y-4">
        {items.map(item => (
          <div key={`${item.id}-${item.size}`} className="bg-white rounded-xl shadow-sm p-4 flex gap-4">
            <div className="w-24 h-24 bg-gray-100 rounded-lg overflow-hidden shrink-0">
              {item.image_url ? <img src={item.image_url} alt={item.name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-300 font-bold text-xl">{item.name[0]}</div>}
            </div>
            <div className="flex-1 min-w-0">
              <h3 className="font-bold text-sm">{item.name}</h3>
              <p className="text-xs text-gray-500">Tam: {item.size}</p>
              <p className="font-bold text-[#E74C3C] mt-1">R$ {item.price.toFixed(2).replace('.', ',')}</p>
            </div>
            <div className="flex flex-col items-end justify-between">
              <button onClick={() => removeItem(item.id)} className="text-gray-400 hover:text-red-500 p-1"><Trash2 className="w-4 h-4" /></button>
              <div className="flex items-center gap-2">
                <button onClick={() => updateItem(item.id, item.product_id, item.size, Math.max(1, item.quantity - 1))} className="w-7 h-7 border rounded flex items-center justify-center hover:bg-gray-100"><Minus className="w-3 h-3" /></button>
                <span className="font-bold w-6 text-center">{item.quantity}</span>
                <button onClick={() => updateItem(item.id, item.product_id, item.size, item.quantity + 1)} className="w-7 h-7 border rounded flex items-center justify-center hover:bg-gray-100"><Plus className="w-3 h-3" /></button>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 bg-white rounded-xl shadow-sm p-6">
        <div className="flex justify-between items-center mb-4">
          <span className="text-lg font-bold">Total ({items.reduce((a, i) => a + i.quantity, 0)} itens)</span>
          <span className="text-2xl font-extrabold text-[#E74C3C]">R$ {total.toFixed(2).replace('.', ',')}</span>
        </div>
        <Link to="/checkout" className="block w-full bg-[#E74C3C] text-white font-bold py-4 rounded-xl text-center text-lg hover:bg-[#C0392B] transition">
          Finalizar Compra
        </Link>
      </div>
    </div>
  )
}