from google import genai
from dotenv import load_dotenv
import os

load_dotenv()

client = genai.Client(
    api_key=os.getenv(
        "GEMINI_API_KEY"
    )
)


def generate_reply(
    user_message: str
):

    system_prompt = """
    You are KYROO.

    Talk casually like a close friend.
    Keep replies short.
    Be warm and natural.
    Avoid robotic language.
    """

    try:
        response = (
            client.models
            .generate_content(
                model="gemini-2.5-flash",
                contents=f"""
                SYSTEM:
                {system_prompt}

                USER:
                {user_message}
                """
            )
        )

        return response.text

    except Exception as e:
        print(
            "Gemini Error:",
            str(e)
        )

        return (
            "Something broke 😭 "
            "Try again."
        )