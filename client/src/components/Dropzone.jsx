import { useRef, useState } from "react";

export default function Dropzone({ file, onFile, accept = "image/*" }) {
  const inputRef = useRef(null);
  const [dragging, setDragging] = useState(false);

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped) onFile(dropped);
  }

  const previewUrl = file ? URL.createObjectURL(file) : null;

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDragging(true);
      }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      className={`border-2 border-dashed rounded-md p-8 text-center cursor-pointer transition-colors
        ${dragging ? "border-key bg-raised" : "border-line bg-panel hover:border-dim"}`}
    >
      <input
        ref={inputRef}
        type="file"
        accept={accept}
        className="hidden"
        onChange={(e) => {
          const selected = e.target.files?.[0];
          if (selected) onFile(selected);
        }}
      />

      {file ? (
        <div className="flex items-center gap-4 text-left">
          <img
            src={previewUrl}
            alt="Selected"
            className="w-16 h-16 object-cover rounded shard-clip"
          />
          <div>
            <p className="font-mono text-sm text-ink">{file.name}</p>
            <p className="font-mono text-xs text-dim">
              {(file.size / 1024).toFixed(1)} KB &middot; click to replace
            </p>
          </div>
        </div>
      ) : (
        <div>
          <p className="font-mono text-sm text-ink">
            drop an image here, or click to browse
          </p>
          <p className="font-mono text-xs text-dim mt-1">PNG, JPG, WEBP</p>
        </div>
      )}
    </div>
  );
}
