// src/api.ts
import axios from "axios";

export const API_URL = "http://localhost:8005";

export const uploadData = async (formData: FormData, clientId: string) => {
  try {
    const response = await axios.post(`${API_URL}/upload/`, formData, {
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
