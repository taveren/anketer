import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { FileText, ArrowLeft } from "lucide-react"
import { surveyStorage } from "../lib/storage"
import type { Survey } from "../lib/types"

export default function SurveyList() {
  const [surveys, setSurveys] = useState<Survey[]>([])

  useEffect(() => {
    setSurveys(surveyStorage.getSurveys().filter(survey => survey.isActive))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Link to="/">
            <Button variant="outline">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Доступные анкеты</h1>
            <p className="text-gray-600">Выберите анкету для заполнения</p>
          </div>
        </div>

        {surveys.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <FileText className="w-12 h-12 mx-auto mb-4 text-gray-400" />
              <p className="text-gray-500 mb-4">Нет доступных анкет</p>
              <p className="text-sm text-gray-400">
                Обратитесь к администратору для получения доступа к анкетам
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {surveys.map((survey) => (
              <Card key={survey.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="flex items-center gap-2">
                        {survey.title}
                        <Badge variant="default">Активна</Badge>
                      </CardTitle>
                      <CardDescription>
                        Создана: {new Date(survey.createdAt).toLocaleDateString("ru-RU")}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between items-center">
                    <div className="text-sm text-gray-600">
                      Вопросов: {survey.questions.length}
                    </div>
                    <Link to={`/survey/${survey.id}`}>
                      <Button>
                        <FileText className="w-4 h-4 mr-2" />
                        Заполнить анкету
                      </Button>
                    </Link>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}


