import { useState } from "react";
import { FileInput } from "./FileInput";
import { Modal } from "../Modal/Modal";
import { uploadData } from "../../utils/api";
import { useStore } from "../../infrastructure/store";

type Props = {
  onUploadSuccess?: (hashList: HashedFile[]) => void;
};

export type HashedFile = {
  name: string;
  type: string;
  hash: string;
};

const hashFile = async (file: File): Promise<string> => {
  const buffer = await file.arrayBuffer();
  const hashBuffer = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(hashBuffer))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
};

export const FileUploader: React.FC<Props> = ({ onUploadSuccess }) => {
  const clientId = useStore((state) => state.clientId);
  const [isOpen, setIsOpen] = useState(false);
  const [images, setImages] = useState<FileList | null>(null);
  const [documents, setDocuments] = useState<FileList | null>(null);

  const handleSubmit = async (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();

    const formData = new FormData();
    const hashList: HashedFile[] = [];

    const appendFiles = async (files: FileList | null, type: string) => {
      if (!files) return;
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        const hash = await hashFile(file);
        formData.append(type, file);
        hashList.push({ name: file.name, type, hash });
      }
    };

    try {
      await appendFiles(images, "images");
      await appendFiles(documents, "documents");

      formData.append("hashes", JSON.stringify(hashList));

      await uploadData(formData, clientId as string);
      setIsOpen(false);
      if (onUploadSuccess) onUploadSuccess(hashList);
    } catch (error) {
      console.error("Error al enviar datos:", error);
    }
  };

  return (
    <>
      <button
        title="Subir archivos"
        onClick={() => setIsOpen(true)}
        className="button-edomex px-2 py-1 rounded-md"
      >
        +
      </button>
      <Modal isOpen={isOpen} onClose={() => setIsOpen(false)}>
        <form
          onSubmit={(e) => e.preventDefault()}
          className="max-w-lg p-6 rounded-lg"
        >
          <h2 className="text-3xl font-bold mb-6 text-gray-800 text-center">
            Subir Archivos
          </h2>

          <FileInput
            label="Imágenes"
            accept="image/*"
            multiple={true}
            name="images"
            onChange={setImages}
          />
          <FileInput
            label="Documentos"
            accept=".pdf,.doc,.docx,.txt"
            multiple={true}
            name="documents"
            onChange={setDocuments}
          />

          <button
            onClick={handleSubmit}
            type="submit"
            className="w-full py-2 px-4 button-edomex text-white font-semibold rounded-lg shadow-md cursor-pointer"
          >
            Listo
          </button>
        </form>
      </Modal>
    </>
  );
};
