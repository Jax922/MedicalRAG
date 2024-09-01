'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { ChatBotIcon } from '@/components/ui/icon';

function Portal() {
  const router = useRouter();
  const [showModal, setShowModal] = useState(false);
  const [selectedOption, setSelectedOption] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('zh'); // 默认普通话

  const handleNavigation = (path: string) => {
    const fullPath = `${path}&cantonese=${selectedLanguage === 'yue'}`;
    window.open(fullPath, '_blank'); // 在新窗口中打开 URL
  };

  const openModal = () => {
    setShowModal(true);
  };

  const closeModal = () => {
    setShowModal(false);
    setSelectedOption('');
  };

  const handleOptionSelect = (option: string) => {
    setSelectedOption(option);
    let url = `/older?prompting=true&non_input=true&state=${option}`;
    if (selectedLanguage === 'yue') {
      url += '&cantonese=true';
    } else {
      url += '&cantonese=false';
    }
    window.open(url, '_blank'); // 在新窗口中打开 URL
    closeModal();
  };

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language);
  };

  const chatbots = [
    {
      name: '机器人 1',
      url: '/older?prompting=false&non_input=true',
    },
    {
      name: '机器人 2',
      url: '/older?prompting=true&non_input=true',
    },
    {
      name: '机器人 3',
      url: '/older?doctor=true&non_input=true',
    }
  ];

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gradient-to-r from-blue-500 to-purple-600">
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-white">无输入框版本</h2>
        <span className="text-2xl font-bold text-white">请选择语言：</span>
        <select
          className="p-2 bg-white rounded-lg shadow-md text-2xl"
          value={selectedLanguage}
          onChange={(e) => handleLanguageChange(e.target.value)}
        >
          <option value="zh">普通话</option>
          <option value="yue">广东话</option>
        </select>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        {chatbots.map((chatbot, index) => (
          <div
            key={index}
            className="flex flex-col items-center justify-center p-8 bg-white rounded-lg shadow-lg hover:shadow-2xl transition-shadow duration-300 cursor-pointer"
            onClick={() => 
              {
                const isPrompting = index  === 1;
                isPrompting ? openModal() : handleNavigation(`${chatbot.url}`)
              }
            }
          >
            <ChatBotIcon className="text-6xl text-blue-500 mb-4" />
            <h2 className="text-2xl font-semibold text-gray-800">{chatbot.name}</h2>
          </div>
        ))}
      </div>

      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white p-8 rounded-lg shadow-lg w-full max-w-lg">
            <h2 className="text-4xl font-semibold mb-6">选择对话模式</h2>
            <div className="flex flex-col gap-4">
              <button
                className="py-3 px-6 bg-blue-500 text-white font-semibold text-4xl rounded-lg shadow-md hover:bg-blue-600 transition duration-300"
                onClick={() => handleOptionSelect('objective')}
              >
                主动型对话
              </button>
              <button
                className="py-3 px-6 bg-green-500 text-white font-semibold text-4xl rounded-lg shadow-md hover:bg-green-600 transition duration-300"
                onClick={() => handleOptionSelect('normal')}
              >
                被动型对话
              </button>
              <button
                className="py-3 px-6 bg-red-500 text-white font-semibold text-4xl rounded-lg shadow-md hover:bg-red-600 transition duration-300"
                onClick={closeModal}
              >
                关闭窗口
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Portal;