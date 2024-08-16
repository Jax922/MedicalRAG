'use server';

import fs from 'fs';
import path from 'path';
import { NextRequest, NextResponse } from 'next/server';
import type { NextApiRequest, NextApiResponse } from 'next';

const settingsFilePath = path.join(process.cwd(), 'public', 'setting.json');
// export default async function handler(req: NextApiRequest, res: NextApiResponse) {
//   switch (req.method) {
//     case 'GET':
//       try {
//         const data = fs.readFileSync(settingsFilePath, 'utf8');
//         res.status(200).json(JSON.parse(data));
//       } catch (error) {
//         res.status(500).json({ error: 'Failed to read settings file' });
//       }
//       break;

//     case 'POST':
//       try {
//         const data = req.body;
//         fs.writeFileSync(settingsFilePath, JSON.stringify(data, null, 2));
//         res.status(200).json({ message: 'Settings updated successfully' });
//       } catch (error) {
//         res.status(500).json({ error: 'Failed to write settings file' });
//       }
//       break;

//     default:
//       res.setHeader('Allow', ['GET', 'POST']);
//       res.status(405).end(`Method ${req.method} Not Allowed`);
//   }
// }

// Handler for GET requests
export async function GET() {
  try {
    const data = fs.readFileSync(settingsFilePath, 'utf8');
    return NextResponse.json(JSON.parse(data));
  } catch (error) {
    return NextResponse.json({ error: 'Failed to read settings file' }, { status: 500 });
  }
}

// Handler for POST requests
export async function POST(request: any) {
  try {
    const data = await request.json();
    fs.writeFileSync(settingsFilePath, JSON.stringify(data, null, 2));
    return NextResponse.json({ message: 'Settings updated successfully' });
  } catch (error) {
    return NextResponse.json({ error: 'Failed to write settings file' }, { status: 500 });
  }
}
