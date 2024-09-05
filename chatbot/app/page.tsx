import Header from "@/components/header";
import Chat from "@/components/chat";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between bg_gray_default">
      <div className="sticky top-0 w-full">
        <Header />
      </div>
      <div className="w-full flex justify-center p-4 bg_gray_default shadow-md">
        <div className="w-full max-w-md md:max-w-2xl">
          <Chat />
        </div>
      </div>
      
    </main>
  );
}
