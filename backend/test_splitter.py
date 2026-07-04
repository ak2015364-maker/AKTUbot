from backend.utils.text_splitter import split_text

text = "Hello World " * 200

chunks = split_text(text)

print("Number of chunks:", len(chunks))
print(chunks[0][:100])