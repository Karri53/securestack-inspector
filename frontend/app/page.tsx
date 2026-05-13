// frontend/app/page.tsx
// Landing page composition. Each section is its own component so the
// file structure stays scannable and reordering is trivial.

import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import StatusDashboard from "@/components/StatusDashboard";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Features />
        <HowItWorks />
        <StatusDashboard />
      </main>
      <Footer />
    </>
  );
}
