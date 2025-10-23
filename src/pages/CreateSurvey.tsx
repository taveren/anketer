import { useState } from "react"
import { useNavigate } from "react-router-dom"
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card"
import { Button } from "../components/ui/button"
import { Input } from "../components/ui/input"
import { Label } from "../components/ui/label"
import { Textarea } from "../components/ui/textarea"
import { Select } from "../components/ui/select"
import { Checkbox } from "../components/ui/checkbox"
import { ConditionForm } from "../components/survey/condition-form"
import { Plus, Trash2, Save } from "lucide-react"
import { surveyStorage } from "../lib/storage"
import type { Survey, Question } from "../lib/types"

export default function CreateSurvey() {
  const navigate = useNavigate()
  const [title, setTitle] = useState("")
  const [questions, setQuestions] = useState<Question[]>([])

  const addQuestion = () => {
    const newQuestion: Question = {
      id: `q${questions.length}`,
      text: "",
      type: "text",
      required: false,
      options: [],
      conditions: []
    }
    setQuestions([...questions, newQuestion])
  }

  const updateQuestion = (index: number, field: keyof Question, value: any) => {
    const newQuestions = [...questions]
    newQuestions[index] = {
      ...newQuestions[index],
      [field]: value,
    }
    setQuestions(newQuestions)
  }

  const removeQuestion = (index: number) => {
    setQuestions(questions.filter((_, i) => i !== index))
  }

  const addOption = (questionIndex: number) => {
    const newQuestions = [...questions]
    newQuestions[questionIndex].options = [
      ...(newQuestions[questionIndex].options || []),
      ""
    ]
    setQuestions(newQuestions)
  }

  const updateOption = (questionIndex: number, optionIndex: number, value: string) => {
    const newQuestions = [...questions]
    if (newQuestions[questionIndex].options) {
      newQuestions[questionIndex].options![optionIndex] = value
    }
    setQuestions(newQuestions)
  }

  const removeOption = (questionIndex: number, optionIndex: number) => {
    const newQuestions = [...questions]
    if (newQuestions[questionIndex].options) {
      newQuestions[questionIndex].options = newQuestions[questionIndex].options!.filter(
        (_, i) => i !== optionIndex
      )
    }
    setQuestions(newQuestions)
  }

  const handleSave = () => {
    if (!title.trim()) {
      alert("Введите название анкеты")
      return
    }

    if (questions.length === 0) {
      alert("Добавьте хотя бы один вопрос")
      return
    }

    const survey: Survey = {
      id: Date.now().toString(),
      title: title.trim(),
      questions,
      createdAt: new Date().toISOString(),
      isActive: true
    }

    const success = surveyStorage.saveSurvey(survey)
    if (success) {
      alert("Анкета успешно сохранена!")
      navigate("/admin")
    } else {
      alert("Ошибка сохранения анкеты. Попробуйте еще раз.")
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-4xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Создание анкеты</h1>
            <p className="text-gray-600">Заполните информацию об анкете</p>
          </div>
          <Button onClick={handleSave}>
            <Save className="w-4 h-4 mr-2" />
            Сохранить анкету
          </Button>
        </div>

        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Основная информация</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <Label htmlFor="title">Название анкеты</Label>
                <Input
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="Введите название анкеты"
                />
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="space-y-6">
          {questions.map((question, index) => (
            <Card key={index}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <CardTitle>Вопрос {index + 1}</CardTitle>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => removeQuestion(index)}
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label>Текст вопроса</Label>
                  <Textarea
                    value={question.text}
                    onChange={(e) => updateQuestion(index, "text", e.target.value)}
                    placeholder="Введите текст вопроса"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label>Тип вопроса</Label>
                    <Select
                      value={question.type}
                      onChange={(e) => updateQuestion(index, "type", e.target.value)}
                    >
                      <option value="text">Текстовый ответ</option>
                      <option value="number">Числовой ответ</option>
                      <option value="radio">Один из вариантов</option>
                      <option value="checkbox">Несколько вариантов</option>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id={`required-${index}`}
                      checked={question.required}
                      onCheckedChange={(checked) => updateQuestion(index, "required", checked)}
                    />
                    <Label htmlFor={`required-${index}`}>Обязательный вопрос</Label>
                  </div>
                </div>

                {(question.type === "radio" || question.type === "checkbox") && (
                  <div>
                    <div className="flex justify-between items-center mb-2">
                      <Label>Варианты ответов</Label>
                      <Button
                        type="button"
                        variant="outline"
                        size="sm"
                        onClick={() => addOption(index)}
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Добавить вариант
                      </Button>
                    </div>
                    <div className="space-y-2">
                      {question.options?.map((option, optionIndex) => (
                        <div key={optionIndex} className="flex gap-2">
                          <Input
                            value={option}
                            onChange={(e) => updateOption(index, optionIndex, e.target.value)}
                            placeholder={`Вариант ${optionIndex + 1}`}
                          />
                          <Button
                            type="button"
                            variant="outline"
                            size="sm"
                            onClick={() => removeOption(index, optionIndex)}
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                <div>
                  <Label>Условия показа вопроса</Label>
                  <ConditionForm
                    questions={questions.slice(0, index)}
                    conditions={question.conditions || []}
                    onConditionsChange={(conditions) => updateQuestion(index, "conditions", conditions)}
                  />
                </div>
              </CardContent>
            </Card>
          ))}

          <Button onClick={addQuestion} variant="outline" className="w-full">
            <Plus className="w-4 h-4 mr-2" />
            Добавить вопрос
          </Button>
        </div>
      </div>
    </div>
  )
}
