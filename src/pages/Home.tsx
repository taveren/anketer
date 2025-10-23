import { useState } from "react"
import { Link } from "react-router-dom"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Settings, Play } from "lucide-react"

export default function Home() {
  const [showAdminLogin, setShowAdminLogin] = useState(false)
  const [password, setPassword] = useState("")
  const [isAuthenticated, setIsAuthenticated] = useState(false)

  const handleAdminLogin = () => {
    if (password === "admin123") {
      setIsAuthenticated(true)
      setShowAdminLogin(false)
    } else {
      alert("Неверный пароль")
    }
  }

  if (isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
        <div className="w-full max-w-2xl">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Панель администратора
            </h1>
            <p className="text-lg text-gray-600">
              Управление анкетами и просмотр ответов
            </p>
          </div>
          
          <div className="card">
            <div className="card-content text-center space-y-6">
              <div className="space-y-4">
                <Link to="/admin" className="block">
                  <Button size="lg" className="w-full">
                    <Settings className="w-5 h-5 mr-2" />
                    Управление анкетами
                  </Button>
                </Link>
                
                <Button 
                  variant="outline" 
                  onClick={() => setIsAuthenticated(false)}
                  className="w-full"
                >
                  Выйти из админки
                </Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4 relative">
      {/* Админ кнопка в правом верхнем углу */}
      <div className="absolute top-4 right-4">
        <Button
          variant="outline"
          size="sm"
          onClick={() => setShowAdminLogin(true)}
          className="flex items-center gap-2"
        >
          <Settings className="w-4 h-4" />
          Админ
        </Button>
      </div>

      <div className="w-full max-w-2xl text-center">
        <div className="mb-12">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Система анкетирования
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Пройти опрос
          </p>
        </div>
        
        <div className="mb-8">
          <Link to="/survey">
            <Button size="lg" className="btn-primary btn-lg text-xl px-12 py-6 rounded-full shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105">
              <Play className="w-6 h-6 mr-3" />
              СТАРТ
            </Button>
          </Link>
        </div>

        <p className="text-gray-500 text-sm">
          Нажмите кнопку выше, чтобы начать заполнение анкеты
        </p>
      </div>

      {/* Модальное окно входа в админку */}
      {showAdminLogin && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="card max-w-md w-full">
            <div className="card-header">
              <h2 className="card-title text-center">Вход в админку</h2>
            </div>
            <div className="card-content space-y-4">
              <div>
                <label className="label">Пароль</label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Введите пароль"
                  onKeyPress={(e) => e.key === 'Enter' && handleAdminLogin()}
                />
              </div>
              <div className="flex gap-2">
                <Button onClick={handleAdminLogin} className="flex-1">
                  Войти
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => {
                    setShowAdminLogin(false)
                    setPassword("")
                  }}
                  className="flex-1"
                >
                  Отмена
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
