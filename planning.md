# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

Searches the mock listings dataset and returns items that match the user's description, size, and budget. It filters by all three parameters and returns the best matches sorted by relevance.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->

- `description` (str): ...A natural language description of the item the user is looking for (e.g. "vintage graphic tee")
- `size` (str): ...The clothing size to filter by (e.g. "M", "L") - can be None to skip size filtering
- `max_price` (float): ...The maximum price the user is willing to pay — can be None to skip price filtering

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->

A list of dicts, where each dict is a listing with fields: id, title, description, category, style_tags, size, condition, price, colors, brand, platform. Returns an empty list [] if no matches are found.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->

The agent tells the user no listings matched their search and suggests they try a broader description, higher price, or no size filter. The agent stops — it does not call suggest_outfit with empty input.

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

Takes a specific thrifted item and the user's existing wardrobe and uses the LLM to suggest one or more complete outfit combinations. It reasons about what already in the wardrobe would pair well with the new item.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->

- `new_item` (dict): ...The listing dict returned by search_listings (contains title, colors, style_tags, etc.)
- `wardrobe` (dict): ...The user's wardrobe following wardrobe_schema.json, with an items list of existing clothing pieces

**What it returns:**
<!-- Describe the return value -->

A string containing one or more outfit suggestions with brief styling notes (e.g. "Pair this with your wide-leg jeans and white sneakers for a relaxed 90s look").

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

If wardrobe['items'] is empty, the agent still calls the LLM but prompts it to give general styling advice for the item instead of wardrobe-specific pairings. It does not crash or return an empty string.

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

Takes a complete outfit suggestion and the new item and uses the LLM to generate a short, shareable caption — the kind of thing someone would post on Instagram or TikTok with their outfit photo.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->

- `outfit` (...): ...The outfit suggestion string returned by suggest_outfit
new_item (dict): The listing dict for the thrifted item (used for details like price and platform)
**What it returns:**
<!-- Describe the return value -->

A string of 1–3 sentences written in a casual, social-media-friendly voice. Should vary each time for different inputs.


**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->

If outfit is an empty string or None, the tool returns a descriptive error message string like "Could not generate fit card: outfit description was missing." It does not raise an exception.
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

After receiving the user's query, the agent calls search_listings first. If the result is an empty list, it sets an error message in the session and returns early — suggest_outfit and create_fit_card are never called. If results are returned, the agent sets session["selected_item"] = results[0] and calls suggest_outfit with that item and the user's wardrobe. If suggest_outfit returns a non-empty string, the agent sets session["outfit_suggestion"] and calls create_fit_card. If suggest_outfit returns empty or fails, the agent returns an error and skips create_fit_card. The loop ends after create_fit_card runs or after any early exit.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

The agent uses a session dict to track state within a single interaction. It stores: session["selected_item"] (the top listing dict from search), session["outfit_suggestion"] (the string from suggest_outfit), session["fit_card"] (the final caption), and session["error"] (an error message string if any tool fails). Each tool receives its inputs directly from the session dict, so the user never has to re-enter information between steps.

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query |Sets session["error"], tells user to try a broader description or higher price, stops the loop |
| suggest_outfit | Wardrobe is empty | LLM is prompted for general styling advice instead of wardrobe-specific suggestions|
| create_fit_card | Outfit input is missing or incomplete | Returns error message string "Could not generate fit card: outfit description was missing" without raising an exception|

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

     User query
    │
    ▼
Planning Loop ──────────────────────────────────────────────────┐
    │                                                           │
    ├─► search_listings(description, size, max_price)           │
    │       │ results=[]                                        │
    │       ├──► [ERROR] "No listings found. Try broader        │
    │       │    search or higher price." → return early ───────┤
    │       │                                                   │
    │       │ results=[item, ...]                               │
    │       ▼                                                   │
    │   session["selected_item"] = results[0]                   │
    │       │                                                   │
    ├─► suggest_outfit(selected_item, wardrobe)                 │
    │       │ wardrobe empty → general styling advice           │
    │       │ failure → [ERROR] return early ───────────────────┤
    │       │                                                   │
    │       │ success                                           │
    │       ▼                                                   │
    │   session["outfit_suggestion"] = "..."                    │
    │       │                                                   │
    └─► create_fit_card(outfit_suggestion, selected_item)       │
            │ outfit empty → [ERROR] return error string ───────┤
            │                                                   │
            │ success                                           │
            ▼                                                   │
        session["fit_card"] = "..."                             │
            │                                                   └─ all error paths end here
            ▼
        Return session to user

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

I'll give Claude the Tool 1 spec (inputs, return value, failure mode) and ask it to implement search_listings() using load_listings() from utils/data_loader.py. I'll verify it filters by all three parameters and handles the empty-results case, then test it with 3 queries before trusting it. For Tool 2, I'll give Claude the Tool 2 spec and ask it to implement suggest_outfit() using the Groq API with llama-3.3-70b-versatile — I'll verify it handles empty wardrobe before using it. For Tool 3, I'll give Claude the Tool 3 spec and ask it to implement create_fit_card() with a temperature above 1.0 so outputs vary — I'll run it 3 times on the same input to confirm variation.
**Milestone 4 — Planning loop and state management:**

I'll give Claude the full Architecture diagram and Planning Loop + State Management sections and ask it to implement run_agent() in agent.py. I'll verify the generated code branches on the search_listings result, stores values in the session dict, and does not call all three tools unconditionally.
---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->

The agent calls search_listings("vintage graphic tee", size=None, max_price=30.0). It scans the listings dataset and returns a list of matching items. The top result is: {"title": "Faded Band Tee", "price": 22.0, "platform": "Depop", "condition": "Good", "size": "M", "colors": ["black", "grey"], "style_tags": ["vintage", "graphic", "band"]}. The agent stores this as session["selected_item"].

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->

The agent calls suggest_outfit(session["selected_item"], wardrobe) where wardrobe contains baggy jeans and chunky sneakers. The LLM returns: "Pair this faded band tee with your wide-leg jeans and chunky sneakers for a classic 90s grunge look — roll the sleeves once and tuck the front corner slightly for shape." The agent stores this as session["outfit_suggestion"].

**Step 3:**
<!-- Continue until the full interaction is complete -->

The agent calls create_fit_card(session["outfit_suggestion"], session["selected_item"]). The LLM returns a casual caption using details from the listing (price, platform) and the outfit suggestion.

**Final output to user:**
<!-- What does the user actually see at the end? -->

The user sees three things: the top listing details (title, price, platform, condition), the outfit suggestion with styling notes, and the fit card caption ready to copy and share.
