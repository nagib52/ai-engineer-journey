from dotenv import load_dotenv
from groq import Groq
import os
import json

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ===== TOOL FUNCTIONS =====

def get_weather(city):
    fake_data = {"Dhaka": "32°C, Sunny", "London": "18°C, Rainy"}
    return fake_data.get(city, "Unknown city")

def calculator(operation, a, b):
    if operation == "add":
        return str(a + b)
    elif operation == "subtract":
        return str(a - b)
    elif operation == "multiply":
        return str(a * b)
    elif operation == "divide":
        return str(a / b) if b != 0 else "Error: division by zero"
    return "Unknown operation"

def currency_converter(amount, from_currency, to_currency):
    fake_rates = {"USD_BDT": 110, "BDT_USD": 1/110}
    key = f"{from_currency}_{to_currency}"
    rate = fake_rates.get(key, 1)
    return str(round(amount * rate, 2))

# ===== TOOL SCHEMAS =====

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather for a city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "City name"}
                },
                "required": ["city"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculator",
            "description": "Perform basic math operations: add, subtract, multiply, divide",
            "parameters": {
                "type": "object",
                "properties": {
                    "operation": {"type": "string", "description": "One of: add, subtract, multiply, divide"},
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "currency_converter",
            "description": "Convert an amount from one currency to another (supports USD and BDT)",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "from_currency": {"type": "string", "description": "e.g. USD"},
                    "to_currency": {"type": "string", "description": "e.g. BDT"}
                },
                "required": ["amount", "from_currency", "to_currency"]
            }
        }
    }
]

# ===== MAIN CHAT LOOP =====

conversation = [{"role": "system", "content": "You are a helpful assistant with access to tools."}]

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break

    conversation.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=conversation,
        tools=tools,
        tool_choice="auto"
    )
    message = response.choices[0].message

    if message.tool_calls:
        conversation.append(message)

        for tool_call in message.tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "get_weather":
                result = get_weather(function_args["city"])
            elif function_name == "calculator":
                result = calculator(function_args["operation"], function_args["a"], function_args["b"])
            elif function_name == "currency_converter":
                result = currency_converter(function_args["amount"], function_args["from_currency"], function_args["to_currency"])
            else:
                result = "Unknown tool"

            conversation.append({"role": "tool", "tool_call_id": tool_call.id, "content": result})

        final_response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=conversation
        )
        reply = final_response.choices[0].message.content
        print("Bot:", reply)
        conversation.append({"role": "assistant", "content": reply})

    else:
        print("Bot:", message.content)
        conversation.append({"role": "assistant", "content": message.content})