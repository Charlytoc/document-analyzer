import { useEffect } from "react";
import { socketClient } from "./infrastructure/socket";
// import { FileUploader } from "./components/Files/FileUploader";
import { Chat } from "./components/Chat/Chat";
import { Navbar } from "./components/Navbar/Navbar";
import { useStore } from "./infrastructure/store";

function App() {
  const createClientId = useStore((state) => state.createClientId);
  const clientId = useStore((state) => state.clientId);

  useEffect(() => {
    createClientId();
  }, []);

  useEffect(() => {
    if (clientId) {
      socketClient.connect(clientId);
    }
  }, [clientId]);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <Navbar />
      <Chat />
    </div>
  );
}

export default App;
