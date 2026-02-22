from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

from main import detect_file_type, extract_resume, download_resume
from resume_parser import build_response
from llm_parser_layer import parse_resume_with_llm

app = FastAPI()

class ResumeRequest(BaseModel):
    resume_url: str


def process_resume(file_path):
    extracted = extract_resume(file_path)
    llm_result = parse_resume_with_llm(extracted["text"])
    if llm_result:
        extracted_links = extracted.get("hyperlinks", [])

        if "links" not in llm_result:
            llm_result["links"] = []
        for link in extracted_links:
            if isinstance(link, dict) and "uri" in link:
                if link["uri"] not in llm_result["links"]:
                    llm_result["links"].append(link["uri"])
        return llm_result

    return build_response(extracted["text"], extracted["tables"])

def process_resume_from_url(resume_url: str):

    try:
        file_path = download_resume(resume_url)

        typee = detect_file_type(file_path)

        if typee != 'pdf' or typee != "docx" :
            raise Exception("Unsupported file type")

        llm_result = process_resume(resume_url)

        if not llm_result:
            raise Exception("LLM parsing failed")

        # Optional: delete temp file
        if os.path.exists(file_path):
            os.remove(file_path)

        return llm_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/parse-resume")
def parse_resume(request: ResumeRequest):

    return process_resume_from_url(request.resume_url)

if __name__ == "__main__":
    resp = process_resume("C:\\Users\\aksha\\Downloads\\Satyam Kumar Mishra Resume.pdf")
    print(resp)

    print("done!!!")


