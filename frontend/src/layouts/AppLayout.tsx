import { Outlet } from "react-router-dom";
import Navigation from "../components/Navigation";

export default function AppLayout() {
  return (
    <div className="flex min-h-screen bg-void">
      <Navigation />
      <main className="min-w-0 flex-1 pb-20 md:pb-0">
        <Outlet />
      </main>
    </div>
  );
}
