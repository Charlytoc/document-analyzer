# utils/pdf_reader.py
from abc import ABC, abstractmethod
import pdfplumber
import fitz
import os
import hashlib

PAGE_CONNECTOR = "\n---PAGE---\n"


class PDFStrategy(ABC):
    document_hash: str | None = None

    @abstractmethod
    def read(self, path: str) -> str:
        pass

    # def hash_text(self, text: str) -> str:
    #     return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def split_pages(self, text: str) -> list[str]:
        return text.split(PAGE_CONNECTOR)


class PDFPlumberStrategy(PDFStrategy):
    def read(self, path: str) -> str:
        pages = []
        with pdfplumber.open(path) as pdf:
            for page in pdf.pages:
                pages.append(page.extract_text() or "")

        text = PAGE_CONNECTOR.join(pages)

        return text


class PyMuPDFStrategy(PDFStrategy):
    def read(self, path: str) -> str:
        pages = []
        with fitz.open(path, filetype="pdf") as pdf:
            for page in pdf:
                pages.append(page.get_text())
        text = PAGE_CONNECTOR.join(pages)

        return text


class PDFReader:
    text: str | None = None

    def __init__(self, engine: str = "pymupdf"):
        self.strategy = self._get_strategy(engine)

    def _get_strategy(self, engine: str) -> PDFStrategy:
        engine = engine.lower()
        if engine == "pdfplumber":
            return PDFPlumberStrategy()
        elif engine == "pymupdf":
            return PyMuPDFStrategy()
        else:
            raise ValueError(f"Engine '{engine}' no soportado")

    def read(self, path: str) -> str:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Archivo no encontrado: {path}")
        self.text = self.strategy.read(path)
        # self.strategy.document_hash = self.strategy.hash_text(self.text)

        return self.text

    # def get_hash(self) -> str:
    #     if self.text is None:
    #         raise ValueError("El texto no ha sido leído")
    #     return self.strategy.hash_text(self.text)

    def split_pages(self, text: str) -> list[str]:
        return self.strategy.split_pages(text)
