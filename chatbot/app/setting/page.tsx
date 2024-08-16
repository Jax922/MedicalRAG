"use client";
import fs from "fs";
import path from "path";
import { use, useEffect, useState } from "react";

type Setting = {
  option: string;
  keywords: string;
};


export default function Home() {

  const [selectedOption, setSelectedOption] = useState("keyword");
  const [keywords, setKeywords] = useState([]);

  useEffect(() => {
    async function fetchSettings() {
      try {
        const response = await fetch('/api/setting', {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        if (!response.ok) {
          throw new Error('网络响应不是 OK');
        }
        const data = await response.json();
        setSelectedOption(data.option || 'keyword');
        setKeywords(data.keywords || []);
      } catch (error) {
        // setError(error.message);
      } finally {
        // setLoading(false);
      }
    }
    fetchSettings();
  }, []); 



  const handleOptionChange = (event: any) => {
    setSelectedOption(event.target.value);
  };

  const handleKeywordsChange = (event: any) => {
    setKeywords(event.target.value);
  };

  const handleUpdateKeywords = () => {
    fetch('/api/setting', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        option: selectedOption,
        keywords: keywords,
      }),
    });
  };

  return (
    <main className="p-6 bg-gray-100 min-h-screen">
      <div className="sticky top-0 w-full bg-white shadow-md">
        <h2 className="text-2xl font-bold text-center p-4">
          问诊陪伴机器人 - 设置页面
        </h2>
      </div>
      <div className="space-y-4 mt-6">
        <div className="flex items-center space-x-4">
          <input
            type="radio"
            id="keyword"
            name="rag"
            value="keyword"
            checked={selectedOption === "keyword"}
            onChange={handleOptionChange}
            className="form-radio"
          />
          <label htmlFor="keyword" className="text-xl">
            关键词触发RAG
          </label>
        </div>
        <div className="flex items-center space-x-4">
          <input
            type="radio"
            id="all"
            name="rag"
            value="all"
            checked={selectedOption === "all"}
            onChange={handleOptionChange}
            className="form-radio"
          />
          <label htmlFor="all" className="text-xl">
            全部触发RAG
          </label>
        </div>
        <div className="flex items-center space-x-4">
          <input
            type="radio"
            id="none"
            name="rag"
            value="none"
            checked={selectedOption === "none"}
            onChange={handleOptionChange}
            className="form-radio"
          />
          <label htmlFor="none" className="text-xl">
            全部不触发RAG
          </label>
        </div>
        <div className="text-xl">
          <label htmlFor="keywords" className="block mb-2">触发关键词列表：</label>
          <textarea
            id="keywords"
            value={keywords}
            onChange={handleKeywordsChange}
            className="w-full p-2 border rounded-lg bg-white"
            rows="6"
            placeholder="请输入触发关键词，用逗号分隔"
          />
          <button
            onClick={handleUpdateKeywords}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            更新
          </button>
        </div>
      </div>
    </main>
  );
}
