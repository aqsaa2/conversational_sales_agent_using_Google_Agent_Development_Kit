# The simulation.py file serves as an internal test harness for the agent logic. 
# ALthough his simulation script doesn't use the ADK's web interface, 
# it directly interacts with the same agent tools and session logic defined in agent.py. 
# That means the same logic powering the ADK experience is being rigorously tested here, 
# just via command-line simulation.
import time
import uuid
import threading
import os
from .agent import handle_user_input, lead_sessions, update_lead_info


# This is the simulation file
# It is for testing the agent and simulating leads 
# with hardcoded responses and test cases as well as a manual user.
# Here you can clearly see all of the management in the terminal and
# the agent's responses to the leads.
# The follow up messages are also displayed after the specified timeline in the chat.



# Helper function to extract lead data and update the csv file
def get_lead_data_for_csv(lead_id, default_name):
    """Update CSV with lead data from the session.
    
    Args:
        lead_id (str): Unique identifier for the lead
        default_name (str): Default name to use if not found in session
    """
    session = lead_sessions.get(lead_id, {})
    

    status = 'initiated'
    current_question = session.get('current_question', '')
    
    if current_question == 'completed':
        status = 'secured'
    elif current_question == 'no_response':
        status = 'no_response'
    elif current_question in ['age', 'country', 'interest']:
        status = 'in_progress'
    
    if session.get('pending_message') is not None or session.get('status') == 'follow_up_sent':
        status = 'follow_up_sent'
        
    update_lead_info(lead_id, {
        'name': session.get('name', default_name),
        'age': session.get('age', ''),
        'country': session.get('country', ''),
        'interest': session.get('interest', ''),
        'status': status
    })
    
    


# Test case: simulate a full conversation with a lead
def simulate_lead(name, responses, delay_between_responses=2):
    """Simulate a complete lead conversation.
    
    Args:
        name (str): Lead name
        responses (list): List of responses for the lead to give
        delay_between_responses (int): Seconds to wait between responses
        
    Returns:
        str: The lead ID
    """
    lead_id = str(uuid.uuid4())[:8]  
    initial_message = f"Lead ID: {lead_id}, Name: {name}"
    result = handle_user_input(initial_message)
    print(f"\n🧪 [{name}] Initial: {initial_message}")
    print(f"[Agent → {name}] {result}")

    # Waiting a moment before responding
    time.sleep(delay_between_responses)
    
    for response in responses:
        formatted = f"{lead_id}: {response}"
        reply = handle_user_input(formatted)
        print(f"[{name} → Agent] {response}")
        print(f"[Agent → {name}] {reply}")
        get_lead_data_for_csv(lead_id, name)
        
        # Waiting before next response
        if responses.index(response) < len(responses) - 1:
            time.sleep(delay_between_responses)

    return lead_id


# Test case: simulate a lead that goes silent after initial response
def simulate_unresponsive_lead(name):
    """Simulate a lead that doesn't respond after initial message.
    
    Args:
        name (str): Lead name
    
    Returns:
        str: The lead ID
    """
    lead_id = str(uuid.uuid4())[:8]
    initial_message = f"Lead ID: {lead_id}, Name: {name}"
    result = handle_user_input(initial_message)
    print(f"\n🧪 [{name}] Initial: {initial_message}")
    print(f"[Agent → {name}] {result}")

    time.sleep(2)
    response = "Yes"
    result = handle_user_input(f"{lead_id}: {response}")
    print(f"[{name} → Agent] {response}")
    print(f"[Agent → {name}] {result}")
    print(f"[{name}] 💤 Lead goes silent... waiting for follow-up\n")

    get_lead_data_for_csv(lead_id, name)

    # Thread to monitor and display follow-up when it gets triggered
    def check_follow_up():
        waited = 0
        while waited < 120:  # Waiting up to 2 minutes for follow-up
            lead_info = lead_sessions.get(lead_id, {})
            follow_up = lead_info.get("pending_message")
            if follow_up:
                print(f"\n[Agent → {name}] 🔔 Follow-Up: {follow_up}")
                lead_info["pending_message"] = None
                get_lead_data_for_csv(lead_id, name)  # Updating the CSV after follow-up
                break
            time.sleep(5)
            waited += 5
        
        # Final CSV update after follow-up check completes
        if waited >= 120:
            print(f"[{name}] Follow-up monitoring timed out after 2 minutes")
        get_lead_data_for_csv(lead_id, name)

    follow_up_thread = threading.Thread(target=check_follow_up, daemon=True)
    follow_up_thread.start()
    
    return lead_id


# This function is for the manual lead simulation
# It allows the user to input their own lead information
def simulate_manual_lead():
    """Run an interactive manual lead simulation where the user can input responses."""
    print("\n📥 Manual Lead Mode")
    lead_id = input("Enter a unique Lead ID (or leave blank to auto-generate): ").strip() or str(uuid.uuid4())[:8]
    name = input("Enter your name: ").strip()

    intro = f"Lead ID: {lead_id}, Name: {name}"
    response = handle_user_input(intro)
    print(f"[Agent] {response}")

    # follow-up checker thread
    def check_follow_up():
        while True:
            session = lead_sessions.get(lead_id, {})
            if session.get("pending_message"):
                follow_up = session.pop("pending_message")
                print(f"\n[Agent - Follow-Up] {follow_up}")
                get_lead_data_for_csv(lead_id, name)
            time.sleep(5)

    follow_up_thread = threading.Thread(target=check_follow_up, daemon=True)
    follow_up_thread.start()

    while True:
        msg = input(f"[{name}] You: ").strip()
        if msg.lower() in ["exit", "quit"]:
            print("[Session ended]")
            break
        
        response = handle_user_input(f"{lead_id}: {msg}")
        print(f"[Agent] {response}")
        get_lead_data_for_csv(lead_id, name)


