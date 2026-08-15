# PawChain ID — glossary

The definitions that let two people argue precisely. If a term in a spec is not here and
its meaning is contested, add it here rather than explaining it twice.

The seven marked **core** are the ones to be able to define out loud, without notes.

| Term | Definition |
|---|---|
| **Embedding / template** *(core)* | A list of 512 numbers that summarises an image. Two photos of the same cat produce two similar lists; two different cats produce dissimilar ones. We store the list, not the photo. |
| **Threshold** *(core)* | The similarity score above which we declare two templates to be the same animal. It is a chosen number, not a discovered one. |
| **FAR / FRR** *(core)* | False accept rate: how often we match two different cats. False reject rate: how often we fail to match the same cat. One threshold controls both, in opposite directions. |
| **1:1 vs 1:N** *(core)* | 1:1 asks "is this the cat you claim it is" — one comparison. 1:N asks "which of my hundred thousand cats is this" — a search. 1:N is much harder, because you get a hundred thousand chances to be wrong. |
| **Open-set evaluation** *(core)* | Testing on cats the model has never seen in training. Closed-set numbers look wonderful and mean nothing for a registry, because every new user is a cat you have never seen. |
| **Golden set** *(core)* | Frozen test data that is never used for training or tuning. The moment you tune against it, your numbers become marketing. |
| **Gate** *(core)* | An automated check that blocks a merge. Lint, types, tests and evals are our four. Red means not done, regardless of anyone's opinion. |
| Lint | A tool that flags style and obvious-mistake problems without running the code. |
| Type check | A tool that proves the pieces fit together — that a function expecting a number is never handed a photo. |
| Unit test | Code that runs your code and asserts a specific result. The assertion is the requirement, written in a language a machine can enforce. |
| CI | A server that runs the gate automatically on every proposed change, so being tired is not a way for bad code to get in. |
| Pull request / diff | A proposed change, shown as exactly the lines added and removed. You review the diff against the spec, not the whole file. |
| Vector index (FAISS, HNSW) | A data structure that finds the nearest few templates out of millions in milliseconds, instead of comparing against every one. |
| Dedup-on-enrol | Running a 1:N search *before* issuing a new ID, so the same animal cannot be registered twice. |
| Liveness | Checks that the thing in front of the camera is a real animal and not a photograph — motion across frames, parallax, focus behaviour. |
| ONNX | A portable file format for a trained model, so the same model runs on a phone and on a server. |
| Quantisation | Storing the model's numbers with less precision so the file is smaller and runs faster, at a small accuracy cost you measure rather than guess. |
| DID / Verifiable Credential | A standard identifier for a subject, and a signed statement about that subject that anyone can check without contacting the issuer. |
| Soulbound token | A token that cannot be transferred by sale. Used when the thing it represents is a responsibility rather than an asset. |
| Attestation | A signed statement by a party you have decided to trust — here, a vet asserting a sterilisation. |
| Escrow / slashing | Money held by a contract, released on a condition or forfeited on an adjudicated finding. |
| ADR | Architecture decision record. One page: context, options, decision, reason, consequence. |
| Operating threshold | The single threshold value the deployed system actually uses, chosen from the measured FAR/FRR curve rather than by hand. |
| Evidence bundle | The complete set of facts required to open a case: match score, matched PetID, scan metadata, reporter identity, model version. |
| Model version / template generation | The identifier of the model that produced a template. Templates from different generations are never compared. |
| Adjudication | A human ruling that closes a case. A biometric match opens a case; only a person closes one. |
| Residual risk | The part of an attack a mitigation does not cover, written down and accepted on purpose. |
| Harness | Everything that makes agent output checkable without reading it: constitution, specs, task briefs, gates, golden sets, decision records. |
| Decidable requirement | One that two people who disagree can settle without a third person. If it cannot be shown wrong, it is not finished. |
