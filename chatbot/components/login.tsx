'use client';
import { useState } from 'react';

export default function LoginForm({ onLogin }: { onLogin: (phone: string) => void }) {
  const [phone, setPhone] = useState('');

  const handleLogin = () => {
    if (phone) onLogin(phone);
  };

  return (
    <div className="space-y-4">
    {/* 加入logo ： eat-helth.png */}
        <img src="/eat-helth.png" alt="Logo" className="w-24 h-24 mx-auto" />
      <h2 className="text-2xl font-bold text-center">欢迎使用智能饮食助手</h2>
      <input
        type="tel"
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        placeholder="手机号"
        className="w-full border border-gray-300 rounded px-4 py-2 text-2xl"
      />
      <button
        onClick={handleLogin}
        className="w-full bg-green-600 text-white py-2 rounded text-2xl"
      >
        登录
      </button>
    </div>
  );
}