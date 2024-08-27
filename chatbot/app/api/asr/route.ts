
import { NextResponse } from 'next/server';



// 短文本在线合成-基础音库，请求地址：http://vop.baidu.com/server_api
// API ID：99081331
// APIKEY：HI9V7RVRZDPnVq2kkkQFnpTq
// Secret Key：B2Z0qhoMCcSPd8Y59f2JV79JGfFVdWxN

// baidu asr fetch




export async function POST(request: Request): Promise<Response> {
  const body = await request.json();
  const audioBase64 = body.audioBase64;
  const size = body.size;

  try {
    const asrRes = await fetch('https://vop.baidu.com/server_api', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        format: 'wav',
        rate: 16000,
        channel: 1,
        token: '25.613b05d3e97b773cf8c5c94312f9fabe.315360000.2038481187.282335-99081331',
        cuid: '123456',
        // dev_pid: 1537,
        speech: audioBase64, 
        len: size
      }),
    });
    const asrJson = await asrRes.json();
    console.log('ASR result:', asrJson);
    const result = JSON.stringify(asrJson);
    return new NextResponse(result, { status: 200, headers: { 'Content-Type': 'application/json' } });
  } catch (error) {
    console.error('Error:', error);
    return new NextResponse(JSON.stringify({ error: 'Internal Server Error' }), { status: 500 });
  }
}
