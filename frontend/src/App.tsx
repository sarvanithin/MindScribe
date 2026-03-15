import { BrowserRouter, Routes, Route, NavLink, Navigate } from 'react-router-dom'
import { Brain, FileText, LayoutDashboard, FlaskConical } from 'lucide-react'
import ScreeningPage from './pages/ScreeningPage'
import NoteGeneratorPage from './pages/NoteGeneratorPage'
import DashboardPage from './pages/DashboardPage'

export default function App() {
    return (
        <BrowserRouter>
            <div className="app-shell">
                <aside className="sidebar">
                    <div className="sidebar-logo">
                        <h1>MindScribe</h1>
                        <p>Clinical AI Assistant</p>
                    </div>

                    <nav className="sidebar-nav">
                        <NavLink to="/screening" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                            <Brain size={18} />
                            Screening
                        </NavLink>
                        <NavLink to="/notes" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                            <FileText size={18} />
                            Note Generator
                        </NavLink>
                        <NavLink to="/dashboard" className={({ isActive }) => `nav-link${isActive ? ' active' : ''}`}>
                            <LayoutDashboard size={18} />
                            Dashboard
                        </NavLink>
                    </nav>

                    <div className="sidebar-footer">
                        <div className="demo-badge">
                            <FlaskConical size={11} />
                            Demo Mode
                        </div>
                        <p className="text-xs text-muted mt-2" style={{ lineHeight: 1.5 }}>
                            No patient data stored. For research &amp; portfolio purposes only.
                        </p>
                    </div>
                </aside>

                <main className="main-content">
                    <Routes>
                        <Route path="/" element={<Navigate to="/screening" replace />} />
                        <Route path="/screening" element={<ScreeningPage />} />
                        <Route path="/notes" element={<NoteGeneratorPage />} />
                        <Route path="/dashboard" element={<DashboardPage />} />
                    </Routes>
                </main>
            </div>
        </BrowserRouter>
    )
}
