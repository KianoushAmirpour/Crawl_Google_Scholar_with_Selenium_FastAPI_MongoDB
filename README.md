# Crawl_Google_Scholar_with_Selenium_FastAPI_MongoDB
### The project is broken into below parts:
1. Scrape the google scholar profiles of given scholars with selenium.
2. Storing the extracted data to MongoDB which is hosted on the cloud.
3. [Develop API endpoints using FastAPI to serve query results](#queries).

### What is google scholar Profile?
Google Scholar Profiles provide a simple way for authors to showcase their academic publications. You can check who is citing your articles, graph citations over time, and compute several citation metrics.
for example, you can see the Albert Einstein's profile in the below images:

![Untitled1](https://github.com/KianoushAmirpour/Crawl_Google_Scholar_with_Selenium_FastAPI_MongoDB/assets/112323618/64805099-24be-4e73-ae45-92a5c6e8e212)

### Database and collections
For this project, we considerd having one database with two collections, namely `profiles` and `papers`.

The `profiles` collection includes documents in JSON format, each containing information such as name, university, total_citations, h_index, and i_10_index for each scholar.

The `papers` collection consists of documents in JSON format, each containing the scholar's name and a list of all published papers. For each paper, details such as title, authors, journal, number of citations, and the publication year are stored

### Endpoints
The picture displays a list of all available endpoints. 

![Untitled](https://github.com/KianoushAmirpour/Crawl_Google_Scholar_with_Selenium_FastAPI_MongoDB/assets/112323618/5d4cb148-d3cf-408c-b517-ccba6a046809)

### Queries
Some of the queries used to retrieve data from database are shown below:

#### Recent_papers
this will return the last three papers for the scholar.
```
{"$match": {"name": scholar_name}},
        {"$project": {"_id": 0, "name": 1,
                      "papers": {"$slice": ["$papers", 3]}}}
```

#### Best_papers
This one finds scholars with an h_index greater than 20 and then finds their papers which have more than 200 citations.
```
{"$lookup": {
            "from": "papers",
            "localField": "name",
            "foreignField": "name",
            "as": "all_papers"
        }
        },
        {"$unwind": "$all_papers"},
        {"$unwind": "$all_papers.papers"},
        {"$match": {"$and": [{"h_index": {"$gte": 20}}, {
            "all_papers.papers.citation": {"$gte": 200}}]}},
        {"$group": {
            "_id": {"name": "$name", "h_index": "$h_index"},
            "papers": {"$push": "$all_papers.papers"}
        }
        },
        {"$project": {"_id": 0, "name": "$_id.name",
                      "h_index": "$_id.h_index", "papers": 1}}
```
### How to use:
We used a local cloud provider for MongoDB which provided us a URI and We used localhost for FastAPI.
#### Before Running:
1. Create a folder named `urls`, and within it, create a `.txt` file named `urls.txt` and add the links of profiles you want to crawl.
2. Create a `.env` file and set (`DB_URI` and `DB_NAME`).

#### How to Run:
1. Set up a virtual environment: `python -m venv venv`.
2. Activate the environment: `venv\Scripts\activate.bat`.
3. Install dependencies: `pip install -r requirements.txt`.
4. Start FastAPI server: `uvicorn app.main:app --reload`.
5. Run the crawler: `python gs-crawler\crawler.py`.
   - Reads URLs from `urls.txt` and crawls them one by one.
   - Utilizes logging to capture exceptions and useful crawling details.
   - Sends a POST request to the database for each link to store new records.
6. Use MongoDB Compass and Postman to interact with your database.

### Todo:
- updating the database regularly
- async crawling
