# TartaurusLoop in this tutorial

**Canonical source:** `PortalVision/distributions/tartaurus_loop_package/tartaurus_loop.py`
and runners under `PortalVision/FullMetalPacket/`.

This folder ships a **slim Anthropic SDK variant** for the AJA CCA-F tutorial:

- `tartaurus_loop.py` — stage orchestration (checklist, session, state graph)
- `advertising_rag_spec.json` — route → probe → gap → synthesize
- `run_advertising_rag.py` — entry point

The full PortalVision TartaurusLoop adds FETCH, tool dispatch (DALL-E, matplotlib, medical
query, simulations), HVM generation, and OpenAI client routing. For exam prep, learn the inner
loop in `../anthropic_agent_loop.py` first; use this runner for the full 10-book pipeline.
