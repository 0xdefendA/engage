from agno.models.google import Gemini
from google.genai import types
import google.auth


generation_config = types.GenerateContentConfig(
    temperature=0,
    top_p=0.1,
    top_k=1,
    max_output_tokens=4096,
)

# TODO for some reason gemini via api key doesn't like category unspecified, enable it if vertex, disable if api key
safety_settings = [
    # types.SafetySetting(
    #     category=types.HarmCategory.HARM_CATEGORY_UNSPECIFIED,
    #     threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    # ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    types.SafetySetting(
        category=types.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]



def get_gemini_model(config=None):
    model_gemini = None
    # create the model in vertex or via api key    
    if "gemini_api_key" in config and config["gemini_api_key"]:

        model_gemini = Gemini(
            id=config["model_name"],
            vertexai=False,
            api_key=config["gemini_api_key"],
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
    else:
        # no api key, we are using vertex
        credentials, PROJECT_ID = google.auth.default()
        LOCATION = "us-central1"
        if config["location"]:
            LOCATION = config["location"]
        model_gemini = Gemini(
            id=config["model_name"],
            vertexai=True,
            project_id=PROJECT_ID,
            location=LOCATION,
            generation_config=generation_config,
            safety_settings=safety_settings,
        )
    return model_gemini