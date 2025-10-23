import { BrowserRouter as Router, Routes, Route } from "react-router-dom"
import Home from "./pages/Home"
import AdminSurveys from "./pages/AdminSurveys"
import CreateSurvey from "./pages/CreateSurvey"
import TakeSurvey from "./pages/TakeSurvey"
import SurveyList from "./pages/SurveyList"
import Responses from "./pages/Responses"

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/admin" element={<AdminSurveys />} />
        <Route path="/admin/surveys/new" element={<CreateSurvey />} />
        <Route path="/admin/surveys/:id/edit" element={<CreateSurvey />} />
        <Route path="/admin/responses/:id" element={<Responses />} />
        <Route path="/survey" element={<SurveyList />} />
        <Route path="/survey/:id" element={<TakeSurvey />} />
      </Routes>
    </Router>
  )
}

export default App
