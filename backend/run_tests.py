"""
Run Q&A test queries against the indexed document and measure performance.
Outputs a clean test results table.
"""
import json
import time
import requests

API_BASE = "http://localhost:8000/api"

# Get the AI report doc_id
docs = requests.get(f"{API_BASE}/documents").json()
ai_doc = None
for doc in docs["documents"]:
    if doc["filename"] == "ai_technology_report.pdf" and doc["status"] == "ready":
        ai_doc = doc
        break

if not ai_doc:
    # Use any ready doc
    for doc in docs["documents"]:
        if doc["status"] == "ready":
            ai_doc = doc
            break

if not ai_doc:
    print("ERROR: No ready document found!")
    exit(1)

doc_id = ai_doc["id"]
print(f"Testing document: {ai_doc['filename']} (ID: {doc_id}, Pages: {ai_doc['page_count']})")
print("=" * 80)

# Test queries
queries = [
    {
        "question": "What is the projected global AI market size by 2030?",
        "expected_keyword": "1.8 trillion",
        "category": "Factual Retrieval"
    },
    {
        "question": "What are the three primary paradigms of machine learning?",
        "expected_keyword": "supervised",
        "category": "Section Lookup"
    },
    {
        "question": "What accuracy did the Mafin 2.5 system achieve on FinanceBench?",
        "expected_keyword": "98.7",
        "category": "Specific Detail"
    },
    {
        "question": "What are the main ethical concerns around AI?",
        "expected_keyword": "bias",
        "category": "Topic Summary"
    },
    {
        "question": "How does PageIndex differ from traditional vector-based RAG?",
        "expected_keyword": "reasoning",
        "category": "Comparison"
    }
]

results = []
for i, q in enumerate(queries, 1):
    print(f"\n--- Test {i}/{len(queries)}: {q['category']} ---")
    print(f"Q: {q['question']}")

    start = time.time()
    try:
        resp = requests.post(
            f"{API_BASE}/query",
            json={"document_id": doc_id, "question": q["question"]},
            timeout=120
        )
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get("answer", "")
            sources = data.get("sources", [])
            reasoning = data.get("reasoning", "")

            # Check if expected keyword is in the answer
            keyword_found = q["expected_keyword"].lower() in answer.lower()
            status = "PASS" if keyword_found else "PARTIAL"

            # Truncate answer for display
            answer_preview = answer[:200].replace("\n", " ")
            source_info = ", ".join(f"p.{s['start_page']}-{s['end_page']}" for s in sources)

            print(f"A: {answer_preview}...")
            print(f"Status: {status} | Time: {elapsed:.1f}s | Sources: {source_info}")
            print(f"Keyword '{q['expected_keyword']}' found: {keyword_found}")

            results.append({
                "test": i,
                "category": q["category"],
                "question": q["question"][:50],
                "status": status,
                "time": f"{elapsed:.1f}s",
                "sources": len(sources),
                "keyword_match": keyword_found,
                "answer_length": len(answer),
            })
        else:
            elapsed = time.time() - start
            print(f"ERROR: HTTP {resp.status_code} - {resp.text[:200]}")
            results.append({
                "test": i,
                "category": q["category"],
                "question": q["question"][:50],
                "status": "FAIL",
                "time": f"{elapsed:.1f}s",
                "sources": 0,
                "keyword_match": False,
                "answer_length": 0,
            })
    except Exception as e:
        elapsed = time.time() - start
        print(f"ERROR: {e}")
        results.append({
            "test": i,
            "category": q["category"],
            "question": q["question"][:50],
            "status": "ERROR",
            "time": f"{elapsed:.1f}s",
            "sources": 0,
            "keyword_match": False,
            "answer_length": 0,
        })

# Print summary table
print("\n" + "=" * 80)
print("TEST RESULTS SUMMARY")
print("=" * 80)
print(f"{'#':<4} {'Category':<18} {'Status':<9} {'Time':<8} {'Sources':<9} {'Keyword':<9} {'Ans Len':<8}")
print("-" * 80)
for r in results:
    print(f"{r['test']:<4} {r['category']:<18} {r['status']:<9} {r['time']:<8} {r['sources']:<9} {'Yes' if r['keyword_match'] else 'No':<9} {r['answer_length']:<8}")

passed = sum(1 for r in results if r["status"] in ("PASS", "PARTIAL"))
total = len(results)
avg_time = sum(float(r["time"].replace("s", "")) for r in results) / total if total > 0 else 0
print("-" * 80)
print(f"Total: {passed}/{total} passed | Avg response time: {avg_time:.1f}s")
print("=" * 80)

# Save results to JSON for later use
with open("test_results.json", "w") as f:
    json.dump({"document": ai_doc, "results": results, "avg_time_seconds": avg_time}, f, indent=2)
print("\nResults saved to test_results.json")
