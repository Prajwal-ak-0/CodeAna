"use client";

import { useState } from "react";
import { ArrowRight, Github, AlertTriangle, FileJson, FileSpreadsheet, Loader2 } from 'lucide-react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import JsonViewer from "./components/json-viewer";
import CsvViewer from "./components/csv-viewer";

interface AnalysisResult {
  json_data: any;
  csv_data: string;
  status: string;
}

export default function Home() {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [viewMode, setViewMode] = useState<'json' | 'csv'>('json');
  const [repoUrl, setRepoUrl] = useState('');
  const [jobId, setJobId] = useState<string | null>(null);

  const handleAnalyzeRepo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!repoUrl.trim()) return;

    setLoading(true);
    setError(null);
    setAnalysisResult(null);
    setJobId(null);

    try {
      // Submit the repo URL to start analysis
      const response = await fetch('http://localhost:8000/analyze', {
        method: 'POST',
        mode: 'cors',
        credentials: 'omit',
        headers: {
          'Content-Type': 'application/json',
          'Accept': 'application/json',
        },
        body: JSON.stringify({ url: repoUrl })
      });

      if (!response.ok) {
        const errorData = await response.json();
        setError(errorData.detail || 'An error occurred while starting the analysis');
        setLoading(false);
        return;
      }

      const data = await response.json();
      setJobId(data.job_id);

      // Start polling for results using the returned job ID
      pollResult(data.job_id);
    } catch (error) {
      setError('Network error or server is not responding');
      setLoading(false);
    }
  };

  const pollResult = (jobId: string) => {
    const interval = setInterval(async () => {
      try {
        const response = await fetch(`http://localhost:8000/result/${jobId}`, {
          method: 'GET',
          mode: 'cors',
          credentials: 'omit',
          headers: {
            'Accept': 'application/json',
          }
        });

        // If the job is still processing, the backend returns a 404
        if (response.status === 404) {
          return;
        }

        const result = await response.json();
        // When result.status is no longer "processing", update the state
        if (result.status !== 'processing') {
          setAnalysisResult(result);
          setLoading(false);
          clearInterval(interval);
        }
      } catch (error) {
        setError('Error while polling for result.');
        setLoading(false);
        clearInterval(interval);
      }
    }, 5000); // poll every 5 seconds
  };

  return (
    <main className="min-h-screen flex flex-col">
      {/* Hero section with gradient background */}
      {!analysisResult && (
        <div className="relative w-full bg-gradient-to-br from-violet-950 via-slate-900 to-zinc-900 py-20 px-4 sm:px-6 lg:px-8">
        <div className="absolute inset-0 bg-[url('/grid-pattern.svg')] bg-center [mask-image:linear-gradient(180deg,white,rgba(255,255,255,0))]"></div>
        <div className="relative max-w-3xl mx-auto text-center">
          <div className="inline-flex items-center justify-center p-2 bg-violet-900/30 backdrop-blur-sm rounded-full mb-6">
            <AlertTriangle className="w-5 h-5 text-amber-400 mr-2" />
            <span className="text-amber-200 text-sm font-medium">Security Vulnerability Scanner</span>
          </div>
          <h1 className="text-4xl font-bold tracking-tight text-white sm:text-5xl mb-6">
            Scan GitHub Repositories for <span className="text-violet-400">Vulnerabilities</span>
          </h1>
          <p className="text-lg text-slate-300 mb-8">
            Analyze your code for potential security risks, third-party dependencies, and data flow issues.
          </p>
          
          <Card className="bg-slate-900/60 backdrop-blur-sm border-slate-800 shadow-xl">
            <CardContent className="pt-6">
              <form onSubmit={handleAnalyzeRepo} className="flex flex-col sm:flex-row gap-3">
                <div className="relative flex-grow">
                  <Github className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                  <Input
                    type="text"
                    placeholder="Enter GitHub repository URL"
                    value={repoUrl}
                    onChange={(e) => setRepoUrl(e.target.value)}
                    className="pl-10 bg-slate-800 border-slate-700 text-white placeholder:text-slate-400 h-12"
                  />
                </div>
                <Button 
                  type="submit" 
                  disabled={loading || !repoUrl.trim()} 
                  className="h-12 px-6 bg-violet-600 hover:bg-violet-700 text-white"
                >
                  {loading ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      Analyze
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </>
                  )}
                </Button>
              </form>
              
              {error && (
                <div className="mt-4 p-3 bg-red-900/40 border border-red-800 rounded-md text-red-200 text-sm">
                  {error}
                </div>
              )}
              
              {loading && !error && (
                <div className="mt-6 flex flex-col items-center justify-center py-8">
                  <div className="relative">
                    <div className="h-24 w-24 rounded-full border-t-2 border-b-2 border-violet-500 animate-spin"></div>
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-violet-400 text-xs font-mono">
                      {jobId ? jobId.substring(0, 8) : '...'}
                    </div>
                  </div>
                  <p className="mt-4 text-slate-300 text-sm">
                    Scanning repository for vulnerabilities...
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
      )}

      {/* Results section */}
      {analysisResult && (
        <div className="flex-grow bg-slate-950">
          <div className="w-90% h-full mx-auto">
            <Tabs 
              defaultValue="json" 
              value={viewMode} 
              onValueChange={(value) => setViewMode(value as 'json' | 'csv')}
              className="w-full"
            >
              <div className="flex items-center justify-between mb-6">
                <TabsList className="bg-slate-900 border border-slate-800">
                  <TabsTrigger 
                    value="json" 
                    className="data-[state=active]:bg-violet-900 data-[state=active]:text-white"
                  >
                    <FileJson className="mr-2 h-4 w-4" />
                    Tree View
                  </TabsTrigger>
                  <TabsTrigger 
                    value="csv" 
                    className="data-[state=active]:bg-violet-900 data-[state=active]:text-white"
                  >
                    <FileSpreadsheet className="mr-2 h-4 w-4" />
                    Table View
                  </TabsTrigger>
                </TabsList>
              </div>
              
              <TabsContent value="json" className="mt-0 h-full">
                <div className="bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden h-[calc(100vh-100px)]">
                  <JsonViewer data={analysisResult.json_data} />
                </div>
              </TabsContent>
              
              <TabsContent value="csv" className="mt-0">
                <div className="bg-slate-900 border border-slate-800 rounded-lg shadow-xl overflow-hidden h-[calc(100vh-100px)]">
                  <CsvViewer data={analysisResult.csv_data} />
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      )}
    </main>
  );
}
