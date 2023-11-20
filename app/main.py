from .schema import PapersSchema, ScholarInfoSchema
from .database import profiles, papers

import pymongo
from typing import List
from fastapi import FastAPI
from fastapi import HTTPException, status

app = FastAPI()

app.state.limiter = None


@app.get("/")
def root():
    return {"message": "Welcome to FastAPI with MongoDB to store Google Scholar data crawled by selenium."}


@app.post("/paperscollection/add_papers", status_code=status.HTTP_201_CREATED, tags=["papers"])
def add_to_papers_collection(data: PapersSchema):
    try:
        papers.insert_one(data.dict())
        return {"message": "scholars papers were stored successfully."}
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate entry: The scholar's papers already exists.")


@app.post("/profilescollection/add_profiles", status_code=status.HTTP_201_CREATED, tags=["profiles"])
def add_to_profiles_collection(data: ScholarInfoSchema):
    try:
        profiles.insert_one(data.dict())
        return {"message": "Scholars profile were stored successfully."}
    except pymongo.errors.DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Duplicate entry: The scholar's profile already exists."
        )


@app.get("/profilescollection/sort", status_code=status.HTTP_200_OK, response_model=List[ScholarInfoSchema], tags=["profiles"])
def get_sorted_papers_by_h_index():
    documents = profiles.find().sort("h_index", -1)
    sorted_profiles = list(documents)
    if not sorted_profiles:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No records found in the database to display."
        )
    return sorted_profiles


@app.get("/paperscollection/recent_papers/{scholar_name}", status_code=status.HTTP_200_OK, tags=["papers"])
def get_recent_papers_by_name(scholar_name: str):
    cursor = papers.aggregate([
        {"$match": {"name": scholar_name}},
        {"$project": {"_id": 0, "name": 1,
                      "papers": {"$slice": ["$papers", 3]}}},
    ])
    recent_papers = next(cursor, None)
    if not recent_papers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scholar not found. Verify the spelling or check for available data."
        )
    return recent_papers


@app.get("/profilescollection/best_papers/{h_index}/{citations}", status_code=status.HTTP_200_OK, tags=["profiles"])
def get_best_papers_by_h_index_citation(h_index: int, citations: int):
    cursor = profiles.aggregate([
        {"$lookup": {
            "from": "papers",
            "localField": "name",
            "foreignField": "name",
            "as": "all_papers"
        }
        },
        {"$unwind": "$all_papers"},
        {"$unwind": "$all_papers.papers"},
        {"$match": {"$and": [{"h_index": {"$gte": h_index}}, {
            "all_papers.papers.citation": {"$gte": citations}}]}},
        {"$group": {
            "_id": {"name": "$name", "h_index": "$h_index"},
            "papers": {"$push": "$all_papers.papers"}
        }
        },
        {"$project": {"_id": 0, "name": "$_id.name",
                      "h_index": "$_id.h_index", "papers": 1}}
    ])
    best_papers = list(cursor)
    if not best_papers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found."
        )
    return best_papers


@app.get("/paperscollection/count/{citation}/{year}", status_code=status.HTTP_200_OK, tags=["papers"])
def get_the_number_of_papers_by_citation_year(citation: int, year: int):
    cursor = papers.aggregate([
        {"$unwind": "$papers"},
        {"$match": {"$and": [{"papers.citation": {"$gte": citation}},
                             {"papers.year": {"$gte": year}}]}},
        {"$count": "numer_of_articles"}
    ])
    number_of_documents = next(cursor, None)
    if not number_of_documents:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No documents found."
        )
    return number_of_documents


@app.delete('/profilescollection/delete/{scholar_name}', status_code=status.HTTP_204_NO_CONTENT, tags=["profiles"])
def delete_profile_by_name(scholar_name: str):
    document = profiles.find_one_and_delete({"name": scholar_name})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scholar with the name '{scholar_name}' found for deletion."
        )
    return f"Scholar profile was successfully deleted for {scholar_name}."


@app.delete('/paperscollection/delete/{scholar_name}', status_code=status.HTTP_204_NO_CONTENT, tags=["papers"])
def delete_papers_by_name(scholar_name: str):
    document = papers.find_one_and_delete({"name": scholar_name})
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No scholar with the name '{scholar_name}' found for deletion."
        )
    return f"Scholar papers were successfully deleted for {scholar_name}."
