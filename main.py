github_client = initialize_github_client()
download_loader("GithubRepositoryReader")

github_url = input("Please enter the GitHub repository URL: ")
owner, repo = parse_github_url(github_url)

while True:
    owner, repo = parse_github_url(github_url)
    if validate_owner_repo(owner, repo):
        loader = GithubRepositoryReader(
            github_client,
            owner=owner,
            repo=repo,
            filter_file_extensions=(
                [".py", ".js", ".ts", ".md"],
                GithubRepositoryReader.FilterType.INCLUDE,
            ),
            verbose=False,
            concurrent_requests=5,
        )
        print(f"Loading {repo} repository by {owner}")
        docs = loader.load_data(branch="main")
        print("Documents uploaded:")
        for doc in docs:
            print(doc.metadata)
        break  # Exit the loop once the valid URL is processed
    else:
        print("Invalid GitHub URL. Please try again.")
        github_url = input("Please enter the GitHub repository URL: ")

print("Uploading to vector store...")

# ====== Create vector store and upload data ======

vector_store = DeepLakeVectorStore(
    dataset_path=DATASET_PATH,
    overwrite=True,
    runtime={"tensor_db": True},
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex.from_documents(docs, storage_context=storage_context)
query_engine = index.as_query_engine()

# Include a simple question to test.
intro_question = "What is the repository about?"
print(f"Test question: {intro_question}")
print("=" * 50)
answer = query_engine.query(intro_question)

print(f"Answer: {textwrap.fill(str(answer), 100)} \n")
while True:
    user_question = input("Please enter your question (or type 'exit' to quit): ")
    if user_question.lower() == "exit":
        print("Exiting, thanks for chatting!")
        break

    print(f"Your question: {user_question}")
    print("=" * 50)

    answer = query_engine.query(user_question)
    print(f"Answer: {textwrap.fill(str(answer), 100)} \n")
