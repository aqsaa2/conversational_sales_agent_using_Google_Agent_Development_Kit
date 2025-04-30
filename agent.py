import datetime
import csv
import os
import threading
import time
from typing import Dict, List, Optional
from google.adk.agents import Agent

#this is the main agent that will be used to handle the conversation with the leads, it runs on the url: http://127.0.0.1:8000

# For storing informaton in csv file
lead_sessions = {}

def initialize_csv():
    """Initialize the leads.csv file if it doesn't exist."""
    if not os.path.exists('D:\Zikra LLC\Sales_Agent_With_ADK_Interface\conversational_agent\leads_data.csv'):
        with open('D:\Zikra LLC\Sales_Agent_With_ADK_Interface\conversational_agent\leads_data.csv', 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['lead_id', 'name', 'age', 'country', 'interest', 'status'])

def update_lead_info(lead_id: str, data: Dict):
    """Update lead information in the CSV file.
   
    Args:
        lead_id (str): Unique identifier for the lead
        data (Dict): Data to update for the lead
    """
    
    existing_data = []
    lead_exists = False
   
    if os.path.exists('D:\Zikra LLC\Sales_Agent_With_ADK_Interface\conversational_agent\leads_data.csv'):
        with open('D:\Zikra LLC\Sales_Agent_With_ADK_Interface\conversational_agent\leads_data.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            headers = next(reader, None)  
           
            for row in reader:
                if row and row[0] == lead_id:
                    # Update existing lead
                    updated_row = [lead_id]
                    updated_row.append(data.get('name', row[1] if len(row) > 1 else ''))
                    updated_row.append(data.get('age', row[2] if len(row) > 2 else ''))
                    updated_row.append(data.get('country', row[3] if len(row) > 3 else ''))
                    updated_row.append(data.get('interest', row[4] if len(row) > 4 else ''))
                    updated_row.append(data.get('status', row[5] if len(row) > 5 else ''))
                    existing_data.append(updated_row)
                    lead_exists = True
                else:
                    existing_data.append(row)
   
    # Add new lead if not exists
    if not lead_exists:
        new_row = [
            lead_id,
            data.get('name', ''),
            data.get('age', ''),
            data.get('country', ''),
            data.get('interest', ''),
            data.get('status', '')
        ]
        existing_data.append(new_row)
   
    
    with open('D:\Zikra LLC\Sales_Agent_With_ADK_Interface\conversational_agent\leads_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['lead_id', 'name', 'age', 'country', 'interest', 'status'])
        writer.writerows(existing_data)

def start_conversation(lead_id: str, lead_name: str) -> dict:
    """Initiates a conversation with a lead.
   
    Args:
        lead_id (str): Unique identifier for the lead
        lead_name (str): Name of the lead
       
    Returns:
        dict: Response containing the initial message
    """
    # Initialize lead session if not exists
    if lead_id not in lead_sessions:
        lead_sessions[lead_id] = {
            'name': lead_name,
            'current_question': 'consent',
            'age': '',
            'country': '',
            'interest': '',
            'last_interaction': datetime.datetime.now(),
            'pending_message': None  # NEW FIELD
        }
       
        # Add lead to CSV with initial status
        update_lead_info(lead_id, {
            'name': lead_name,
            'status': 'initiated'
        })
       
        # Start follow-up thread for this lead
        follow_up_thread = threading.Thread(
            target=schedule_follow_up,
            args=(lead_id,)
        )
        follow_up_thread.daemon = True
        follow_up_thread.start()
       
        return {
            "status": "success",
            "message": f"Hey {lead_name}, thank you for filling out the form. I'd like to gather some information from you. Is that okay?"
        }
    else:
        return {
            "status": "success",
            "message": f"Welcome back, {lead_name}! Let's continue our conversation."
        }

def handle_response(lead_id: str, response: str) -> dict:
    """Processes a response from a lead and moves the conversation forward.
   
    Args:
        lead_id (str): Unique identifier for the lead
        response (str): The lead's response to the current question
       
    Returns:
        dict: Next question or acknowledgment
    """
    if lead_id not in lead_sessions:
        return {
            "status": "error",
            "message": "Lead session not found. Please start a new conversation."
        }
   
    # Update last interaction time
    lead_sessions[lead_id]['last_interaction'] = datetime.datetime.now()
   
    current_question = lead_sessions[lead_id]['current_question']
   
    # Handle consent question
    if current_question == 'consent':
        if any(word in response.lower() for word in ['yes', 'ok', 'okay', 'sure', 'fine', 'right', 'great', 'yes please', 'why not', 'agree', 'i agree', 'sure please', 'go ahead', 'interest', 'yeah', 'ya', 'yeah sure']):
            lead_sessions[lead_id]['current_question'] = 'age'
            update_lead_info(lead_id, {'status': 'in_progress'})
            return {
                "status": "success",
                "message": "Great! What is your age?"
            }
        else:
            lead_sessions[lead_id]['current_question'] = 'no_response'
            update_lead_info(lead_id, {'status': 'no_response'})
            return {
                "status": "success",
                "message": "Alright, no problem. Have a great day!"
            }
   
    # Handle age question
    elif current_question == 'age':
        lead_sessions[lead_id]['age'] = response
        lead_sessions[lead_id]['current_question'] = 'country'
        update_lead_info(lead_id, {'age': response})
        return {
            "status": "success",
            "message": "Thank you! Which country are you from?"
        }
   
    # Handle country question
    elif current_question == 'country':
        lead_sessions[lead_id]['country'] = response
        lead_sessions[lead_id]['current_question'] = 'interest'
        update_lead_info(lead_id, {'country': response})
        return {
            "status": "success",
            "message": "Great! What product or service are you interested in?"
        }
   
    # Handle interest question
    elif current_question == 'interest':
        lead_sessions[lead_id]['interest'] = response
        lead_sessions[lead_id]['current_question'] = 'completed'
       
        # Update CSV with all information and mark as secured
        update_lead_info(lead_id, {
            'interest': response,
            'status': 'secured'
        })
       
        return {
            "status": "success",
            "message": "Thank you for providing all the information! We'll be in touch soon."
        }
   
    # If conversation is already completed or declined
    else:
        return {
            "status": "success",
            "message": "Thank you for your response! Is there anything else I can help you with?"
        }

def send_follow_up(lead_id: str) -> dict:
    """Sends a follow-up message to an unresponsive lead.
   
    Args:
        lead_id (str): Unique identifier for the lead
       
    Returns:
        dict: Result of the follow-up operation
    """
    if lead_id not in lead_sessions:
        return {
            "status": "error",
            "message": "Lead not found for follow-up."
        }
   
    # Update last interaction time
    lead_sessions[lead_id]['last_interaction'] = datetime.datetime.now()
   
    # Update status in CSV
    update_lead_info(lead_id, {'status': 'follow_up_sent'})
   
    return {
        "status": "success",
        "message": "Just checking in to see if you're still interested. Let me know when you're ready to continue.",
        "lead_id": lead_id,
        "lead_name": lead_sessions[lead_id]['name']
    }

def schedule_follow_up(lead_id: str):
    follow_up_delay = 60  # seconds (test value), this value is just for testing, it can be adjusted as required.

    try:
        time.sleep(follow_up_delay)

        if lead_id in lead_sessions:
            current_question = lead_sessions[lead_id]['current_question']

            if current_question not in ['completed', 'no_response']:
                # Store the follow-up message to show in the chat later
                follow_up_text = (
                    "Just checking in to see if you're still interested. "
                    "Let me know when you're ready to continue."
                )
                lead_sessions[lead_id]['pending_message'] = follow_up_text

                
                update_lead_info(lead_id, {'status': 'follow_up_sent'})

                print(f"[Follow-Up] Stored for {lead_id}: {follow_up_text}")

    except Exception as e:
        print(f"[Error] Failed to schedule follow-up for lead {lead_id}: {str(e)}")


def process_user_message(message: str) -> dict:
    """Process the user's message and extract lead information or handle responses.
    
    Args:
        message (str): The user's message
        
    Returns:
        dict: The response to send back to the user
    """
    # Check if the message contains lead information
    if "Lead ID:" in message and "Name:" in message:
        try:
            parts = message.split(",")
            lead_id = parts[0].split(":")[1].strip()
            lead_name = parts[1].split(":")[1].strip()
            
            # Start conversation with the extracted information
            return start_conversation(lead_id, lead_name)
        except Exception as e:
            return {
                "status": "error",
                "message": f"Please use the format:\n`Lead ID: your_id, Name: your_name`\n\nError: {str(e)}"
            }
    
    # If the lead information is not provided, check if we have an active session
    elif ":" in message:
        try:
            # Try to extract lead_id from the message (required format which is set : lead_id: response, lead_name: name)
            lead_id = message.split(":")[0].strip()
            response_text = message.split(":", 1)[1].strip()
            
            if lead_id in lead_sessions:
                # Process the response for this lead
                return handle_response(lead_id, response_text)
            else:
                # Lead session not found
                return {
                    "status": "error",
                    "message": "Lead session not found. Please provide your Lead ID and Name to start a conversation."
                }
        except Exception:
            # If parsing fails, ask for proper lead information
            return {
                "status": "error",
                "message": "👋 Hello! Before we start, please provide:\n- Your **Lead ID** (e.g., lead123)\n- Your **Name** (e.g., John Doe)\n\nFormat: `Lead ID: your_id, Name: your_name`"
            }
    else:
        # Default case: ask for lead information
        return {
            "status": "error",
            "message": "👋 Hello! Before we start, please provide:\n- Your **Lead ID** (e.g., lead123)\n- Your **Name** (e.g., John Doe)\n\nFormat: `Lead ID: your_id, Name: your_name`"
        }

# Initializing the CSV file when module is loaded
initialize_csv()

# A proper prompt template for the agent to act as required, sales agent
sales_agent = Agent(
    name="sales_agent",
    model="gemini-2.0-flash",
    description="Agent to handle sales lead conversations and collect information.",
    instruction=(
        "You are a helpful sales agent who engages with leads, collects information, "
        "and follows up when necessary. Keep conversations professional and friendly."
    ),
    tools=[start_conversation, handle_response, send_follow_up, process_user_message],
)

# This is the entry point function that should be called when handling user messages
def handle_user_input(message: str) -> str:
    """Main function to handle user input and return appropriate response."""
    lead_id = None
    
    if ":" in message:
        possible_id = message.split(":")[0].strip()
        if possible_id in lead_sessions:
            lead_id = possible_id

    # If lead_id is found and a follow-up message is pending, return it first
    if lead_id and lead_sessions[lead_id].get("pending_message"):
        pending = lead_sessions[lead_id].pop("pending_message")  
        return pending

    # Continue with normal message processing
    response = process_user_message(message)
    return response.get("message", "Sorry, I couldn't process your request. Please try again.")


root_agent = sales_agent