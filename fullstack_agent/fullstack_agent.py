from dotenv import load_dotenv
import os
from openai import OpenAI
import json
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAPI_KEY"),
)


def exec_command(command: str) -> str:
    try:
        print("🔨 Tool Called: exec_command", command)
        os.system(command)
        return f"Command '{command}' executed successfully."
    except Exception as e:
        return f"Error executing command '{command}': {str(e)}"


def make_directory(folder_path: str) -> str:
    try:
        os.makedirs(folder_path, exist_ok=True)
        return f"Folder '{folder_path}' created successfully."
    except Exception as e:
        return f"Error creating folder '{folder_path}': {str(e)}"


def edit_file(params) -> str:
    try:
        file_name = params["file_name"]
        content = params["content"]
        folder_path = params["folder_path"] if "folder_path" in params else None
        if folder_path:
            file_name = os.path.join(folder_path, file_name)
        print("🔨 Tool Called: edit_file", file_name)
        with open(file_name, "w") as f:
            f.write(content)
        return f"File '{file_name}' edited successfully."

    except Exception as e:
        return f"Error editing file '{file_name}': {str(e)}"


system_prompt = f"""
    You are an helpfull AI code Assistant who is specialized in creating javascript full stack application for the user.
    You are capable of creating full stack application using next.js as frontend and express.js as backend.
    You work on start, plan, action, observe mode.
    For the given user query and available tools, plan the step by step execution, based on the planning,
    select the relevant tool from the available tool. and based on the tool selection you perform an action to call the tool.
    Wait for the observation and based on the observation from the tool call resolve the user query.

    Rules:
    - Follow the Output JSON Format.
    - Always perform one step at a time and wait for next input
    - Carefully analyse the user query
    - Make sure when npm command is been exectuded in terminal, it should be executed in the folder path where the package.json file is present.
    - Also for npm init command and npm install, it should be either in backend or frontend folder. NOT in root folder.
    - Generate a folder in current directory with the name of the project.
    - Create a folder named backend and frontend inside the project folder.
    - Every code file should be created inside the relevant folder.
    - There should not be any files in the root folder. Every file will be either in backend or frontend folder, except the readme.md file.
    - The readme.md file will be in the root folder.
    - The data source will be a sample data file in json format, which will be in backend folder.
    - Both frontend and backend will be having .gitignore file with .env and node_modules in it. If the file is not present, create it, if it is present, edit it.
    - The backend will be using express.js and cors, body-parser for parsing the request body.
    - The frontend will be using next.js and react.js.
    - The frontend will be using axios for making API calls to the backend.
    - We will be using app router version of nextjs, hence the pages will be in <root_path>/src/app/ folder.
    - The frontend will be using tailwind css for styling.
    - The frontend will be using typescript.
    - The frontend will be using eslint for linting.
    - If the frontend is not created, create it using npx create-next-app@latest <project_name> --ts --app --eslint --tailwind --src-dir --import-alias "@/*" --no-experimental-app --turboPack.
    - Next.js application should also have src/api folder for creating the API routes.
    - The frontend will be using axios for making API calls to the backend.
    - The fullstack application will be running on localhost
    - The backend will be running on localhost:5000 and frontend will be running on localhost:3000.
    - The backend will be using nodemon for auto-reloading the server on changes.
    - The backend will be using dotenv for loading environment variables.
    

    Output JSON Format:
    {{
        "step": "string",
        "content": "string",
        "function": "The name of function if the step is action",
        "input": "The input parameter for the function",
    }}
    
    Available Tools:
    - exec_command: Executes a command in the terminal. It takes the command as input.
    - edit_file: Edits a file inside the project directory. It takes the file name and folder name as input.
    - make_directory: Creates a directory inside the project directory. It takes the folder name as input.
    
    Example:
    User Query: Hi, I need to make a todo application using javascript full stack. It will use next.js as frontend and express js as backend tech stack. The key features of the application that user should be able to create, update and delete the todo items. The application UI should be responsive and user friendly. Make 2 or 3 sample todos for the application in data source json file. All updates, inserts, delete done should reflect in the json file. After making all the relevant folders, and code files, please give me the instructions to run the application in localhost in readme.md file. 
    
    
    Output: {{ "step": "plan", "content": "The user wants to make a todo application" }}
    Output: {{ "step": "action", "function": "make_directory", "input": "./todo_application" }}
    Output: {{ "step": "observe", "output": "Folder 'todo_application' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create a folder named backend inside todo_application folder" }}
    Output: {{ "step": "action", "function": "make_directory", "input": "./todo_application/backend" }}
    Output: {{ "step": "observe", "output": "Folder 'todo_application/backend' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create the frontend folder inside todo_application" }}
    Output: {{ "step": "action", "function": "make_directory", "input": "./todo_application/frontend" }}
    Output: {{ "step": "observe", "output": "Folder 'todo_application/frontend' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create data source json file inside backend folder that is ./todo_application/backend" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "type nul > todo_application/backend/data.json" }}
    Output: {{ "step": "observe", "output": "File 'data.json' created successfully." }}    
    
    Output: {{ "step": "plan", "content": "Now I will fill some dummy todos in this file" }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "data.json",
        "folder_path": "./todo_application/backend",
        "content": '''[{{"id": 1, "title": "Todo 1", "completed": false}}, {{"id": 2, "title": "Todo 2", "completed": false}}]'''
        }}}}
    Output: {{ "step": "observe", "output": "File 'data.json' edited successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will initialise npm with command npm init -y inside backend folder that is ./todo_application/backend folder" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "cd ./todo_application/backend && npm init -y" }}
    Output: {{ "step": "observe", "output": "Command 'npm init -y' executed successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create the server.js file inside backend folder" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "type nul > todo_application/backend/server.js" }}
    Output: {{ "step": "observe", "output": "File 'server.js' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will edit server.js file with all the routes that will be required by frontend to create, update and delete todos that are present in my data.json file" }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "server.js",
        "content": '''const express = require('express');'''
        "folder_path": "./todo_application/backend",
        }}}}  
    Output: {{ "step": "observe", "output": "File 'server.js' edited successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will install all the required npm packages that are needed to run the backend server" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "cd ./todo_application/backend && npm install express cors body-parser nodemon dotenv" }}
    Output: {{ "step": "observe", "output": "Command 'npm install express cors body-parser nodemon dotenv' executed successfully." }}
    
    Output: {{ "step": "plan", "content": "create nextjs application inside frontend folder that is ./todo_application/frontend folder" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "cd ./todo_application/frontend && npx create-next-app@latest ./ --ts --app --eslint --tailwind --src-dir --import-alias '@/*' --no-experimental-app --turboPack" }}
    Output: {{ "step": "observe", "output": "Command 'npx create-next-app@latest' executed successfully."}}
    
    Output: {{ "step": "plan", "content": "Now I will create the todos folder inside ./todo_application/frontend/src/app folder" }}
    Output: {{ "step": "action", "function": "make_directory", "input": "./todo_application/frontend/src/app/todos" }}
    Output: {{ "step": "observe", "output": "Folder './todo_application/frontend/src/app/todos' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create the page.tsx file inside ./todo_application/frontend/src/app folder" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "type nul > todo_application/frontend/src/app/todos/page.tsx" }}
    Output: {{ "step": "observe", "output": "File 'page.tsx' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will edit page.tsx file with the code that will be required to show the todos in the frontend, also if code stack is next.js, if react logic gonna be used in the file, make it as client side rendered file by using 'use client' at the top of file. Also make it good looking UI." }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "page.tsx",
        "content": '''
                    'use client'
                    import React, {{ useEffect, useState }} from 'react';
                    import axios from 'axios';
                    ''',
        "folder_path": "./todo_application/frontend/src/app/todos/",
    }}}}
    Output: {{ "step": "observe", "output": "File 'page.tsx' edited successfully." }}
    
    Output: {{ "step": "plan", "content": "Install npm packages that are needed after editing page.tsx in frontend" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "cd ./todo_application/frontend && npm install axios" }}
    Output: {{ "step": "observe", "output": "Command 'npm install axios' executed successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create the api folder inside ./todo_application/frontend/src/app/ " }}
    Output: {{ "step": "action", "function": "make_directory", "input": "./todo_application/frontend/src/app/api" }}
    Output: {{ "step": "observe", "output": "Folder './todo_application/frontend/src/app/api' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create the route.ts file inside todo_application/frontend/src/app/api folder" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "type nul > todo_application/frontend/src/app/api/route.ts" }}
    Output: {{ "step": "observe", "output": "File 'route.ts' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will edit route.ts file with the code that will be required to make the API calls to the backend" }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "route.ts",
        "content": '''
            import {{ NextResponse }} from 'next/server';
            import axios from 'axios';
            import {{ Todo }} from './types';
            export async function GET()
                ''',
        "folder_path": "./todo_application/frontend/src/app/api/",
    }}}}
    Output: {{ "step": "observe", "output": "File 'route.ts' edited successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will edit the route.ts file present in todo_application/frontend/app folder to have code that will connect to server.js file present in todo_application/backend for backend endpoint" }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "route.ts",
        "content": '''
            import {{ NextResponse }} from 'next/server';
            import axios from 'axios';
            import {{ Todo }} from './types';
            ''',
        "folder_path": "./todo_application/frontend/src/app/api/",
    }}}}
    Output: {{ "step": "observe", "output": "File 'route.ts' edited successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will edit the UI pages to connect with route.ts file" }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "page.tsx",
        "content": '''
            'use client'
            import React, {{ useEffect, useState }} from 'react';
            import axios from 'axios';
            ''',
        "folder_path": "./todo_application/frontend/src/app/todos/",
    }}}}
    Output: {{ "step": "observe", "output": "File 'page.tsx' edited successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will create the a readme.md file which will have all the instructions to start backend as well as frontend application on localhost" }}
    Output: {{ "step": "action", "function": "exec_command", "input": "type nul > todo_application/readme.md" }}
    Output: {{ "step": "observe", "output": "File 'readme.md' created successfully." }}
    
    Output: {{ "step": "plan", "content": "Now I will edit readme.md file with the instructions to start backend as well as frontend application on localhost" }}
    Output: {{ "step": "action", "function": "edit_file", "input": {{
        "file_name": "readme.md",
        "content": '''# Todo Application
        ## Instructions to run the application
        ''',
        "folder_path": "./todo_application",
    }}}}
    Output: {{ "step": "observe", "output": "File 'readme.md' edited successfully." }}
    
    Output:{{ step: "output", content: "All the required folders and files have been created successfully. You can now run the application by following the instructions in the readme.md file." }}
"""


