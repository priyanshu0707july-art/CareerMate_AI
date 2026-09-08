"use client";

import { useState, useEffect } from 'react';
import { fetchApi } from '@/lib/api';
import { useParams, useRouter } from 'next/navigation';
import { Send, CheckCircle } from 'lucide-react';

export default function InterviewRoom() {
  const { id } = useParams();
  const router = useRouter();
  
  const [questionId, setQuestionId] = useState<number | null>(null);
  const [questionText, setQuestionText] = useState('');
  const [answer, setAnswer] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  const [evaluation, setEvaluation] = useState<any>(null);
  const [status, setStatus] = useState('IN_PROGRESS');

  useEffect(() => {
    // Load first question from session storage
    const stored = sessionStorage.getItem(`interview_${id}_q`);
    if (stored) {
      const q = JSON.parse(stored);
      setQuestionId(q.id);
      setQuestionText(q.text);
    }
  }, [id]);

  const handleSubmit = async () => {
    if (!answer.trim() || !questionId) return;
    setSubmitting(true);
    setEvaluation(null);

    try {
      const data = await fetchApi(`/interviews/${id}/answer`, {
        method: 'POST',
        body: JSON.stringify({ question_id: questionId, answer_text: answer })
      });
      
      setEvaluation(data.evaluation);
      setStatus(data.status);
      
      if (data.status === 'IN_PROGRESS') {
        // Prepare next question but wait for user to click next
        sessionStorage.setItem(`interview_${id}_q`, JSON.stringify({
          id: data.next_question_id,
          text: data.next_question
        }));
      }
    } catch (err: any) {
      alert(err.message);
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (status === 'COMPLETED') {
      router.push('/dashboard');
      return;
    }
    const stored = sessionStorage.getItem(`interview_${id}_q`);
    if (stored) {
      const q = JSON.parse(stored);
      setQuestionId(q.id);
      setQuestionText(q.text);
      setAnswer('');
      setEvaluation(null);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
        <h2 className="text-xl font-bold text-gray-900 mb-2">Question</h2>
        <p className="text-gray-800 text-lg">{questionText || "Loading..."}</p>
      </div>

      {!evaluation ? (
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200">
          <label className="block text-sm font-medium text-gray-700 mb-2">Your Answer</label>
          <textarea
            rows={8}
            className="w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-3 border"
            placeholder="Type your answer here..."
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
          />
          <div className="mt-4 flex justify-end">
            <button
              onClick={handleSubmit}
              disabled={submitting || !answer.trim()}
              className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-300"
            >
              {submitting ? 'Evaluating...' : <><Send className="w-4 h-4 mr-2" /> Submit Answer</>}
            </button>
          </div>
        </div>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow border border-gray-200 space-y-6">
          <div className="flex items-center justify-between border-b pb-4">
            <h2 className="text-xl font-bold text-green-600 flex items-center">
              <CheckCircle className="w-6 h-6 mr-2" /> Answer Evaluated
            </h2>
            <button
              onClick={handleNext}
              className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 font-medium text-sm"
            >
              {status === 'COMPLETED' ? 'Finish Interview' : 'Next Question'}
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-gray-900">{evaluation.technical_accuracy}/10</div>
              <div className="text-sm text-gray-500">Tech Accuracy</div>
            </div>
            <div className="bg-gray-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-gray-900">{evaluation.completeness}/10</div>
              <div className="text-sm text-gray-500">Completeness</div>
            </div>
            <div className="bg-gray-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-gray-900">{evaluation.clarity}/10</div>
              <div className="text-sm text-gray-500">Clarity</div>
            </div>
            <div className="bg-gray-50 p-4 rounded text-center">
              <div className="text-2xl font-bold text-gray-900">{evaluation.communication}/10</div>
              <div className="text-sm text-gray-500">Communication</div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Strengths</h3>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600">
                {evaluation.strengths?.map((s: string, i: number) => <li key={i}>{s}</li>)}
              </ul>
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 mb-2">Weaknesses</h3>
              <ul className="list-disc pl-5 space-y-1 text-sm text-gray-600">
                {evaluation.weaknesses?.map((s: string, i: number) => <li key={i}>{s}</li>)}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
