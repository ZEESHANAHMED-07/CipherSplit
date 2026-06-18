# CipherSplit

split the key. not the trust.

CipherSplit encrypts an image with AES-256-GCM, then splits the decryption key into 5 fragments using Shamir's Secret Sharing (3-of-5 threshold). No single fragment, or even any 2 of them together, can decrypt anything. Any 3 of the 5 fully reconstruct the key and recover the original image.

## How it works

1. Upload an image.
2. The image is encrypted with a randomly generated AES-256 key (AES-256-GCM).
3. That key is split into 5 shares using Shamir's Secret Sharing, threshold 3.
4. The encrypted image is saved server-side. The 5 shares are returned to the client and never persisted in the database.
5. To recover the image, submit the `image_id` plus any 3 of the 5 shares. The key is reconstructed, the image is decrypted, and the original file is returned.

## Tech stack

- **Backend:** FastAPI (Python), running on port 8001
- **Crypto:** AES-256-GCM for encryption, Shamir's Secret Sharing for key splitting
- **Frontend:** React + Vite, Tailwind CSS, react-router
- **Database:** MongoDB Atlas — metadata and audit logging only
- **Storage:** local filesystem for encrypted/recovered files

## Project structure

```
CipherSplit/
  server/
    app/
      crypto/
        aes.py            AES-256-GCM encrypt/decrypt
        shares.py          Shamir's Secret Sharing split/recover
      routes/
        encrypt.py          POST /encrypt
        reconstruct.py       POST /reconstruct
      db.py               MongoDB client + collection access
      main.py              FastAPI app, CORS, startup
    storage/
      encrypted/            encrypted images live here
      recovered/             decrypted output lands here
    requirements.txt
  client/
    src/
      api/
        client.js          fetch wrapper for the backend
      components/
        Dropzone.jsx
        Layout.jsx
        ShardCard.jsx
      pages/
        Encrypt.jsx
        Reconstruct.jsx
    package.json
```

## Setup

### Backend

```powershell
cd server
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create `server/.env`:

```
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=ciphersplit
```

Run:

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

API docs available at `http://localhost:8001/docs`.

### Frontend

```powershell
cd client
npm install
```

Create `client/.env`:

```
VITE_API_URL=http://localhost:8001
```

Run:

```powershell
npm run dev
```

## API

**POST /encrypt**
multipart/form-data, field `file`.
Returns `{ image_id, threshold, total_shares, shares: [...] }`.

**POST /reconstruct**
JSON body `{ image_id, shares: [...] }`, at least 3 shares required.
Returns the decrypted image as binary.

## Security notes

Shares are never written to the database, only ever returned to the client. MongoDB stores metadata (original filename, encrypted file path, timestamps, reconstruct count), never the key material itself. Storing all 5 shares in one place would let anyone with database access reconstruct the key without needing 3 separate holders, which defeats the entire point of secret sharing.

The encrypted file lookup during reconstruction doesn't depend on the database either. Files are located on disk by `image_id` directly, so the crypto core keeps working even if MongoDB is unreachable. The database is an audit and metadata layer, not part of the trust model.

## Status

- [x] AES-256-GCM encrypt/decrypt
- [x] Shamir's Secret Sharing, 3-of-5
- [x] FastAPI backend (`/encrypt`, `/reconstruct`)
- [x] React frontend (upload, download shards, reconstruct)
- [x] MongoDB metadata + audit logging (non-blocking, doesn't gate the crypto flow)
- [ ] Scheduled cleanup for files in `storage/`
- [ ] Tighten MongoDB Atlas network access beyond `0.0.0.0/0`