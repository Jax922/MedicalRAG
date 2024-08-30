import { NextResponse } from 'next/server';
import CryptoJS from 'crypto-js';
import { w3cwebsocket as W3CWebSocket } from 'websocket';

type Config = {
  hostUrl: string;
  host: string;
  appid: string;
  apiSecret: string;
  apiKey: string;
  uri: string;
};

const config: Config = {
  hostUrl: "wss://tts-api.xfyun.cn/v2/tts",
  host: "tts-api.xfyun.cn",
  appid: "d12b0493",
  apiSecret: "MzcyM2M3Yjk5MmVhMGQzZmM4NjAwN2Vi",
  apiKey: "9a5ed5cacad7b53ea6475276529704eb",
  uri: "/v2/tts",
};

export async function POST(req: Request) {
  const body = await req.json();

  if (req.method !== 'POST') {
    return new NextResponse("Just POST method is allowed", { status: 405 });
  }

  const { text } = body;
  let lan_type = 'xiaoyan';

  if (body.lan_type) {
    lan_type = body.lan_type;
  }

  if (!text) {
    return new NextResponse(JSON.stringify({ message: 'Text is required' }), { status: 400 });
  }

  const date = new Date().toUTCString();

  function getAuthStr(date: string): string {
    const signatureOrigin = `host: ${config.host}\ndate: ${date}\nGET ${config.uri} HTTP/1.1`;
    const signatureSha = CryptoJS.HmacSHA256(signatureOrigin, config.apiSecret);
    const signature = CryptoJS.enc.Base64.stringify(signatureSha);
    const authorizationOrigin = `api_key="${config.apiKey}", algorithm="hmac-sha256", headers="host date request-line", signature="${signature}"`;
    return CryptoJS.enc.Base64.stringify(CryptoJS.enc.Utf8.parse(authorizationOrigin));
  }

  const wssUrl = `${config.hostUrl}?authorization=${getAuthStr(date)}&date=${date}&host=${config.host}`;

  return new Promise<NextResponse>((resolve) => {
    const client = new W3CWebSocket(wssUrl);
    let audioChunks: Buffer[] = [];

    client.onopen = () => {
      console.log('WebSocket connection opened');
      send(text);
    };

    client.onmessage = (message) => {
      console.log('Received:', message.data.toString());

      const resData = JSON.parse(message.data.toString());

      if (resData.code !== 0) {
        client.close();
        resolve(new NextResponse(JSON.stringify({ message: `${resData.code}: ${resData.message}` }), { status: 500 }));
        return;
      }

      const audio = resData.data.audio;
      const audioBuf = Buffer.from(audio, 'base64');
      audioChunks.push(audioBuf);

      if (resData.code === 0 && resData.data.status === 2) {
        client.close();
        const fullAudioBuffer = Buffer.concat(audioChunks);
        resolve(new NextResponse(fullAudioBuffer, { status: 200, headers: { 'Content-Type': 'audio/mp3' } }));
      }
    };

    client.onclose = () => {
      console.log('WebSocket connection closed');
    };

    client.onerror = (err) => {
      console.error('WebSocket connection error:', err);
      resolve(new NextResponse(JSON.stringify({ message: 'WebSocket connection error' }), { status: 500 }));
    };

    function send(text: string) {
      const frame = {
        common: {
          app_id: config.appid,
        },
        business: {
          aue: "lame", // 请求 MP3 格式的音频
          sfl: 1, // 1 表示音频采样率为 16k 参考文档：https://www.xfyun.cn/doc/tts/online_tts/API.html#%E6%8E%A5%E5%8F%A3%E8%A6%81%E6%B1%82
          auf: "audio/L16;rate=8000",
        //   vcn: "xiaoyan", // 普通话 "xiaomei" // 广东话
            vcn: lan_type, 
          tte: "UTF8",
          volume: 70
        },
        data: {
          text: Buffer.from(text).toString('base64'),
          status: 2,
        },
      };
      client.send(JSON.stringify(frame));
    }
  });
}