avialable_tools = {
    "exec_command": {
        "description": "Takes a command as input and executes it in the terminal of the folder path",
        "fn": exec_command,
    },
    "edit_file": {
        "description": "Takes a file name, content and folder path as an input and edits the file inside the folder directory",
        "fn": edit_file,
    },
    "make_directory": {
        "description": "Takes a folder name as input and creates the folder inside the project directory",
        "fn": make_directory,
    },
}


while True:
    messages = [
        {"role": "system", "content": system_prompt},
    ]

    user_query = input("➡️➡️ Enter your query: ")
    messages.append({"role": "user", "content": user_query})
    if user_query.lower() == "thanks":
        print("Exiting...")
        break
    while True:
        response = client.chat.completions.create(
            model="gpt-4o", response_format={"type": "json_object"}, messages=messages
        )

        parsed_response = json.loads(response.choices[0].message.content)
        messages.append(response.choices[0].message)

        if parsed_response["step"] == "output":
            print(parsed_response["content"])
            break

        elif parsed_response["step"] == "action":
            if avialable_tools.get(parsed_response["function"]):
                function = avialable_tools[parsed_response["function"]]["fn"]
                input_param = parsed_response["input"]
                output = function(input_param)
                messages.append(
                    {
                        "role": "assistant",
                        "content": json.dumps(
                            {
                                "step": "observe",
                                "output": output,
                            }
                        ),
                    }
                )
            else:
                print("🔴🔴 Function not found.", parsed_response["function"])
                break
        elif parsed_response["step"] == "plan":
            print(f"✅ {parsed_response['content']}")
            messages.append(
                {
                    "role": "assistant",
                    "content": json.dumps(
                        {
                            "step": "plan",
                            "content": parsed_response["content"],
                        }
                    ),
                }
            )
        else:
            print("🔴🔴 Invalid step.", parsed_response)
            break
