'use client';
import { useEffect, useState } from 'react';
import LoginForm from '@/components/login';
import BasicInfo from '@/components/baseInfo';
import { API_BASE } from '@/lib/config';
import { useRouter } from 'next/navigation'; // 注意：app 目录是 next/navigation，pages 是 next/router


export default function Home() {
  const [phone, setPhone] = useState('');
  const [isNew, setIsNew] = useState(false);

  const router = useRouter(); // ✅ 使用 useRouter 获取路由对象
  // ✅ 检查是否已登录
  useEffect(() => {
    const savedPhone = localStorage.getItem('userPhone');
    if (savedPhone) {
        router.push('/diet'); // ✅ 更推荐的方式
    }
  }, []);

  const handleLogin = async (phoneNumber: string) => {
    const res = await fetch(`${API_BASE}/api/check-user`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ phone: phoneNumber })
    });
    const data = await res.json();
    setPhone(phoneNumber);
    setIsNew(data.isNewUser);

    if (!data.isNewUser) {
      localStorage.setItem('userPhone', phoneNumber);
      router.push('/diet'); // ✅ 更推荐的方式
    }
  };

  // ✅ 登录/信息补充完成后处理
  const handleComplete = () => {
    localStorage.setItem('userPhone', phone);
    router.push('/diet'); // ✅ 更推荐的方式
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-gray-100 px-4">
      <div className="w-full max-w-md bg-white p-6 rounded shadow">
        {isNew ? <BasicInfo phone={phone} onSubmit={handleComplete} /> : <LoginForm onLogin={handleLogin} />}
      </div>
    </main>
  );
}
