import { useState, useEffect } from "react"
import { useParams, useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { QuestionCard } from "../components/survey/question-card"
import { surveyStorage } from "../lib/storage"
import { shouldShowQuestion } from "../lib/survey-logic"
import type { Survey, Response } from "../lib/types"
import { ArrowLeft, CheckCircle } from "lucide-react"

export default function TakeSurvey() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [survey, setSurvey] = useState<Survey | null>(null)
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [answers, setAnswers] = useState<Record<string, any>>({})
  const [isCompleted, setIsCompleted] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!id) return

    const surveyData = surveyStorage.getSurvey(id)
    if (!surveyData) {
      alert("Анкета не найдена")
      navigate("/")
      return
    }

    setSurvey(surveyData)
    setLoading(false)
  }, [id, navigate])

  const visibleQuestions = survey?.questions.filter((question) => {
    return shouldShowQuestion(question, answers)
  }) || []

  const currentQuestion = visibleQuestions[currentQuestionIndex]
  const progress = visibleQuestions.length > 0 ? ((currentQuestionIndex + 1) / visibleQuestions.length) * 100 : 0

  // Отладочная информация
  console.log('Debug:', {
    currentQuestionIndex,
    visibleQuestionsLength: visibleQuestions.length,
    isLastQuestion: currentQuestionIndex === visibleQuestions.length - 1,
    buttonText: currentQuestionIndex === visibleQuestions.length - 1 ? "Завершить" : "Далее"
  })

  const handleAnswerChange = (questionId: string, value: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }))
  }

  // Сброс индекса если он выходит за границы видимых вопросов
  useEffect(() => {
    if (currentQuestionIndex >= visibleQuestions.length && visibleQuestions.length > 0) {
      setCurrentQuestionIndex(visibleQuestions.length - 1)
    }
  }, [visibleQuestions.length, currentQuestionIndex])

  const handleNext = () => {
    if (currentQuestionIndex < visibleQuestions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1)
    } else {
      handleSubmit()
    }
  }

  const handlePrevious = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1)
    }
  }

  const handleSubmit = () => {
    if (!survey) return

    const response: Response = {
      id: `response_${Date.now()}`,
      surveyId: survey.id,
      answers,
      completedAt: new Date().toISOString()
    }

    surveyStorage.saveResponse(response)
    setIsCompleted(true)
  }

  const isCurrentQuestionValid = () => {
    if (!currentQuestion) return true
    if (!currentQuestion.required) return true
    
    const answer = answers[currentQuestion.id]
    if (currentQuestion.type === "checkbox") {
      return Array.isArray(answer) && answer.length > 0
    }
    return answer !== undefined && answer !== "" && answer !== null
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка анкеты...</p>
        </div>
      </div>
    )
  }

  if (!survey) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Анкета не найдена</h2>
            <Button onClick={() => navigate("/")} className="w-full">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Вернуться на главную
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  if (isCompleted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="p-6 text-center">
            <CheckCircle className="w-16 h-16 text-green-600 mx-auto mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800 mb-2">Спасибо!</h2>
            <p className="text-gray-600 mb-6">Ваши ответы успешно сохранены</p>
            <Button onClick={() => navigate("/")} className="w-full">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Вернуться на главную
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-2xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <Button
              variant="outline"
              onClick={() => navigate("/")}
              className="mb-4"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Назад
            </Button>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">{survey.title}</h1>
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>Вопрос {currentQuestionIndex + 1} из {visibleQuestions.length}</span>
              <span>{Math.round(progress)}% завершено</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>

          {/* Question */}
          {currentQuestion && (
            <Card className="mb-6">
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  {currentQuestion.text}
                  {currentQuestion.required && <span className="text-red-500">*</span>}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <QuestionCard
                  question={currentQuestion}
                  value={answers[currentQuestion.id]}
                  onChange={(value) => handleAnswerChange(currentQuestion.id, value)}
                />
              </CardContent>
            </Card>
          )}

          {/* Navigation */}
          <div className="flex justify-between">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentQuestionIndex === 0}
            >
              Назад
            </Button>
            
            <Button
              onClick={handleNext}
              disabled={!isCurrentQuestionValid()}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {currentQuestionIndex === visibleQuestions.length - 1 ? "Завершить" : "Далее"}
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}
