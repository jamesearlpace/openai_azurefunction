



#Update this code to show miliseconds in the timestamp

import os
import logging
import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.core.exceptions import ResourceNotFoundError, HttpResponseError
import openai
import datetime

def main(myblob: func.InputStream):
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")

    # Parse connection string and container name from the environment variables
    connection_string = "DefaultEndpointsProtocol=https;AccountName=saopenaisandbox;AccountKey=3zOOdiUMlWk1nSCdTdaAkjn3+bzGaeqaYUvCLfe6C82bhB/zi56uLHBEYOTxmbUZDyRBbgyS2RbW+AStD/aEHA==;EndpointSuffix=core.windows.net"

    # Create BlobServiceClient using the connection string
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    # Modify the file name by appending '_edited' to the end
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S") # generate timestamp

    file_name = myblob.name.replace(".txt", f"_{timestamp}.json")

    # Create BlobClient for the new blob with the modified name in the same container
    new_blob_client = blob_service_client.get_blob_client(container="destination", blob=file_name)

    # Copy the contents of the original blob to a new variable
    file_content = myblob.read().decode('utf-8')


    # Set the contents of the new file to the output of the OpenAI API call
    prompt = file_content
    beginning_text = "This is a call center conversation ###"
    ending_text = """### Summarize this in json by 
                customer_satisfaction on a scale of 1-10 with 1 being the least satisfied,
                customer_sentiment,
                chat_duration in seconds,
                issue_resolved true/false,
                issue_category,
                issue_subcategory,
                agent_name,
                customer_name."""
    prompt = beginning_text + prompt + ending_text



    openai.api_type = "azure"
    openai.api_base = "https://openai-sandbox-jep.openai.azure.com/"
    openai.api_version = "2022-12-01"
    openai.api_key = os.getenv("MyKey")

    response = openai.Completion.create(
    engine="davinci3",
    prompt=prompt,
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )

    file_content = response.choices[0].text

    # Save the modified contents to the new blob
    new_blob_client.upload_blob(file_content, overwrite=True)

    logging.info(f"Blob {myblob.name} duplicated in the same container with text completions and renamed to {file_name}.")
