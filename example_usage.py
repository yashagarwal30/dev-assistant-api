"""Example usage of the Dev Assistant API."""

import asyncio
import httpx


BASE_URL = "http://localhost:8000"


async def example_chat():
    """Example: Basic chat functionality."""
    print("\n=== Example 1: Basic Chat ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat/",
            json={
                "message": "What are Python decorators and how do they work?",
                "temperature": 0.7,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"Session ID: {data['session_id']}")
            print(f"Model: {data['model']}")
            print(f"Tokens Used: {data['tokens_used']}")
            print(f"Cached: {data['cached']}")
            print(f"\nResponse:\n{data['message']}")
            return data['session_id']
        else:
            print(f"Error: {response.status_code}")
            return None


async def example_conversation(session_id: str):
    """Example: Continue a conversation."""
    print("\n=== Example 2: Continue Conversation ===")

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat/",
            json={
                "message": "Can you show me a practical example?",
                "session_id": session_id,
                "temperature": 0.7,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\nResponse:\n{data['message']}")


async def example_code_analysis():
    """Example: Code analysis."""
    print("\n=== Example 3: Code Analysis ===")

    code = """
def calculate_total(items):
    total = 0
    for item in items:
        total = total + item['price']
    return total
"""

    async with httpx.AsyncClient() as client:
        # Code review
        print("\n--- Code Review ---")
        response = await client.post(
            f"{BASE_URL}/code/analyze",
            json={
                "code": code,
                "analysis_type": "review",
                "file_path": "cart.py",
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n{data['result']}")

        # Optimization suggestions
        print("\n--- Optimization Suggestions ---")
        response = await client.post(
            f"{BASE_URL}/code/analyze",
            json={
                "code": code,
                "analysis_type": "optimize",
                "file_path": "cart.py",
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n{data['result']}")


async def example_chat_with_context():
    """Example: Chat with code context."""
    print("\n=== Example 4: Chat with Code Context ===")

    code_context = """
class UserManager:
    def __init__(self):
        self.users = []

    def add_user(self, name, email):
        self.users.append({'name': name, 'email': email})

    def get_user(self, email):
        for user in self.users:
            if user['email'] == email:
                return user
        return None
"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/chat/",
            json={
                "message": "What potential issues do you see with this code? How would you improve it?",
                "context": code_context,
                "temperature": 0.5,
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n{data['message']}")


async def example_generate_tests():
    """Example: Generate unit tests."""
    print("\n=== Example 5: Generate Unit Tests ===")

    code = """
def validate_email(email):
    if '@' not in email:
        return False
    parts = email.split('@')
    if len(parts) != 2:
        return False
    if '.' not in parts[1]:
        return False
    return True
"""

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/code/analyze",
            json={
                "code": code,
                "analysis_type": "test",
                "file_path": "validators.py",
            },
        )

        if response.status_code == 200:
            data = response.json()
            print(f"\n{data['result']}")


async def example_stats():
    """Example: Get API statistics."""
    print("\n=== Example 6: API Statistics ===")

    async with httpx.AsyncClient() as client:
        # Overall stats
        response = await client.get(f"{BASE_URL}/admin/stats")
        if response.status_code == 200:
            print("\nOverall Stats:")
            print(response.json())

        # Cache stats
        response = await client.get(f"{BASE_URL}/admin/cache/stats")
        if response.status_code == 200:
            print("\nCache Stats:")
            print(response.json())


async def main():
    """Run all examples."""
    print("Dev Assistant API - Usage Examples")
    print("=" * 50)

    try:
        # Example 1: Basic chat
        session_id = await example_chat()

        # Example 2: Continue conversation
        if session_id:
            await example_conversation(session_id)

        # Example 3: Code analysis
        await example_code_analysis()

        # Example 4: Chat with context
        await example_chat_with_context()

        # Example 5: Generate tests
        await example_generate_tests()

        # Example 6: Statistics
        await example_stats()

        print("\n" + "=" * 50)
        print("Examples completed!")

    except httpx.ConnectError:
        print("\n❌ Error: Could not connect to API")
        print("Make sure the API is running: python run.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
