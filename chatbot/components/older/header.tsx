
'use client';

import Image from 'next/image'
import CONFIG from '@/lib/config'
import Link from 'next/link'


export default function OlderHeader() {
  return (
    <>
      <style jsx>{`
        :root {
          --lightYellow: #FFFACD;
          --darkGray: #333333;
        }
        header {
          background-color: var(--lightYellow);
        }
        h2 {
          color: var(--darkGray);
        }
      `}</style>
      <header className="flex items-center justify-between w-full h-[6rem] text-black z-50 border-b border-solid border-gray-300 shadow-sm">
        <div className="flex items-center">
          <a href="#">
            <Image src="/logo.svg" alt="logo" width={60} height={60} />
          </a>
          <h2 className="font-bold text-[1.7rem] ml-6">
            {CONFIG.web_title}
          </h2>
        </div>
        <Link href="/" className="mr-4 p-3 text-[1.7rem] bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-700">
          返回普通版
        </Link>
      </header>
    </>
  )
}