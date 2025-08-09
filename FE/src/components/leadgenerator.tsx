"use client"

import { useState } from "react";
import { Button } from "./ui/button";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./ui/select";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/table";
import { Checkbox } from "./ui/checkbox";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";
import { Search, FileSpreadsheet, AlertCircle, CheckCircle } from "lucide-react";
import { industries, locations } from "@/contents";
import { apiService, Lead } from "@/lib/api";
import { Alert, AlertDescription } from "./ui/alert";

interface LeadGeneratorProps {
  onNavigateToAI: (selectedLeadsData: Lead[]) => void;
}

export function LeadGenerator({ onNavigateToAI }: LeadGeneratorProps) {
    const [selectedIndustry, setSelectedIndustry] = useState<string>("");
    const [selectedLocation, setSelectedLocation] = useState<string>("");
    const [leads, setLeads] = useState<Lead[]>([]);
    const [selectedLeads, setSelectedLeads] = useState<Set<string>>(new Set());
    const [isSearching, setIsSearching] = useState(false);
    const [isExporting, setIsExporting] = useState(false);
    const [error, setError] = useState<string>("");
    const [success, setSuccess] = useState<string>("");

    const handleFindLeads = async () => {
        if (!selectedIndustry || !selectedLocation) return;

        setIsSearching(true);
        setError("");
        setSuccess("");
        
        try {
            const response = await apiService.searchLeads({
                industry: selectedIndustry,
                location: selectedLocation
            });
            
            setLeads(response.leads);
            setSuccess(`Found ${response.total} leads successfully!`);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to search leads');
            setLeads([]);
        } finally {
            setIsSearching(false);
        }
    };

    const handleExportToExcel = async () => {
        if (selectedLeads.size === 0) {
            setError("Please select at least one lead to export");
            return;
        }

        setIsExporting(true);
        setError("");

        try {
            const selectedLeadData = leads.filter(lead => selectedLeads.has(lead.id));
            const blob = await apiService.exportToExcel(selectedLeadData);
            
            const filename = `leads_${selectedIndustry}_${selectedLocation}_${new Date().toISOString().split('T')[0]}.csv`;
            apiService.downloadFile(blob, filename);
            
            setSuccess(`Exported ${selectedLeads.size} leads successfully!`);
        } catch (err) {
            setError('Failed to export leads');
        } finally {
            setIsExporting(false);
        }
    };

    const handleSelectLead = (leadId: string, checked: boolean) => {
        const newSelected = new Set(selectedLeads);
        if (checked) {
            newSelected.add(leadId);
        } else {
            newSelected.delete(leadId);
        }
        setSelectedLeads(newSelected);
    };

    const handleSelectAll = (checked: boolean) => {
        if (checked) {
            setSelectedLeads(new Set(leads.map(lead => lead.id)));
        } else {
            setSelectedLeads(new Set());
        }
    };

    const allSelected = leads.length > 0 && selectedLeads.size === leads.length;
    const someSelected = selectedLeads.size > 0 && selectedLeads.size < leads.length;

    return (
        <div className="w-full max-w-7xl mx-auto p-6 space-y-6">
            <div className="text-center space-y-2">
                <h1 className="text-3xl font-medium text-foreground">B2B Lead Generator</h1>
                <p className="text-muted-foreground">Find and export high-quality B2B leads for your business</p>
            </div>

            <div className="flex justify-center">
                <Button
                    onClick={() => {
                        const selectedLeadData = leads.filter(lead => selectedLeads.has(lead.id));
                        onNavigateToAI(selectedLeadData);
                    }}
                    variant="outline"
                    className="flex items-center gap-2 border-primary text-primary hover:bg-primary hover:text-primary-foreground"
                >
                    AI Outreach Message Generator
                </Button>
            </div>

            {error && (
                <Alert className="border-red-200 bg-red-50">
                    <AlertCircle className="h-4 w-4 text-red-600" />
                    <AlertDescription className="text-red-800">{error}</AlertDescription>
                </Alert>
            )}

            {success && (
                <Alert className="border-green-200 bg-green-50">
                    <CheckCircle className="h-4 w-4 text-green-600" />
                    <AlertDescription className="text-green-800">{success}</AlertDescription>
                </Alert>
            )}

            <Card>
                <CardHeader>
                    <CardTitle>Search Filters</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex flex-col md:flex-row gap-4 items-end">
                        <div className="flex-1 space-y-2">
                            <label htmlFor="industry" className="text-sm text-muted-foreground">Industry</label>
                            <Select value={selectedIndustry} onValueChange={setSelectedIndustry}>
                                <SelectTrigger id="industry" className="w-full">
                                    <SelectValue placeholder="Select Industry" />
                                </SelectTrigger>
                                <SelectContent>
                                    {industries.map((industry) => (
                                        <SelectItem key={industry} value={industry}>
                                            {industry}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex-1 space-y-2">
                            <label htmlFor="location" className="text-sm text-muted-foreground">Location</label>
                            <Select value={selectedLocation} onValueChange={setSelectedLocation}>
                                <SelectTrigger id="location" className="w-full">
                                    <SelectValue placeholder="Select location" />
                                </SelectTrigger>
                                <SelectContent>
                                    {locations.map((location) => (
                                        <SelectItem key={location} value={location}>
                                            {location}
                                        </SelectItem>
                                    ))}
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="flex gap-2">
                            <Button 
                                onClick={handleFindLeads} 
                                disabled={isSearching || !selectedIndustry || !selectedLocation}
                                className="bg-primary text-primary-foreground hover:bg-primary/90"
                            >
                                <Search className="w-4 h-4 mr-2" />
                                {isSearching ? "Searching..." : "Find Leads"}
                            </Button>

                            <Button
                                variant="outline"
                                onClick={handleExportToExcel}
                                disabled={isExporting || selectedLeads.size === 0}
                                className="text-foreground"
                            >
                                <FileSpreadsheet className="w-4 h-4 mr-2" />
                                {isExporting ? "Exporting..." : `Export ${selectedLeads.size > 0 ? `(${selectedLeads.size})` : ''}`}
                            </Button>
                        </div>
                    </div>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <div className="flex justify-between items-center">
                        <div>
                            <CardTitle>Lead Results</CardTitle>
                            {leads.length > 0 && (
                                <p className="text-sm text-muted-foreground mt-1">
                                    {leads.length} leads found • {selectedLeads.size} selected
                                </p>
                            )}
                        </div>
                    </div>
                </CardHeader>
                <CardContent>
                    {leads.length === 0 ? (
                        <div className="text-center py-12">
                            <div className="text-muted-foreground text-lg">No Leads Found</div>
                            <p className="text-sm text-muted-foreground mt-2">
                                Select Filters and Click "Find Leads" to Start Your Search
                            </p>
                        </div>
                    ) : (
                        <div className="border rounded-lg overflow-hidden">
                            <Table>
                                <TableHeader>
                                    <TableRow className="bg-muted/50">
                                        <TableHead className="w-12">
                                            <Checkbox
                                                checked={allSelected}
                                                onCheckedChange={handleSelectAll}
                                                ref={checkbox => {
                                                    if (checkbox) (checkbox as HTMLInputElement).indeterminate = someSelected;
                                                }}
                                            />
                                        </TableHead>
                                        <TableHead>Company</TableHead>
                                        <TableHead>Industry</TableHead>
                                        <TableHead>Location</TableHead>
                                        <TableHead>Website</TableHead>
                                        <TableHead>LinkedIn URL</TableHead>
                                        <TableHead>Contact</TableHead>
                                        <TableHead>Employees</TableHead>
                                        <TableHead>Priority</TableHead>
                                        <TableHead>Outreach Angle</TableHead>
                                        <TableHead>Last Updated</TableHead>
                                    </TableRow>
                                </TableHeader>
                                <TableBody>
                                    {leads.map((lead) => (
                                        <TableRow key={lead.id}>
                                            <TableCell>
                                                <Checkbox
                                                    checked={selectedLeads.has(lead.id)}
                                                    onCheckedChange={(checked) => handleSelectLead(lead.id, checked as boolean)}
                                                />
                                            </TableCell>
                                            <TableCell className="font-medium">{lead.company}</TableCell>
                                            <TableCell>{lead.industry}</TableCell>
                                            <TableCell>{lead.location}</TableCell>
                                            <TableCell>
                                                {lead.website !== "N/A" ? (
                                                    <a href={lead.website} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                                                        {lead.website}
                                                    </a>
                                                ) : (
                                                    "N/A"
                                                )}
                                            </TableCell>
                                            <TableCell>
                                                {lead.linkedinUrl !== "N/A" ? (
                                                    <a href={lead.linkedinUrl} target="_blank" rel="noopener noreferrer" className="text-primary hover:underline">
                                                        LinkedIn
                                                    </a>
                                                ) : (
                                                    "N/A"
                                                )}
                                            </TableCell>
                                            <TableCell>{lead.contact}</TableCell>
                                            <TableCell>{lead.employees}</TableCell>
                                            <TableCell>
                                                <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs ${
                                                    lead.priority === "High" ? "bg-red-100 text-red-800" :
                                                    lead.priority === "Medium" ? "bg-yellow-100 text-yellow-800" :
                                                    "bg-green-100 text-green-800"
                                                }`}>
                                                    {lead.priority}
                                                </span>
                                            </TableCell>
                                            <TableCell>{lead.outreachAngle}</TableCell>
                                            <TableCell>{lead.lastUpdated}</TableCell>
                                        </TableRow>
                                    ))}
                                </TableBody>
                            </Table>
                        </div>
                    )}
                </CardContent>
            </Card>
        </div>
    );
}