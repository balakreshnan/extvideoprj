import base64
import streamlit as st
import requests
import json
import os
import time
from dotenv import load_dotenv
load_dotenv()

# st.set_option('server.maxUploadSize', 1024)  # in MB, adjust as needed

# Initialize session state
if 'operationId' not in st.session_state:
    st.session_state.operationId = None

if 'request_body' not in st.session_state:
    st.session_state.request_body = None

@st.cache_data
def parse_json(data):
    # Basic info
    id = data["id"]
    status = data["status"]
    
    # Result details
    result = data["result"]
    analyzer_id = result["analyzerId"]
    api_version = result["apiVersion"]
    created_at = result["createdAt"]
    
    # Content details
    contents = result["contents"][0]  # Assuming single content item
    markdown = contents["markdown"].strip()
    title = contents["fields"]["Title"]["valueString"]
    description = contents["fields"]["Description"]["valueString"]
    kind = contents["kind"]
    start_page = contents["startPageNumber"]
    end_page = contents["endPageNumber"]
    unit = contents["unit"]
    page_number = contents["pages"][0]["pageNumber"]
    
    # Print extracted information
    st.write(f"ID: {id}")
    st.write(f"Status: {status}")
    st.write(f"Analyzer ID: {analyzer_id}")
    st.write(f"API Version: {api_version}")
    st.write(f"Created At: {created_at}")
    st.write(f"Markdown: {markdown}")
    st.write(f"Title: {title}")
    st.write(f"Description: {description}")
    st.write(f"Kind: {kind}")
    st.write(f"Page Range: {start_page}-{end_page}")
    st.write(f"Unit: {unit}")
    st.write(f"Page Number: {page_number}")

