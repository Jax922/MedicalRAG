import OlderHeader from "@/components/older/header";
import OlderChat from "@/components/older/chat";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <div className="sticky top-0 w-full">
        <OlderHeader />
      </div>
      <div className="w-full flex justify-center p-4 bg-white shadow-md">
        <div className="w-full max-w-md md:max-w-2xl">
          <OlderChat />
        </div>
      </div>
      
    </main>
  );
}
