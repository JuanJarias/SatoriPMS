import { Routes, Route } from 'react-router-dom';
import Conversations from './pages/Conversations';

function App() {
  return (
    <Routes>
      <Route path="/" element={<Conversations />} />
      <Route path="/conversations" element={<Conversations />} />
      {/* TODO: agregar rutas futuras: /login, /bookings, /shop, /finance, /settings */}
    </Routes>
  );
}

export default App;
