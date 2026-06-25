# From Tokens to Latent States: Leveraging Pre-trained Language Models for

| Field | Value |
|---|---|
| Topic | rl |
| arXiv ID | — |
| arXiv URL | — |
| Year | — |
| Authors | Improving Partially Observable Reinforcement Learning |
| Local PDF | `/home/croft/Downloads/22724-AAAI26.LiM-ML.pdf` |

## Abstract

Partially observable Markov decision processes (POMDPs) present significant challenges for reinforcement learning, as agents must learn optimal policies while maintaining belief states over unobserved environment states based on partial observations. We observe a compelling analogy: large lan￾guage models (LLMs) autoregressively generate token prob￾ability distributions based on preceding context, mirroring how belief states are maintained and updated in POMDPs. This insight motivates leveraging the rich prior knowledge embedded in pre-trained LLMs for latent states estimation from observation-action histories. However, two critical chal￾lenges emerge: on the one hand, modality misalignment pre￾vents LLMs from directly encoding visual observations and discrete actions; on the other hand, semantic misalignment exists between observation-action sequences and token se￾quences. To address these challenges, we introduce a novel framework ELSLLM that employs a Johnson-Lindenstrauss projection (JLP) module to transform input dimensions while preserving state similarity with theoretical guarantees, and utilizes modern Hopfield networks (MHN) to store all word embeddings from pre-trained LLMs as a knowledge reposi￾tory. Through retrieval and querying mechanisms, ELSLLM achieves token-level knowledge alignment without requir￾ing fine-tuning of the pre-trained LLMs. Extensive experi￾ments on partially observable environments demonstrate that ELSLLM achieves state-of-the-art performance,

## Why it matters for our work

_(empty — add notes here when you've engaged with this paper)_

## Key takeaways

_(empty — add notes here)_

## Cross-references

_(link related entries via `[[topic/slug]]`)_

<!-- manual-edits-below — do not regenerate -->
