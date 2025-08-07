import json
import requests
from ragas import evaluate
from ragas.run_config import RunConfig
from langchain_ollama import OllamaLLM
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import EvaluationDataset
from ragas.metrics import LLMContextRecall, Faithfulness, FactualCorrectness


def answer_rag(question):
    response = requests.post("http://localhost:8000/rag", json={"question": question})
    answer = response.json()["answer"]
    relevant_docs = response.json()["relevant_docs"]
    return answer, relevant_docs

llm = OllamaLLM(model="dolphin-mistral", request_timeout=300, timeout=300, keep_alive=300)
evaluator_llm = LangchainLLMWrapper(llm)

data = [
    {
        "question": "What is the primary hazard of internal corrosion in sprinkler systems?",
        "answer": "Internal corrosion can result in partial or full blockage of piping, reducing water flow and impairing fire protection. It can also cause pinhole leaks, leading to system impairment and equipment damage."
    },
    {
        "question": "What is recommended for removing trapped air in wet-pipe systems?",
        "answer": "Install FM Approved automatic or manual air-release valves at the system high points and remove air each time the system is drained and refilled."
    },
    {
        "question": "Why should galvanized steel pipe not be used in wet-pipe systems?",
        "answer": "Galvanized steel pipe should not be used because trapped water can cause corrosion, leading to pinhole leaks and potential hydrogen accumulation hazards in certain conditions."
    },
    {
        "question": "What is the purpose of using nitrogen in dry-pipe or wet-pipe sprinkler systems?",
        "answer": "Nitrogen is used to reduce the presence of oxygen, thereby decreasing oxygen-related corrosion reactions in both dry and wet-pipe systems."
    },
    {
        "question": "What is the typical nitrogen concentration target in a wet-pipe system?",
        "answer": "At least 98% nitrogen concentration is targeted to effectively reduce corrosion rates."
    },
    {
        "question": "How does graphitic corrosion affect underground cast iron pipes?",
        "answer": "Graphitic corrosion selectively removes iron from cast iron pipes, leaving behind a weak graphite structure, which can lead to pipe failure, especially in wet soil."
    },
    {
        "question": "What are the signs of microbiologically influenced corrosion (MIC) in sprinkler systems?",
        "answer": "Signs include tubercles or nodule deposits, pinhole leaks, and pitting corrosion, often in stagnant water areas or dead ends of piping."
    },
    {
        "question": "What is the recommended treatment for pipes affected by MIC?",
        "answer": "Chemical treatment is not recommended; instead, replacing the affected pipe is advised."
    },
    {
        "question": "What materials are suggested to avoid corrosion in underground piping?",
        "answer": "FM Approved non-metallic underground pipe is recommended in areas with high water tables or corrosive soil conditions."
    },
    {
        "question": "What is environmental stress cracking (ESC) in CPVC pipes?",
        "answer": "ESC occurs when CPVC pipes absorb organic chemicals under stress, weakening the material and potentially causing cracks or failure."
    }
]

sample_queries = [data[i]["question"] for i in range(len(data))]
expected_responses = [data[i]["answer"] for i in range(len(data))]

sample_dicts = []
for query, reference in zip(sample_queries, expected_responses):
    answer, relevant_docs = answer_rag(query)
    
    sample_dict = {
        "user_input": query,
        "retrieved_contexts": relevant_docs,
        "response": answer,
        "reference": reference
    }
    sample_dicts.append(sample_dict)


run_config = RunConfig(timeout=300, max_workers=1)

result = evaluate(
    dataset=EvaluationDataset.from_list(sample_dicts),
    metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
    llm=evaluator_llm,
    run_config=run_config
)
print(result)

# Save results as json
with open("results.json", "w") as f:
    json.dump(result.to_dict(), f)
    