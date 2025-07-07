"use client"

import { useState, useEffect, createContext, useContext } from 'react';
import { apiClient, User, LoginRequest } from '@/lib/api';
import React from 'react';

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    login: (credentials: LoginRequest) => Promise<{ success: boolean; error?: string }>;
    logout: () => void;
    refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    const isAuthenticated = !!user;

    const login = async (credentials: LoginRequest) => {
        try {
            const response = await apiClient.login(credentials);

            if (response.error) {
                return { success: false, error: response.error };
            }

            if (response.data) {
                // Get user info after successful login
                const userResponse = await apiClient.getCurrentUser();
                if (userResponse.data) {
                    setUser(userResponse.data);
                }
                return { success: true };
            }

            return { success: false, error: 'Login failed' };
        } catch (error) {
            return {
                success: false,
                error: error instanceof Error ? error.message : 'Login failed'
            };
        }
    };

    const logout = () => {
        apiClient.logout();
        setUser(null);
    };

    const refreshUser = async () => {
        try {
            const response = await apiClient.getCurrentUser();
            if (response.data) {
                setUser(response.data);
            } else {
                setUser(null);
            }
        } catch (error) {
            setUser(null);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        // Check if user is already logged in on app start
        refreshUser();
    }, []);

    const value: AuthContextType = {
        user,
        isLoading,
        isAuthenticated,
        login,
        logout,
        refreshUser,
    };

    return React.createElement(AuthContext.Provider, { value }, children);
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
} 