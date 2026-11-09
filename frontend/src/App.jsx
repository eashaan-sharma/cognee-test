import { useState } from "react";
import axios from "axios";

function App() {
  const [text, setText] = useState("");
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState("");

  const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [cypher, setCypher] = useState("");
  const [queryResults, setQueryResults] = useState([]);

  const [loading, setLoading] = useState(false);

  async function handleExtract() {
    try {
      setLoading(true);

      const response = await axios.post(
        `${API_URL}/extract`,
        {
          text: text,
        }
      );

      setResult(response.data);
      setStatus("Extraction completed successfully.");
    } catch (error) {
      console.error(error);
      setStatus("Extraction failed.");
    } finally {
      setLoading(false);
    }
  }

  async function handlePopulate() {
    try {
      setLoading(true);

      const response = await axios.post(
        `${API_URL}/populate`,
        {
          text: text,
        }
      );

      setResult(response.data.graph);
      setStatus(response.data.message);
    } catch (error) {
      console.error(error);
      setStatus("Failed to populate graph.");
    } finally {
      setLoading(false);
    }
  }

  async function handleQuery() {
    try {
      setLoading(true);
      setAnswer("");
      setCypher("");
      setQueryResults([]);

      const response = await axios.post(
        `${API_URL}/query`,
        {
          question: question,
        }
      );

      setAnswer(response.data.answer);
      setCypher(response.data.cypher);
      setQueryResults(response.data.results);
      setStatus("Query executed successfully.");
    } catch (error) {
      console.error(error);
      setStatus("Query failed.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <div className="mx-auto max-w-7xl px-6 py-10">

        <header className="mb-10 text-center">
          <h1 className="text-4xl font-bold">
            Harry Potter Knowledge Graph
          </h1>

          <p className="mt-3 text-slate-400">
            AI-powered Knowledge Graph using Gemini, Neo4j, FastAPI and React
          </p>
        </header>

        <div className="grid gap-6 lg:grid-cols-2">

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold">
              Extract Knowledge
            </h2>

            <textarea
              rows={12}
              placeholder="Paste Harry Potter text here..."
              value={text}
              onChange={(e) => setText(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 p-4 text-sm outline-none focus:border-indigo-500"
            />

            <div className="mt-5 flex gap-3">

              <button
                onClick={handleExtract}
                disabled={loading}
                className="rounded-lg bg-indigo-600 px-5 py-2 font-medium transition hover:bg-indigo-500 disabled:opacity-50"
              >
                {loading ? "Working..." : "Extract"}
              </button>

              <button
                onClick={handlePopulate}
                disabled={loading}
                className="rounded-lg border border-slate-600 px-5 py-2 font-medium transition hover:bg-slate-800 disabled:opacity-50"
              >
                Populate Graph
              </button>

            </div>

          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold">
              Ask the Knowledge Graph
            </h2>

            <input
              type="text"
              placeholder="Who are Harry Potter's friends?"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              className="w-full rounded-lg border border-slate-700 bg-slate-950 p-3 outline-none focus:border-indigo-500"
            />

            <button
              onClick={handleQuery}
              disabled={loading}
              className="mt-5 rounded-lg bg-indigo-600 px-5 py-2 font-medium transition hover:bg-indigo-500 disabled:opacity-50"
            >
              {loading ? "Working..." : "Ask"}
            </button>

          </div>

        </div>

        <div className="mt-6 rounded-xl border border-slate-800 bg-slate-900 p-4">

          <span className="font-semibold text-slate-300">
            Status
          </span>

          <p className="mt-2 text-slate-400">
            {status || "Ready"}
          </p>

        </div>
        <div className="mt-6 grid gap-6">

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold">
              Extracted JSON
            </h2>

            <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-300">
{result
  ? JSON.stringify(result, null, 2)
  : "No data extracted yet."}
            </pre>

          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold">
              Answer
            </h2>

            <p className="whitespace-pre-wrap leading-7 text-slate-300">
{answer || "Ask a question to receive an answer."}
            </p>

          </div>
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold">
              Generated Cypher
            </h2>

            <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 font-mono text-sm text-green-400">
{cypher || "No query generated yet."}
            </pre>

          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6 shadow-lg">

            <h2 className="mb-4 text-xl font-semibold">
              Results
            </h2>

            <pre className="overflow-x-auto rounded-lg bg-slate-950 p-4 text-sm text-slate-300">
{queryResults.length > 0
  ? JSON.stringify(queryResults, null, 2)
  : "No results yet."}
            </pre>

          </div>

        </div>

      </div>
    </div>
  );
}

export default App;