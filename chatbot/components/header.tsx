
import Image from 'next/image'
import CONFIG from '@/lib/config'
import Link from 'next/link'

export default function Header() {
    return (
      <header className="flex items-center justify-between w-full h-20 bg-white text-black z-50 border-b border-solid border-gray-300 shadow-sm">
  <div className="flex items-center">
    <a href="#">
      <Image src="/logo.svg" alt="logo" width={50} height={50} />
    </a>
    <h2 className="font-bold text-xl text-gray-500 ml-4">
      {CONFIG.web_title}
    </h2>
  </div>
  <Link href="/older" className="mr-4 p-2 text-lg bg-blue-500 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-700">
    老年版
  </Link>
</header>

    )
}