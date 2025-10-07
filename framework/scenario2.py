import asyncio
import os
from openai import RateLimitError

from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient

from framework.agentFactory import AgentFactory

os.environ["OPENAI_API_KEY"] = ""


async def main():
    model_client = OpenAIChatCompletionClient( model="gpt-4o" )
    factory = AgentFactory( model_client )
    database_agent = factory.create_database_agent( system_message=("""
            You are a Database specialist responsible for retrieving user registration data.

            Your task:
            1. Connect to the MySQL database 'rahulshettyacademy'
            2. Query the 'RegistrationDetails' table to get a random record
            3. Query the 'Usernames' table to get additional user data
            4. Combine the data from both tables to create complete registration information
            5. Ensure the email is unique by adding a timestamp or random number if needed
            6. Prepare all the registration data in a structured format so that another agent can understand
            When ready, write: "DATABASE_DATA_READY - APIAgent should proceed next"
            """) )

    api_agent = factory.create_api_agent( system_message=("""
          You are an API testing specialist with access to both REST API tools and filesystem.

            Your task:
            1. FIRST: Extract the EXACT registration data from DatabaseAgent's REGISTRATION_DATA message
            2. Read the EcomBasic.postman_collection.json file to understand the API contract
            3. Before making a registration API call- construct its  body field with the  DatabaseAgent's  data inline with below format rules:
            Email should be unique. add timestamp/random data,
            password should be a format of SecurePass123
            Mobile number format - 1234567890

            once json body field is constructed as per above, then make registration API call with constructed body field as mandatory field
            4. If registration succeeds OR fails with "user already exists", proceed with login
            5. Make login API call with userEmail and userPassword from database data
            6. Report the actual API response status and success/failure

            CRITICAL: You MUST use the exact data from DatabaseAgent's REGISTRATION_DATA, not the sample data from Postman collection.
                and also complete login api call to validate the data you registered using registration api.

            Base URL: https://rahulshettyacademy.com
            Content-Type: application/json

            When login attempt is  complete with successful registration api call , write: "API_TESTING_COMPLETE - ExcelAgent should proceed next"
            Include the final login status (success/failure) in your response.
            """) )

    excel_agent = factory.create_excel_agent( system_message=("""
            You are an Excel data management specialist. ONLY proceed when APIAgent has completed testing.

            Your task:
            1. Wait for APIAgent to complete with "API_TESTING_COMPLETE" message that includes login call success
            2. Extract the registration data from DatabaseAgent's REGISTRATION_DATA message
            3. Check APIAgent's response for actual login success/failure status
            4. Only save data if login was actually successful
            5. Open /Users/apple/Documents/Python_projects/Agentic-AI-AutoGen/Resource/newdata.xlsx
            6. Append the registration data with current timestamp
            7. Save and verify the data

            CRITICAL: Only save data if APIAgent reports successful login, not just attempted login.

            When complete, write: "REGISTRATION PROCESS COMPLETE" and stop.
            """) )

    team = RoundRobinGroupChat( participants=[database_agent, api_agent, excel_agent],
                                termination_condition=TextMentionTermination( "REGISTRATION PROCESS COMPLETE" ) )

    for attempt in range(5):
        try:
            task_result = await Console(team.run_stream(task="Execute Sequential User Registration Process:\n\n"

                                                             "STEP 1 - DatabaseAgent (FIRST):\n"
                                                             "Get random registration data from database tables and format it clearly.\n\n"

                                                             "STEP 2 - APIAgent:\n"
                                                             "Read Postman collection files, then make registration followed by login APIs using the database data.\n\n"

                                                             "STEP 3 - ExcelAgent:\n"
                                                             "Save successful registration login details to Excel file.\n\n"

                                                             "Each agent should complete their work fully before the next agent begins. "
                                                             "Pass data clearly between agents using the specified formats."))
            break
        except RateLimitError:
            wait_time = (attempt + 1) * 15  # e.g., 15s, 30s, 45s...
            print(f"Rate limit hit. Retrying in {wait_time} seconds...")
            await asyncio.sleep(wait_time)


    # task_result = await Console( team.run_stream( task="Execute Sequential User Registration Process:\n\n"
    #
    #                                                    "STEP 1 - DatabaseAgent (FIRST):\n"
    #                                                    "Get random registration data from database tables and format it clearly.\n\n"
    #
    #                                                    "STEP 2 - APIAgent:\n"
    #                                                    "Read Postman collection files, then make registration followed by login APIs using the database data.\n\n"
    #
    #                                                    "STEP 3 - ExcelAgent:\n"
    #                                                    "Save successful registration login details to Excel file.\n\n"
    #
    #                                                    "Each agent should complete their work fully before the next agent begins. "
    #                                                    "Pass data clearly between agents using the specified formats." ) )
    final_message = task_result.messages[-1]
    final_message.content

