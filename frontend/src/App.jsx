import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Home } from './pages/Home';
import { Analytics } from './pages/Analytics';
import { Auth } from './pages/Auth';
import { Profile } from './pages/Profile';
import Chat from './pages/Chat';
import HistoryPage from './pages/History';
import LiveMetrics from './pages/LiveMetrics';
import { Layout } from './components/layout/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';

function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/auth" element={<Auth />} />
                <Route path="*" element={
                    <Layout>
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/chat" element={
                                <ProtectedRoute>
                                    <Chat />
                                </ProtectedRoute>
                            } />
                            <Route path="/history" element={
                                <ProtectedRoute>
                                    <HistoryPage />
                                </ProtectedRoute>
                            } />
                            <Route path="/analytics" element={
                                <ProtectedRoute>
                                    <Analytics />
                                </ProtectedRoute>
                            } />
                            <Route path="/live-metrics" element={
                                <ProtectedRoute>
                                    <LiveMetrics />
                                </ProtectedRoute>
                            } />
                            <Route path="/profile" element={
                                <ProtectedRoute>
                                    <Profile />
                                </ProtectedRoute>
                            } />
                        </Routes>
                    </Layout>
                } />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
