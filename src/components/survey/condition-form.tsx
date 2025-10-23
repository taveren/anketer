import { Button } from "../ui/button"
import { Input } from "../ui/input"
import { Select } from "../ui/select"
import { Trash2 } from "lucide-react"
import type { Condition, Question } from "../../lib/types"

interface ConditionFormProps {
  questions: Question[]
  conditions: Condition[]
  onConditionsChange: (conditions: Condition[]) => void
}

export function ConditionForm({ questions, conditions, onConditionsChange }: ConditionFormProps) {
  const addCondition = () => {
    onConditionsChange([
      ...conditions,
      {
        targetId: "",
        operator: "equals",
        value: "",
      },
    ])
  }

  const updateCondition = (index: number, field: keyof Condition, value: string) => {
    const newConditions = [...conditions]
    newConditions[index] = {
      ...newConditions[index],
      [field]: value,
    }
    onConditionsChange(newConditions)
  }

  const removeCondition = (index: number) => {
    onConditionsChange(conditions.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-4">
      {conditions.map((condition, index) => (
        <div key={index} className="border p-4 rounded space-y-2">
          <div className="flex gap-2">
            <Select
              value={condition.targetId}
              onChange={(e) => updateCondition(index, "targetId", e.target.value)}
            >
              <option value="">Выберите вопрос</option>
              {questions.map((q) => (
                <option key={q.id} value={q.id}>
                  {q.text}
                </option>
              ))}
            </Select>

            <Select
              value={condition.operator}
              onChange={(e) => updateCondition(index, "operator", e.target.value)}
            >
              <option value="equals">Равно</option>
              <option value="not_equals">Не равно</option>
              <option value="contains">Содержит</option>
              <option value="greater_than">Больше</option>
              <option value="less_than">Меньше</option>
            </Select>

            <Input
              value={condition.value}
              onChange={(e) => updateCondition(index, "value", e.target.value)}
              placeholder="Значение"
            />

            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={() => removeCondition(index)}
            >
              <Trash2 className="w-4 h-4" />
            </Button>
          </div>
        </div>
      ))}

      <Button type="button" variant="outline" size="sm" onClick={addCondition}>
        Добавить условие
      </Button>
    </div>
  )
}
