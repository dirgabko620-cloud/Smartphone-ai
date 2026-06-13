import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import toast from 'react-hot-toast';

export default function GeneratePage() {
  const { token } = useAuth();
  const [activeTab, setActiveTab] = useState('image');
  const [imagePrompt, setImagePrompt] = useState('');
  const [codePrompt, setCodePrompt] = useState('');
  const [codeLanguage, setCodeLanguage] = useState('python');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const generateImage = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/generate/image', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt: imagePrompt,
          size: '512x512',
          model: 'stable-diffusion'
        })
      });
      const data = await response.json();
      setResult(data);
      toast.success('Image generation started!');
    } catch (error) {
      toast.error('Failed to generate image');
    } finally {
      setLoading(false);
    }
  };

  const generateCode = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/generate/code', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          prompt: codePrompt,
          language: codeLanguage,
          model: 'ollama'
        })
      });
      const data = await response.json();
      setResult(data);
      toast.success('Code generation started!');
    } catch (error) {
      toast.error('Failed to generate code');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-900 p-6">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-white mb-8">✨ AI Generation Hub</h1>

        {/* Tabs */}
        <div className="flex space-x-4 mb-8">
          <button
            onClick={() => setActiveTab('image')}
            className={`px-6 py-2 rounded font-bold transition ${
              activeTab === 'image'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            🖼️ Image Generation
          </button>
          <button
            onClick={() => setActiveTab('code')}
            className={`px-6 py-2 rounded font-bold transition ${
              activeTab === 'code'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            💻 Code Generation
          </button>
        </div>

        {/* Image Generation Tab */}
        {activeTab === 'image' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <textarea
              value={imagePrompt}
              onChange={(e) => setImagePrompt(e.target.value)}
              placeholder="Describe the image you want to generate..."
              className="w-full bg-gray-700 text-white px-4 py-3 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-600"
              rows="4"
            />
            <button
              onClick={generateImage}
              disabled={loading || !imagePrompt.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded font-bold hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Image'}
            </button>
          </div>
        )}

        {/* Code Generation Tab */}
        {activeTab === 'code' && (
          <div className="bg-gray-800 p-6 rounded-lg">
            <select
              value={codeLanguage}
              onChange={(e) => setCodeLanguage(e.target.value)}
              className="w-full bg-gray-700 text-white px-4 py-2 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-600"
            >
              <option value="python">Python</option>
              <option value="javascript">JavaScript</option>
              <option value="typescript">TypeScript</option>
              <option value="java">Java</option>
              <option value="cpp">C++</option>
              <option value="go">Go</option>
              <option value="rust">Rust</option>
            </select>
            <textarea
              value={codePrompt}
              onChange={(e) => setCodePrompt(e.target.value)}
              placeholder="Describe the code you want to generate..."
              className="w-full bg-gray-700 text-white px-4 py-3 rounded mb-4 focus:outline-none focus:ring-2 focus:ring-blue-600"
              rows="4"
            />
            <button
              onClick={generateCode}
              disabled={loading || !codePrompt.trim()}
              className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded font-bold hover:opacity-90 transition disabled:opacity-50"
            >
              {loading ? 'Generating...' : 'Generate Code'}
            </button>
          </div>
        )}

        {/* Result */}
        {result && (
          <div className="mt-8 bg-gray-800 p-6 rounded-lg">
            <h2 className="text-xl font-bold text-white mb-4">Result:</h2>
            <pre className="bg-gray-900 text-green-400 p-4 rounded overflow-x-auto">
              {JSON.stringify(result, null, 2)}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
}