#     excel_agent = factory.create_excel_agent(system_message=("""
#                 You are an Excel data management specialist. ONLY proceed when APIAgent has completed testing.
#
#                 Your task:
#                 1. Open /Users/apple/Documents/Python_projects/Agentic-AI-AutoGen/Resource/newdata.xlsx
#                 2. Add following entries in 3rd row at respective column Email = JohnDoe434+1697058922@gmail.com, Password = SecurePass123, Token = eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2OGUzNWM5MmY2NjlkNmNiMGFmZmU5M2UiLCJ1c2VyRW1haWwiOiJKb2huRG9lNDM0KzE2OTcwNTg5MjJAZ21haWwuY29tIiwidXNlck1vYmlsZSI6MTIzNDU2Nzg5MCwidXNlclJvbGUiOiJFbmdpbmVlciIsImlhdCI6MTc1OTczMDg0MCwiZXhwIjoxNzkxMjg4NDQwfQ.eaxxngCCMmj0ap3VQs05o-jvh9FD2klT1dwhDLLf5os, User ID = 68e35c92f669d6cb0affe93e, Registration Status = Registered Successfully, Login Status= Login Successfully
#                 3. Save and verify the data
#
#
#                 When complete, write: "REGISTRATION PROCESS COMPLETE" and stop.
#                 """))
#
#     team = RoundRobinGroupChat(participants=[excel_agent],termination_condition=TextMentionTermination( "REGISTRATION PROCESS COMPLETE" ) )
#
#     task_result = await Console(team.run_stream(task="""
# Execute the following Excel operations:
#
# 1. Open /Users/apple/Documents/Python_projects/Agentic-AI-AutoGen/Resource/newdata.xlsx
# 2. Read and display all current data in the sheet
# 3. Append with the following data:
#    - Column A (Email): JohnDoe434+1697058922@gmail.com
#    - Column B (Password): SecurePass123
#    - Column C (Token): eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJfaWQiOiI2OGUzNWM5MmY2NjlkNmNiMGFmZmU5M2UiLCJ1c2VyRW1haWwiOiJKb2huRG9lNDM0KzE2OTcwNTg5MjJAZ21haWwuY29tIiwidXNlck1vYmlsZSI6MTIzNDU2Nzg5MCwidXNlclJvbGUiOiJFbmdpbmVlciIsImlhdCI6MTc1OTczMDg0MCwiZXhwIjoxNzkxMjg4NDQwfQ.eaxxngCCMmj0ap3VQs05o-jvh9FD2klT1dwhDLLf5os
#    - Column D (User ID): 68e35c92f669d6cb0affe93e
#    - Column E (Registration Status): Registered Successfully
#    - Column F (Login Status): Login Successfully
# 4. Save the file
# 5. Read the file again to verify the data was saved correctly
# """))
#
#     final_message = task_result.messages[-1]
#     print("\n" + "=" * 80)
#     print("FINAL RESULT:")
#     print("=" * 80)
#     print(final_message.content)
#
#
#     await model_client.close()




asyncio.run( main() )
