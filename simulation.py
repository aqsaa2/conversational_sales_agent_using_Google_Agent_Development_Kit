import time
import uuid
import threading
from .agent import handle_user_input, lead_sessions, update_lead_info

#This the simulation file, 
# it is for testing the agent and simulating leads 
# with hardcoded responses and test cases as well as a manual user.
# Here you can clearly see all of the management in the terminal and
# the agent's responses to the leads.
# The follow up messages are also displayed after the specified timeline in the chat.

# helper function to extract lead data and update the csv file
def get_lead_data_for_csv(lead_id, default_name, source):
    session = lead_sessions.get(lead_id, {})
    update_lead_info(lead_id, {
        'name': session.get('name', default_name),
        'age': session.get('age', ''),
        'country': session.get('country', ''),
        'interest': session.get('interest', ''),
        'status': (
            'secured' if session.get('current_question') == 'completed'
            else session.get('current_question', 'in_progress')
        )
    })

# test case: simulate a full conversation with a lead
def simulate_lead(name, responses, delay_between_responses=2):
    lead_id = str(uuid.uuid4())[:8]  
    initial_message = f"Lead ID: {lead_id}, Name: {name}"
    result = handle_user_input(initial_message)
    print(f"\n🧪 [{name}] Initial: {initial_message}")
    print(f"[{name}] Agent: {result}")

    update_lead_info(lead_id, {'name': name, 'status': 'initiated'})

    for response in responses:
        time.sleep(delay_between_responses)
        formatted = f"{lead_id}: {response}"
        reply = handle_user_input(formatted)
        print(f"[{name}] Lead: {response}")
        print(f"[{name}] Agent: {reply}")
        get_lead_data_for_csv(lead_id, name, source='test')

    return lead_id


# test case: simulate a lead that goes silent after initial response
def simulate_unresponsive_lead(name):
    lead_id = str(uuid.uuid4())[:8]
    initial_message = f"Lead ID: {lead_id}, Name: {name}"
    result = handle_user_input(initial_message)
    print(f"\n🧪 [{name}] Initial: {initial_message}")
    print(f"[{name}] Agent: {result}")

    update_lead_info(lead_id, {'name': name, 'status': 'initiated'})

    time.sleep(2)
    response = "Yes"
    result = handle_user_input(f"{lead_id}: {response}")
    print(f"[{name}] Lead: {response}")
    print(f"[{name}] Agent: {result}")
    print(f"[{name}] 💤 Lead goes silent... waiting for follow-up\n")

    get_lead_data_for_csv(lead_id, name, source='test')

    # thread to monitor and display follow-up when it gets triggered
    def check_follow_up():
        waited = 0
        while waited < 120:
            lead_info = lead_sessions.get(lead_id, {})
            follow_up = lead_info.get("pending_message")
            if follow_up:
                print(f"[{name}] 🔔 Follow-Up: {follow_up}")
                lead_info["pending_message"] = None
                break
            time.sleep(5)
            waited += 5

    threading.Thread(target=check_follow_up, daemon=True).start()

# this function is for the manual lead simulation
# it allows the user to input their own lead information
def simulate_manual_lead():
    print("\n📥 Manual Lead Mode")
    lead_id = input("Enter a unique Lead ID (or leave blank to auto-generate): ").strip() or str(uuid.uuid4())[:8]
    name = input("Enter your name: ").strip()

    intro = f"Lead ID: {lead_id}, Name: {name}"
    response = handle_user_input(intro)
    print(f"[Agent] {response}")

    update_lead_info(lead_id, {'name': name, 'status': 'initiated'})

    while True:
        msg = input(f"[{name}] You: ").strip()
        if msg.lower() in ["exit", "quit"]:
            print("[Session ended]")
            break
        response = handle_user_input(f"{lead_id}: {msg}")
        print(f"[Agent] {response}")
        get_lead_data_for_csv(lead_id, name, source='test')

        # Follow-up printout
        session = lead_sessions.get(lead_id, {})
        if session.get("pending_message"):
            print(f"[Agent - Follow-Up] {session['pending_message']}")
            session["pending_message"] = None

# starts everything: manual input first, then runs test cases in threads
def run_simulation():
    print("\n🤖 Sales Agent Simulation System")
    print("Manual mode starts first. Type 'exit' anytime to finish.\n")

    simulate_manual_lead()

    print("\n🧪 Starting automated test simulations...\n")

    threading.Thread(target=simulate_lead, args=("John Doe", ["Yes", "32", "USA", "Cloud hosting"])).start()
    threading.Thread(target=simulate_lead, args=("Jane Smith", ["No, I'm not interested"])).start()
    threading.Thread(target=simulate_unresponsive_lead, args=("Mike Johnson",)).start()

    def delayed_response():
        lead_id = simulate_lead("Sarah Williams", ["Yes", "28", "Canada"])
        time.sleep(30)
        msg = "AI and ML tools"
        print(f"[Sarah Williams] Lead: {msg}")
        result = handle_user_input(f"{lead_id}: {msg}")
        print(f"[Sarah Williams] Agent: {result}")
        get_lead_data_for_csv(lead_id, "Sarah Williams", source='test')

    threading.Thread(target=delayed_response).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulation interrupted.")


if __name__ == "__main__":
    run_simulation()
