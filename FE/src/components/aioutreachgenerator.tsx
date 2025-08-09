import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { Checkbox } from "@/components/ui/checkbox";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MessageSquare, FileText, ArrowLeft, Search, Users } from "lucide-react";

interface Lead {
  id: string;
  company: string;
  industry: string;
  location: string;
  website?: string;
  linkedinUrl?: string;
  contact?: string;
  employees?: string;
  priority?: string;
  outreachAngle?: string;
}

interface AIOutreachGeneratorProps {
  onNavigateBack: () => void;
  existingLeads?: Lead[]; 
}

export function AIOutreachGenerator({ onNavigateBack, existingLeads = [] }: AIOutreachGeneratorProps) {
  const [messageType, setMessageType] = useState<string>("cold_email");
  const [tone, setTone] = useState<string>("");
  const [personalizationLevel, setPersonalizationLevel] = useState<string>("");
  const [targetRole, setTargetRole] = useState<string>("");
  const [companyDescription, setCompanyDescription] = useState<string>("");
  const [valueProposition, setValueProposition] = useState<string>("");
  const [senderName, setSenderName] = useState<string>("");
  const [selectedLead, setSelectedLead] = useState<Lead | null>(null);
  const [generateBulk, setGenerateBulk] = useState<boolean>(false);
  const [selectedLeadIds, setSelectedLeadIds] = useState<string[]>([]);
  const [isGenerating, setIsGenerating] = useState<boolean>(false);
  const [generatedMessage, setGeneratedMessage] = useState<string>("");
  const [errorDetails, setErrorDetails] = useState<string>("");
  const [leadSearchTerm, setLeadSearchTerm] = useState<string>("");
  const [showLeadSelector, setShowLeadSelector] = useState<boolean>(true);

  // Search and filter leads
  const filteredLeads = existingLeads.filter(lead => 
    lead.company.toLowerCase().includes(leadSearchTerm.toLowerCase()) ||
    lead.industry.toLowerCase().includes(leadSearchTerm.toLowerCase()) ||
    (lead.contact && lead.contact.toLowerCase().includes(leadSearchTerm.toLowerCase()))
  );

  const messageTypes = [
    { value: "cold_email", label: "Cold Email" },
    { value: "linkedin_message", label: "LinkedIn Message" },
    { value: "cold_call_script", label: "Cold Call Script" }
  ];

  const tones = [
    { value: "professional", label: "Professional" },
    { value: "friendly", label: "Friendly" },
    { value: "casual", label: "Casual" },
    { value: "urgent", label: "Urgent" }
  ];

  const personalizationLevels = [
    { value: "low", label: "Low" },
    { value: "medium", label: "Medium" },
    { value: "high", label: "High" }
  ];

  const handleGenerateMessage = async () => {
    if (!canGenerate) return;

    setIsGenerating(true);
    setGeneratedMessage("");
    setErrorDetails("");

    try {
      const requestBody = {
        message_type: messageType,
        tone: tone,
        personalization_level: personalizationLevel,
        target_role: targetRole,
        company_description: companyDescription,
        value_proposition: valueProposition,
        sender_name: senderName,
        lead: selectedLead
      };

      console.log("Request body:", JSON.stringify(requestBody, null, 2));

      const response = await fetch("http://localhost:8000/api/outreach/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      console.log("Response status:", response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error("Error response:", errorText);
        setErrorDetails(`Status: ${response.status}\nResponse: ${errorText}`);
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      console.log("Response data:", data);
      
      if (data.success && data.message?.message) {
        setGeneratedMessage(data.message.message);
      } else {
        setGeneratedMessage("No message content returned from AI");
      }
    } catch (error) {
      console.error("Failed to generate message:", error);
      setGeneratedMessage(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleBulkGenerate = async () => {
    if (selectedLeadIds.length === 0) return;

    setIsGenerating(true);
    setGeneratedMessage("");
    setErrorDetails("");

    try {
      const requestBody = {
        lead_ids: selectedLeadIds,
        outreach_request: {
          message_type: messageType,
          tone: tone,
          personalization_level: personalizationLevel,
          target_role: targetRole,
          company_description: companyDescription,
          value_proposition: valueProposition,
          sender_name: senderName
        }
      };

      const response = await fetch("http://localhost:8000/api/outreach/generate-bulk", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(requestBody),
      });

      if (!response.ok) {
        const errorText = await response.text();
        setErrorDetails(`Status: ${response.status}\nResponse: ${errorText}`);
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();
      
      if (data.success && data.messages) {
        const messagesText = data.messages.map((msg: any, index: number) => 
          `--- Message ${index + 1} (${msg.lead_id}) ---\n${msg.message}\n`
        ).join('\n');
        setGeneratedMessage(messagesText);
      }
    } catch (error) {
      console.error("Failed to generate bulk messages:", error);
      setGeneratedMessage(`Error: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsGenerating(false);
    }
  };

  const canGenerate = selectedLead && targetRole && companyDescription && valueProposition && senderName && tone && personalizationLevel;
  const canGenerateBulk = selectedLeadIds.length > 0 && targetRole && companyDescription && valueProposition && senderName && tone && personalizationLevel;

  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-6xl mx-auto py-8 px-6 space-y-8">
        <div className="space-y-4">
          <Button
            variant="outline"
            onClick={onNavigateBack}
            className="flex items-center gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Lead Generator
          </Button>
          
          <div className="text-center space-y-3">
            <div className="flex items-center justify-center gap-3">
              <h1 className="text-3xl font-medium text-foreground">AI Outreach Message Generator</h1>
            </div>
            <p className="text-muted-foreground">Generate Personalized Outreach Messages for Your Leads</p>
          </div>
        </div>

        {showLeadSelector && (
          <Card className="shadow-sm border-gray-200">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                Select Leads ({existingLeads.length} available)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              {existingLeads.length === 0 ? (
                <div className="text-center py-8 space-y-3">
                  <Users className="w-12 h-12 text-gray-300 mx-auto" />
                  <div className="text-muted-foreground">No Leads Available</div>
                  <p className="text-sm text-muted-foreground">
                    Generate Leads First Using the Lead Generator, Then Come Back to Create Messages.
                  </p>
                  <Button onClick={onNavigateBack} variant="outline">
                    Generate Leads First
                  </Button>
                </div>
              ) : (
                <>
                  <div className="flex items-center space-x-2">
                    <Search className="w-4 h-4 text-gray-400" />
                    <Input
                      placeholder="Search leads by company, industry, or contact..."
                      value={leadSearchTerm}
                      onChange={(e) => setLeadSearchTerm(e.target.value)}
                      className="bg-gray-50 border-gray-200"
                    />
                  </div>

                  <Tabs defaultValue="single" className="w-full">
                    <TabsContent value="single" className="space-y-2">
                      <div className="max-h-64 overflow-y-auto space-y-2">
                        {filteredLeads.map((lead) => (
                          <div
                            key={lead.id}
                            className={`p-3 border rounded-lg cursor-pointer transition-colors ${
                              selectedLead?.id === lead.id 
                                ? 'border-blue-500 bg-blue-50' 
                                : 'border-gray-200 hover:border-gray-300'
                            }`}
                            onClick={() => setSelectedLead(lead)}
                          >
                            <div className="font-semibold">{lead.company}</div>
                            <div className="text-sm text-gray-600">
                              {lead.industry} • {lead.location}
                            </div>
                            {lead.contact && (
                              <div className="text-sm text-gray-500">{lead.contact}</div>
                            )}
                          </div>
                        ))}
                      </div>
                      {selectedLead && (
                        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
                          <div className="text-sm font-medium text-green-800">
                            Selected: {selectedLead.company}
                          </div>
                        </div>
                      )}
                    </TabsContent>
                  </Tabs>
                </>
              )}
            </CardContent>
          </Card>
        )}

        <Card className="shadow-sm border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              Message Configuration
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="messageType">Message Type</Label>
                <Select value={messageType} onValueChange={setMessageType}>
                  <SelectTrigger id="messageType" className="bg-gray-50 border-gray-200">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {messageTypes.map((type) => (
                      <SelectItem key={type.value} value={type.value}>
                        {type.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="tone">Tone</Label>
                <Select value={tone} onValueChange={setTone}>
                  <SelectTrigger id="tone" className="bg-gray-50 border-gray-200">
                    <SelectValue placeholder="Select tone" />
                  </SelectTrigger>
                  <SelectContent>
                    {tones.map((toneOption) => (
                      <SelectItem key={toneOption.value} value={toneOption.value}>
                        {toneOption.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="personalization">Personalization Level</Label>
                <Select value={personalizationLevel} onValueChange={setPersonalizationLevel}>
                  <SelectTrigger id="personalization" className="bg-gray-50 border-gray-200">
                    <SelectValue placeholder="Select level" />
                  </SelectTrigger>
                  <SelectContent>
                    {personalizationLevels.map((level) => (
                      <SelectItem key={level.value} value={level.value}>
                        {level.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="targetRole">Target Role</Label>
                <Input
                  id="targetRole"
                  value={targetRole}
                  onChange={(e) => setTargetRole(e.target.value)}
                  className="bg-gray-50 border-gray-200"
                  placeholder="e.g., Marketing Director, CEO, Sales Manager"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="companyDescription">Your Company Description</Label>
                <Textarea
                  id="companyDescription"
                  value={companyDescription}
                  onChange={(e) => setCompanyDescription(e.target.value)}
                  className="bg-gray-50 border-gray-200 min-h-[100px] resize-none"
                  placeholder="Brief description of your company and what you do..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="valueProposition">Value Proposition</Label>
                <Textarea
                  id="valueProposition"
                  value={valueProposition}
                  onChange={(e) => setValueProposition(e.target.value)}
                  className="bg-gray-50 border-gray-200 min-h-[100px] resize-none"
                  placeholder="What specific value do you provide to companies like theirs..."
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="senderName">Sender Name</Label>
                <Input
                  id="senderName"
                  value={senderName}
                  onChange={(e) => setSenderName(e.target.value)}
                  className="bg-gray-50 border-gray-200"
                  placeholder="Your full name"
                />
              </div>
            </div>

            <div className="pt-4 border-t border-gray-100 space-y-4">
              <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
                {!generateBulk ? (
                  <Button
                    onClick={handleGenerateMessage}
                    disabled={!canGenerate || isGenerating}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-2.5 shadow-sm"
                    size="lg"
                  >
                    {isGenerating ? "Generating..." : "Generate Message"}
                  </Button>
                ) : (
                  <Button
                    onClick={handleBulkGenerate}
                    disabled={!canGenerateBulk || isGenerating}
                    className="bg-primary text-primary-foreground hover:bg-primary/90 px-8 py-2.5 shadow-sm"
                    size="lg"
                  >
                    {isGenerating ? "Generating..." : `Generate ${selectedLeadIds.length} Messages`}
                  </Button>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="shadow-sm border-gray-200">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <FileText className="w-5 h-5" />
              Generated Messages
            </CardTitle>
          </CardHeader>
          <CardContent>
            {errorDetails && (
              <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-md">
                <h4 className="text-red-800 font-semibold mb-2">Error Details:</h4>
                <pre className="text-sm text-red-700 whitespace-pre-wrap">{errorDetails}</pre>
              </div>
            )}
            
            {generatedMessage ? (
              <div className="text-left space-y-3 bg-gray-50 p-4 rounded-md border border-gray-200">
                <pre className="whitespace-pre-wrap text-sm">{generatedMessage}</pre>
                <div className="flex gap-2 pt-2">
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => navigator.clipboard.writeText(generatedMessage)}
                  >
                    Copy Message
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setGeneratedMessage("")}
                  >
                    Clear
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-12 space-y-3">
                <MessageSquare className="w-12 h-12 text-gray-300 mx-auto" />
                <div className="text-muted-foreground">
                  No Message Generated Yet
                </div>
                <p className="text-sm text-muted-foreground">
                  Select {generateBulk ? 'leads' : 'a lead'} & Configure Your Message Settings Above
                </p>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}