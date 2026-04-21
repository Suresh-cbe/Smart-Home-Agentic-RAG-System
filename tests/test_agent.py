from app.agent import Agent

agent = Agent()


def run_test(question: str):
    print("\n" + "="*60)
    print(f"QUESTION: {question}")

    response = agent.get_response(question)

    print("\nANSWER:")
    print(response["answer"])

    print("\nREASONING TRACE:")
    for step in response["reasoning_trace"]:
        print(step)

    print("\nCONTEXT:")
    print(response["retrieved_context"])

    print("\nCONFIDENCE:")
    print(response["confidence_score"])
    print("="*60)


if __name__ == "__main__":
    test_cases = [
        "What is the temperature in the living room?",
        "Which devices are in the kitchen?",
        "Describe the devices in the bedroom",
        "Is any light on?",
        "Give details about sensors",
        "What devices are connected to thermostat?"
    ]

    for q in test_cases:
        run_test(q)