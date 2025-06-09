from dotenv import load_dotenv
from langchain_core.prompts.chat import ChatPromptTemplate
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage
import os
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain.agents import create_tool_calling_agent, AgentExecutor
from tools import search_tool, wiki_tool, save_tool, lead_qualifier, followup, quotation, pipeline_manager, sales_coach
from typing import List
import json
import re

tools = [search_tool, wiki_tool, save_tool, lead_qualifier, followup, quotation, pipeline_manager, sales_coach]

load_dotenv()

class Response(BaseModel):
    topic: str
    summary: str
    source: List[str]
    tools_used: List[str]

#llm2 = ChatOpenAI(model = "gpt-40-min")
#llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
parser = PydanticOutputParser(pydantic_object=Response)

prompt = ChatPromptTemplate.from_messages(
  [
      (
          "system",
          """
You are Project Pro, the AI assistant for ASP Crane Services.
Your primary role is to provide excellent and professional customer service, manage service requests using the information and tools available to you, and never reveal details about your internal processes or tools.

Additionally, you assist with:
- AI-augmented lead capture and enrichment.
- Visual pipeline management and opportunity tracking.
- Smart scheduling and task allocation.
- Multi-channel communication and follow-up.
- Quotation generation and document handling.
- Research and knowledge lookup.

For any user query, always use the most relevant tool(s) available to you.
If the user's query is not in the exact format a tool expects, extract the necessary information and convert it to the correct input format for the tool.
When you use a tool, always use the tool's output directly as the summary in your response—do not summarize, rephrase, or apologize, just return the tool's output as the summary, even if it is raw or unformatted.
If the tool returns a dictionary with a 'summary' key, always use the value of 'summary' as your summary, even if it is long or unformatted.
Never say you cannot access the internet if the tool returns any output.
Wrap the output in this format and provide no other text:
{format_instructions}
          """,
      ),
      ("placeholder", "{chat_history}"),
      ("human", "{query}"),
      ("placeholder", "{agent_scratchpad}"),
  ]
).partial(format_instructions=parser.get_format_instructions())

tools = [search_tool, wiki_tool, save_tool, lead_qualifier, followup, quotation, pipeline_manager, sales_coach]
agent = create_tool_calling_agent(
  llm=llm,
  prompt=prompt,
  tools=tools
)

def clean_json_output(output_str):
    # Remove Markdown code block if present
    output_str = re.sub(r"^```(?:json)?\s*([\s\S]*?)\s*```$", r"\1", output_str.strip(), flags=re.MULTILINE)
    # Replace single quotes with double quotes (be careful: this is naive)
    if output_str and output_str[0] in ["'", "{"] and "'" in output_str:
        output_str = output_str.replace("'", '"')
    return output_str

def ensure_response_schema(output_str):
    """
    Ensures the output string is a JSON object with all required fields for the Response schema.
    If fields are missing, fills them with sensible defaults.
    """
    try:
        data = json.loads(output_str)
        if not isinstance(data, dict):
            raise ValueError("Output is not a dict")
    except Exception:
        # If not valid JSON, treat the whole output as summary
        data = {}

    # Fill missing fields with defaults
    data.setdefault("topic", "General")
    data.setdefault("summary", output_str if "summary" not in data else data["summary"])
    data.setdefault("source", [])
    data.setdefault("tools_used", [])

    # Ensure correct types
    if not isinstance(data["source"], list):
        data["source"] = [str(data["source"])]
    if not isinstance(data["tools_used"], list):
        data["tools_used"] = [str(data["tools_used"])]

    return json.dumps(data)

if __name__ == "__main__":
    i = -1
    while i < 0:
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        query = input("What can i help you with? ")
        raw_response = agent_executor.invoke({"query": query})

        try:
            output_str = raw_response.get("output", "")
            if output_str.startswith("```"):
                output_str = output_str.strip("`")
                if output_str.startswith("json"):
                    output_str = output_str[4:].strip()

            # Clean and ensure output matches schema
            output_str = clean_json_output(output_str)
            output_str = ensure_response_schema(output_str)

            structured_response = parser.parse(output_str)

            # Professional formatted output with clear sections
            print("\n" + "═"*70)
            print(f"{'🤖 CRM Assistant Result':^70}")
            print("═"*70)

            # Topic section with title case
            print(f"\n📌 Topic:")
            print("─"*70)
            print(f"{structured_response.topic.title()}")

            # Summary section with proper spacing and capitalization
            print(f"\n📋 Response:")
            print("─"*70)
            summary_lines = structured_response.summary.split('\n')
            for line in summary_lines:
                if line.strip():
                    line = line.replace("**", "")
                    if ':' in line and not line.strip().startswith('['):
                        key, value = line.split(':', 1)
                        print(f"{key.strip().title()}: {value.strip()}")
                    else:
                        print(line.strip())
                else:
                    print()
            
            if structured_response.tools_used:
                print("\n🛠️  Tools Used:")
                print("─"*70)
                print(f"{', '.join(tool.title() for tool in structured_response.tools_used)}")

            print("\n" + "═"*70 + "\n")

        except Exception as e:
            print("\n" + "═"*70)
            print(f"{'❌ Error Processing Response':^70}")
            print("═"*70)
            print(f"Error: {e}")
            print(f"\nRaw Output:\n{raw_response.get('output', 'No output')}")
            print("\n" + "═"*70 + "\n")