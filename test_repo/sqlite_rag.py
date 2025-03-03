import os
import asyncio
import sqlite3
import json
from typing import List, Dict, Any
from dotenv import load_dotenv
from openai import AsyncOpenAI
from chunking import CustomChunking
from batch_embedding import AsyncEmbeddingGenerator
from database_handler import DatabaseHandler
from csv_writer import CSVWriter
from result_database import ResultDatabase
import logging
from config import (
    SOW_FIELDS_TO_EXTRACT, 
    SOW_POINTS_TO_REMEMBER, 
    SOW_QUERIES, 
    SOW_QUERY_FOR_EACH_FIELD, 
    MSA_FIELDS_TO_EXTRACT, 
    MSA_POINTS_TO_REMEMBER, 
    MSA_QUERIES, 
    MSA_QUERY_FOR_EACH_FIELD
)
from schemas import (
    client_company_name_schema,
    currency_schema,
    start_date_schema,
    end_date_schema,
    info_security_schema,
    limitation_of_liability_schema,
    data_processing_agreement_schema,
    insurance_required_schema,
    cola_schema,
    credit_period_schema,
    inclusive_or_exclusive_gst_schema,
    sow_value_schema,
    sow_no_schema,
    type_of_billing_schema,
    po_number_schema,
    amendment_no_schema,
    billing_unit_type_and_rate_cost_schema,
    particular_role_rate_schema,
)

