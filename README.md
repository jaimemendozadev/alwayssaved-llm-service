# 🧠 [AlwaysSaved LLM Service](https://github.com/jaimemendozadev/alwayssaved-llm-service)

Welcome to the **AlwaysSaved** LLM Service — the user-facing web app that powers your private, searchable knowledge base for long-form media. Built to deliver fast, intelligent, and intuitive experiences, this interface lets users upload, explore, and query their personal content with ease.

This is the repository for the LLM Service - Step 7 of the [App Flow](#alwayssaved-system-design--app-flow) where a User can ask the LLM questions about their uploaded data.


For more information about What is AlwaysSaved and its Key Features, refer to the [AlwaysSaved Frontend README](https://github.com/jaimemendozadev/alwayssaved-fe-app).

---

## Table of Contents (TOC)

- [3rd Party Services Needed](#3rd-party-services-needed)
- [Environment and AWS Systems Manager Parameter Store Variables](#environment-and-aws-systems-manager-parameter-store-variables)
- [Starting the App](#starting-the-app)
- [File Structure and Text Vectorizing Flow](#file-structure-and-text-vectorizing-flow)
- [AlwaysSaved System Design / App Flow](#alwayssaved-system-design--app-flow)


---


## 3rd Party Services Needed

- As a friendly reminder from the [AlwaysSaved Frontend](https://github.com/jaimemendozadev/alwayssaved-fe-app), if you successfully imlemented User Authentication with <a href="https://clerk.com/" target="_blank">Clerk.com</a>, you'll need to save the `CLERK_SECRET_KEY` and `CLERK_JWT_KEY` in the AWS Parameter Store in order to protect the FastAPI Backend with Clerk.

  - Aside from the ambiguous documentation in the [Clerk.com Python SDK](https://github.com/clerk/clerk-sdk-python?tab=readme-ov-file#request-authentication), one helpful resource that shows you how to integrate Clerk into a FastAPI Backend, including the use of the `CLERK_SECRET_KEY` and `CLERK_JWT_KEY` environment variables, is the following [YouTube video](https://youtu.be/13tMEW8r6C0?t=3752).

<br />

- You'll also need to setup a Mistral AI account ([see the docs for instructions](https://docs.mistral.ai/getting-started/quickstart/)), add your credit card  information, and create a new API Key that you will also store in the AWS Parameter Store.

- Finally, you'll need to spin up the [Frontend app](https://github.com/jaimemendozadev/alwayssaved-fe-app) to get the LLM Service to work. Remember to save whatever `localhost` URL the Frontend uses because you'll need to save it as an environment variable named `FASTAPI_DEVELOPMENT_APP_DOMAIN` ([see next section](#environment-and-aws-systems-manager-parameter-store-variables)).

<br />


[Back to TOC](#table-of-contents-toc)


---

## Environment and AWS Systems Manager Parameter Store Variables

In order to setup the app for local development, you'll need to create a `.env` file at the root of this repo and prefill all the required Environment Variables as shown below:



```
FASTAPI_DEVELOPMENT_APP_DOMAIN=http://localhost:3000

QDRANT_COLLECTION_NAME=alwayssaved_user_files

LLM_COMPANY=MistralAI

LLM_MODEL=open-mistral-7b

EMBEDDING_MODEL=multi-qa-MiniLM-L6-cos-v1

PYTHON_MODE=development

AWS_REGION=us-east-1

```

<br />


For both development and production, there were some variables that we couldn't store in the .env file, so we had to resort to using the <a href="https://aws.amazon.com/systems-manager/" target="_blank">AWS Systems Manager Parameter Store</a> ahead of time in order to get the app functioning.


The following variable keys have their values stored in the Parameter store as follows:

```
/alwayssaved/MISTRAL_API_KEY


/alwayssaved/LLM_SERVICE_CLERK_SECRET_KEY

/alwayssaved/LLM_SERVICE_CLERK_JWT_KEY


/alwayssaved/QDRANT_URL

/alwayssaved/QDRANT_API_KEY


/alwayssaved/MONGO_DB_USER

/alwayssaved/MONGO_DB_PASSWORD

/alwayssaved/MONGO_DB_BASE_URI

/alwayssaved/MONGO_DB_NAME

/alwayssaved/MONGO_DB_CLUSTER_NAME

```

The only new variables you have to save in the AWS Parameter Store are the `/alwayssaved/LLM_SERVICE_CLERK_SECRET_KEY`, `/alwayssaved/LLM_SERVICE_CLERK_JWT_KEY`, and the `/alwayssaved/MISTRAL_API_KEY`.

<br />

All the other `/alwayssaved/MONGO_DB` or `/alwayssaved/QDRANT` variables should already be in the Parameter Store if you already setup the [AlwaysSaved Frontend](#https://github.com/jaimemendozadev/alwayssaved-fe-app), the [Extractor Service](https://github.com/jaimemendozadev/alwayssaved-extractor-service), or the [Embedding Service](https://github.com/jaimemendozadev/alwayssaved-embedding-service).



<br />

[Back to TOC](#table-of-contents-toc)

---
## Starting the App

We need to use a virtual environment (we use the [Pipenv virtualenv management tool](https://pipenv.pypa.io/en/latest/)) to run the app.

Navigate to the root of the project folder in your computer. Open 2 separate terminal windows that both point to the root of the project. In one of those terminal windows run the following commands:


Create and enter the virtual environment:
```
$ pipenv --python 3.11

```


Enter the virtual environment:

```
$ pipenv shell
```

Install the dependencies in the `Pipfile`:

```
$ pipenv install
```


Start the Embedding Service at the root `service.py` file:

```
$ python3 service.py
```




[Back to TOC](#table-of-contents-toc)

---
## File Structure and Text Vectorizing Flow

```
/
|
|___/server
|    |
|    |
|    |__/routes
|    |   |
|    |   |__convos.py
|    |
|    |__/utils
|    |   |
|    |   |__/aws
|    |   |   |
|    |   |   |__ssm.py
|    |   |
|    |   |__/llm
|    |   |   |
|    |   |   |__mistral.py
|    |   |
|    |   |
|    |   |__clerk.py
|    |   |
|    |   |
|    |   |__embedding.py
|    |   |
|    |   |
|    |   |__mongodb.py
|    |   |
|    |   |
|    |   |__qdrant.py
|    |
|    |
|    |
|    |__main.py
|
|
|
|__service.py


```
For v1, the LLM Service just has one responsibility, to service all incoming request from the Frontend to `/llm-api/convos` so that when the user submits a question to the LLM Service, we:

 - Get the User text question, convert the text to chunks, and use the `EMBEDDING_MODEL` to convert each text `"chunk"` into a `"vector embedding"`;

 <br />

 - Use the `vector embeddings` from the User's text question to search the Qdrant Vector Database for all relevant chunks of information that match the User's question;

 <br />

 - Using the Vector Database results found from the Vector Database search, take the found text results along with the User's text question and make an API Request to the Mistral AI LLM that will generate a human readable response to the User's original question.<br />

<br />



[Back to TOC](#table-of-contents-toc)

---


## AlwaysSaved System Design / App Flow

<img src="https://raw.githubusercontent.com/jaimemendozadev/alwayssaved-fe-app/refs/heads/main/README/alwayssaved-system-design.png" alt="Screenshot of AlwaysSaved System Design and App Flow" />

Above 👆🏽you will see the entire System Design and App Flow for Always Saved.

If you need a better view of the entire screenshot, feel free to [download the Excalidraw File](https://github.com/jaimemendozadev/alwayssaved-fe-app/blob/main/README/alwayssaved-system-design.excalidraw) and view the System Design document in <a href="https://excalidraw.com/" target="_blank">Excalidraw</a>.

<br />

[Back to TOC](#table-of-contents-toc)

---

## Created By

**Jaime Mendoza**
[https://github.com/jaimemendozadev](https://github.com/jaimemendozadev)
