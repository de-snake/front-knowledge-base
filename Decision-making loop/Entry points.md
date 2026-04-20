[[Basic info and definitions#Canonical loop]]
### Session modes — the same loop, three entry points

The canonical loop is traversed differently depending on what kind of session the user is in. The UI and agent prompts must recognise the mode.

- **Decision session (first deposit or new capital).** Full traversal from Discover through Execute. This is what most technical specs implicitly assume. It is actually the _rarest_ session type by frequency.
- **Monitoring session (return visit).** Enters the loop at Stage 6 (Monitor). Most sessions are this — 10–30 seconds, "glance at safety and returns, leave." A meaningful deviation loops the user back to Analyze (and possibly all the way to Discover if they want to switch venues).
- **Emergency session (pressure event).** Enters Stage 6 in danger state, then goes directly to Propose → Preview → Execute without re-running Analyze. The thesis is already "reduce risk now"; the constraint is speed. The UI and agent must collapse the path from "awareness of danger" to "signed remediation" to under two clicks.

Design implication: the _same_ data fields the agent needs for due diligence are also the fields needed for monitoring and for emergency response — served with a different ranking, surface, and tone. Building one schema for all three modes is the product-engineering lever.

