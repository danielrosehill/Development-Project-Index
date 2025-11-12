Here's the goal of this repo 

I would like to create a unified data source for my various code projects

These exist on hugging face and github 

I have added secrets for both to .env

In both cases, I only want to show the public projects. Pirvate gh repos and private hf spaces for example should never be indexed

The methodology I'm thinking of is like this.

A script which incrementally pulls in the data and organises it by type.

So:

Github/Repos
HuggingFace/Spaces
HuggingFace/Datasets
HuggingFace/Models

Some classes may be empty or the API might not provide them

The idea is to build a unified json with a common hierarchy

Source: (Github/HF)
Type: (Repo / Space / Dataset / Model etc)
Creation Date:
Link:
Description:

