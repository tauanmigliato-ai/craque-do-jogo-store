import { Link } from 'react-router-dom'
import { ArrowRight, Star, Truck, Shield } from 'lucide-react'
import { useEffect, useState } from 'react'
import { api } from '@/lib/api'
import type { Product } from '@/lib/api'

function ProductCard({ p }: { p: Product }) {
  return (
    <Link to={`/produto/${p.id}`} className="group bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-all">
      <div className="aspect-square bg-gray-100 relative overflow-hidden">
        {p.image_url ? (
          <img src={p.image_url} alt={p.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400 text-4xl font-bold">
            {p.name[0]}
          </div>
        )}
        {p.compare_price && p.compare_price > p.price && (
          <span className="absolute top-2 left-2 bg-yellow-400 text-black text-xs font-bold px-2 py-0.5 rounded">
            -{Math.round((1 - p.price / p.compare_price) * 100)}%
          </span>
        )}
        {p.featured && (
          <span className="absolute top-2 right-2 bg-red-500 text-white text-xs font-bold px-2 py-0.5 rounded">Destaque</span>
        )}
      </div>
      <div className="p-4">
        <p className="text-xs text-gray-500 mb-1">{p.team || p.league || ''}</p>
        <h3 className="font-semibold text-sm leading-tight mb-2 line-clamp-2">{p.name}</h3>
        <div className="flex items-center gap-2">
          <span className="font-bold text-lg text-[#E74C3C]">R$ {p.price.toFixed(2).replace('.', ',')}</span>
          {p.compare_price && (
            <span className="text-xs text-gray-400 line-through">R$ {p.compare_price.toFixed(2).replace('.', ',')}</span>
          )}
        </div>
        <div className="flex gap-1 mt-2 flex-wrap">
          {p.sizes.map(s => (
            <span key={s} className="text-xs border border-gray-200 px-1.5 py-0.5 rounded text-gray-600">{s}</span>
          ))}
        </div>
      </div>
    </Link>
  )
}

export default function Home() {
  const [featured, setFeatured] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.getFeatured(8).then(setFeatured).catch(console.error).finally(() => setLoading(false))
  }, [])

  return (
    <div>
      {/* Hero */}
      <div className="bg-gradient-to-r from-[#E74C3C] to-[#C0392B] text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 md:py-24">
          <div className="max-w-xl">
            <h1 className="text-4xl md:text-5xl font-extrabold mb-4 leading-tight">
             Vista a sua paixão
            </h1>
            <p className="text-lg md:text-xl text-white/90 mb-6">
              Camisas de times do Brasil e do mundo. Qualidade original, preço justo, entrega rápida.
            </p>
            <div className="flex gap-3">
              <Link to="/catalogo" className="inline-flex items-center gap-2 bg-white text-[#E74C3C] font-bold px-6 py-3 rounded-full hover:bg-gray-100 transition">
                Ver Catálogo <ArrowRight className="w-4 h-4" />
              </Link>
              <Link to="/login" className="inline-flex items-center gap-2 border-2 border-white text-white font-bold px-6 py-3 rounded-full hover:bg-white/10 transition">
                Cadastrar
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Value Props */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 py-6 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="flex items-center gap-3">
            <Truck className="w-8 h-8 text-[#E74C3C]" />
            <div><strong className="block text-sm">Frete Grátis</strong><span className="text-xs text-gray-500">Em compras acima de R$ 299</span></div>
          </div>
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-[#E74C3C]" />
            <div><strong className="block text-sm">Compra Segura</strong><span className="text-xs text-gray-500">PIX, feedback em instantes</span></div>
          </div>
          <div className="flex items-center gap-3">
            <Star className="w-8 h-8 text-[#E74C3C]" />
            <div><strong className="block text-sm">Qualidade Garantida</strong><span className="text-xs text-gray-500">Material premium, costura reforçada</span></div>
          </div>
        </div>
      </div>

      {/* Featured Products */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold">Destaques</h2>
          <Link to="/catalogo" className="text-[#E74C3C] font-semibold text-sm flex items-center gap-1 hover:underline">
            Ver todos <ArrowRight className="w-4 h-4" />
          </Link>
        </div>

        {loading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="bg-gray-200 rounded-xl aspect-square animate-pulse" />
            ))}
          </div>
        ) : featured.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {featured.map(p => <ProductCard key={p.id} p={p} />)}
          </div>
        ) : (
          <div className="text-center py-16 text-gray-500">
            <p className="text-lg font-semibold mb-2">Catálogo em preparação</p>
            <p>Aguarde! Em breve teremos muitas camisas disponíveis.</p>
            <Link to="/catalogo" className="inline-block mt-4 bg-[#E74C3C] text-white font-bold px-6 py-3 rounded-full">
              Ver Catálogo
            </Link>
          </div>
        )}
      </div>

      {/* Categories */}
      <div className="bg-gray-100">
        <div className="max-w-7xl mx-auto px-4 py-12">
          <h2 className="text-2xl font-bold mb-6">Explore por categoria</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { slug: 'copa-do-mundo', label: 'Copa do Mundo 2026', emoji: '🌍' },
              { slug: 'brasileirao',   label: 'Brasileirão',        emoji: '🇧🇷' },
            ].map(cat => (
              <Link key={cat.slug} to={`/catalogo?category=${cat.slug}`}
                className="bg-white rounded-xl p-6 text-center hover:shadow-md transition group">
                <div className="text-4xl mb-2">{cat.emoji}</div>
                <div className="font-bold group-hover:text-[#E74C3C] transition">{cat.label}</div>
              </Link>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}