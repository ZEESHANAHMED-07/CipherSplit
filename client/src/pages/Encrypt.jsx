import { useState } from "react";
import Dropzone from "../components/Dropzone.jsx";
import ShardCard from "../components/ShardCard.jsx";
import { encryptImage } from "../api/client.js";

export default function Encrypt() {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState("idle"); // idle | working | done | error
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null); // { image_id, shares }

  async function handleEncrypt() {
    if (!file) return;
    setStatus("working");
    setError(null);
    try {
      const data = await encryptImage(file);
      setResult(data);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  function downloadShard(index, value) {
    const blob = new Blob([value], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${result.image_id}_shard_${index}_of_5.txt`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function downloadAllShards() {
    result.shares.forEach((value, i) => downloadShard(i + 1, value));
  }

  function reset() {
    setFile(null);
    setResult(null);
    setStatus("idle");
    setError(null);
  }

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h2 className="font-display text-lg mb-1">encrypt &amp; split</h2>
        <p className="text-dim text-sm">
          Upload an image. It gets encrypted with AES-256-GCM, and the key is
          split into 5 shards — any 3 reconstruct it, no 2 do.
        </p>
      </div>

      {status !== "done" && (
        <>
          <Dropzone file={file} onFile={setFile} />

          <button
            onClick={handleEncrypt}
            disabled={!file || status === "working"}
            className="self-start px-6 py-3 font-mono text-sm uppercase tracking-wide bg-key text-void
              disabled:bg-line disabled:text-dim disabled:cursor-not-allowed
              hover:bg-opacity-90 transition-colors"
          >
            {status === "working" ? "encrypting..." : "encrypt & split"}
          </button>

          {status === "error" && (
            <p className="text-danger font-mono text-sm">
              encryption failed — {error}
            </p>
          )}
        </>
      )}

      {status === "done" && result && (
        <div className="flex flex-col gap-6">
          <div className="bg-panel border border-line p-4">
            <p className="font-mono text-xs text-dim mb-1">image_id</p>
            <p className="font-mono text-sm text-ink break-all">
              {result.image_id}
            </p>
          </div>

          <div>
            <p className="font-mono text-xs text-dim mb-3 uppercase tracking-wide">
              5 shards — keep them somewhere they can't all be lost together
            </p>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {result.shares.map((value, i) => (
                <ShardCard
                  key={i}
                  index={i + 1}
                  value={value}
                  onDownload={downloadShard}
                  animate
                />
              ))}
            </div>
          </div>

          <div className="flex gap-4">
            <button
              onClick={downloadAllShards}
              className="px-5 py-2.5 font-mono text-sm uppercase tracking-wide border border-key text-key hover:bg-key hover:text-void transition-colors"
            >
              download all 5
            </button>
            <button
              onClick={reset}
              className="px-5 py-2.5 font-mono text-sm uppercase tracking-wide text-dim hover:text-ink transition-colors"
            >
              encrypt another
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
