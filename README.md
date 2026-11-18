# Zoviz AI Marketing Agent

A small Python agent that takes a website URL, extracts the brand's identity (name, description, colors) with the Zoviz `brand-extractor` API, and uses it to generate a matching 1024x1024 social media visual with the Zoviz `image-generator-2` API.

It accompanies the DEV.to tutorial **"Build an AI Marketing Agent with Zoviz MCP"**, which builds the same workflow two ways: through Zoviz's MCP server inside Claude, and with this script.

## How it works

```
website URL --> brand-extractor --> {brand name, description, colors}
                                              |
                                        build prompt
                                              |
                                              v
                                    image-generator-2 --> PNG in generated_assets/
```

## Setup

You need Python 3 and a Zoviz developer API key (create one in the Zoviz developer portal under **API Keys**). Tested on Windows (PowerShell) with Python 3.15.

```bash
git clone https://github.com/harsh70117-lang/zoviz-ai-marketing-agent
cd zoviz-ai-marketing-agent
pip install -r requirements.txt
```

Set your key as an environment variable (don't hardcode it):

```bash
# macOS / Linux
export ZOVIZ_API_KEY="your-key-here"

# Windows PowerShell
$env:ZOVIZ_API_KEY="your-key-here"
```

## Run

```bash
python zoviz_agent.py https://stripe.com
```

The website is a command-line argument. Leave it out and it defaults to `https://stripe.com`. The image is saved to `generated_assets/<brand_name>_social_post.png`, where the brand name is reduced to letters, digits, `_` and `-`.

If `ZOVIZ_API_KEY` isn't set, or the extractor returns no brand name or description, the script stops with a clear message instead of carrying on.

Example output:

```
--- Zoviz AI Marketing Agent ---
[*] Created output directory: generated_assets/
[*] Extracting brand data from: https://stripe.com
[+] Brand Identified: Stripe
[+] Brand Colors: {'primary': '#635bff', 'secondary': '#0a2540'}
[*] Generating image for: Stripe
[*] Waiting for AI to generate image (this takes ~10-20s)...
[+] SUCCESS: Image saved to generated_assets\Stripe_social_post.png
```

## Example outputs

| Route | Input | Output |
|---|---|---|
| REST (this script) | `https://stripe.com` | [`Stripe_social_post.png`](Stripe_social_post.png) |
| MCP (in Claude) | One-line brand idea: an imaginary cold brew coffee shop | [`Kettleglow_social_post.png`](Kettleglow_social_post.png) |
| MCP (in Claude), logo as reference | Same brand, Nano Banana 2 with the logo as a reference image | [`11-kettleglow-branded-post.png`](11-kettleglow-branded-post.png) |

## Cost

Image Generator 2 costs 2 credits per image (see the Services page in the Zoviz developer portal). Don't run it in a loop while you're still tuning the prompt.

## The MCP route

The same workflow runs without code through Zoviz's MCP server:

1. In Claude, go to **Settings > Connectors > Add custom connector**, name it `Zoviz`, and use the URL `https://mcp.zoviz.com/mcp`. Click **Add**, then **Connect**, and sign in.
2. Use a prompt like this:

```
Using Zoviz, create a brand for an imaginary cold brew coffee shop called
Kettleglow Cold Brew.

Tone: friendly and playful
Audience: college students and young professionals
Key message: "Slow-steeped. Fast mornings."
Visual style: warm, modern, hand-crafted

Create logo options, save the first one to my brands, then generate a
1024x1024 social post with Zoviz Image Generator 2 in the brand's colors.
```

Claude calls `create_logo`, `add_brand`, `models_explore` and `generate_image`. The full walkthrough, with screenshots, is in the tutorial.

## Known limitations

- It makes one image from one URL. There are no retries and no rate-limit handling.
- The extracted colors are passed into the prompt as-is (a Python dict), which worked in testing but isn't strictly formatted.
- It doesn't write marketing copy. The Zoviz MCP server I connected to (27 tools) doesn't expose a copy-writing tool, so in the tutorial Claude writes the caption and Zoviz makes the visual.
