

import { Message } from '@/lib/types';
import OpenAI from "openai";
import SYSTEM_PROMPT from "@/lib/prompting";

// 本地化，基于session Storage, 存储bot和user的msg
export function saveMessage(msg: Message) {
    const messages = JSON.parse(sessionStorage.getItem('messages') || '[]');
    messages.push(msg);
    sessionStorage.setItem('messages', JSON.stringify(messages));
}

export function getMessages(): Message[] {
    return JSON.parse(sessionStorage.getItem('messages') || '[]');
}


export async function fetchMessage(messages: Message[]): Promise<Message> {
    try {
        const openai = new OpenAI({ 
            apiKey: "sk-D4YRkSe0WYNVycYhuLRsxVK8MjA9Uu6K49bwQQyAqjaejwUN",
            baseURL: "https://api.chatanywhere.tech/v1",
            dangerouslyAllowBrowser: true,
        });
        const formattedMessages = [
          { role: 'system', content: SYSTEM_PROMPT },
          ...messages.map(msg => ({
            role: msg.type === 'user' ? 'user' : 'assistant',
            content: msg.content
          }))
        ];
    
        const response = await openai.chat.completions.create({
          model: "gpt-3.5-turbo",
          messages: formattedMessages,
          temperature: 0.7,
        });



    
        const botResponse = response.choices[0].message.content;
        console.log('botResponse:', botResponse);
    
        const botMessage: Message = {
          id: String(Date.now()),
          type: 'bot',
          content: botResponse
        };
        return botMessage;
    
      } catch (error) {
        console.error("Error fetching message:", error);
        throw new Error('Failed to fetch message from LLM.');
      }
}

export async function* fetchMessageStream(messages: Message[]): AsyncIterable<string> {
    try {
        const openai = new OpenAI({
            apiKey: "sk-D4YRkSe0WYNVycYhuLRsxVK8MjA9Uu6K49bwQQyAqjaejwUN",
            baseURL: "https://api.chatanywhere.tech/v1",
            dangerouslyAllowBrowser: true,
        });

        const formattedMessages = [
            { role: 'system', content: SYSTEM_PROMPT },
            ...messages.map(msg => ({
                role: msg.type === 'user' ? 'user' : 'assistant',
                content: msg.content
            }))
        ];

        const response = await fetch("https://api.chatanywhere.tech/v1/completions", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${openai.apiKey}`
            },
            body: JSON.stringify({
                model: "gpt-3.5-turbo",
                messages: formattedMessages,
                temperature: 0.7,
                stream: true // 启用流式传输
            })
        });

        if (!response.body) {
            throw new Error('No response body.');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let done = false;

        while (!done) {
            const { value, done: doneReading } = await reader.read();
            done = doneReading;
            const chunk = decoder.decode(value, { stream: true });
            yield chunk;
        }

    } catch (error) {
        console.error("Error fetching message:", error);
        throw new Error('Failed to fetch message from LLM.');
    }
}

// // fetch msg from dify (streaming)
// export async function* fetchMessageStreamDify(messages: Message[]): AsyncIterable<string> {
//     try {
//         const response = await fetch('/api/dify', {
//           method: 'POST',
//           headers: {
//             'Content-Type': 'application/json',
//           },
//           body: JSON.stringify({
//             query: messages[messages.length - 1].content,
//             response_mode: 'streaming',
//             conversation_id: '',
//             user: 'abc-123',
//             inputs: {},
//           }),
//         });
  
//         if (!response.ok) {
//           throw new Error('Network response was not ok');
//         }
  
//         const reader = response.body?.getReader();
//         const decoder = new TextDecoder('utf-8');
//         let result = '';
  
//         while (true) {
//           const { done, value } = await reader.read();
//           if (done) break;
//           result += decoder.decode(value, { stream: true });
//           return result;
//         }  
//       } catch (error) {
//         console.error('Error fetching data:', error);
//       }
// }

// fetch msg from dify (streaming)
export async function* fetchMessageStreamDify(messages: Message[]): AsyncIterable<string> {
    try {
        const response = await fetch('/api/dify', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: messages[messages.length - 1].content,
                response_mode: 'streaming',
                conversation_id: '',
                user: 'abc-123',
                inputs: {},
            }),
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });

            const parts = buffer.split('data: ');
            for (let i = 0; i < parts.length - 1; i++) {
                const chunk = parts[i].trim();
                if (chunk) {
                    console.log('chunk:', chunk);
                    const chunkOBJ = JSON.parse(chunk);
                    if (chunkOBJ['answer']) {
                        yield chunkOBJ['answer'];
                    }   
                }
            }
            buffer = parts[parts.length - 1];
        }
    } catch (error) {
        console.error('Error in fetchMessageStreamDify:', error);
    }
}