'use client';
import { useEffect, useRef, useState } from 'react';
import { Input, Button, Toast } from 'antd-mobile';
import { UpOutline, DownOutline } from 'antd-mobile-icons';
import Image from 'next/image';

const fakeBotReply = (msg: string) =>
  `您说的是「${msg}」，我建议多喝水，保持饮食清淡哦~ 🥗`;

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export default function DietPage() {
  const [recommendation, setRecommendation] = useState('');
  const [expanded, setExpanded] = useState(false);
  const [messages, setMessages] = useState<{ from: 'user' | 'bot'; text: string }[]>([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  const [location, setLocation] = useState('未知位置');

  const phone = typeof window !== 'undefined' ? localStorage.getItem('userPhone') || '' : '';

  const getReply = async (phoneNumber: string, message: string, location: string) => {
    try {
      const res = await fetch(`${API_BASE}/api/generate-reply`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone: phoneNumber,
          message: message,
          location: location
        })
      });
  
      const data = await res.json();
      if (data.reply) {
        return data.reply;
      } else {
        console.error('AI 回复失败：', data.error || '未知错误');
        return '抱歉，暂时无法生成建议，请稍后再试。';
      }
    } catch (error) {
      console.error('请求出错：', error);
      return '网络异常，请稍后重试。';
    }
  };
  

  useEffect(() => {
    setRecommendation('早餐：燕麦+鸡蛋\n午餐：番茄炒蛋+米饭番茄炒蛋+米饭番茄炒蛋+米饭番茄炒蛋+米饭番茄炒蛋+米饭\n晚餐：清蒸鱼+青菜番茄炒蛋+米饭番茄炒蛋+米饭番茄炒蛋+米饭');
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [messages]);

  const logMessage = async (message: string, sender: 'user' | 'bot') => {
    try {
      await fetch(`${API_BASE}/api/save-chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ phone, message, sender })
      });
    } catch (e) {
      console.error('保存聊天失败', e);
    }
  };

//   const handleSend = async () => {
//     const trimmed = input.trim();
//     if (!trimmed) return;

//     setMessages(prev => [...prev, { from: 'user', text: trimmed }]);
//     await logMessage(trimmed, 'user');
//     setInput('');

//     setTimeout(async () => {
//       const botReply = fakeBotReply(trimmed);
//       setMessages(prev => [...prev, { from: 'bot', text: botReply }]);
//       await logMessage(botReply, 'bot');
//     }, 600);
//   };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed) return;
  
    setMessages(prev => [...prev, { from: 'user', text: trimmed }]);
    await logMessage(trimmed, 'user');
    setInput('');
  
    const reply = await getReply(phone, trimmed, location);
    setMessages(prev => [...prev, { from: 'bot', text: reply }]);
    await logMessage(reply, 'bot');
  };

  useEffect(() => {
    const phone = localStorage.getItem('userPhone');
    if (phone) {
      fetch(`${API_BASE}/api/log-action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          phone,
          action: 'enter_diet_page',
          detail: '进入饮食推荐页面'
        })
      });
    }
  }, []);

  const getUserLocation = async (): Promise<string> => {
    return new Promise((resolve) => {
      if (!navigator.geolocation) {
        resolve('未知位置');
        return;
      }
  
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const { latitude, longitude } = position.coords;
  
          // 使用高德地图 API、百度、腾讯、或者 OpenStreetMap
          const res = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
          const data = await res.json();
          const city = data.address?.city || data.address?.town || data.address?.state || '未知城市';
          resolve(city);
        },
        () => resolve('未知位置'),
        { timeout: 5000 }
      );
    });
  };
  
  

    useEffect(() => {
    getUserLocation().then(setLocation);
    }, []);


  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* 顶部推荐卡片 */}
      <div
        className={`sticky top-0 z-10 bg-white shadow text-gray-800 transition-all duration-300 ${
          expanded ? 'max-h-[1000px]' : 'max-h-[180px] overflow-hidden'
        }`}
      >
        <div className="p-4 text-2xl">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold">🥗 今日饮食推荐</span>
            <button
              className="text-base text-blue-500 flex items-center gap-1"
              onClick={() => setExpanded(!expanded)}
            >
              {expanded ? (
                <>
                  收起 <UpOutline />
                </>
              ) : (
                <>
                  展开 <DownOutline />
                </>
              )}
            </button>
          </div>
          <pre className="whitespace-pre-wrap leading-relaxed text-xl">
            {recommendation}
          </pre>
        </div>
      </div>

      {/* 对话区域 */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto px-4 py-2 space-y-3 pt-2"
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={`flex ${msg.from === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.from === 'bot' && (
              <Image
                src="/eat-helth.png"
                alt="bot"
                width={32}
                height={32}
                unoptimized
                className="mr-2 rounded-full w-[32px] h-[32px] object-cover"
              />
            )}
            <div
              className={`rounded-lg px-4 py-2 max-w-[70%] text-xl ${
                msg.from === 'user'
                  ? 'bg-green-100 text-right'
                  : 'bg-white text-left shadow'
              }`}
            >
              {msg.text}
            </div>
          </div>
        ))}
      </div>

      {/* 输入框区域 */}
      <div className="p-3 border-t bg-white flex items-center gap-2">
        <Input
          className="flex-1 text-lg"
          placeholder="请输入您今天吃了什么或心情..."
          value={input}
          onChange={val => setInput(val)}
          clearable
        />
        <Button color="primary" onClick={handleSend} className="text-2xl">
          发送
        </Button>
      </div>
    </div>
  );
}