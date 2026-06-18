import { NavLink } from "react-router-dom";

const tabBase =
  "px-4 py-2 text-sm font-mono uppercase tracking-wide border-b-2 transition-colors";
const tabActive = "border-key text-ink";
const tabInactive = "border-transparent text-dim hover:text-ink";

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-void text-ink font-body">
      <header className="border-b border-line">
        <div className="max-w-4xl mx-auto px-6 pt-8 pb-4">
          <div className="flex items-baseline justify-between flex-wrap gap-2">
            <h1 className="font-display text-2xl tracking-tight">
              CIPHER<span className="text-key">SPLIT</span>
            </h1>
            <p className="text-dim text-sm font-mono">
              split the key. not the trust.
            </p>
          </div>
          <nav className="flex gap-2 mt-6 -mb-px">
            <NavLink
              to="/encrypt"
              className={({ isActive }) =>
                `${tabBase} ${isActive ? tabActive : tabInactive}`
              }
            >
              01 / Encrypt
            </NavLink>
            <NavLink
              to="/reconstruct"
              className={({ isActive }) =>
                `${tabBase} ${isActive ? tabActive : tabInactive}`
              }
            >
              02 / Reconstruct
            </NavLink>
          </nav>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">{children}</main>

      <footer className="max-w-4xl mx-auto px-6 py-8 text-dim text-xs font-mono">
        AES-256-GCM &middot; Shamir 3-of-5 &middot; nothing leaves this
        machine unencrypted
      </footer>
    </div>
  );
}
