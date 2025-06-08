from flask import Flask, request, jsonify, send_from_directory
from main import agent, tools, parser  # Import your agent setup

from langchain.agents import AgentExecutor

app = Flask(__name__)

@app.route('/api/ask', methods=['POST'])
def ask():
    data = request.json
    query = data.get('message', '')
    agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=False)
    raw_response = agent_executor.invoke({"query": query})

    output_str = raw_response.get("output", "")
    if output_str.startswith("```"):
        output_str = output_str.strip("`")
        if output_str.startswith("json"):
            output_str = output_str[4:].strip()
    structured_response = parser.parse(output_str)

    # Return as JSON for your frontend
    return jsonify({
        "topic": structured_response.topic,
        "summary": structured_response.summary,
        "tools_used": structured_response.tools_used
    })

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)