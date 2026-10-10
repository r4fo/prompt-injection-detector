# Dataset Sources and Attribution

This project creates a binary prompt-injection detection dataset from public E2A benchmark components.

## E2A Bench

Main source repository: `tokencanopy/e2a-bench`.

The project uses:
- E2A prompt-injection rendered emails
- matched benign controls
- benign SpamAssassin ham examples curated in the E2A phishing package
- NotInject hard-negative controls

The E2A prompt-injection benchmark documents upstream payload sources including LLMail-Inject, InjecAgent, and AgentDojo.

## Redistribution

This repository does not claim ownership of the original data. Raw and derived data should retain the attribution and license requirements of the upstream sources. Review the E2A repository's source notes and attribution files for detailed provenance.
