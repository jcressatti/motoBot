import os
from transformers import pipeline

########################
# 1. CONFIG & MODELS
########################

# Adjust these labels to suit your definition of "engaging"
LABELS = ["controversial", "exciting", "mild"]

def load_summaries(filename="interpreted_summaries.txt"):
    """
    Reads article summaries from a text file.
    Expects each line to be a separate summary.
    """
    if not os.path.exists(filename):
        print(f"File not found: {filename}")
        return []

    with open(filename, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines


def select_most_engaging_summary(summaries):
    """
    Uses a zero-shot classification pipeline to
    find the summary most likely to be 'exciting' or 'controversial.'
    """
    if not summaries:
        return None

    # Load a zero-shot classification model from Hugging Face
    classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

    best_summary = None
    best_score = -1.0

    for summary in summaries:
        # Zero-shot classification
        result = classifier(summary, candidate_labels=LABELS)
        # The model returns scores for each label in the order of candidate_labels
        # For instance: result["scores"] might look like [0.7, 0.2, 0.1] for [controversial, exciting, mild]

        # We want to pick the highest between "controversial" and "exciting" for a single measure
        # One approach: sum the two scores to get a combined 'engagement' metric
        scores_dict = dict(zip(result["labels"], result["scores"]))
        engagement_score = scores_dict["controversial"] + scores_dict["exciting"]

        if engagement_score > best_score:
            best_score = engagement_score
            best_summary = summary

    return best_summary


def convert_summary_to_opinion(summary):
    """
    Uses a text-generation (or instruction-based) pipeline to turn the summary into an opinion.
    """
    # For demonstration, we’ll use a small GPT-2 model. You can pick
    # something like 'google/flan-t5-base' or a specialized instruction model.
    generator = pipeline("text-generation", model="EleutherAI/gpt-neo-1.3B")

    prompt = (
        "Read the following news summary and craft a short, provocative opinion "
        "that might spark conversation. Summary:\n\n"
        f"{summary}\n\nOpinion:"
    )

    # Generate a short statement
    outputs = generator(
        prompt,
        max_length=80,     # Adjust as needed
        num_return_sequences=1,
        no_repeat_ngram_size=2,
        do_sample=True,
        top_p=0.9,
        top_k=50,
    )
    opinion_text = outputs[0]["generated_text"]

    # Often the model will include the prompt in its output. Let's keep just
    # the part after "Opinion:"
    if "Opinion:" in opinion_text:
        opinion_text = opinion_text.split("Opinion:")[-1].strip()

    return opinion_text


def main():
    # 2. Load article summaries from a text file
    summaries = load_summaries("interpreted_summaries.txt")
    if not summaries:
        print("No summaries found. Exiting.")
        return

    # 3. Select the most engaging summary
    best_summary = select_most_engaging_summary(summaries)
    if not best_summary:
        print("Could not determine a most engaging summary. Exiting.")
        return

    print("\n--- Most Engaging Summary ---")
    print(best_summary)

    # 4. Convert that summary into an opinion
    opinion_post = convert_summary_to_opinion(best_summary)

    print("\n--- AI-Generated Opinion ---")
    print(opinion_post)

    # 5. (Optional) Post to Bluesky
    # You likely have an existing bot function or client that handles posting, e.g.:
    # post_to_bluesky(opinion_post)

if __name__ == "__main__":
    main()