class SQLiteOpenAIRAG:
    def __init__(self, db_path: str = "vector_store.db"):
        load_dotenv()
        self.db_path = db_path
        # self._init_db()
        self.db_handler = DatabaseHandler(db_path)
        self.db_handler._init_db()
        self.async_client = AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            timeout=60.0,
            max_retries=3
        )

    def format_chunks_to_xml(self, chunks: List[Dict]) -> str:
        """Format chunks into XML structure for better LLM processing."""
        xml_parts = ['<CONTENT>']
        
        for i, chunk in enumerate(chunks, 1):
            xml_parts.extend([
                f'<CHUNK_{i}>',
                '<PAGE_NUMBER>',
                str(chunk['page_number']),
                '</PAGE_NUMBER>',
                '<CHUNK_CONTENT>',
                chunk['chunk'].strip(),
                '</CHUNK_CONTENT>',
                f'</CHUNK_{i}>'
            ])
        
        xml_parts.append('</CONTENT>')
        return '\n'.join(xml_parts)

    async def extract_field_value(self, field: str, chunks: List[Dict], doc_type: str = "MSA") -> Dict[str, Any]:
        """Extract field value from chunks using gpt-4."""
        try:
            if not chunks:
                return {
                    "field_value": "",
                    "page_number": "",
                    "confidence": 0,
                    "reasoning": "No relevant chunks found",
                    "proof": ""
                }

            # Format chunks into XML structure
            chunks_content = self.format_chunks_to_xml(chunks)
            
            # Select configuration based on document type
            queries = MSA_QUERIES if doc_type == "MSA" else SOW_QUERIES
            query_for_field = MSA_QUERY_FOR_EACH_FIELD if doc_type == "MSA" else SOW_QUERY_FOR_EACH_FIELD
            points_to_remember = MSA_POINTS_TO_REMEMBER if doc_type == "MSA" else SOW_POINTS_TO_REMEMBER
            
            # Get field-specific configurations
            field_query = query_for_field.get(field, queries.get(field, [f"Extract the {field} from the contract"])[0])
            field_points = points_to_remember.get(field, "")
            
            # Get the corresponding schema
            schema_name = f"{field}_schema"
            if schema_name in globals():
                schema = globals()[schema_name]
            else:
                print(f"Warning: No schema found for field {field}, using default schema")

                # -----------PLACE YOUR DEFAULT SCHEMA HERE-----------

            # Prepare the prompt
            context = f"""
                You are a contract analysis expert. Extract information accurately and provide confidence levels and reasoning.
                Always return your response in the exact JSON format specified, with all required fields.

                Extract the {field} from the following contract text.

                The response must include:
                1. field_value: The extracted value
                2. page_number: The page where the information was found
                3. confidence: A number between 1-10 indicating confidence level
                4. reasoning: Clear explanation of why this value was extracted
                5. proof: The exact text from the contract supporting this extraction

                Contract Text:
                {chunks_content}
            """
            
            # Make API call with JSON mode
            response = await self.async_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": """You are a contract analysis expert. Extract information accurately and provide confidence levels and reasoning.
                    Always return your response in the exact JSON format specified, with all required fields."""},
                    {"role": "user", "content": context}
                ],
                response_format={"type": "json_schema", "json_schema": schema},
            )
            
            # Parse and validate the response
            try:
                result = json.loads(response.choices[0].message.content)
                
                # Ensure all required fields are present with correct types
                if "field_value" not in result:
                    result["field_value"] = ""
                if "page_number" not in result:
                    result["page_number"] = ""
                if "confidence" not in result:
                    result["confidence"] = 1
                if "reasoning" not in result:
                    result["reasoning"] = "No reasoning provided"
                if "proof" not in result:
                    result["proof"] = ""
                
                # Convert old confidence format (high/medium/low) to numeric if needed
                if isinstance(result["confidence"], str):
                    confidence_map = {"high": 9, "medium": 6, "low": 3}
                    result["confidence"] = confidence_map.get(result["confidence"].lower(), 1)

                # make a clean separator, then for each field print field_value, page_number, confidence, reasoning, proof
                if field == "insurance_required":
                    insurance_data = result['field_value']
                    print("\n\nInsurance Details:")
                    print(f"Insurance Required: {insurance_data['insurance_required']}")
                    print(f"Types of Insurance: {', '.join(insurance_data['type_of_insurance_required']) if insurance_data['type_of_insurance_required'] else 'None'}")
                    print(f"Cyber Insurance Required: {insurance_data['is_cyber_insurance_required']}")
                    print(f"Cyber Insurance Amount: ${insurance_data['cyber_insurance_amount']}")
                    print(f"Workman's Compensation Insurance Required: {insurance_data['is_workman_compensation_insurance_required']}")
                    print(f"Workman's Compensation Insurance Amount: ${insurance_data['workman_compensation_insurance_amount']}")
                    print(f"Other Insurance Required: {', '.join(insurance_data['other_insurance_required']) if insurance_data['other_insurance_required'] else 'None'}")
                    if insurance_data['other_insurance_amount']['insurance_details']:
                        print("Other Insurance Details:")
                        for detail in insurance_data['other_insurance_amount']['insurance_details']:
                            print(f"  - {detail['insurance_type']}: ${detail['amount']}")
                    else:
                        print("No Other Insurance Details")
                                

                print(f"\n\n--- {field} ---")
                print(f"field_value: {result['field_value']}, \npage_number: {result['page_number']}, \nconfidence: {result['confidence']}, \nreasoning: {result['reasoning']}, \nproof: {result['proof']}")
                print(f"\n\n")
                
                return result
                
            except json.JSONDecodeError as e:
                print(f"Error parsing GPT response for field {field}: {str(e)}")
                return {
                    "field_value": "",
                    "page_number": "",
                    "confidence": 1,
                    "reasoning": f"Error: Failed to parse GPT response - {str(e)}",
                    "proof": ""
                }
                
        except Exception as e:
            print(f"Error during extraction for field {field}: {str(e)}")
            return {
                "field_value": "",
                "page_number": "",
                "confidence": 1,
                "reasoning": f"Error during extraction: {str(e)}",
                "proof": ""
            }

    async def process_field(self, field: str, doc_type: str = "MSA") -> Dict[str, Any]:
        """Process a single field by getting relevant chunks and extracting value."""
        try:
            # Get relevant chunks for all queries for this field
            queries = MSA_QUERIES if doc_type == "MSA" else SOW_QUERIES
            field_queries = queries.get(field, [f"Extract the {field} from the contract"])
            
            chunk_tasks = []
            for query in field_queries:
                chunk_tasks.append(self.db_handler.get_relevant_chunks (
                    query,
                    async_client=self.async_client,
                    k=3
                ))
            
            # Get all chunks in parallel
            chunks_results = await asyncio.gather(*chunk_tasks)
            
            # Combine and deduplicate chunks
            all_chunks = []
            seen_chunks = set()
            for chunks in chunks_results:
                for chunk in chunks:
                    chunk_text = chunk["chunk"]
                    if chunk_text not in seen_chunks:
                        seen_chunks.add(chunk_text)
                        all_chunks.append(chunk)
            
            # Extract value from chunks
            try:
                value = await self.extract_field_value(field, all_chunks, doc_type)
                if not isinstance(value, dict) or "field_value" not in value:
                    value = {
                        "field_value": "",
                        "page_number": "",
                        "confidence": 1,
                        "reasoning": "Error: Invalid response format",
                        "proof": ""
                    }
            except Exception as e:
                print(f"Error extracting value for field {field}: {str(e)}")

            return {
                "field": field,
                "value": value,
            }
        except Exception as e:
            print(f"Error processing field '{field}': {str(e)}")
            return {
                "field": field,
                "value": {
                    "field_value": "",
                    "page_number": "",
                    "confidence": 1,
                    "reasoning": f"Error: {str(e)}",
                    "proof": ""
                },
                "chunks": []
            }

    async def extract_all_fields(self, doc_type: str = "MSA") -> List[Dict[str, Any]]:
        """Extract all fields in parallel."""
        # Select fields based on document type
        fields_to_extract = MSA_FIELDS_TO_EXTRACT if doc_type == "MSA" else SOW_FIELDS_TO_EXTRACT
        
        # Process all fields in parallel
        tasks = [self.process_field(field, doc_type) for field in fields_to_extract]
        return await asyncio.gather(*tasks)

async def main():
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize the chunking system
    chunker = CustomChunking(overlap_words=50)

    doc_type = "SOW"
    pdf_path = "contract_file/Stream.pdf"

    print("-" * 30 + f"Loading {doc_type} document from '{pdf_path}'" + "-" * 30)
    
    # Extract the file name from the path
    file_name = os.path.basename(pdf_path)
    
    # Load and chunk the document
    chunked_docs = chunker.load_documents(pdf_path)
    
    if not chunked_docs:
        print(f"Failed to load document: {pdf_path}")

    # Initialize the database
    db = ResultDatabase()

    # Initialize the RAG system
    rag_system = SQLiteOpenAIRAG()
    
    # Check if we need to store new documents
    conn = sqlite3.connect(rag_system.db_path)
    c = conn.cursor()
    c.execute('SELECT COUNT(*) FROM document_chunks')
    count = c.fetchone()[0]
    conn.close()
    
    if count == 0 and chunked_docs:
        # Generate embeddings
        embedding_generator = AsyncEmbeddingGenerator()
        embedded_docs = await embedding_generator.embed_chunks(chunked_docs)
        
        # Store documents
        rag_system.db_handler.store_chunked_docs(embedded_docs)
    
    # Extract all fields in parallel
    results = await rag_system.extract_all_fields(doc_type)

    print(type(results))
    print(results)

    # Save results to CSV
    csv_writer = CSVWriter()
    csv_writer.write_results(results, doc_type)

    # Store results
    doc_id = db.store_results(results, doc_type=doc_type, file_name=file_name)

    # Get latest results
    latest_results = db.get_latest_results(doc_type=doc_type, detailed=True)

    # Get document history
    history = db.get_document_history(doc_type=doc_type)

    # Print results
    print("\n" * 2)
    print("-" * 30 + f"Results for {doc_type} document" + "-" * 30)
    print("\n" * 2)

    print(f"Latest results: {latest_results}")
    print(f"Document history: {history}")


if __name__ == "__main__":
    asyncio.run(main())