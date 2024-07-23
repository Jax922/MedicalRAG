'use server';

// fetch msg from LLM
// openAI API
import type { NextApiRequest, NextApiResponse } from 'next';
import OpenAI from "openai";
import SYSTEM_PROMPT from "@/lib/prompting";
import { Message } from '@/lib/types';


const openai = new OpenAI({ 
    apiKey: "sk-D4YRkSe0WYNVycYhuLRsxVK8MjA9Uu6K49bwQQyAqjaejwUN",
    baseURL: "https://api.chatanywhere.tech/v1"
});

export default async function POST(req: NextApiRequest, res: NextApiResponse) {
    console.log('req:', req);
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }
  
    const { messages }: { messages: Message[] } = req.body;
  
    try {
      const formattedMessages = [
        { role: 'system', content: SYSTEM_PROMPT },
        ...messages.map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }))
      ];
  
      const response = await openai.chat.completions.create({
        model: "gpt-4o-mini",
        messages: formattedMessages,
        temperature: 0.7,
      });
  
      const botResponse = response.choices[0].message.content;
  
      const botMessage: Message = {
        id: String(Date.now()),
        type: 'bot',
        content: botResponse,
      };
  
      res.status(200).json(botMessage);
    } catch (error) {
      console.error("Error fetching message:", error);
      res.status(500).json({ error: 'Failed to fetch message from LLM.' });
    }
  }
