import React from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authService } from '../services/auth';

/**
 * ProtectedRoute - Synchronous token check.
 * 
 * We intentionally use a simple localStorage check here rather than calling
 * /api/v1/auth/me on every navigation because:
 * 1. Calling /me on every render causes redirect loops if the backend
 *    momentarily returns 401 (e.g. during server reload, network hiccup).
 * 2. Token validity is enforced implicitly by the backend on every API request.
 * 3. If any API call returns 401, the api service logs the user out globally.
 */
export const ProtectedRoute = ({ children }) => {
    const location = useLocation();

    if (!authService.isAuthenticated()) {
        return <Navigate to="/auth" state={{ from: location }} replace />;
    }

    return children;
};
