'use client';
import { useState } from 'react';
import LoginForm from '@/components/login';
import BasicInfo from '@/components/baseInfo';

export default function Home() {
  const [phone, setPhone] = useState('');
  const [isNew, setIsNew] = useState(false);

  const handleLogin = async (phoneNumber: string) => {
    const res = await fetch('/api/check-user', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: phoneNumber })
    });
    const data = await res.json();
    setPhone(phoneNumber);
    setIsNew(data.isNewUser);
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md bg-white p-6 rounded shadow">
        {isNew ? <BasicInfo phone={phone} onSubmit={() => window.location.href='/home'} /> : <LoginForm onLogin={handleLogin} />}
      </div>
    </main>
  );
}