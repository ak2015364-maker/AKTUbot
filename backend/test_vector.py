from backend.services.vector_store import add_document, search_document

# Add sample notes
add_document(
    "1",
    "Deadlock is a situation where two or more processes wait indefinitely for resources."
)

# Search
results = search_document("What is deadlock?")

print(results)