
import { NextResponse } from 'next/server';

export async function POST(request: Request): Promise<Response> {
  const body = await request.json();

  try {
    const difyRes = await fetch('https://api.dify.ai/v1/chat-messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer app-psN1nX565prAVAS7L0KZ2T45`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!difyRes.ok) {
      const error = await difyRes.text();
      return new NextResponse(error, { status: difyRes.status });
    }

    const reader = difyRes.body?.getReader();
    if (!reader) {
      throw new Error('Failed to get reader from response');
    }

    const decoder = new TextDecoder('utf-8');
    let result = '';

    // Stream the response data
    while (true) {
      const { done, value } = await reader.read();
      if (done) break;
      result += decoder.decode(value, { stream: true });
    }

    return new NextResponse(result, { status: 200, headers: { 'Content-Type': 'application/json' } });
  } catch (error) {
    console.error('Error:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
  }
}
