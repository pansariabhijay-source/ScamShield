import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { FamilyProtection } from "@/components/landing/FamilyProtection";
import { ScamMap } from "@/components/landing/ScamMap";
import { RecentScans } from "@/components/landing/RecentScans";
import { FinalCTA } from "@/components/landing/FinalCTA";

export default function Home() {
  return (
    <main className="relative min-h-screen bg-canvas">
      <Navbar />
      <Hero />
      <HowItWorks />
      <FamilyProtection />
      <ScamMap />
      <RecentScans />
      <FinalCTA />
    </main>
  );
}
