'use client';

import { useAuth } from '@/components/auth/AuthProvider';
import LoginPage from '@/components/auth/LoginPage';
import HomePage from '@/components/home/HomePage';

export default function Page() {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-emerald-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return user ? <HomePage /> : <LoginPage />;
}