import { Navigate, Route, Routes } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute.jsx';
import MainLayout from './layouts/MainLayout.jsx';
import ActivitiesPage from './pages/ActivitiesPage.jsx';
import HistoryPage from './pages/HistoryPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import ResultPage from './pages/ResultPage.jsx';
import RoomsPage from './pages/RoomsPage.jsx';
import StudentDashboardPage from './pages/StudentDashboardPage.jsx';
import TestPage from './pages/TestPage.jsx';
import { useAuth } from './store/auth-store.jsx';

const HomeRedirect = () => {
  const { user } = useAuth();
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return <Navigate to="/student" replace />;
};

const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />

      <Route
        path="/student"
        element={
          <ProtectedRoute roles={['STUDENT']}>
            <MainLayout>
              <StudentDashboardPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/tests/:testId"
        element={
          <ProtectedRoute roles={['STUDENT']}>
            <MainLayout>
              <TestPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/results/:attemptId"
        element={
          <ProtectedRoute roles={['STUDENT']}>
            <MainLayout>
              <ResultPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/history"
        element={
          <ProtectedRoute roles={['STUDENT']}>
            <MainLayout>
              <HistoryPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/activities"
        element={
          <ProtectedRoute roles={['STUDENT']}>
            <MainLayout>
              <ActivitiesPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/rooms"
        element={
          <ProtectedRoute roles={['STUDENT']}>
            <MainLayout>
              <RoomsPage />
            </MainLayout>
          </ProtectedRoute>
        }
      />

      <Route path="/" element={<HomeRedirect />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
