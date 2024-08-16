import OlderHeader from "@/components/older/header";
import DoctorChat from "@/components/doctor/chat";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      <div className="sticky top-0 w-full">
        <h2 className="text-2xl font-bold text-center p-4 bg-white shadow-md">
            医生端
        </h2>
      </div>
      <div className="w-full flex justify-center p-4 bg-white shadow-md">
        <div className="w-full max-w-md md:max-w-2xl">
          <DoctorChat />
        </div>
      </div>
      
    </main>
  );
}