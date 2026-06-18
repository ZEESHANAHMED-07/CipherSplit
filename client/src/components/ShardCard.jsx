import { useState } from "react";

function truncate(str, len = 28) {
  if (str.length <= len) return str;
  return `${str.slice(0, len)}\u2026`;
}

/**
 * index: 1-5, the share's position
 * value: the raw share string
 * onDownload: optional, shows a download action (Encrypt page)
 * onRemove: optional, shows a remove action (Reconstruct page)
 * animate: stagger the entrance animation by index
 */
export default function ShardCard({
  index,
  value,
  onDownload,
  onRemove,
  animate = false,
}) {
  const [copied, setCopied] = useState(false);

  async function handleCopy() {
    await navigator.clipboard.writeText(value);
    setCopied(true);
    setTimeout(() => setCopied(false), 1500);
  }

  return (
    <div
      className="shard-clip bg-panel border border-line p-4 flex flex-col gap-2 shard-enter"
      style={animate ? { animationDelay: `${index * 60}ms` } : undefined}
    >
      <div className="flex items-center justify-between">
        <span className="font-mono text-xs text-shard uppercase tracking-wide">
          shard {index} / 5
        </span>
        {onRemove && (
          <button
            onClick={() => onRemove(index)}
            className="text-dim hover:text-danger text-xs font-mono"
            aria-label={`Remove shard ${index}`}
          >
            ✕
          </button>
        )}
      </div>

      <p className="font-mono text-xs text-dim break-all">
        {truncate(value)}
      </p>

      <div className="flex gap-3 mt-1">
        <button
          onClick={handleCopy}
          className="text-xs font-mono text-key hover:underline"
        >
          {copied ? "copied" : "copy"}
        </button>
        {onDownload && (
          <button
            onClick={() => onDownload(index, value)}
            className="text-xs font-mono text-key hover:underline"
          >
            download
          </button>
        )}
      </div>
    </div>
  );
}
