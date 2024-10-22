import os  
import pandas as pd  
import tiktoken  
from graphrag.query.context_builder.entity_extraction import EntityVectorStoreKey  
from graphrag.query.indexer_adapters import (  
    read_indexer_entities,  
    read_indexer_relationships,  
    read_indexer_reports,  
    read_indexer_text_units,  
)  
from graphrag.query.input.loaders.dfs import store_entity_semantic_embeddings  
from graphrag.query.llm.oai.chat_openai import ChatOpenAI  
from graphrag.query.llm.oai.embedding import OpenAIEmbedding  
from graphrag.query.llm.oai.typing import OpenaiApiType  
from graphrag.query.structured_search.local_search.mixed_context import LocalSearchMixedContext  
from graphrag.query.structured_search.local_search.search import LocalSearch  
from graphrag.vector_stores.lancedb import LanceDBVectorStore  
  
def get_latest_timestamp_dir(base_dir):  
    # List all directories in the base directory  
    all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]  
      
    # Sort the directories based on their names assuming they are timestamped  
    all_dirs.sort(reverse=True)  
      
    # Return the latest directory  
    return all_dirs[0] if all_dirs else None  
  
async def query():  
    OUTPUT_DIR = r"output"  
    latest_timestamp = get_latest_timestamp_dir(OUTPUT_DIR)  
  
    if latest_timestamp:  
        INPUT_DIR = os.path.join(OUTPUT_DIR, latest_timestamp, "artifacts")  
        print("INPUT_DIR:", INPUT_DIR)  
    else:  
        print("No directories found.")  
        return  
  
    LANCEDB_URI = f"{INPUT_DIR}/lancedb"  
    COMMUNITY_REPORT_TABLE = "create_final_community_reports"  
    ENTITY_TABLE = "create_final_nodes"  
    ENTITY_EMBEDDING_TABLE = "create_final_entities"  
    RELATIONSHIP_TABLE = "create_final_relationships"  
    TEXT_UNIT_TABLE = "create_final_text_units"  
    COMMUNITY_LEVEL = 2  
  
    # Read nodes table to get community and degree data  
    entity_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_TABLE}.parquet")  
    entity_embedding_df = pd.read_parquet(f"{INPUT_DIR}/{ENTITY_EMBEDDING_TABLE}.parquet")  
    entities = read_indexer_entities(entity_df, entity_embedding_df, COMMUNITY_LEVEL)  
  
    # Load description embeddings to an in-memory LanceDB vector store  
    description_embedding_store = LanceDBVectorStore(collection_name="entity_description_embeddings")  
    description_embedding_store.connect(db_uri=LANCEDB_URI)  
    store_entity_semantic_embeddings(  
        entities=entities,  
        vectorstore=description_embedding_store  
    )  
  
    relationship_df = pd.read_parquet(f"{INPUT_DIR}/{RELATIONSHIP_TABLE}.parquet")  
    relationships = read_indexer_relationships(relationship_df)  
    print(f"Relationship count: {len(relationship_df)}")  
  
    report_df = pd.read_parquet(f"{INPUT_DIR}/{COMMUNITY_REPORT_TABLE}.parquet")  
    reports = read_indexer_reports(report_df, entity_df, COMMUNITY_LEVEL)  
    text_unit_df = pd.read_parquet(f"{INPUT_DIR}/{TEXT_UNIT_TABLE}.parquet")  
    text_units = read_indexer_text_units(text_unit_df)  
  
    api_key = "9101287fb67e484b9970dd8d7e31aa05"  
    api_base = "https://diesl-eus-openai-dev.openai.azure.com/"  
    api_version = "2024-02-15-preview"  
    llm_model = "gpt-4o"  
    embedding_model = "text-embedding-ada-002"  
  
    llm = ChatOpenAI(  
        api_key=api_key,  
        api_base=api_base,  
        api_version=api_version,  
        model=llm_model,  
        api_type=OpenaiApiType.AzureOpenAI,  
        max_retries=4,  
    )  
  
    token_encoder = tiktoken.get_encoding("cl100k_base")  
    text_embedder = OpenAIEmbedding(  
        api_key=api_key,  
        api_base=api_base,  
        api_version=api_version,  
        api_type=OpenaiApiType.AzureOpenAI,  
        model=embedding_model,  
        deployment_name=embedding_model,  
        max_retries=3,  
    )  
  
    context_builder = LocalSearchMixedContext(  
        community_reports=reports,  
        text_units=text_units,  
        entities=entities,  
        relationships=relationships,  
        entity_text_embeddings=description_embedding_store,  
        embedding_vectorstore_key=EntityVectorStoreKey.ID,  
        text_embedder=text_embedder,  
        token_encoder=token_encoder,  
    )  
  
    local_context_params = {  
        "text_unit_prop": 0.5,  
        "community_prop": 0.1,  
        "conversation_history_max_turns": 5,  
        "conversation_history_user_turns_only": True,  
        "top_k_mapped_entities": 10,  
        "top_k_relationships": 10,  
        "include_entity_rank": True,  
        "include_relationship_weight": True,  
        "include_community_rank": False,  
        "return_candidate_context": False,  
        "embedding_vectorstore_key": EntityVectorStoreKey.ID,  
        "max_tokens": 12_000,  
    }  
  
    llm_params = {  
        "max_tokens": 2_000,  
        "temperature": 0.0,  
    }  
  
    search_engine = LocalSearch(  
        llm=llm,  
        context_builder=context_builder,  
        token_encoder=token_encoder,  
        llm_params=llm_params,  
        context_builder_params=local_context_params,  
        response_type="multiple paragraphs",  
    )  
  
    result = await search_engine.asearch(  
        """Step 1: Leverage the 'Section Includes' portion of the document to identify the key product(s) within the text document.  
        Step 2: Identify the aliases used to refer to the key products outlined within the 'Section Includes' portion of the PDF.  
        a) Example aliases include 'GYPBD-1, RF-1'. Return only a numbered list of products that have an alias.  
        Step 3: Using the list of products and aliases you created in step 2, verify no product or alias is excluded from our list.  
        If you identify a new product and alias, add this new product to the existing list."""  
    )  

    return result
      
    # print(result.response)  
  
if __name__ == "__main__":  
    import asyncio  
    asyncio.run(query())  
