import { useEffect, useState, useRef } from "react";
import { socketClient } from "../../infrastructure/socket";
import { FileUploader, HashedFile } from "../Files/FileUploader";
import { Message, TMessage } from "./Message";
import toast from "react-hot-toast";
import { useStore } from "../../infrastructure/store";
import { FileCard } from "../Files/FileCard";

const defaultMessages: TMessage[] = [
  {
    role: "assistant",
    content:
      "¡Hola! Soy el **Analista de sentencias** del [Poder Judicial del Estado de México](https://www.pjedomex.gob.mx/). Estoy aquí para ayudarte a entender cualquier sentencia.",
  },
  {
    role: "assistant",
    content:
      "Por favor **sube los archivos** de la sentencia que quieres analizar.",
  },
];

export const Chat = () => {
  const [messages, setMessages] = useState<TMessage[]>(defaultMessages);
  const [files, setFiles] = useState<HashedFile[]>([]);
  const textAreaRef = useRef<HTMLTextAreaElement>(null);
  const clientId = useStore((state) => state.clientId);

  useEffect(() => {
    if (!socketClient.isConnected() && clientId) {
      socketClient.connect(clientId);
    }

    socketClient.on("message_response", (data) => {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.message },
      ]);
    });

    return () => {
      socketClient.off("message_response");
    };
  }, [clientId]);

  const handleSendMessage = () => {
    const message = textAreaRef.current?.value.trim();
    if (!message) return;

    if (files.length === 0) {
      toast.error("Sube al menos un archivo para continuar");
      return;
    }

    socketClient.emit("message", {
      prompt: message,
      messages: messages,
      files: files,
      client_id: clientId,
    });
    setMessages((prev) => [...prev, { role: "user", content: message }]);
    textAreaRef.current!.value = "";
  };

  const handleUploadSuccess = (hashList: HashedFile[]) => {
    const newFilesSet = new Set([...files, ...hashList]);
    const newFiles = Array.from(newFilesSet);
    setFiles(newFiles);
  };

  return (
    <div className="h-[80vh] flex flex-col overflow-hidden w-full">
      <div className="flex flex-col overflow-auto p-1 w-full gap-1 pb-50 no-scrollbar">
        {messages.map((message, index) => (
          <Message key={index} message={message} />
        ))}
      </div>

      <div className="fixed bottom-0 left-0 w-full bg-white border-t border-gray-300 p-2 flex flex-col items-center gap-2">
        {files.length > 0 && (
          <div className="flex flex-row gap-2 w-full overflow-x-auto no-scrollbar">
            {files.map((file) => (
              <FileCard
                file={file}
                key={file.hash}
                onRemove={() => {
                  setFiles(files.filter((f) => f.hash !== file.hash));
                }}
              />
            ))}
          </div>
        )}
        <div className="flex flex-row gap-2 w-full items-center">
          <textarea
            name="prompt"
            ref={textAreaRef}
            className="flex-1 border border-gray-300 rounded-md p-2 resize-none h-20 text-gray-900"
            placeholder="Escribe tu pregunta..."
            onKeyUp={(e) => {
              if (e.key === "Enter" && !e.shiftKey) {
                e.preventDefault();
                handleSendMessage();
              }
            }}
          />
          <div className="flex flex-col gap-1">
            {files.length > 0 && (
              <button
                title="Enviar"
                onClick={handleSendMessage}
                className="button-edomex px-2 py-1 rounded-md"
              >
                ➡
              </button>
            )}
            <FileUploader onUploadSuccess={handleUploadSuccess} />
          </div>
        </div>
      </div>
    </div>
  );
};
