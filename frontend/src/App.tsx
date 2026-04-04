import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import './App.css'
import { Layout } from '@/components/Layout'
import Home from '@/pages/Home'
import Catalogo from '@/pages/Catalogo'
import Produto from '@/pages/Produto'
import Carrinho from '@/pages/Carrinho'
import Checkout from '@/pages/Checkout'
import Login from '@/pages/Login'
import AdminDashboard from '@/pages/admin/Dashboard'
import AdminProducts from '@/pages/admin/Products'

function AdminLayout() {
  return (
    <div className="flex min-h-screen bg-gray-100">
      <aside className="w-64 bg-[#2C3E50] text-white shrink-0">
        <div className="p-4 font-extrabold text-xl border-b border-white/10">Admin CJ</div>
        <nav className="p-4 space-y-1">
          <a href="/admin" className="block px-3 py-2 rounded hover:bg-white/10 text-sm font-semibold">Dashboard</a>
          <a href="/admin/produtos" className="block px-3 py-2 rounded hover:bg-white/10 text-sm font-semibold">Produtos</a>
          <a href="/" className="block px-3 py-2 rounded hover:bg-white/10 text-sm font-semibold mt-4 border-t border-white/10">Ver Site</a>
        </nav>
      </aside>
      <div className="flex-1 overflow-auto">
        <Routes>
          <Route path="/" element={<AdminDashboard />} />
          <Route path="/produtos" element={<AdminProducts />} />
        </Routes>
      </div>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Home />} />
          <Route path="/catalogo" element={<Catalogo />} />
          <Route path="/produto/:id" element={<Produto />} />
          <Route path="/carrinho" element={<Carrinho />} />
          <Route path="/checkout" element={<Checkout />} />
          <Route path="/login" element={<Login />} />
        </Route>
        <Route path="/admin" element={<AdminLayout />} />
        <Route path="/admin/produtos" element={<AdminLayout />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  )
}