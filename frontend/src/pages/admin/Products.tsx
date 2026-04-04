import { useState, useEffect } from 'react'
import { api, type Product, type ProductInput } from '@/lib/api'
import { Plus, Trash2, Edit, Star, Eye, EyeOff } from 'lucide-react'

const CATEGORIES = ['brasileiros', 'internacionais', 'selecoes', 'nba', 'mlb', 'retro']
const TYPES = ['home', 'away', 'third', 'retro']
const SIZES = ['P', 'M', 'G', 'GG', 'XG', 'EXG']

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '')
}

export default function AdminProducts() {
  const [products, setProducts] = useState<Product[]>([])
  const [loading, setLoading] = useState(true)
  const [editing, setEditing] = useState<Product | null>(null)
  const [form, setForm] = useState<ProductInput>({
    name: '', slug: '', price: 0, compare_price: 0, image_url: '', images: [], sizes: [],
    team: '', league: '', year: '', type: '', stock: 0, featured: false, active: true,
  })
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    loadProducts()
  }, [])

  const loadProducts = () => {
    setLoading(true)
    api.getProducts({ per_page: 100 }).then(d => setProducts(d.items)).catch(console.error).finally(() => setLoading(false))
  }

  const resetForm = () => {
    setEditing(null)
    setForm({ name: '', slug: '', price: 0, compare_price: 0, image_url: '', images: [], sizes: [], team: '', league: '', year: '', type: '', stock: 0, featured: false, active: true })
  }

  const handleSave = async () => {
    setSaving(true)
    try {
      const data = { ...form, slug: form.slug || slugify(form.name) }
      if (editing) {
        await api.updateProduct(editing.id, data)
      } else {
        await api.createProduct(data)
      }
      resetForm()
      loadProducts()
    } catch (err: any) {
      alert(err.message)
    } finally {
      setSaving(false)
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Excluir este produto?')) return
    await api.deleteProduct(id)
    loadProducts()
  }

  const handleToggleActive = async (p: Product) => {
    await api.updateProduct(p.id, { active: !p.active })
    loadProducts()
  }

  const handleToggleFeatured = async (p: Product) => {
    await api.updateProduct(p.id, { featured: !p.featured })
    loadProducts()
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-extrabold">Produtos</h1>
        <button onClick={resetForm} className="flex items-center gap-2 bg-[#E74C3C] text-white font-bold px-4 py-2 rounded-lg hover:bg-[#C0392B]">
          <Plus className="w-4 h-4" /> Novo Produto
        </button>
      </div>

      {/* Form */}
      {(editing || form.name) && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-6 space-y-4">
          <h2 className="font-bold">{editing ? 'Editar Produto' : 'Novo Produto'}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input placeholder="Nome do produto" value={form.name} onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="Time / League" value={form.team || ''} onChange={e => setForm(f => ({ ...f, team: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="Liga (ex: Brasileirão, NBA, MLB)" value={form.league || ''} onChange={e => setForm(f => ({ ...f, league: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="Ano (ex: 2025-26)" value={form.year || ''} onChange={e => setForm(f => ({ ...f, year: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="Preço (R$)" type="number" value={form.price || ''} onChange={e => setForm(f => ({ ...f, price: parseFloat(e.target.value) || 0 }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="Preço de (para exibir desconto)" type="number" value={form.compare_price || ''} onChange={e => setForm(f => ({ ...f, compare_price: parseFloat(e.target.value) || 0 }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="Estoque" type="number" value={form.stock || ''} onChange={e => setForm(f => ({ ...f, stock: parseInt(e.target.value) || 0 }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
            <input placeholder="URL da imagem (upload futuro)" value={form.image_url || ''} onChange={e => setForm(f => ({ ...f, image_url: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C] md:col-span-2" />
          </div>

          {/* Category */}
          <div className="flex flex-wrap gap-3">
            <select value={form.league || ''} onChange={e => setForm(f => ({ ...f, league: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm">
              <option value="">Categoria</option>
              {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
            </select>
            <select value={form.type || ''} onChange={e => setForm(f => ({ ...f, type: e.target.value }))}
              className="border rounded-lg px-3 py-2 text-sm">
              <option value="">Tipo</option>
              {TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <div className="flex items-center gap-2">
              <span className="text-sm">Tamanhos:</span>
              {SIZES.map(s => (
                <label key={s} className="flex items-center gap-1 text-sm">
                  <input type="checkbox" checked={form.sizes.includes(s)}
                    onChange={e => setForm(f => ({
                      ...f,
                      sizes: e.target.checked ? [...f.sizes, s] : f.sizes.filter(x => x !== s)
                    }))} />
                  {s}
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.featured}
                onChange={e => setForm(f => ({ ...f, featured: e.target.checked }))} />
              Destaque
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="checkbox" checked={form.active}
                onChange={e => setForm(f => ({ ...f, active: e.target.checked }))} />
              Ativo
            </label>
          </div>

          <div className="flex gap-3">
            <button onClick={handleSave} disabled={saving}
              className="bg-[#E74C3C] text-white font-bold px-6 py-2 rounded-lg hover:bg-[#C0392B] disabled:opacity-50">
              {saving ? 'Salvando...' : editing ? 'Salvar Alterações' : 'Criar Produto'}
            </button>
            <button onClick={resetForm} className="border px-6 py-2 rounded-lg">Cancelar</button>
          </div>
        </div>
      )}

      {/* Table */}
      {loading ? (
        <div className="text-center py-12 text-gray-400">Carregando...</div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          <table className="w-full text-sm">
            <thead className="bg-gray-50 border-b">
              <tr>
                <th className="text-left p-4 font-bold">Produto</th>
                <th className="text-left p-4 font-bold">Time</th>
                <th className="text-left p-4 font-bold">Preço</th>
                <th className="text-left p-4 font-bold">Estoque</th>
                <th className="text-left p-4 font-bold">Status</th>
                <th className="text-left p-4 font-bold">Ações</th>
              </tr>
            </thead>
            <tbody>
              {products.map(p => (
                <tr key={p.id} className="border-b hover:bg-gray-50">
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-gray-100 rounded-lg overflow-hidden shrink-0">
                        {p.image_url ? <img src={p.image_url} alt="" className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center text-gray-400 font-bold">{p.name[0]}</div>}
                      </div>
                      <span className="font-semibold">{p.name}</span>
                    </div>
                  </td>
                  <td className="p-4 text-gray-500">{p.team || p.league || '-'}</td>
                  <td className="p-4 font-bold text-[#E74C3C]">R$ {p.price.toFixed(2).replace('.', ',')}</td>
                  <td className="p-4">{p.stock}</td>
                  <td className="p-4">
                    <div className="flex gap-1">
                      {p.featured && <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-0.5 rounded">Destaque</span>}
                      {p.active ? <span className="text-xs bg-green-100 text-green-800 px-2 py-0.5 rounded">Ativo</span> : <span className="text-xs bg-gray-200 text-gray-600 px-2 py-0.5 rounded">Inativo</span>}
                    </div>
                  </td>
                  <td className="p-4">
                    <div className="flex gap-2">
                      <button onClick={() => { setEditing(p); setForm(p as ProductInput) }} className="p-1.5 text-gray-500 hover:text-[#E74C3C]"><Edit className="w-4 h-4" /></button>
                      <button onClick={() => handleToggleFeatured(p)} className="p-1.5 text-gray-500 hover:text-yellow-500"><Star className="w-4 h-4" /></button>
                      <button onClick={() => handleToggleActive(p)} className="p-1.5 text-gray-500 hover:text-gray-700">{p.active ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}</button>
                      <button onClick={() => handleDelete(p.id)} className="p-1.5 text-gray-500 hover:text-red-500"><Trash2 className="w-4 h-4" /></button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          {products.length === 0 && <p className="text-center py-8 text-gray-400">Nenhum produto ainda. Clique em "Novo Produto" para adicionar.</p>}
        </div>
      )}
    </div>
  )
}