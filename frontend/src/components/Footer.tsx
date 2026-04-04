import { Link } from 'react-router-dom'
import { Package } from 'lucide-react'

export function Footer() {
  return (
    <footer className="bg-[#2C3E50] text-white mt-auto">
      <div className="max-w-7xl mx-auto px-4 py-10">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <div className="flex items-center gap-2 font-extrabold text-xl mb-3">
              <Package className="w-6 h-6" />
              Craque Do Jogo Store
            </div>
            <p className="text-sm text-gray-300">
              As melhores camisas de futebol, basquete e baseball do Brasil. Qualidade garantida, entrega rápida.
            </p>
          </div>
          <div>
            <h3 className="font-bold mb-3">Navegação</h3>
            <ul className="space-y-1 text-sm text-gray-300">
              <li><Link to="/catalogo" className="hover:text-white">Catálogo</Link></li>
              <li><Link to="/catalogo?category=brasileiros" className="hover:text-white">Brasileiros</Link></li>
              <li><Link to="/catalogo?category=internacionais" className="hover:text-white">Internacionais</Link></li>
              <li><Link to="/catalogo?category=nba" className="hover:text-white">NBA</Link></li>
              <li><Link to="/catalogo?category=selecoes" className="hover:text-white">Seleções</Link></li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold mb-3">Contato</h3>
            <ul className="space-y-1 text-sm text-gray-300">
              <li>WhatsApp: (21) 99999-9999</li>
              <li>Email: contato@craquedojogo.com.br</li>
            </ul>
            <p className="text-xs text-gray-400 mt-4">
              © {new Date().getFullYear()} Craque Do Jogo Store. Todos os direitos reservados.
            </p>
          </div>
        </div>
      </div>
    </footer>
  )
}