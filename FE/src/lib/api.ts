export interface Lead {
  id: string;
  company: string;
  industry: string;
  location: string;
  website: string;
  linkedinUrl: string;
  contact: string;
  employees: string;
  priority: 'High' | 'Medium' | 'Low';
  outreachAngle: string;
  lastUpdated: string;
}

export interface SearchRequest {
  industry: string;
  location: string;
}

export interface SearchResponse {
  leads: Lead[];
  total: number;
}

export interface HealthCheckResponse {
  status: string;
  apollo_api: string;
  timestamp: string;
}

// API Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiService {
  private baseURL: string;

  constructor(baseURL: string = API_BASE_URL) {
    this.baseURL = baseURL;
  }

  // Search for Leads Based on Industry & Location
  async searchLeads(params: SearchRequest): Promise<SearchResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/search-leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify(params),
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      const data: SearchResponse = await response.json();
      
      if (!data.leads || !Array.isArray(data.leads)) {
        throw new Error('Invalid Response Format: Missing Leads Array');
      }

      return data;
    } catch (error) {
      console.error('Error Searching Leads:', error);
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to Connect to the Server. Please Check if the Backend is Running.');
      }
      
      throw error;
    }
  }

  // Export Selected Leads to CSV Format
  async exportToExcel(leads: Lead[]): Promise<Blob> {
    if (!leads || leads.length === 0) {
      throw new Error('No Leads Provided for Export');
    }

    try {
      const response = await fetch(`${this.baseURL}/api/export-leads`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'text/csv, application/octet-stream',
        },
        body: JSON.stringify(leads),
      });

      if (!response.ok) {
        let errorMessage = `HTTP error! status: ${response.status}`;
        try {
          const errorData = await response.json();
          errorMessage = errorData.detail || errorMessage;
        } catch {
          errorMessage = response.statusText || errorMessage;
        }
        throw new Error(errorMessage);
      }

      const blob = await response.blob();
    
      if (blob.size === 0) {
        throw new Error('Export Failed: Received Empty File');
      }

      return blob;
    } catch (error) {
      console.error('Error Exporting Leads:', error);
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to Connect to the Server. Please Check if the Backend is Running.');
      }
      
      throw error;
    }
  }

  // Download a File Blob to the User's Computer
  downloadFile(blob: Blob, filename: string): void {
    try {
      const url = window.URL.createObjectURL(blob);
      
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      
      document.body.appendChild(link);
      link.click();
      
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading file:', error);
      throw new Error('Failed to Download File. Please Try Again.');
    }
  }

  // Check API Health and Configuration Status
  async healthCheck(): Promise<HealthCheckResponse> {
    try {
      const response = await fetch(`${this.baseURL}/api/health`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error(`Health Check Failed: ${response.status} ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Health Check Failed:', error);
      
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to Connect to the Backend Server');
      }
      
      throw error;
    }
  }

  // Test the API Connection
  async testConnection(): Promise<boolean> {
    try {
      await this.healthCheck();
      return true;
    } catch {
      return false;
    }
  }

  // Get API Base URL 
  getBaseURL(): string {
    return this.baseURL;
  }

  // Generate Filename for Export With Current Timestamp
  generateExportFilename(industry: string, location: string, extension: string = 'csv'): string {
    const timestamp = new Date().toISOString().split('T')[0]; 
    const sanitizedIndustry = industry.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
    const sanitizedLocation = location.replace(/[^a-zA-Z0-9]/g, '_').toLowerCase();
    
    return `leads_${sanitizedIndustry}_${sanitizedLocation}_${timestamp}.${extension}`;
  }
}

// Create & Export Singleton Instance
export const apiService = new ApiService();

// Export Class for Testing or Custom Instances
export { ApiService };

// Utility Function to Check if Backend is Reachable
export async function checkBackendConnection(): Promise<{
  connected: boolean;
  message: string;
  details?: HealthCheckResponse;
}> {
  try {
    const health = await apiService.healthCheck();
    return {
      connected: true,
      message: 'Successfully Connected to Backend',
      details: health,
    };
  } catch (error) {
    return {
      connected: false,
      message: error instanceof Error ? error.message : 'Unknown Connection Error',
    };
  }
}

// Utility Function for Error Handling in Components
export function getErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message;
  }
  
  if (typeof error === 'string') {
    return error;
  }
  
  return 'An Unexpected Error Occurred';
}