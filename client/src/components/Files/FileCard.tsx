import { socketClient } from "../../infrastructure/socket";
import { Markdowner } from "../Markdowner/Markdowner";
import { Modal } from "../Modal/Modal";
import { HashedFile } from "./FileUploader";
import { useEffect, useState } from "react";

type AnalysisProcessData = {
  percentage: number;
  done: boolean;
  analysis: string;
};

export const FileCard = ({
  file,
  onRemove,
}: {
  file: HashedFile;
  onRemove: () => void;
}) => {
  const [inProcessing, setInProcessing] = useState(true);
  const [showAnalysis, setShowAnalysis] = useState(false);
  const [analysis, setAnalysis] = useState("");
  useEffect(() => {
    socketClient.on(
      `analysis_process_${file.hash}`,
      (data: AnalysisProcessData) => {
        console.log(data, "DATA IN PROCESS");
        setInProcessing(!data.done);
        setAnalysis(data.analysis);
      }
    );
    return () => {
      socketClient.off(`analysis_process_${file.hash}`);
    };
  }, []);

  return (
    <div
      className={`bg-gray-200 rounded-md p-2 text-gray-900  ${
        inProcessing ? "animate-pulse" : ""
      }`}
    >
      <div
        title={file.name}
        className="flex flex-row justify-between items-center gap-2 "
      >
        <div className="text-sm ">{file.name.slice(0, 20)}</div>
        <div className="flex flex-row gap-0">
          <button
            className="text-sm bg-gray-900 text-white px-2 py-1 rounded-md cursor-pointer"
            onClick={() => setShowAnalysis(true)}
          >
            {inProcessing ? "Analizando..." : "Ver análisis"}
          </button>
          <button
            className="text-sm button-edomex text-white px-2 py-1 rounded-md cursor-pointer flex items-center justify-center "
            onClick={onRemove}
          >
            X
          </button>
        </div>
      </div>
      <Modal isOpen={showAnalysis} onClose={() => setShowAnalysis(false)}>
        <Markdowner markdown={analysis} />
      </Modal>
    </div>
  );
};
