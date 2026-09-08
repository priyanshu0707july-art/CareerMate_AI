"use client";

import { useState, useEffect } from 'react';
import { fetchApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { Play } from 'lucide-react';

export default function MockInterviewSetup() {
  const [resumes, setResumes] = useState<any[]>([]);
  const [jobs, setJobs] = useState<any[]>([]);
  const [selectedResume, setSelectedResume] = useState('');
  const [selectedJob, setSelectedJob] = useState('');
  const [category, setCategory] = useState('General');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  useEffect(() => {
    async function loadData() {
      try {
        const rData = await fetchApi('/resumes/');
        const jData = await fetchApi('/jobs/');
        setResumes(rData || []);
        setJobs(jData || []);
        
        if (rData && rData.length > 0) setSelectedResume(rData[0].id);
        if (jData && jData.length > 0) setSelectedJob(jData[0].id);
      } catch (e) {}
    }
    loadData();
  }, []);

  const handleStart = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await fetchApi('/interviews/start', {
        method: 'POST',
        body: JSON.stringify({
          resume_id: parseInt(selectedResume),
          job_id: parseInt(selectedJob),
          category
        })
      });
      // Save first question in session storage to avoid extra fetch
      sessionStorage.setItem(`interview_${data.interview_id}_q`, JSON.stringify({
        id: data.first_question_id,
        text: data.first_question
      }));
      router.push(`/mock-interview/${data.interview_id}`);
    } catch (err: any) {
      alert(err.message);
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white p-8 rounded-lg shadow border border-gray-200">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Start Mock Interview</h1>
      
      <form onSubmit={handleStart} className="space-y-6">
        <div>
          <label className="block text-sm font-medium text-gray-700">Select Resume</label>
          <select 
            value={selectedResume} 
            onChange={(e) => setSelectedResume(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          >
            {resumes.map(r => (
              <option key={r.id} value={r.id}>Resume #{r.id} - {new Date(r.created_at).toLocaleDateString()}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Select Job Description</label>
          <select 
            value={selectedJob} 
            onChange={(e) => setSelectedJob(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          >
            {jobs.map(j => (
              <option key={j.id} value={j.id}>Job #{j.id}</option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700">Focus Category</label>
          <select 
            value={category} 
            onChange={(e) => setCategory(e.target.value)}
            className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md border"
          >
            <option>General</option>
            <option>Python</option>
            <option>System Design</option>
            <option>Behavioral</option>
            <option>Data Structures</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={!selectedResume || !selectedJob || loading}
          className="w-full flex justify-center py-3 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300"
        >
          {loading ? 'Initializing AI...' : <><Play className="w-5 h-5 mr-2" /> Start Interview</>}
        </button>
      </form>
    </div>
  );
}
