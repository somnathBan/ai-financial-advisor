import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Updated import

# 1. Load the hidden .env file
load_dotenv()

# 2. Grab the OpenRouter key
api_key = os.getenv("OPENROUTER_API_KEY")

def test_connection():
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in .env file!")
        return

    print(f"✅ Key detected: {api_key[:5]}...{api_key[-4:]}")

    try:
        # 3. Initialize the Qwen3 model via OpenRouter Bridge
        llm = ChatOpenAI(
            model="qwen/qwen3-next-80b-a3b-instruct", 
            openai_api_key=api_key,
            base_url="https://openrouter.ai/api/v1"  # Crucial for OpenRouter
        )
        
        print("⏳ Sending a handshake to OpenRouter (Qwen3)...")
        
        # 4. Ask a simple question
        response = llm.invoke("Hello! I am building an AI Financial Advisor. Are you ready to help?")
        
        print("\n🤖 AI's Response:")
        print("-" * 30)
        print(response.content)
        print("-" * 30)
        print("\n🎉 Connection Successful!")

    except Exception as e:
        print(f"\n❌ Handshake failed: {e}")

if __name__ == "__main__":
    test_connection()