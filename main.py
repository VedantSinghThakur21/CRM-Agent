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

tools = [search_tool, wiki_tool, save_tool, lead_qualifier, followup, quotation, pipeline_manager, sales_coach]

load_dotenv()

class Response(BaseModel):
  topic : str
  summary : str
  source : list [str]
  tools_used : list [str]

#llm2 = ChatOpenAI(model = "gpt-40-min")
#llm = ChatAnthropic(model="claude-3-5-sonnet-20241022")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-lite")
parser = PydanticOutputParser(pydantic_object=Response)

prompt = ChatPromptTemplate.from_messages(
  [
      (
          "system",
          """
          You are a CRM assistant for a B2B sales team. For any user query, always use the most relevant tool(s) available to you.
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
        # Split summary into lines and print with proper formatting
        summary_lines = structured_response.summary.split('\n')
        for line in summary_lines:
            if line.strip():
                # Remove markdown ** characters
                line = line.replace("**", "")
                
                # If the line looks like a label: value pair
                if ':' in line and not line.strip().startswith('['):
                    key, value = line.split(':', 1)
                    print(f"{key.strip().title()}: {value.strip()}")
                else:
                    # Just print full sentences or paragraphs as-is
                    print(line.strip())
            else:
                print()
        

        # Tools section with title case (only if tools were used)
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