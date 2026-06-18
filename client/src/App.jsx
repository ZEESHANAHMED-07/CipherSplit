import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Layout from "./components/Layout.jsx";
import Encrypt from "./pages/Encrypt.jsx";
import Reconstruct from "./pages/Reconstruct.jsx";

export default function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/encrypt" replace />} />
          <Route path="/encrypt" element={<Encrypt />} />
          <Route path="/reconstruct" element={<Reconstruct />} />
          <Route path="*" element={<Navigate to="/encrypt" replace />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}
