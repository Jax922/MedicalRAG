
import Image from 'next/image'
import CONFIG from '@/lib/config'

export default function Header() {
    return (
        <header className="flex items-center w-full h-20 bg-white text-black z-50 border-b border-solid border-gray-300 shadow-sm">
        <a href="#">
          <Image src="/logo.svg" alt="logo" width={50} height={50} />
        </a>
        <h2 className="font-bold text-xl text-gray-500">
            {CONFIG.web_title}
        </h2>
      </header>
    )
}