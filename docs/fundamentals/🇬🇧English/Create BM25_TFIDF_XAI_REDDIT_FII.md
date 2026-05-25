# 🔍 Conceptual Review — BM25, TF-IDF, XAI, and Reddit in the FII Intelligence Platform Project


<br><br>

## 1. What is XAI (Explainable AI)?

**XAI (Explainable Artificial Intelligence)** is a set of methods, techniques, and principles that make the results of AI systems **understandable, auditable, and interpretable by humans**.

Instead of just producing an answer ("black box"), systems with XAI can explain:

*   **why** a decision was made;
*   **which variables influenced the result**;
*   **how the algorithm reached the conclusion**;
*   **what limitations or uncertainties exist**.

### Simple example

A traditional AI might say:

> "Source X is the best for FII marketing."

An XAI approach would explain:

> "Source X received a higher score because it showed a higher frequency of the terms *dividend yield*, *vacancy*, *management*, and *P/VP*, in addition to a higher semantic density related to the FII universe."


<br><br>

## 2. Does it make sense to cite XAI if the project uses Reddit?

**Yes — but with the correct scope.**

The use of **Reddit does not eliminate the need for XAI**.

In fact, XAI remains important because the project performs **ranking, NLP, and analytical inference** on textual content.

However, it is important to adjust how XAI is academically described, avoiding exaggeration or the appearance of "corporate overengineering."

### ✅ Correct wording for this project

The project uses an approach of **analytical interpretability inspired by XAI principles**, as the methods employed are **transparent and auditable**.

This is possible because:

| Technique                        | Explainable?     | Reason                                         |
| :------------------------------- | :--------------- | :--------------------------------------------- |
| **Word Count**                   | ✅ Yes           | Frequencies are fully auditable                |
| **BM25**                         | ✅ Yes           | Interpretable mathematical score               |
| **Sentiment Analysis**           | ⚠️ Partially     | Polarity is explainable, but depends on the model |
| **Topic Modeling (LDA)**         | ⚠️ Partially     | Requires human interpretation                  |
| **Enrichment via Reddit**        | ✅ Yes           | Transparent and traceable source               |


<br><br>

## 3. BM25 instead of TF-IDF — does it still make sense?

### ✅ Yes, but it needs to be well justified.

The question is:

> Why use **BM25 instead of TF-IDF**?

The answer should be aligned with the **system's objective**, which is ranking financial texts and information retrieval.


<br><br>

## 4. Limitations of TF-IDF in this project

TF-IDF is effective for measuring the importance of words in documents, but it has limitations for financial ranking tasks.

### 1. Does not handle term saturation well

If a document repeats:

> "dividend yield"

TF-IDF can overvalue this excessively.

Example:

*   Document A: "dividend yield" (3 times)
*   Document B: "dividend yield" (30 times)

TF-IDF tends to disproportionately reward repetition, even when it does not increase relevance.

BM25 mitigates this behavior.


<br><br>

### 2. Weak normalization by document length

In the FII ecosystem:

*   some sources publish long analyses;
*   others publish short texts.

TF-IDF tends to favor larger documents.

BM25 introduces normalization by document length, reducing this bias.

This is essential when comparing:

*   InfoMoney
*   Funds Explorer
*   Clube FII
*   Reddit
*   Valor Investe
*   Investing.com Brasil
*   among others

Each source has different editorial styles and text lengths.

<br><br>


### 3. BM25 is more suitable for Information Retrieval (IR)

The project's central problem is:

> Which sources have a higher concentration of relevant content about FIIs?

This is a classic problem of **Information Retrieval (IR)**.

BM25 was designed precisely for this context and is widely used in:

*   search engines
*   document ranking systems
*   information retrieval pipelines
*   classic semantic search systems

<br><br>

## 5. Comparison BM25 vs TF-IDF

| Criterion                        | TF-IDF      | BM25                  | Better for the project |
| :------------------------------- | :---------- | :-------------------- | :--------------------- |
| Term frequency                   | Yes         | Yes                   | Tie                    |
| Term saturation control          | ❌ Weak     | ✅ Strong              | BM25                   |
| Length normalization             | ⚠️ Limited  | ✅ Strong              | BM25                   |
| Ranking quality                  | ⚠️ Basic    | ✅ Robust              | BM25                   |
| Interpretability                 | ✅ High     | ✅ High                | Tie                    |
| Explainability (XAI perspective) | ✅ Yes      | ✅ Yes                 | Tie                    |
| Use in IR systems                | ⚠️ Medium   | ✅ Industry standard   | BM25                   |
| Multi-source robustness          | ⚠️ Medium   | ✅ High                | BM25                   |

<br><br>

## 🧠 Conclusion

BM25 is preferred over TF-IDF in this project because it provides:

*   better ranking stability among heterogeneous sources;
*   better normalization for different document lengths;
*   greater alignment with Information Retrieval principles;
*   and maintains adequate interpretability for an XAI-inspired system.
