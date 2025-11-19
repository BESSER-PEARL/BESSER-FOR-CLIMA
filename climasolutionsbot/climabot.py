# You may need to add your working directory to the Python path. To do so, uncomment the following lines of code
# import sys
# sys.path.append("/Path/to/directory/agentic-framework") # Replace with your directory path

import logging

from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter

from besser.agent import nlp
from besser.agent.core.agent import Agent
from besser.agent.core.session import Session
from besser.agent.exceptions.logger import logger
from besser.agent.nlp.intent_classifier.intent_classifier_configuration import LLMIntentClassifierConfiguration
from besser.agent.nlp.llm.llm_huggingface_api import LLMHuggingFaceAPI
from besser.agent.nlp.llm.llm_openai_api import LLMOpenAI
from besser.agent.nlp.llm.llm_replicate_api import LLMReplicate
from besser.agent.nlp.rag.rag import RAGMessage, RAG

# Configure the logging module
logger.setLevel(logging.INFO)

# Create the agent
agent = Agent('clima_solutions_agent')
# Load agent properties stored in a dedicated file
agent.load_properties('config.ini')
# Define the platform your agent will use
websocket_platform = agent.use_websocket_platform(use_ui=False)

# Create Vector Store (RAG's DB)
vector_store: Chroma = Chroma(
    embedding_function=OpenAIEmbeddings(openai_api_key=agent.get_property(nlp.OPENAI_API_KEY)),
    persist_directory='vector_store'
)
# Create text splitter (RAG creates a vector for each chunk)
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
# Create the LLM (for the answer generation)
gpt = LLMOpenAI(
    agent=agent,
    name='gpt-4o-mini',
    parameters={},
    num_previous_messages=10
)

# # Configure the intent classifier
# ic_config = LLMIntentClassifierConfiguration(
#     llm_name='gpt-4o-mini',
#     parameters={},
#     use_intent_descriptions=True,
#     use_training_sentences=False,
#     use_entity_descriptions=True,
#     use_entity_synonyms=False
# )
# agent.set_default_ic_config(ic_config)


bot_intent = agent.new_intent('bot_intent', [
    'bot'
])
rag_intent = agent.new_intent('rag_intent', [
    'rag'
])
# Other example LLM
# llama = LLMHuggingFaceAPI(agent=agent, name='meta-llama/Meta-Llama-3.1-8B-Instruct', parameters={}, num_previous_messages=10)
# mixtral = LLMReplicate(agent=agent, name='mistralai/mixtral-8x7b-instruct-v0.1', parameters={}, num_previous_messages=10)

# Create the RAG
rag = RAG(
    agent=agent,
    vector_store=vector_store,
    splitter=splitter,
    llm_name='gpt-4o-mini',
    k=4,
    num_previous_messages=0
)

rag.llm_prompt = "You are an assistant for question-answering tasks. Based on the previous messages in the conversation (if provided), and additional context retrieved from a database (if provided), answer the user question. If you don't know the answer, just say that you don't know. Note that if the question refers to a previous message, you may have to ignore the context since it is retrieved from the database based only on the question (the retrieval does not take into account the previous messages). Use only text and no type of markdown."

# Uncomment to fill the DB
# rag.load_pdfs('./pdfs')

# STATES
initial_state = agent.new_state('initial_state', initial=True)
idle_rag_state = agent.new_state('idle_rag_state')
idle_llm_state = agent.new_state('idle_llm_state')
rag_state = agent.new_state('rag_state')
llm_state = agent.new_state('llm_state')

# STATES BODIES' DEFINITION + TRANSITIONS
def initial_body(session: Session):
    session.reply('How can I help you with climate solutions or visualizations today?')

initial_state.set_body(initial_body)
initial_state.when_intent_matched(rag_intent).go_to(idle_rag_state)
initial_state.when_intent_matched(bot_intent).go_to(idle_llm_state)

idle_rag_state.when_no_intent_matched().go_to(rag_state)
idle_llm_state.when_no_intent_matched().go_to(llm_state)

def rag_body(session: Session):
    rag_message: RAGMessage = session.run_rag(session.event.message)
    websocket_platform.reply_rag(session, rag_message)

rag_state.set_body(rag_body)
rag_state.go_to(idle_rag_state)

def llm_body(session: Session):
    # Create a context similar to what's in your Dashboard Chat component
    context = """You are a climate solutions expert and dashboard visualization assistant. 
    
    When users ask climate-related questions, provide informative and accurate responses.
    
    When users request visualizations, select an appropriate data visualization and respond with a JSON structure:
    {
        "answer": "Your natural language response",
        "visualization": {
            "type": "LineChart|PieChart|BarChart|StatChart",
            "kpi_id": "The KPI ID (e.g. temp001, money001, energy001)",
            "title": "A descriptive title for the visualization",
            "unitText": "The unit from the KPI (e.g. Celsius, Euros, Percentage)",
            "target": The target value from the KPI or null
        }
    }
    """

    # Combine the context with the user's message
    prompt = f"{context}\n\nUser message: {session.event.message}"

    # Call the LLM with the combined prompt
    websocket_platform.reply_llm(session, gpt.predict(prompt))

llm_state.set_body(llm_body)
llm_state.go_to(idle_llm_state)

# RUN APPLICATION
if __name__ == '__main__':
    agent.run()