# Function to send DELETE request
def delete_analyzer(endpoint, analyzer_id, api_version, headers):
    # Construct the URL
    url = f"{endpoint}/contentunderstanding/analyzers/{analyzer_id}?api-version={api_version}"
    
    try:
        # Send DELETE request
        response = requests.delete(url, headers=headers)
        
        # Check response status
        if response.status_code == 204:
            st.success(f"Analyzer {analyzer_id} deleted successfully (Status: {response.status_code})")
            return True
        elif response.status_code == 404:
            st.error(f"Analyzer {analyzer_id} not found (Status: {response.status_code})")
            return False
        else:
            st.error(f"Failed to delete analyzer {analyzer_id}. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except requests.RequestException as e:
        st.error(f"Error sending DELETE request: {e}")
        return False
    
def videoint():
    st.header("Video Analytics")
    # Define the variables
    endpoint = os.getenv("CONTENT_UNDERSTANDING_ENDPOINT")  # Replace with your actual endpoint
    analyzerId = "aivisionwestus25-video"  # Replace with your actual analyzer ID
    api_version = "2024-12-01-preview"
    key = os.getenv("CONTENT_UNDERSTANDING_KEY")  # Replace with your actual subscription key
    fileUrl = "https://cdn.pixabay.com/photo/2016/03/08/20/03/flag-1244649_1280.jpg"  # Replace with the URL of the file you want to analyze

    url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}?api-version={api_version}"

    headers = {
        "Ocp-Apim-Subscription-Key": key,
        "Content-Type": "application/json"
    }
    operationId = None

    tab1, tab2 = st.tabs(["Upload Video", "Analyze Video"])

    with tab1:
        st.header("Upload the Video")
        # json_content = json.load("request_body_video.json")
        # Correct way to read a JSON file
        with open("request_body_video.json", "r") as f:
            json_content = json.load(f)

        st.session_state.request_body = json_content
        jsonschema = st.json(json_content)

        if st.button("Save as JSON File"):
            try:
                # Define output file path = jsonschema
                json_string = json.dumps(st.session_state.request_body, indent=2)
                # st.session_state.request_body = jsonschema
                output_file = "request_body_video.json"
                # Write request_body to JSON file
                with open(output_file, "w") as f:
                    json.dump(json_content, f, indent=2)
                st.success(f"JSON saved to {output_file}")
            except Exception as e:
                st.error(f"Failed to save JSON file: {e}")
        
        # Button to trigger DELETE
        if st.button("Delete Analyzer"):
            with st.spinner("Deleting analyzer..."):
                success = delete_analyzer(endpoint, analyzerId, api_version, headers)
                if success:
                    st.write("Operation completed successfully.")
                else:
                    st.write("Operation failed. Check the error messages above.")

        if st.button("Create Schema"):
            with st.spinner("Creating schema ....."):
                url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}?api-version={api_version}"
                with open("request_body_video.json", "r") as file:
                    data = file.read()

                response = requests.put(url, headers=headers, data=data)

                st.write(f"{response.status_code} with Text: {response.text}")
        # File uploader widget
        uploaded_file = st.file_uploader("Choose an MP4 file", type=["mp4"])

        # Check if a file was uploaded
        if uploaded_file is not None:
            # Display file details
            st.write("File Name:", uploaded_file.name)
            st.write("File Size:", f"{uploaded_file.size / (1024 * 1024):.2f} MB")
            
            # Read and display the video
            video_file = uploaded_file.read()
            st.video(video_file)
            
            # Optional: Save the uploaded file
            # with open(uploaded_file.name, "wb") as f:
            #     f.write(video_file)
            # st.success(f"File saved as {uploaded_file.name}")
        else:
            st.info("Please upload an MP4 file.")

        if st.button("Process Video"):
            url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}:analyze?api-version={api_version}"
            # url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}:analyze?_overload=analyzeBinary&api-version={api_version}"
            
            headers = {
                "Ocp-Apim-Subscription-Key": key,
                "Content-Type": "application/json"
            }

            # fileUrl = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerFun.mp4"
            # fileUrl = "http://commondatastorage.googleapis.com/gtv-videos-bucket/sample/SubaruOutbackOnStreetAndDirt.mp4"

            # data = json.dumps({"url": fileUrl})

            

            if uploaded_file is not None:
                # Read and display the video
                data = uploaded_file.read()

            # Open the MP4 file in binary read mode
            file_location = "SubaruOutbackOnStreetAndDirt.mp4"
            with open(file_location, "rb") as file:
                data = file.read()

            # url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}:analyze?_overload=analyzeBinary&api-version={api_version}"
            headers = {
                "Ocp-Apim-Subscription-Key": key,
                "Content-Type": "application/octet-stream"
            }

            #response = requests.post(url, headers=headers, data=data)
            response = requests.post(url, headers=headers, data=data)

            st.write(f"{response.status_code} with Text: {response.text}")

            result = json.loads(response.text)
            operationId = result["id"]

            url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}/results/{operationId}?api-version={api_version}"

            headers = {
                "Ocp-Apim-Subscription-Key": key
            }

            response = requests.get(url, headers=headers)

            # st.write(f"{response.status_code} with Text: {response.text}")

            result = json.loads(response.text)
            #st.write(result)
            operationId = result["id"]
            st.session_state.operationId = operationId
            with st.spinner("Waiting for process to complete..."):
                while True:
                    response = requests.get(url, headers=headers)
                    result = json.loads(response.text)
                    status = result["status"]
                    #st.write(f"{response.status_code} with Text: {response.text}")

                    if status != "Running":
                        break
                    time.sleep(2)  # Wait before polling again
            st.write(f"Operation ID: {operationId} and Status: {result["status"]}")
            # st.write(f"{response.status_code} with Text: {response.text}")
            data = json.loads(response.text)
            #parse_json(data)
            # Parse the contents
            contents = data["result"]["contents"]

        file_location = "SubaruOutbackOnStreetAndDirt.mp4"
        st.video(file_location)

    with tab2:
        st.header("Analyze")
        if st.button("Proecess Results"):
            if st.session_state.operationId is not None:
                with st.spinner("Processing ...."):
                    url = f"{endpoint}/contentunderstanding/analyzers/{analyzerId}/results/{st.session_state.operationId}?api-version={api_version}"

                    headers = {
                        "Ocp-Apim-Subscription-Key": key
                    }

                    response = requests.get(url, headers=headers)

                    # print(response.status_code)
                    # print(response.text)

                    # st.write(f"{response.status_code} with Text: {response.text}")

                    # rs = json.loads(response.text)
                    # #print(rs["status"])

                    # rs1 = rs["result"]
                    # #print(rs1)
                    # # print(rs1["contents"])[0]["fields"]["Title"]["valueString"]
                    # # Extract and print the valueString content
                    # if rs1.get("contents"):
                    #     for content in rs1["contents"]:
                    #         title_field = content.get("fields", {}).get("Title", {})
                    #         value_string = title_field.get("valueString")
                    #         if value_string:
                    #             print('Content extracted: ' , value_string)
                    #             st.markdown(value_string)
                    data = json.loads(response.text)
                    #parse_json(data)
                    # Parse the contents
                    contents = data["result"]["contents"]

                    # # Function to convert milliseconds to time format (MM:SS.mmm)
                    def ms_to_time(ms):
                        seconds, milliseconds = divmod(ms, 1000)
                        minutes, seconds = divmod(seconds, 60)
                        return f"{minutes:02d}:{seconds:02d}.{milliseconds:03d}"

                    # # Extract and print key information for each shot
                    for shot in contents:
                        start_time_ms = shot["startTimeMs"]
                        end_time_ms = shot["endTimeMs"]
                        title = shot["fields"]["title"]["valueString"]
                        description = shot["fields"]["description"]["valueString"]
                        sentiment = shot["fields"]["sentiment"]["valueString"]
                        key_frames = shot["markdown"].split("## Key Frames\n")[1].split("\n")[:-1]
                        width = shot["width"]
                        height = shot["height"]

                        st.markdown(f"Shot: {ms_to_time(start_time_ms)} => {ms_to_time(end_time_ms)}")
                        st.markdown(f"Title: {title}")
                        st.markdown(f"Description: {description}")
                        st.markdown(f"Sentiment: {sentiment}")
                        st.markdown(f"Key Frames: {', '.join(frame.strip('- ') for frame in key_frames)}")
                        st.markdown(f"Resolution: {width}x{height}")
                        st.markdown("-" * 50)
            st.write("Completed.............................")