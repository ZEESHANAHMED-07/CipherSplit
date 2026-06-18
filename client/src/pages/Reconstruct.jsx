import { useEffect, useRef, useState } from "react";
import { reconstructImage } from "../api/client.js";

const MIN_SHARDS = 3;
const MAX_SHARDS = 5;

export default function Reconstruct() {
  const [imageId, setImageId] = useState("");
  const [shards, setShards] = useState(Array(MIN_SHARDS).fill(""));
  const [status, setStatus] = useState("idle"); // idle | working | done | error
  const [error, setError] = useState(null);
  const [recoveredUrl, setRecoveredUrl] = useState(null);
  const [justUnlocked, setJustUnlocked] = useState(false);
  const fileInputs = useRef([]);

  const loadedCount = shards.filter((s) => s.trim().length > 0).length;
  const thresholdMet = loadedCount >= MIN_SHARDS;
  const canSubmit = imageId.trim().length > 0 && thresholdMet;

  useEffect(() => {
    if (thresholdMet) {
      setJustUnlocked(true);
      const t = setTimeout(() => setJustUnlocked(false), 650);
      return () => clearTimeout(t);
    }
  }, [thresholdMet]);

  function updateShard(i, value) {
    setShards((prev) => {
      const next = [...prev];
      next[i] = value;
      return next;
    });
  }

  function addSlot() {
    if (shards.length < MAX_SHARDS) setShards((prev) => [...prev, ""]);
  }

  function removeSlot(i) {
    if (shards.length <= MIN_SHARDS) return;
    setShards((prev) => prev.filter((_, idx) => idx !== i));
  }

  function handleFileLoad(i, file) {
    const reader = new FileReader();
    reader.onload = () => updateShard(i, String(reader.result).trim());
    reader.readAsText(file);
  }

  async function handleReconstruct() {
    setStatus("working");
    setError(null);
    try {
      const nonEmpty = shards.map((s) => s.trim()).filter(Boolean);
      const url = await reconstructImage(imageId.trim(), nonEmpty);
      setRecoveredUrl(url);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  }

  function reset() {
    setImageId("");
    setShards(Array(MIN_SHARDS).fill(""));
    setStatus("idle");
    setError(null);
    setRecoveredUrl(null);
  }

  return (
    <div className="flex flex-col gap-8">
      <div>
        <h2 className="font-display text-lg mb-1">reconstruct</h2>
        <p className="text-dim text-sm">
          Enter the image ID and any {MIN_SHARDS} of the 5 shards. The key
          rebuilds and the original image decrypts.
        </p>
      </div>

      {status !== "done" && (
        <>
          <div>
            <label className="block font-mono text-xs text-dim mb-2 uppercase tracking-wide">
              image_id
            </label>
            <input
              type="text"
              value={imageId}
              onChange={(e) => setImageId(e.target.value)}
              placeholder="paste the image_id from the encrypt step"
              className="w-full bg-panel border border-line px-4 py-3 font-mono text-sm text-ink
                placeholder:text-dim focus:border-key outline-none"
            />
          </div>

          <div
            className={`flex items-center justify-between rounded p-3 border transition-colors
              ${thresholdMet ? "border-key bg-raised" : "border-line bg-panel"}
              ${justUnlocked ? "lock-pulse" : ""}`}
          >
            <span className="font-mono text-xs uppercase tracking-wide">
              {loadedCount} / {MIN_SHARDS} shards loaded
              {thresholdMet ? " — threshold met" : ""}
            </span>
            {thresholdMet && <span className="text-key text-sm">●</span>}
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {shards.map((value, i) => (
              <div
                key={i}
                className="shard-clip bg-panel border border-line p-4 flex flex-col gap-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-mono text-xs text-shard uppercase tracking-wide">
                    shard {i + 1}
                  </span>
                  {shards.length > MIN_SHARDS && (
                    <button
                      onClick={() => removeSlot(i)}
                      className="text-dim hover:text-danger text-xs font-mono"
                      aria-label={`Remove shard slot ${i + 1}`}
                    >
                      ✕
                    </button>
                  )}
                </div>

                <textarea
                  value={value}
                  onChange={(e) => updateShard(i, e.target.value)}
                  placeholder="paste shard text here"
                  rows={2}
                  className="w-full bg-void border border-line px-2 py-1.5 font-mono text-xs text-ink
                    placeholder:text-dim focus:border-key outline-none resize-none"
                />

                <button
                  onClick={() => fileInputs.current[i]?.click()}
                  className="text-xs font-mono text-key hover:underline self-start"
                >
                  or load from file
                </button>
                <input
                  ref={(el) => (fileInputs.current[i] = el)}
                  type="file"
                  accept=".txt,.json"
                  className="hidden"
                  onChange={(e) => {
                    const f = e.target.files?.[0];
                    if (f) handleFileLoad(i, f);
                  }}
                />
              </div>
            ))}
          </div>

          {shards.length < MAX_SHARDS && (
            <button
              onClick={addSlot}
              className="self-start text-xs font-mono text-dim hover:text-ink"
            >
              + add another shard slot
            </button>
          )}

          <button
            onClick={handleReconstruct}
            disabled={!canSubmit || status === "working"}
            className="self-start px-6 py-3 font-mono text-sm uppercase tracking-wide bg-key text-void
              disabled:bg-line disabled:text-dim disabled:cursor-not-allowed
              hover:bg-opacity-90 transition-colors"
          >
            {status === "working" ? "reconstructing..." : "reconstruct image"}
          </button>

          {status === "error" && (
            <p className="text-danger font-mono text-sm">
              reconstruction failed — {error}
            </p>
          )}
        </>
      )}

      {status === "done" && recoveredUrl && (
        <div className="flex flex-col gap-4">
          <p className="font-mono text-xs text-key uppercase tracking-wide">
            key rebuilt — image decrypted
          </p>
          <img
            src={recoveredUrl}
            alt="Recovered"
            className="max-w-full rounded border border-line shard-clip"
          />
          <div className="flex gap-4">
            <a
              href={recoveredUrl}
              download={`${imageId.trim() || "recovered"}.png`}
              className="px-5 py-2.5 font-mono text-sm uppercase tracking-wide border border-key text-key hover:bg-key hover:text-void transition-colors"
            >
              download image
            </a>
            <button
              onClick={reset}
              className="px-5 py-2.5 font-mono text-sm uppercase tracking-wide text-dim hover:text-ink transition-colors"
            >
              reconstruct another
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