# Simulating a lead with delayed responses to test follow-up functionality
def simulate_delayed_response(name):
    """Simulate a lead with delayed responses to test follow-up functionality.
    
    Args:
        name (str): Lead name
    """
    lead_id = str(uuid.uuid4())[:8]
    initial_message = f"Lead ID: {lead_id}, Name: {name}"
    result = handle_user_input(initial_message)
    print(f"\n🧪 [{name}] Initial: {initial_message}")
    print(f"[Agent → {name}] {result}")
    
    # Wait 2 seconds and respond to initial message
    time.sleep(2)
    response = "Yes, I'm interested"
    result = handle_user_input(f"{lead_id}: {response}")
    print(f"[{name} → Agent] {response}")
    print(f"[Agent → {name}] {result}")
    get_lead_data_for_csv(lead_id, name)
    
    # Respond with age
    time.sleep(2)
    response = "28"
    result = handle_user_input(f"{lead_id}: {response}")
    print(f"[{name} → Agent] {response}")
    print(f"[Agent → {name}] {result}")
    get_lead_data_for_csv(lead_id, name)
    
    print(f"[{name}] 💤 Lead goes silent for country question... waiting for follow-up\n")
    
    # Thread to monitor for follow-up and then respond
    def monitor_and_respond():
        waited = 0
        follow_up_received = False
        
        # Wait for follow-up message to appear
        while waited < 120 and not follow_up_received:
            lead_info = lead_sessions.get(lead_id, {})
            follow_up = lead_info.get("pending_message")
            if follow_up:
                print(f"\n[Agent → {name}] 🔔 Follow-Up: {follow_up}")
                lead_info["pending_message"] = None
                follow_up_received = True
                get_lead_data_for_csv(lead_id, name)
                break
            time.sleep(5)
            waited += 5
        
        if follow_up_received:
            # Wait a moment and then respond to the follow-up
            time.sleep(3)
            response = "Canada"
            result = handle_user_input(f"{lead_id}: {response}")
            print(f"[{name} → Agent] {response}")
            print(f"[Agent → {name}] {result}")
            get_lead_data_for_csv(lead_id, name)
            
            # Complete the conversation
            time.sleep(2)
            response = "AI and ML tools"
            result = handle_user_input(f"{lead_id}: {response}")
            print(f"[{name} → Agent] {response}")
            print(f"[Agent → {name}] {result}")
            get_lead_data_for_csv(lead_id, name)
        else:
            print(f"[{name}] Follow-up monitoring timed out after 2 minutes")
    
    monitor_thread = threading.Thread(target=monitor_and_respond, daemon=True)
    monitor_thread.start()


# Starts everything: manual input first, then runs test cases in threads
def run_simulation():
    """Run the complete simulation with all test cases."""
    print("\n🤖 Sales Agent Simulation System")
    print("Choose simulation mode:")
    print("1. Manual mode (interactive)")
    print("2. Automated test cases")
    print("3. Both (manual first, then automated)")
    
    choice = input("Enter choice (1/2/3): ").strip()
    
    if choice in ["1", "3"]:
        simulate_manual_lead()
    
    if choice in ["2", "3"]:
        print("\n🧪 Starting automated test simulations...\n")
        
        # Clear terminal and print CSV file header
        print("\n" + "="*50)
        print("STARTING AUTOMATED TEST CASES")
        print("="*50)
        
        # Case 1: Complete flow
        threading.Thread(target=simulate_lead, 
                         args=("John Doe", ["Yes", "32", "USA", "Cloud hosting"]),
                         kwargs={"delay_between_responses": 2}).start()
        
        # Case 2: Declined flow
        threading.Thread(target=simulate_lead,
                         args=("Jane Smith", ["No, I'm not interested"]),
                         kwargs={"delay_between_responses": 2}).start()
        
        # Case 3: Unresponsive lead
        threading.Thread(target=simulate_unresponsive_lead,
                         args=("Mike Johnson",)).start()
        
        # Case 4: Delayed response with follow-up
        threading.Thread(target=simulate_delayed_response,
                         args=("Sarah Williams",)).start()
        
        # Wait for test cases to complete
        try:
            print("\nTest cases are running. Press Ctrl+C to stop the simulation.\n")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nSimulation interrupted.")
            
        # # Final CSV data display
        # print("\n" + "="*50)
        # print("FINAL CSV DATA")
        # print("="*50)
        
        # if os.path.exists('leads.csv'):
        #     with open('leads.csv', 'r') as file:
        #         csv_content = file.read()
        #         print(csv_content)

if __name__ == "__main__":
    run_simulation()
