import { useState, useEffect } from "react"
import { Link } from "react-router-dom"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Badge } from "../components/ui/badge"
import { Plus, Edit, Trash2, Eye, Download, Upload, Database } from "lucide-react"
import { surveyStorage } from "../lib/storage"
import type { Survey } from "../lib/types"

export default function AdminSurveys() {
  const [surveys, setSurveys] = useState<Survey[]>([])

  useEffect(() => {
    console.log('AdminSurveys: Loading surveys...')
    const surveys = surveyStorage.getSurveys()
    console.log('AdminSurveys: Loaded surveys:', surveys)
    setSurveys(surveys)
  }, [])

  const handleDelete = (id: string) => {
    if (confirm("Вы уверены, что хотите удалить эту анкету?")) {
      surveyStorage.deleteSurvey(id)
      setSurveys(surveyStorage.getSurveys())
    }
  }

  const handleExport = (surveyId: string) => {
    const csvContent = surveyStorage.exportToCSV(surveyId)
    if (csvContent) {
      const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" })
      const link = document.createElement("a")
      const url = URL.createObjectURL(blob)
      link.setAttribute("href", url)
      link.setAttribute("download", `survey-${surveyId}-responses.csv`)
      link.style.visibility = "hidden"
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }

  const handleExportAll = () => {
    const jsonData = surveyStorage.exportAllData()
    const blob = new Blob([jsonData], { type: "application/json" })
    const link = document.createElement("a")
    const url = URL.createObjectURL(blob)
    link.setAttribute("href", url)
    link.setAttribute("download", `asrr-backup-${new Date().toISOString().split('T')[0]}.json`)
    link.style.visibility = "hidden"
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const handleImport = () => {
    const input = document.createElement("input")
    input.type = "file"
    input.accept = ".json"
    input.onchange = (e) => {
      const file = (e.target as HTMLInputElement).files?.[0]
      if (file) {
        const reader = new FileReader()
        reader.onload = (e) => {
          const content = e.target?.result as string
          if (surveyStorage.importData(content)) {
            setSurveys(surveyStorage.getSurveys())
            alert("Данные успешно импортированы!")
          }
        }
        reader.readAsText(file)
      }
    }
    input.click()
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Управление анкетами</h1>
            <p className="text-gray-600">Создавайте и управляйте анкетами</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" onClick={handleExportAll}>
              <Database className="w-4 h-4 mr-2" />
              Экспорт всех данных
            </Button>
            <Button variant="outline" onClick={handleImport}>
              <Upload className="w-4 h-4 mr-2" />
              Импорт данных
            </Button>
            <Link to="/admin/surveys/new">
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Создать анкету
              </Button>
            </Link>
          </div>
        </div>

        {surveys.length === 0 ? (
          <Card>
            <CardContent className="text-center py-12">
              <p className="text-gray-500 mb-4">Анкеты не найдены</p>
              <Link to="/admin/surveys/new">
                <Button>Создать первую анкету</Button>
              </Link>
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {surveys.map((survey) => {
              const responses = surveyStorage.getSurveyResponses(survey.id)
              return (
                <Card key={survey.id}>
                  <CardHeader>
                    <div className="flex justify-between items-start">
                      <div>
                        <CardTitle className="flex items-center gap-2">
                          {survey.title}
                          <Badge variant={survey.isActive ? "default" : "secondary"}>
                            {survey.isActive ? "Активна" : "Неактивна"}
                          </Badge>
                        </CardTitle>
                        <CardDescription>
                          Создана: {new Date(survey.createdAt).toLocaleDateString("ru-RU")}
                        </CardDescription>
                      </div>
                      <div className="flex gap-2">
                        <Link to={`/admin/surveys/${survey.id}/edit`}>
                          <Button variant="outline" size="sm">
                            <Edit className="w-4 h-4" />
                          </Button>
                        </Link>
                        <Link to={`/admin/responses/${survey.id}`}>
                          <Button variant="outline" size="sm">
                            <Eye className="w-4 h-4" />
                          </Button>
                        </Link>
                        {responses.length > 0 && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleExport(survey.id)}
                          >
                            <Download className="w-4 h-4" />
                          </Button>
                        )}
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(survey.id)}
                        >
                          <Trash2 className="w-4 h-4" />
                        </Button>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                      <div>
                        <span className="font-medium">Вопросов:</span> {survey.questions.length}
                      </div>
                      <div>
                        <span className="font-medium">Ответов:</span> {responses.length}
                      </div>
                      <div>
                        <span className="font-medium">Последний ответ:</span>{" "}
                        {responses.length > 0
                          ? new Date(responses[responses.length - 1].completedAt).toLocaleDateString("ru-RU")
                          : "Нет"}
                      </div>
                      <div>
                        <Link to={`/survey/${survey.id}`}>
                          <Button variant="link" size="sm">
                            Просмотреть анкету
                          </Button>
                        </Link>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        )}
      </div>
    </div>
  )
}
