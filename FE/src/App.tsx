import Sidebar from "./components/layout/Sidebar";
import Dashboard from "./features/dashboard/Dashboard";

export default function App() {
  return (
   
    <div className="flex h-screen bg-bg-main text-text-primary antialiased">
      <Sidebar />

      <main className="flex-1 flex justify-center overflow-y-auto">
        {/* Responsive container with proper max-width for SBAR integration */}
        <div className="w-full max-w-[1600px] px-4 py-4 md:px-6 md:py-6 lg:px-8 lg:py-8 xl:px-10 xl:py-10">
          <Dashboard />
        </div>
      </main>
    </div>
  );
}