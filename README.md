# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

## Tool Inventory

**search_listings(description: str, size: str | None, max_price: float | None) → list[dict]**
Searches the mock listings dataset for items matching the description, optional size, and price ceiling. Scores each listing by keyword overlap and returns results sorted by relevance. Returns an empty list if nothing matches.

**suggest_outfit(new_item: dict, wardrobe: dict) → str**
Given a thrifted item and the user's wardrobe, uses the Groq LLM to suggest 1–2 complete outfit combinations using specific wardrobe pieces. If the wardrobe is empty, returns general styling advice instead.

**create_fit_card(outfit: str, new_item: dict) → str**
Generates a short Instagram-style caption for the outfit. Uses temperature 1.2 so outputs vary. Returns a descriptive error string if outfit input is empty.

## Planning Loop

The agent parses the user's query with regex to extract a description, size, and max price. It calls `search_listings()` first. If results are empty, it sets `session["error"]` and returns early — `suggest_outfit` is never called with empty input. If results exist, it picks `results[0]`, calls `suggest_outfit()`, then `create_fit_card()`, and returns the session.

## State Management

All state lives in a session dict with keys: `query`, `parsed`, `search_results`, `selected_item`, `wardrobe`, `outfit_suggestion`, `fit_card`, `error`. The item from `search_listings` flows directly into `suggest_outfit`, and the outfit from `suggest_outfit` flows directly into `create_fit_card` — the user never re-enters anything.

## Error Handling

**search_listings:** Returns `[]` on no matches, never raises. Example: `search_listings("designer ballgown", size="XXS", max_price=5)` returns `[]` and the agent responds: "No listings found... Try a broader description, higher price, or skip the size filter."

**suggest_outfit:** If `wardrobe['items']` is empty, prompts the LLM for general styling advice instead of crashing.

**create_fit_card:** If outfit is empty, returns `"Could not generate fit card: outfit description was missing."` Example tested: `create_fit_card("", results[0])` returned this message without raising an exception.

## Spec Reflection

The spec was most useful during Milestone 3 — having exact input/output types defined made each tool easy to test in isolation before wiring them together. One divergence: the spec implied the planning loop might need complex branching, but a simple sequential flow with one early-exit on empty search results was sufficient. The agent's behavior still genuinely changes based on what `search_listings` returns.

## AI Usage

**Instance 1:** I gave Claude my Tool 1 spec from planning.md (inputs, return value, failure mode, and the 5 TODO steps) and asked for help understanding how to structure the keyword scoring logic. It suggested joining title, description, style_tags, and colors into a searchable string. I used this idea but wrote the filtering and scoring loop myself, then verified it handled all three parameters and the empty-results case before using it.

**Instance 2:** I gave Claude my Architecture diagram from planning.md and asked whether my session dict approach would correctly pass state between tools. It confirmed the structure and noted I should store `results[0]` in the session before calling `suggest_outfit`. I applied this when implementing `run_agent()` and tested that state flowed correctly by printing session values between steps.