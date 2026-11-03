import { Routes, Route } from 'react-router-dom';
import Conversations from './pages/Conversations';
import ReservasDebug from './pages/ReservasDebug';

function App() {
  return (
    <Routes>
      <Route path="/" element={<ReservasDebug />} />
      <Route path="/conversations" element={<Conversations />} />
      <Route path="/reservas-debug" element={<ReservasDebug />} />
      {/* TODO: agregar rutas futuras: /login, /bookings, /shop, /finance, /settings */}
    </Routes>
  );
}

export default App;
