# I Built a Second Brain with a $170 Voice Recorder and Claude — Here's How It Changed Everything

## How I connected my Plaud Notes to Claude via MCP and turned every conversation into searchable, actionable intelligence

---

*Every day, I have conversations that matter. Client calls. Doctor appointments. Strategy sessions with coworkers. Quick phone calls where someone rattles off three action items while I'm driving.*

*I used to lose most of that information within 24 hours.*

*Not anymore.*

For the past several months, I've been running a setup that fundamentally changed how I capture, retain, and use information from my daily life. It starts with a tiny AI voice recorder called **Plaud Note** clipped to my shirt, and ends with **Claude** — Anthropic's AI assistant — having instant access to every transcript and summary from every conversation I've recorded.

The missing piece in the middle? An **MCP server** I built that connects the two. And I open-sourced it.

---

## The Problem: Your Brain Wasn't Designed to Be a Database

Here's something nobody talks about enough: the information bottleneck in most people's professional lives isn't access to new information. It's **retention and retrieval** of information they already received.

Think about the last week:

- How many meetings did you attend?
- How many phone calls did you take?
- How many times did someone tell you something important while you were focused on something else?

Now — how much of that can you recall right now, word for word?

I'm a developer who works with multiple clients simultaneously. On any given day, I might have a client discovery call in the morning, a technical architecture discussion at lunch, a doctor's appointment in the afternoon, and a quick phone call with a contractor in the evening. Each of those conversations contains details I'll need later — sometimes weeks or months later.

I tried handwritten notes. I tried typing during meetings. I tried voice memos that I never went back to listen to. None of it worked reliably because they all required the same thing: **me remembering to do something in the moment, and then me remembering to go find it later.**

What I needed was a system that captures everything passively and makes it all searchable on demand.

---

## The Setup: Plaud Note + Claude + MCP

Here's my actual daily workflow:

### The Hardware: Plaud Note

