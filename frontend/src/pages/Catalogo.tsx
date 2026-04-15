import { useState, useEffect } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '@/lib/api'
import type { Product } from '@/lib/api'
import { ChevronLeft, ChevronRight } from 'lucide-react'


function ProductCard({ p }: { p: Product }) {
  return (
    <Link to={`/produto/${p.id}`} className="group bg-white rounded-xl shadow-sm overflow-hidden hover:shadow-md transition-all">
      <div className="aspect-square bg-gray-100 relative overflow-hidden">
        {p.image_url ? (
          <img src={p.image_url} alt={p.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300" />
        ) : (
          <div className="w-full h-full flex items-center justify-center text-gray-400 text-5xl font-bold">{p.name[0]}</div>
        )}
        {p.compare_price && p.compare_price > p.price && (
          <span className="absolute top-2 left-2 bg-yellow-400 text-black text-xs font-bold px-2 py-0.5 rounded">
            -{Math.round((1 - p.price / p.compare_price) * 100)}%
          </span>
        )}
      </div>
      <div className="p-4">
        <p className="text-xs text-gray-500 mb-1">{p.team || p.league || ''}</p>
        <h3 className="font-semibold text-sm leading-tight mb-2 line-clamp-2">{p.name}</h3>
        <div className="flex items-center gap-2">
          <span className="font-bold text-lg text-[#E74C3C]">R$ {p.price.toFixed(2).replace('.', ',')}</span>
          {p.compare_price && <span className="text-xs text-gray-400 line-through">R$ {p.compare_price.toFixed(2).replace('.', ',')}</span>}
        </div>
        <div className="flex gap-1 mt-2 flex-wrap">
          {p.sizes.map(s => <span key={s} className="text-xs border border-gray-200 px-1.5 py-0.5 rounded text-gray-600">{s}</span>)}
        </div>
      </div>
    </Link>
  )
}

export default function Catalogo() {
  const [searchParams, setSearchParams] = useSearchParams()
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const category = searchParams.get('category') || ''
  const search = searchParams.get('search') || ''
  const [searchInput, setSearchInput] = useState(search)

  useEffect(() => {
    setLoading(true)
    api.getProducts({ page, category, ...(search ? { search } : {}) } as any).then(data => {
      setProducts(data.items)
      setTotalPages(data.pages)
    }).catch(console.error).finally(() => setLoading(false))
  }, [page, category, search])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    setSearchParams(p => { p.set('search', searchInput); p.delete('category'); return p })
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row gap-8">
        {/* Filters Sidebar */}
        <aside className="md:w-56 shrink-0">
          <div className="bg-white rounded-xl p-4 shadow-sm sticky top-24">
            <h3 className="font-bold mb-3 text-sm">Categorias</h3>
            <ul className="space-y-1">
              {['', 'copa-do-mundo', 'brasileirao'].map(cat => {
                const labels: Record<string, string> = { '': 'Todos', 'copa-do-mundo': '🌍 Copa do Mundo 2026', 'brasileirao': '🇧🇷 Brasileirão' }
                return (
                  <li key={cat}>
                    <button
                      onClick={() => { setPage(1); setSearchParams(cat ? { category: cat } : {}); setSearchInput('') }}
                      className={`w-full text-left text-sm px-3 py-2 rounded-lg transition ${category === cat ? 'bg-[#E74C3C] text-white' : 'hover:bg-gray-100'}`}
                    >
                      {labels[cat]}
                    </button>
                  </li>
                )
              })}
            </ul>
          </div>
        </aside>

        {/* Products */}
        <div className="flex-1">
          {/* Search & Sort */}
          <div className="flex gap-3 mb-6">
            <form onSubmit={handleSearch} className="flex-1 flex gap-2">
              <input
                value={searchInput}
                onChange={e => setSearchInput(e.target.value)}
                placeholder="Buscar por time, ano..."
                className="flex-1 border rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]"
              />
              <button type="submit" className="bg-[#E74C3C] text-white font-bold px-4 py-2 rounded-lg text-sm hover:bg-[#C0392B]">Buscar</button>
            </form>
          </div>

          <p className="text-sm text-gray-500 mb-4">{products.length} produtos</p>

          {loading ? (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {Array.from({ length: 12 }).map((_, i) => (
                <div key={i} className="bg-gray-200 rounded-xl aspect-square animate-pulse" />
              ))}
            </div>
          ) : products.length === 0 ? (
            <div className="text-center py-16 text-gray-500">
              <p className="text-lg font-semibold mb-2">Nenhum produto encontrado</p>
              <p className="text-sm">Tente buscar por outro termo ou categoria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
              {products.map(p => <ProductCard key={p.id} p={p} />)}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}
                className="p-2 border rounded-lg disabled:opacity-50 hover:bg-gray-100">
                <ChevronLeft className="w-4 h-4" />
              </button>
              <span className="text-sm px-3">Página {page} de {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}
                className="p-2 border rounded-lg disabled:opacity-50 hover:bg-gray-100">
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}