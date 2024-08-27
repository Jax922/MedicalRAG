

import { Message } from '@/lib/types';
import OpenAI from "openai";
import SYSTEM_PROMPT from "@/lib/prompting";
import { toReference } from "@/lib/utils";

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

// fetch msg from local with rag 
// http:localhost:8000/single_agent
// request:
// {
//     "user_query": "string",
//     "history": [
//       {
//}
//     ]
//   }
// response:
// "string" (success)
// 
// or error:
// {
//   "detail": [
//     {
//       "loc": [
//         "string",
//         0
//       ],
//       "msg": "string",
//       "type": "string"
//     }
//   ]
// }
export async function fetchMessageLocal(messages: Message[], language?: string, mode?: Object): Promise<Message> {
    try {
        const response = await fetch("http://10.37.81.23:8000/single_agent", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_query: messages[messages.length - 1].content,
                // history: messages.map(msg => msg.content),
                history: messages.map(msg => ({
                    role: msg.type === 'bot' ? 'assistant' : 'user',
                    content: msg.content
                })),
                language: language || 'ma',
                mode: mode || {}
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const result = data.response;
        if (result.final_response) {
            const botMessage: Message = {
                id: String(Date.now()),
                type: 'bot',
                content: result.final_response,
            };
            return botMessage;
        } else { // error response
            throw new Error(data.detail[0].msg);
        }

        // const botMessage: Message = {
        //     id: String(Date.now()),
        //     type: 'bot',
        //     content: data.response,
        // };
        // return botMessage;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw new Error('Failed to fetch message from RAG.');
    }
}

// fetch non-prompting local
export async function fetchMessageLocalNonPrompting(messages: Message[], language?: string): Promise<Message> {
    try {
        const response = await fetch("http://10.37.81.23:8000/chat_without_prompt", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_query: messages[messages.length - 1].content,
                history: messages.map(msg => ({
                    role: msg.type === 'bot' ? 'assistant' : 'user',
                    content: msg.content
                })),
                language: language || 'mandarin',
                mode: {}
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const result = data.response;
        if (result.final_response) {
            const botMessage: Message = {
                id: String(Date.now()),
                type: 'bot',
                content: result.final_response,
            };
            return botMessage;
        } else { // error response
            throw new Error(data.detail[0].msg);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        throw new Error('Failed to fetch message from RAG.');
    }
}


// 短文本在线合成-基础音库，请求地址：http://tsn.baidu.com/text2audio
// API ID：99081331
// APIKEY：HI9V7RVRZDPnVq2kkkQFnpTq
// Secret Key：B2Z0qhoMCcSPd8Y59f2JV79JGfFVdWxN

// baidu tts fetch
export async function fetchTTSBaidu(text: string): Promise<string> {
    try {
        const response = await fetch("http://tsn.baidu.com/text2audio", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
            },
            body: new URLSearchParams({
                tex: text,
                lan: 'zh',
                ctp: 1,
                tok: '25.613b05d3e97b773cf8c5c94312f9fabe.315360000.2038481187.282335-99081331',
                cuid: '123456',
                per: 0,
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);
        return url;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw new Error('Failed to fetch TTS from Baidu.');
    }
}


// fetch RAG from local
// request:
// {
//     "user_query": "string",
//     "history": [
//              {
            // "role": "string",
            // "content": "string"
            // }
//     ]
//   }

// response: "string"
// error response:
// {
//   "detail": [
//     {
//       "loc": [
//         "string",
//         0
//       ],
//       "msg": "string",
//       "type": "string"
//     }
//   ]
// }

// http://localhost:8000/rag_chat_final_use

export async function fetchRAGLocal(messages: Message[]): Promise<Message> {
    try {
        const response = await fetch("http://10.37.81.23:8000/rag_chat_final_use", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                user_query: messages[messages.length - 1].content,
                history: messages.map(msg => ({
                    role: msg.type === 'bot' ? 'assistant' : 'user',
                    content: msg.content
                })),
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        const result = data
        console.log('result:', result);
        if (result.response) {
            const botMessage: Message = {
                id: String(Date.now()),
                type: 'bot',
                content: result.response,
                references: toReference(result.references),
            };
            return botMessage;
        } else { // error response
            throw new Error(data.detail[0].msg);
        }
    } catch (error) {
        console.error('Error fetching data:', error);
        throw new Error('Failed to fetch message from RAG.');
    }
}


// reset the history of the chat
export async function fetchResetHistory(): Promise<void> {
    try {
        const response = await fetch("http://10.37.81.23:8000/reset", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({}),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('data:', data);
    } catch (error) {
        console.error('Error fetching data:', error);
        throw new Error('Failed to reset history.');
    }
}


// 生成 UUID
function generateUUID() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        var r = Math.random() * 16 | 0,
            v = c == 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// 获取或生成 CUID
function getCUID() {
    let cuid = localStorage.getItem('cuid');
    if (!cuid) {
        cuid = generateUUID();
        localStorage.setItem('cuid', cuid);
    }
    return cuid;
}

// 短文本在线合成-基础音库，请求地址：http://vop.baidu.com/server_api
// API ID：99081331
// APIKEY：HI9V7RVRZDPnVq2kkkQFnpTq
// Secret Key：B2Z0qhoMCcSPd8Y59f2JV79JGfFVdWxN

// baidu asr fetch
export async function fetchASRBaidu(audio: Blob): Promise<string> {
    const cuid = getCUID();

    // 将音频数据转换为 Base64
    const audioBase64 = await new Promise<string>((resolve, reject) => {
        const reader = new FileReader();
        reader.onloadend = () => {
            const base64String = reader.result?.toString().split(',')[1];
            if (base64String) {
                // console.log('Base64 String:', base64String);
                resolve(base64String);
            } else {
                reject('Failed to convert audio to Base64.');
            }
        };
        reader.onerror = reject;
        reader.readAsDataURL(audio);
    });

    // 将音频数据转换为 Base64


    try {
        const response = await fetch("http://vop.baidu.com/server_api", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                format: 'pcm',
                rate: 16000,
                channel: 1,
                token: '25.613b05d3e97b773cf8c5c94312f9fabe.315360000.2038481187.282335-99081331',
                cuid: '123456',
                dev_pid: 1537,
                speech: audioBase64, 
                len: audio.size
            }),
            mode: 'no-cors'
        });

        console.log('baidu ASR response:', response);

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        const data = await response.json();
        console.log('data:', data);
        const result = data.result ? data.result[0] : '';
        return result;
    } catch (error) {
        console.error('Error fetching data:', error);
        throw new Error('Failed to fetch ASR from Baidu.');
    }
}

// export async function fetchASRBaiduByAPI(audio: Blob): Promise<any> {


//     const audioBase64 = await new Promise<string>((resolve, reject) => {
//         const reader = new FileReader();
//         reader.onloadend = () => {
//             const base64String = reader.result?.toString().split(',')[1];
//             if (base64String) {
//                 resolve(base64String);
//             } else {
//                 reject('Failed to convert audio to Base64.');
//             }
//         };
//         reader.onerror = reject;
//         reader.readAsDataURL(audio);
//     });

//     const response = await fetch('/api/asr', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/json',
//         },
//         body: JSON.stringify({
//             audioBase64: audioBase64,
//             size: audio.size // 这里传递的是原始大小
//         }),
//     });

//     if (!response.ok) {
//         throw new Error('Network response was not ok');
//     }

//     const data = await response.json();
//     return data; // 处理返回的数据
// }
// fetch 
export async function fetchTTSXFei(text: string): Promise<any> {
    const response = await fetch('/api/tts', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ text }),
    });
  
    if (response.ok) {
       
        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        return url;
    } else {
      console.error('Error fetching audio:', response.statusText);
    }
  }
  