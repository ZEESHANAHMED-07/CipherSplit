const BASE_URL = import.meta.env.VITE_API_URL;

if (!BASE_URL) {
  // Loud on purpose. A silent missing env var turns into a confusing
  // "network error" on the first click instead of a clear message here.
  console.error(
    "VITE_API_URL is not set. Copy .env.example to .env and restart `npm run dev`."
  );
}

/**
 * ASSUMPTIONS ABOUT THE BACKEND CONTRACT
 * ---------------------------------------------------------------------
 * These match the most common FastAPI pattern for this kind of endpoint.
 * If your actual /encrypt or /reconstruct signatures differ, this is the
 * one file to edit — everything else consumes the two functions below.
 *
 * POST /encrypt
 *   request:  multipart/form-data, field name "file"
 *   response: JSON { image_id: string, shares: string[] }   (5 strings)
 *
 * POST /reconstruct
 *   request:  JSON { image_id: string, shares: string[] }   (>= 3 strings)
 *   response: raw image bytes (Content-Type: image/*)
 * ---------------------------------------------------------------------
 */

export async function encryptImage(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await fetch(`${BASE_URL}/encrypt`, {
    method: "POST",
    body: form,
  });

  if (!res.ok) {
    const detail = await safeErrorDetail(res);
    throw new Error(detail || `Encrypt failed with status ${res.status}`);
  }

  const data = await res.json();

  if (!data.image_id || !Array.isArray(data.shares)) {
    throw new Error(
      "Unexpected response shape from /encrypt. Check api/client.js assumptions against your backend."
    );
  }

  return data; // { image_id, shares }
}

export async function reconstructImage(imageId, shares) {
  const res = await fetch(`${BASE_URL}/reconstruct`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image_id: imageId, shares }),
  });

  if (!res.ok) {
    const detail = await safeErrorDetail(res);
    throw new Error(detail || `Reconstruct failed with status ${res.status}`);
  }

  const blob = await res.blob();
  return URL.createObjectURL(blob);
}

async function safeErrorDetail(res) {
  try {
    const body = await res.json();
    return body.detail || body.message || null;
  } catch {
    return null;
  }
}
