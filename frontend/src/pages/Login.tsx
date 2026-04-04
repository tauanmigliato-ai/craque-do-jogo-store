import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, setToken } from '@/lib/api'

export default function Login() {
  const navigate = useNavigate()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  const [form, setForm] = useState({ email: '', password: '', name: '' })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      if (mode === 'register') {
        await api.register(form)
      }
      const { access_token } = await api.login({ email: form.email, password: form.password })
      setToken(access_token)
      const user = await api.me()
      navigate(user.role === 'admin' ? '/admin' : '/')
    } catch (err: any) {
      setError(err.message || 'Erro na autenticação')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
      <div className="bg-white rounded-2xl shadow-lg p-8 w-full max-w-md">
        <div className="text-center mb-6">
          <div className="w-16 h-16 bg-[#E74C3C] rounded-full flex items-center justify-center mx-auto mb-3">
            <span className="text-white text-2xl font-extrabold">CJ</span>
          </div>
          <h1 className="text-2xl font-extrabold">
            {mode === 'login' ? 'Entrar na conta' : 'Criar conta'}
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            {mode === 'login' ? 'Bem-vindo de volta!' : 'Cadastre-se para comprar'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {mode === 'register' && (
            <input name="name" placeholder="Seu nome" value={form.name} onChange={handleChange} required
              className="w-full border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
          )}
          <input name="email" placeholder="Email" type="email" value={form.email} onChange={handleChange} required
            className="w-full border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />
          <input name="password" placeholder="Senha" type="password" value={form.password} onChange={handleChange} required
            className="w-full border rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-[#E74C3C]" />

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <button type="submit" disabled={loading}
            className="w-full bg-[#E74C3C] text-white font-bold py-3 rounded-xl hover:bg-[#C0392B] disabled:opacity-50 transition">
            {loading ? 'Aguarde...' : mode === 'login' ? 'Entrar' : 'Cadastrar'}
          </button>
        </form>

        <p className="text-center text-sm text-gray-500 mt-4">
          {mode === 'login' ? 'Não tem conta?' : 'Já tem conta?'}{' '}
          <button onClick={() => setMode(m => m === 'login' ? 'register' : 'login')}
            className="text-[#E74C3C] font-bold hover:underline">
            {mode === 'login' ? 'Cadastre-se' : 'Entrar'}
          </button>
        </p>
      </div>
    </div>
  )
}