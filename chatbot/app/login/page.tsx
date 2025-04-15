import OlderHeader from "@/components/older/header";
import Portal from "@/components/portal";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between">
      {/* <div className="sticky top-0 w-full">
        <OlderHeader />
      </div> */}
      <div className="w-full flex justify-center p-4 bg-white shadow-md">
        <div className="w-full max-w-full lg:max-w-5xl">
          <Portal />






        </div>
      </div>
      
    </main>
  );
}
