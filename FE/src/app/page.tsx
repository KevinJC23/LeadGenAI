"use client"

import { useState, useEffect } from 'react';
import { LeadGenerator } from "@/components/leadgenerator";
import { AIOutreachGenerator } from "@/components/aioutreachgenerator";

type CurrentView = "leads" | "ai-outreach";

export default function App() {
  const [currentView, setCurrentView] = useState<CurrentView>("leads");
  const [leads, setLeads] = useState<any[]>([]); 
  const [selectedLeads, setSelectedLeads] = useState<any[]>([]); 

  const fetchLeads = async () => {
    try {
      const response = await fetch("http://localhost:8000/api/leads");
      if (response.ok) {
        const leadsData = await response.json();
        setLeads(Array.isArray(leadsData) ? leadsData : []);
      }
    } catch (error) {
      console.error("Failed to fetch leads:", error);
    }
  };

  useEffect(() => {
    fetchLeads();
  }, []);

  const handleNavigateToAI = (selectedLeadsData: any[] = []) => {
    setSelectedLeads(Array.isArray(selectedLeadsData) ? selectedLeadsData : []);
    setCurrentView("ai-outreach");
  };

  const handleNavigateBack = () => {
    setCurrentView("leads");
  };

  return (
    <div className="min-h-screen bg-background">
      {currentView === "leads" ? (
        <LeadGenerator onNavigateToAI={handleNavigateToAI} />
      ) : (
        <AIOutreachGenerator 
          onNavigateBack={handleNavigateBack}
          existingLeads={selectedLeads} 
        />
      )}
    </div>
  );
}