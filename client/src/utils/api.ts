// src/api.ts
import axios from "axios";

export const API_URL = "http://localhost:8005";

export const generateSentenceBrief = async (formData: FormData) => {
  try {
    const response = await axios.post(
      `${API_URL}/api/generate-sentence-brief`,
      formData
    );
    return response.data;
  } catch (error) {
    console.error("Error al generar resumen de la sentencia:", error);
    throw new Error("Hubo un error al generar el resumen de la sentencia");
  }
};

export const uploadData = async (formData: FormData, clientId: string) => {
  try {
    const response = await axios.post(`${API_URL}/api/upload/`, formData, {
      headers: {
        "client-id": clientId,
      },
    });
    return response.data;
  } catch (error) {
    console.error("Error al enviar datos:", error);
    throw new Error("Hubo un error al enviar los datos");
  }
};
