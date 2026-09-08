"use client";

import { useEffect, useState } from 'react';
import { fetchApi } from '@/lib/api';
import Link from 'next/link';
import { PlayCircle, FileText, Briefcase } from 'lucide-react';

export default function DashboardPage() {
  const [interviews, setInterviews] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const data = await fetchApi('/interviews/history');
        setInterviews(data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Welcome Back!</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-indigo-600 mr-3" />
            <h2 className="text-xl font-semibold">1. Resume</h2>
          </div>
          <p className="mt-2 text-gray-600 text-sm">Upload your latest resume to start matching with jobs.</p>
          <Link href="/resume" className="mt-4 inline-block text-indigo-600 font-medium hover:underline">
            Upload Resume &rarr;
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center">
            <Briefcase className="h-8 w-8 text-indigo-600 mr-3" />
            <h2 className="text-xl font-semibold">2. Job Match</h2>
          </div>
          <p className="mt-2 text-gray-600 text-sm">Paste a job description and let AI analyze your fit.</p>
          <Link href="/job-analysis" className="mt-4 inline-block text-indigo-600 font-medium hover:underline">
            Analyze Job &rarr;
          </Link>
        </div>

        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <div className="flex items-center">
            <PlayCircle className="h-8 w-8 text-indigo-600 mr-3" />
            <h2 className="text-xl font-semibold">3. Mock Interview</h2>
          </div>
          <p className="mt-2 text-gray-600 text-sm">Practice with adaptive AI tailored to the role.</p>
          <Link href="/mock-interview" className="mt-4 inline-block text-indigo-600 font-medium hover:underline">
            Start Interview &rarr;
          </Link>
        </div>
      </div>

      <div className="mt-10">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Recent Interviews</h2>
        {loading ? (
          <p>Loading...</p>
        ) : interviews.length === 0 ? (
          <div className="bg-white p-8 text-center rounded-lg shadow border border-gray-200 text-gray-500">
            No interviews completed yet. Ready to start practicing?
          </div>
        ) : (
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <ul className="divide-y divide-gray-200">
              {interviews.map((interview) => (
                <li key={interview.id}>
                  <div className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-indigo-600 truncate">
                        {interview.category} Mock Interview
                      </p>
                      <div className="ml-2 flex-shrink-0 flex">
                        <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${interview.status === 'COMPLETED' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                          {interview.status}
                        </p>
                      </div>
                    </div>
                    <div className="mt-2 sm:flex sm:justify-between">
                      <div className="sm:flex">
                        <p className="flex items-center text-sm text-gray-500">
                          Difficulty: {interview.difficulty}
                        </p>
                      </div>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
}