The [Plaud Note](https://www.plaud.ai) is a credit-card-sized AI voice recorder. I clip it to my shirt collar or set it on the table at the start of every meeting, call, or appointment. It records, then automatically transcribes and generates AI summaries via the Plaud app.

I use it for:
- **Client meetings** (in-person and phone)
- **Doctor appointments** (I never forget post-visit instructions anymore)
- **Coworker strategy sessions**
- **Phone calls** (it attaches magnetically to the back of my phone)
- **Brainstorming sessions** where I'm thinking out loud

After each recording, Plaud gives me:
- A full transcript with speaker labels
- An AI-generated summary with key points
- Organized tags and folders

That alone is valuable. But it becomes **transformative** when you connect it to Claude.

### The Bridge: Plaud Notes MCP Server

Here's where it gets interesting. I built an open-source **MCP (Model Context Protocol) server** that connects my Plaud Notes account directly to Claude. MCP is a standard that lets AI assistants like Claude talk to external tools and data sources.

Once connected, Claude can:
- **List all my recordings** with dates, durations, and titles
- **Pull full transcripts** with speaker labels from any recording
- **Retrieve AI summaries** Plaud generated
- **Search across ALL my notes** for any topic, name, or keyword
- **Load recent recordings** in bulk for context

The server is open source and available on my GitHub: **[github.com/jameshenning/PlaudNotes](https://github.com/jameshenning/PlaudNotes)**

It takes about 15 minutes to set up — no coding experience required. There's a step-by-step checklist guide that walks you through everything.

### The Brain: Claude

Claude is where it all comes together. With my Plaud Notes connected, Claude becomes my **second brain** — one that has perfect recall of every conversation I've recorded.

I don't have to remember which meeting we discussed the API migration timeline. I don't have to dig through folders of recordings to find what my doctor said about my medication. I just ask Claude.

---

## My Daily Workflow

Here's what a typical day looks like:

```
Morning: Client call about Project X
  → Plaud Note records automatically
  → Transcript + summary sync to Plaud cloud

Afternoon: Working on Project X in Claude Code
  → "Load my last 3 Plaud recordings for context"
  → Claude pulls the transcripts and summaries
  → Claude now has full context of what the client said
  → I reference specific client requirements while coding

Later: Client emails asking about a detail from last month
  → "Search my Plaud notes for anything about the payment API"
  → Claude finds the exact conversation, pulls the transcript
  → I respond to the email in 2 minutes with perfect accuracy
```

### How I Use It for Client Development

This is where the setup pays for itself ten times over. When I'm working on a client project in Claude Code, I can pull in the actual words from our meetings as project context.

Instead of working from my imperfect memory of what the client wanted, I'm working from their **exact words**. Claude can reference specific requirements, constraints, and preferences that the client mentioned — even ones I didn't write down because I didn't realize they'd be important at the time.

My workflow for client development:

1. **Record all client interactions** with Plaud Note
2. **Start a Claude Code project** for the client's work
3. **Load relevant recordings** — "Pull the transcripts from my last 3 meetings with [client]"
4. **Claude uses that context** while we develop — it knows what the client asked for, in their own words
5. **When questions come up**, I search my notes instead of bothering the client with repeat questions

The result: fewer misunderstandings, faster delivery, and clients who are impressed that I remember every detail from every conversation.

---

## The Workflow Diagram

Here's how the pieces fit together:

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR DAILY LIFE                       │
│                                                         │
│  Client Calls  ·  Meetings  ·  Doctor Visits  ·  Phone  │
└──────────────────────┬──────────────────────────────────┘
                       │ Records automatically
                       ▼
              ┌─────────────────┐
              │   Plaud Note    │
              │  (AI Recorder)  │
              └────────┬────────┘
                       │ Syncs via app
                       ▼
              ┌─────────────────┐
              │   Plaud Cloud   │
              │                 │
              │ · Transcripts   │
              │ · AI Summaries  │
              │ · Speaker IDs   │
              │ · Audio Files   │
              └────────┬────────┘
                       │ Connected via MCP
                       ▼
              ┌─────────────────┐
              │  MCP Server     │
              │  (PlaudNotes)   │
              │                 │
              │ github.com/     │
              │ jameshenning/   │
              │ PlaudNotes      │
              └────────┬────────┘
                       │ 12 tools available
                       ▼
              ┌─────────────────┐
              │     Claude      │
              │  (Second Brain) │
              │                 │
              │ · Search notes  │
              │ · Pull context  │
              │ · Reference     │
              │   meetings      │
              │ · Aid in client │
              │   development   │
              └─────────────────┘
```

---

## Real Examples from My Life

**Client development:** A client mentioned during a casual aside three weeks ago that they'd eventually want their dashboard to support dark mode. I didn't write it down. When I was building the settings page last week, Claude surfaced it from the transcript. I added dark mode support proactively. The client was thrilled.

**Doctor appointments:** My doctor adjusted a medication dosage and gave me specific timing instructions. Instead of trying to remember or calling the office back, I asked Claude: *"What did my doctor say about the timing for the new medication?"* — instant, accurate answer pulled from the transcript.

**Phone calls while driving:** Someone calls with three action items while I'm on the highway. Plaud captures it all. Later I ask Claude: *"What were the action items from my call with [name] today?"* — done.

**Recurring meetings:** Before a weekly client standup, I ask Claude to summarize what we discussed last week. I walk in fully prepared with perfect context of where we left off.

---

## Why Claude Specifically?

I've tried other AI assistants. Claude stands out for this use case because:

1. **MCP support** — Claude has native support for the Model Context Protocol, making it possible to connect external data sources like Plaud Notes seamlessly
2. **Long context** — Claude can ingest multiple full meeting transcripts at once and reason across all of them
3. **Claude Code** — For developers, the ability to load meeting transcripts directly into your coding workflow is a game-changer
4. **Nuance** — Claude handles conversational transcripts well, understanding context, speaker intent, and the difference between casual remarks and action items
5. **Privacy controls** — Claude lets you opt out of training, use incognito chats, and control exactly how your data is handled

---

## How to Build This Yourself

Everything you need is open source. Here's the quick version:

1. **Get a Plaud Note** ($169) from [plaud.ai](https://www.plaud.ai) — or use any Plaud device (NotePin, Note Pro)
2. **Record your conversations** and let Plaud transcribe them
3. **Set up the MCP server** from my repo: **[github.com/jameshenning/PlaudNotes](https://github.com/jameshenning/PlaudNotes)**
   - There's a [step-by-step setup guide](https://github.com/jameshenning/PlaudNotes/issues/2) with checkboxes — no coding experience needed
   - One-click deploy to Railway or run locally with Docker
4. **Connect it to Claude** (Desktop or Code) — takes about 2 minutes
5. **Start asking Claude about your recordings**

**Important:** Before connecting, follow the [security guide](https://github.com/jameshenning/PlaudNotes/blob/main/SECURITY_SETUP.md) in the repo to lock down your Claude account. Your conversations are private — make sure they stay that way.

---

## The Bigger Picture: AI-Augmented Memory

What I've built here isn't really about note-taking. It's about **augmenting human memory with AI.**

We live in an age where the most valuable information we encounter often comes through conversation — not documents, not emails, not Slack messages. Conversations are where real decisions get made, real requirements get communicated, and real relationships get built.

But conversations are also the most ephemeral form of information. They happen once and then they exist only in the imperfect, biased, fading memories of the people who were there.

By passively capturing those conversations and making them instantly searchable through an AI that can understand context and nuance, you're not just taking better notes. You're **building a searchable archive of your professional and personal life** that gets more valuable every single day.

Every recording is another node in your second brain. Every transcript is another piece of context Claude can draw on. After a few months, the compound effect is remarkable — Claude has context on your clients, your projects, your health, your decisions, and your history that no human assistant could match.

---

## Try It

The MCP server is MIT licensed and free to use. The setup guide is designed for non-developers. And the Plaud Note pays for itself the first time it saves you from a "wait, what did they say?" moment.

**Repo:** [github.com/jameshenning/PlaudNotes](https://github.com/jameshenning/PlaudNotes)
**Setup Guide:** [Step-by-step checklist](https://github.com/jameshenning/PlaudNotes/issues/2)
**Security Guide:** [Harden your Claude first](https://github.com/jameshenning/PlaudNotes/blob/main/SECURITY_SETUP.md)

If you build this and it changes how you work, I'd love to hear about it. Connect with me on LinkedIn or open an issue on the repo.

---

*James Henning is a developer who believes the best AI tools are the ones you forget you're using. He builds open-source integrations that make AI practical for everyday workflows.*
