"use client";

import { useState, useEffect } from 'react';
import { fetchApi } from '@/lib/api';
import { CheckCircle2, XCircle, AlertCircle } from 'lucide-react';
import Link from 'next/link';

export default function JobAnalysisPage() {
  const [jobText, setJobText] = useState('');
  const [analyzing, setAnalyzing] = useState(false);
  const [matchResult, setMatchResult] = useState<any>(null);
  const [error, setError] = useState('');
  const [resumeId, setResumeId] = useState<number | null>(null);

  useEffect(() => {
    async function getResume() {
      try {
        const resumes = await fetchApi('/resumes/');
        if (resumes && resumes.length > 0) {
          setResumeId(resumes[0].id);
        }
      } catch (e) {}
    }
    getResume();
  }, []);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resumeId) {
      setError("Please upload a resume first.");
      return;
    }
    setAnalyzing(true);
    setError('');

    try {
      // 1. Submit Job
      const jobData = await fetchApi('/jobs/', {
        method: 'POST',
        body: JSON.stringify({ description_text: jobText })
      });
      
      // 2. Analyze Match
      const matchData = await fetchApi(`/analysis/${resumeId}/${jobData.id}`, {
        method: 'POST'
      });
      
      setMatchResult(matchData);
    } catch (err: any) {
      setError(err.message || 'Analysis failed');
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h1 className="text-2xl font-bold text-gray-900 mb-4">Job Match Analysis</h1>
        {!resumeId ? (
          <div className="bg-yellow-50 p-4 rounded-md">
            <p className="text-yellow-700">You need to upload a resume first.</p>
            <Link href="/resume" className="mt-2 inline-block font-medium text-yellow-800 hover:underline">
              Go to Resumes
            </Link>
          </div>
        ) : (
          <form onSubmit={handleAnalyze} className="space-y-4">
            <label className="block text-sm font-medium text-gray-700">Paste Job Description</label>
            <textarea
              required
              rows={8}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border"
              placeholder="Paste the full job description here..."
              value={jobText}
              onChange={(e) => setJobText(e.target.value)}
            />
            {error && <p className="text-red-500 text-sm">{error}</p>}
            <button
              type="submit"
              disabled={!jobText || analyzing}
              className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300"
            >
              {analyzing ? 'Analyzing Algorithmically...' : 'Analyze Match'}
            </button>
          </form>
        )}
      </div>

      {matchResult && (
        <div className="bg-white shadow rounded-lg p-6 border border-gray-200">
          <div className="flex items-center justify-between border-b pb-4 mb-4">
            <h2 className="text-xl font-bold text-gray-900">Match Results</h2>
            <div className="flex items-center">
              <span className="text-3xl font-extrabold text-indigo-600 mr-2">{matchResult.overall_score}%</span>
              <span className="text-sm text-gray-500 uppercase tracking-wide">Match</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h3 className="text-lg font-medium text-green-700 flex items-center mb-3">
                <CheckCircle2 className="w-5 h-5 mr-2" /> Matched Skills
              </h3>
              <ul className="space-y-2">
                {matchResult.matched_skills.map((s: string, i: number) => (
                  <li key={i} className="flex items-start text-sm text-gray-700">
                    <span className="h-1.5 w-1.5 rounded-full bg-green-500 mt-1.5 mr-2 flex-shrink-0"></span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>

            <div>
              <h3 className="text-lg font-medium text-red-700 flex items-center mb-3">
                <XCircle className="w-5 h-5 mr-2" /> Missing Skills
              </h3>
              <ul className="space-y-2">
                {matchResult.missing_skills.map((s: string, i: number) => (
                  <li key={i} className="flex items-start text-sm text-gray-700">
                    <span className="h-1.5 w-1.5 rounded-full bg-red-500 mt-1.5 mr-2 flex-shrink-0"></span>
                    {s}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="mt-8 border-t pt-6">
            <h3 className="text-lg font-medium text-yellow-700 flex items-center mb-3">
              <AlertCircle className="w-5 h-5 mr-2" /> AI Recommendations
            </h3>
            <ul className="space-y-2">
              {matchResult.recommendations.map((r: string, i: number) => (
                <li key={i} className="flex text-sm text-gray-700">
                  <span className="mr-2">•</span> {r}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}
