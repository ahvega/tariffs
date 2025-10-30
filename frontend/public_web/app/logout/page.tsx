'use client';

import { useEffect } from 'react';
import { signOut } from 'next-auth/react';
import { useRouter } from 'next/navigation';

export default function LogoutPage() {
  const router = useRouter();

  useEffect(() => {
    const handleLogout = async () => {
      // Clear session storage (quote data, etc.)
      sessionStorage.clear();

      // Sign out and redirect to login
      await signOut({
        redirect: false,
        callbackUrl: '/login'
      });

      // Redirect to login page
      router.push('/login');
    };

    handleLogout();
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        <p className="mt-4 text-gray-600 dark:text-gray-400">Cerrando sesión...</p>
      </div>
    </div>
  );
}
