from FlagEmbedding import FlagReranker


print("=" * 70)
print("TEST BGE RERANKER")
print("=" * 70)

MODEL_NAME = "BAAI/bge-reranker-v2-m3"

print("\nLoading reranker...")

reranker = FlagReranker(
    MODEL_NAME,
    use_fp16=True
)

print("Reranker loaded successfully.")


query = "Đăng ký khai sinh mất bao lâu?"

documents = [
    "Thủ tục đăng ký khai sinh. Thời hạn giải quyết theo quy định.",
    "Thủ tục đăng ký lại khai sinh. Hồ sơ và trình tự đăng ký lại.",
    "Thủ tục đăng ký khai tử. Hồ sơ đăng ký khai tử.",
    "Thủ tục đăng ký kết hôn. Hồ sơ và thời hạn giải quyết."
]


print("\nQuery:")
print(query)

print("\nReranking...\n")

scores = reranker.compute_score(
    [
        [query, document]
        for document in documents
    ],
    normalize=True
)


results = list(
    zip(documents, scores)
)

results.sort(
    key=lambda x: x[1],
    reverse=True
)


print("=" * 70)
print("RERANK RESULTS")
print("=" * 70)

for i, (document, score) in enumerate(
    results,
    start=1
):

    print(
        f"\n#{i}"
    )

    print(
        f"Score: {score:.4f}"
    )

    print(
        f"Document: {document}"
    )


print("\n")
print("=" * 70)
print("TEST COMPLETED")
print("=" * 70)