import { Link, useLocation } from 'react-router-dom'
import { ShoppingCart, User, Menu, X, Package } from 'lucide-react'
import { useEffect, useState } from 'react'
import { getToken, setToken } from '@/lib/api'

interface HeaderProps {
  cartCount?: number
}

export function Header({ cartCount = 0 }: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false)
  const [authed, setAuthed] = useState(false)
  const location = useLocation()

  useEffect(() => {
    setAuthed(!!getToken())
  }, [location])

  const handleLogout = () => {
    setToken('')
    window.location.href = '/'
  }

  return (
    <header className="bg-[#E74C3C] text-white sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2">
            <Package className="w-7 h-7" />
            <span className="font-extrabold text-xl tracking-tight">Craque Do Jogo</span>
          </Link>

          {/* Desktop Nav */}
          <nav className="hidden md:flex items-center gap-6 text-sm font-semibold">
            <Link to="/" className="hover:underline">Início</Link>
            <Link to="/catalogo" className="hover:underline">Camisas Retrô</Link>
            <Link to="/catalogo?category=brasileiros" className="hover:underline">Brasileiros</Link>
            <Link to="/catalogo?category=internacionais" className="hover:underline">Internacionais</Link>
            <Link to="/catalogo?category=nba" className="hover:underline">NBA</Link>
            <Link to="/catalogo?category=selecoes" className="hover:underline">Seleções</Link>
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <Link to="/carrinho" className="relative p-2 hover:bg-white/10 rounded-full">
              <ShoppingCart className="w-5 h-5" />
              {cartCount > 0 && (
                <span className="absolute -top-1 -right-1 bg-yellow-400 text-black text-xs font-bold rounded-full w-5 h-5 flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>
            {authed ? (
              <div className="flex items-center gap-2">
                <Link to="/admin" className="hidden md:flex items-center gap-1 text-xs bg-white/10 px-3 py-1.5 rounded-full hover:bg-white/20">
                  <User className="w-4 h-4" /> Admin
                </Link>
                <button onClick={handleLogout} className="text-xs bg-white/10 px-3 py-1.5 rounded-full hover:bg-white/20">Sair</button>
              </div>
            ) : (
              <Link to="/login" className="hidden md:flex items-center gap-1 text-xs bg-white/10 px-3 py-1.5 rounded-full hover:bg-white/20">
                <User className="w-4 h-4" /> Entrar
              </Link>
            )}
            <button className="md:hidden p-2" onClick={() => setMenuOpen(!menuOpen)}>
              {menuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {menuOpen && (
        <div className="md:hidden bg-[#C0392B] border-t border-white/10">
          <nav className="flex flex-col px-4 py-3 gap-2 text-sm font-semibold">
            <Link to="/" onClick={() => setMenuOpen(false)}>Início</Link>
            <Link to="/catalogo" onClick={() => setMenuOpen(false)}>Camisas Retrô</Link>
            <Link to="/catalogo?category=brasileiros" onClick={() => setMenuOpen(false)}>Brasileiros</Link>
            <Link to="/catalogo?category=internacionais" onClick={() => setMenuOpen(false)}>Internacionais</Link>
            <Link to="/catalogo?category=nba" onClick={() => setMenuOpen(false)}>NBA</Link>
            <Link to="/catalogo?category=selecoes" onClick={() => setMenuOpen(false)}>Seleções</Link>
            <div className="border-t border-white/10 pt-2 mt-1">
              {authed ? (
                <>
                  <Link to="/admin" onClick={() => setMenuOpen(false)} className="block py-1">Painel Admin</Link>
                  <button onClick={handleLogout} className="block py-1 text-left w-full">Sair</button>
                </>
              ) : (
                <Link to="/login" onClick={() => setMenuOpen(false)}>Entrar / Cadastrar</Link>
              )}
            </div>
          </nav>
        </div>
      )}
    </header>
  )
}