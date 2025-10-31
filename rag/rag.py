from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.agent.workflow import AgentWorkflow
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

import asyncio
import argparse
import os

# Settings control global defaults
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-base-en-v1.5")
Settings.llm = Ollama(
        model="mistral",
        request_timeout=180.0,
        # Manually set the context window to limit memory usage
        context_window=2000,
        generate_kwargs={"num_predict": 128},
        temperature=0,
)

# Create a RAG tool using LlamaIndex
documents = SimpleDirectoryReader("data").load_data()
index = VectorStoreIndex.from_documents(
    documents,
    # we can optionally override the embed_model here
    # embed_model=Settings.embed_model,
)
query_engine = index.as_query_engine(
    # we can optionally override the llm here
    # llm=Settings.llm,
)


def multiply(a: float, b: float) -> float:
    """Useful for multiplying two numbers."""
    return a * b


async def search_documents(query: str) -> str:
    """Useful for answering natural language questions about an personal essay written by Paul Graham."""
    response = await query_engine.aquery(query)
    return str(response)


# Create an enhanced workflow with both tools
agent = AgentWorkflow.from_tools_or_functions(
    [multiply, search_documents],
    llm=Settings.llm,
    system_prompt=(
        "Sei un assistente utile che risponde sempre in italiano. "
        "Puoi eseguire calcoli e rispondere a domande sui documenti forniti."
    ),
)

async def main():
    parser = argparse.ArgumentParser(description="RAG chatbot CLI")
    parser.add_argument(
        "-m",
        "--message",
        type=str,
        required=True,
        help="Prompt da passare al modello",
    )
    args = parser.parse_args()

    response = await agent.run(args.message)
    print("\n🧠 Risposta:")
    print(response)


# Run the agent
if __name__ == "__main__":
    asyncio.run(main())