'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { ChatBotIcon } from '@/components/ui/icon';

function Portal() {
  const router = useRouter();

  const handleNavigation = (path: string) => {
    router.push(path);
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600">
      {/* <h1 className="text-5xl font-bold text-white mb-8"></h1> */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {['机器人 1', '机器人 2', '机器人 3'].map((chatbot, index) => (
          <div
            key={index}
            className="flex flex-col items-center justify-center p-8 bg-white rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300 cursor-pointer"
            onClick={() => handleNavigation(`/chatbot${index + 1}`)}
          >
            <ChatBotIcon className="text-6xl text-blue-500 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800">{chatbot}</h2>
          </div>
        ))}
      </div>
    </div>
  );
}

export default Portal;
