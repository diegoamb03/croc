import os
import json
import fitz  # PyMuPDF
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from decimal import Decimal
from typing import Optional, List

load_dotenv()
# Se define los modelos de datos para la salida estructurada
class InvoiceLine(BaseModel):
    numero_pedido: Optional[str] = Field(None, description="Identificador del pedido/orden")
    id_producto: Optional[int] = Field(None, ge=0, description="Identificador del producto (entero no negativo)")
    descripcion: str = Field(None, description="Descripción del producto")
    cantidad: int = Field(None, description="Cantidad vendida del producto")
    unidad_de_medida: Optional[str] = Field(None, description="Unidad de medida (ej: 'UN', 'PQ')")
    costo_unitario: Decimal = Field(..., description="Costo unitario / precio unitario (Decimal)")
    importe: Decimal = Field(..., description="Importe neto de la línea (cantidad * costo_unitario)")

class Invoice(BaseModel):
    cliente: str = Field(..., description="Nombre o razón social del cliente")
    nit_cliente: Optional[str] = Field(None, description="NIT o identificación fiscal")
    numero_factura: Optional[str] = Field(None, description="Identificador de la factura")
    fecha_de_orden: str = Field(..., description="Fecha de la orden (YYYY-MM-DD)")
    fecha_de_entrega: Optional[str] = Field(None, description="Fecha de entrega prevista/real (YYYY-MM-DD)")
    sub_total: Decimal = Field(..., description="Sub-total de la factura")
    iva: Decimal = Field(..., description="IVA aplicado a la factura")
    total: Decimal = Field(..., description="Total de la factura (sub_total + iva)")
    items: List[InvoiceLine] = Field(..., description="Lista de items de la factura")

#
class OCRPipelineError(Exception):
    """Custom exception for OCR pipeline errors."""
    pass

class OCRPipeline:
    def __init__(self, pdf_path: str = "") -> None:
        self.pdf_path = Path(pdf_path) if pdf_path else None
        if self.pdf_path and not self.pdf_path.exists():
            raise OCRPipelineError(f"PDF file not found: {pdf_path}")

    def extract_text_data(self, pdf_path: Optional[str] = None) -> List[dict]:
        file_path = Path(pdf_path) if pdf_path else self.pdf_path
        flat_data = []
        try:
            doc = fitz.open(file_path)
            for page_num in range(doc.page_count):
                # get_text("words") devuelve una lista de [x0, y0, x1, y1, "palabra", block_no, line_no, word_no]
                words_on_page = doc[page_num].get_text("words")
                for word_info in words_on_page:
                    flat_data.append({
                        'page': page_num + 1,
                        'text': word_info[4],
                        'block_no': word_info[5]
                    })
            return flat_data
        except Exception as e:
            print(f"Error al procesar el archivo PDF: {e}")
            return []
        finally:
            if 'doc' in locals() and doc:
                doc.close()

    @staticmethod
    def structure_to_json(estructura: List[dict]) -> dict:
        paginas_agrupadas = defaultdict(lambda: defaultdict(list))
        if not estructura:
            return {}
        for item in estructura:
            paginas_agrupadas[item['page']][item['block_no']].append(item['text'])

        # 3. Formatear los datos agrupados a la estructura de salida final.
        resultado_final = {}
        # Ordenamos las páginas por su número.
        for page_num, blocks in sorted(paginas_agrupadas.items()):
            # Creamos la clave del diccionario final, ej: "page_1".
            clave_pagina = f"page_{page_num}"
            resultado_final[clave_pagina] = []
    
            # Ordenamos las líneas por su 'block_no'.
            for line_num, words in sorted(blocks.items()):
                # Unimos las palabras para formar el texto completo de la línea.
                texto_linea = " | ".join(words)
        
                # Creamos la clave para la línea, ej: "line_1", "line_2".
                # Sumamos 1 porque los bloques empiezan en 0.
                clave_linea = f"line_{line_num + 1}"
                resultado_final[clave_pagina].append({clave_linea: texto_linea})
            
        return resultado_final
    
    @staticmethod
    def structure_to_markdown(structured_data: dict) -> str:
        processed_pages = []
        # Sort pages by number
        sorted_pages = sorted(structured_data.keys(), key=lambda p: int(p.split('_')[1]))
        
        for page_key in sorted_pages:
            page_lines = structured_data[page_key]
            
            # Extract text content from each line dictionary
            page_content = []
            for line_dict in page_lines:
                # Get the first (and only) value from the dictionary
                line_text = next(iter(line_dict.values()))
                if line_text.strip():  # Only add non-empty lines
                    page_content.append(line_text)
            
            if page_content:  # Only add pages with content
                processed_pages.append("\n".join(page_content))

        page_separator = "\n\n--- PAGE BREAK ---\n\n"
        return page_separator.join(processed_pages)
    
    def process_pdf_to_markdown(self, pdf_path: Optional[str] = None) -> str:
        try:
            word_data = self.extract_text_data(pdf_path)
            structured_data = self.structure_to_json(word_data)
            return self.structure_to_markdown(structured_data)
        except OCRPipelineError:
            raise
        except Exception as e:
            raise OCRPipelineError(f"Pipeline processing failed: {e}")
#
class LLMPipeline:
    def __init__(self, model_name: str = "gemini-2.0-flash") -> None:
        self.api_key = "AIzaSyD020WDsn1hX8ACAQNIGYw6XarqONt79V0"
        self.model_name = model_name

    def llm_extract_invoice_data(self, invoice_text: str) -> Invoice:
        prompt = f"""
            Eres un extractor experto que devuelve SOLO JSON válido y estricto. No escribas nada fuera del JSON (ni explicaciones, ni texto adicional).

            Contexto:
            - Empresa: CROC S.A.S (NIT: 830125610 / 830125610-1). Empresa de alimentos.
            - El documento es una factura de venta.
            - El texto de entrada está en Markdown.

            Reglas de extracción y formato (obligatorias):
            1. Devuelve JSON que respete el esquema exacto. Si un campo falta en el texto, pon `null`.
            2. No inventes datos: si no aparece en el texto, devuelve `null`.
            3. Responde **solo** con JSON.

            Entrada:
            --- INICIO DEL TEXTO DE LA FACTURA ---
            {invoice_text}
            --- FIN DEL TEXTO DE LA FACTURA ---
            """
        # Llamada al modelo
        client = genai.Client(api_key=self.api_key)
        response = client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                max_output_tokens=1200, # Ajusta según sea necesario
                temperature=0,
                response_mime_type='application/json',
                response_schema=Invoice))
        #
        if not response.text:
            print("La respuesta del modelo es None o vacía. Revisa la configuración y el API Key.")
            return None
        try:
            return json.loads(response.text)
        except json.JSONDecodeError as e:
            print(f"Respuesta no es JSON válido: {e}")
            return response.text

if __name__ == "__main__":
    pipeline = OCRPipeline(r"C:\Users\Lenovo\Downloads\scripts\dev_desarrollo_pdf\ENTREMES.pdf")
    markdown_result = pipeline.process_pdf_to_markdown()
    # Llamada al LLM
    llm_pipeline = LLMPipeline()
    invoice_data = llm_pipeline.llm_extract_invoice_data(markdown_result)
    print(invoice_data)