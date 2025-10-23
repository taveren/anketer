import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { ArrowLeft, Download, Eye } from "lucide-react"
import { surveyStorage } from "../lib/storage"
import type { Survey, Response } from "../lib/types"

export default function Responses() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [survey, setSurvey] = useState<Survey | null>(null)
  const [responses, setResponses] = useState<Response[]>([])
  const [selectedResponse, setSelectedResponse] = useState<Response | null>(null)

  useEffect(() => {
    if (id) {
      const foundSurvey = surveyStorage.getSurvey(id)
      if (foundSurvey) {
        setSurvey(foundSurvey)
        setResponses(surveyStorage.getSurveyResponses(id))
      } else {
        navigate("/admin")
      }
    }
  }, [id, navigate])

  const handleExport = () => {
    const csvContent = surveyStorage.exportToCSV(id!)
    if (csvContent) {
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      const url = URL.createObjectURL(blob)
      link.setAttribute("href", url)
      link.setAttribute("download", `survey-${id}-responses.csv`)
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  if (!survey) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-4">Анкета не найдена</h1>
          <Button onClick={() => navigate("/admin")}>
            Вернуться в админку
          </Button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="outline" onClick={() => navigate("/admin")}>
            <ArrowLeft className="w-4 h-4 mr-2" />
            Назад
          </Button>
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900">Ответы на анкету</h1>
            <p className="text-gray-600">{survey.title}</p>
          </div>
          {responses.length > 0 && (
            <Button onClick={handleExport}>
              <Download className="w-4 h-4 mr-2" />
              Экспорт в CSV
            </Button>
          )}
        </div>

        {responses.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-gray-500 mb-4">Ответов пока нет</p>
              <p className="text-sm text-gray-400">
                Ответы появятся после того, как пользователи заполнят анкету
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {responses.map((response) => (
              <Card key={response.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle className="text-lg">
                        Ответ #{response.id.slice(-6)}
                      </CardTitle>
                      <p className="text-sm text-gray-600">
                        Заполнен: {new Date(response.completedAt).toLocaleString("ru-RU")}
                      </p>
                    </div>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedResponse(
                        selectedResponse?.id === response.id ? null : response
                      )}
                    >
                      <Eye className="w-4 h-4" />
                    </Button>
                  </div>
                </CardHeader>
                
                {selectedResponse?.id === response.id && (
                  <CardContent>
                    <div className="space-y-4">
                      {survey.questions.map((question) => {
                        const answer = response.answers[question.id]
                        return (
                          <div key={question.id} className="border-l-4 border-blue-200 pl-4">
                            <h4 className="font-medium text-gray-900 mb-1">
                              {question.text}
                              {question.required && <span className="text-red-500 ml-1">*</span>}
                            </h4>
                            <p className="text-gray-700">
                              {Array.isArray(answer) 
                                ? answer.join(", ") 
                                : answer || "Не отвечено"
                              }
                            </p>
                          </div>
                        )
                      })}
                    </div>
                  </CardContent>
                )}
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
