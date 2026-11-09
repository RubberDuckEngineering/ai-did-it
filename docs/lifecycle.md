# 🔄 The Lifecycle, Lap by Lap

> Seven letters, six links, five practitioners, three rounds, one human gate. Somewhere a
> numerologist is very excited.

This page draws how the pieces connect: the lanes, the baton handed between links, the loops and
their budget, and who decides what. [The stage guide](stages.md) zooms into each stage. The
agent-facing contract is [`shared/lifecycle.md`](../src/aididit/pack/shared/lifecycle.md).

## 🏁 The Big Picture

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart LR
    BOARD[/"board<br/>Ready column"/]:::note --> A(["A · Assemble<br/>the orchestrator"]):::duck
    subgraph LANE["one lane per work item: six links, six fresh sessions"]
        direction LR
        I1(["1 · I<br/>Ideate"]):::link --> D1(["2 · D<br/>Draft"]):::link --> I2(["3 · I<br/>Iterate"]):::link --> D2(["4 · D<br/>Deliver"]):::link
        D2 --> M{{"you<br/>merge"}}:::human
        M --> I3(["5 · I<br/>Investigate"]):::link --> T(["6 · T<br/>Tidy"]):::link
    end
    A -->|"file-disjoint<br/>lanes"| I1
    T -.->|"filed rule changes<br/>sharpen the next lane"| BOARD
    classDef duck fill:#FFD23F,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef human fill:#C2185B,color:#FFFFFF,stroke:#FFD23F,stroke-width:3px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

Read the name as a sentence: *"A. I did it."* The claim of completion comes last, which is the only
honest place for it. Nothing is done until Tidy, and Tidy runs only after the merge and after
Investigate has checked the change against the running system.

Why this shape? It answers a problem the [Agile Manifesto](sources.md#agile-manifesto) never had
to consider: the developer forgets everything between sessions. XP's practices still apply, with
small releases, test first and continuous integration ([Beck & Andres](sources.md#beck-2004)). AI
Did It adds a written memory between sessions so those practices survive the forgetting.

## 🏃 The Baton: How One Link Hands to the Next

Every link ends the same way. The handoff note is on disk **before** the next link starts, so a
killed session never takes the lane's state with it.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart TB
    S(["Stage N finishes its work"]):::link --> R(["retro<br/>(every stage except Tidy)"]):::link
    R --> C(["commit the tracked retro output"]):::link
    C --> G{"git status --short<br/>is empty?"}:::gate
    G -->|"no"| X(["hard stop: never<br/>hand off a dirty tree"]):::stop
    G -->|"yes"| H[/"write handoff.md<br/>and read it back"/]:::note
    H --> P[/"write next-link.prompt.md:<br/>sanitized, 8 sections"/]:::note
    P --> RUN{"lanes.runner"}:::gate
    RUN -->|"inline"| IN(["same session re-reads the note<br/>and runs Stage N+1"]):::link
    RUN -->|"claude"| CL(["spawn a detached<br/>headless session"]):::link
    RUN -->|"claude-remote"| CR(["spawn a session you can<br/>watch from the app"]):::link
    IN --> N(["Stage N+1 starts cold: re-grounds in<br/>the note, the contract, git state"]):::ok
    CL --> N
    CR --> N
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef ok fill:#1E7B34,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

"A summary adds to the window. A handoff subtracts from it." Long contexts degrade quietly
([Liu et al.](sources.md#liu-2024); [Hong, Troynikov & Huber](sources.md#hong-2025)). So each
boundary is a deliberate garbage-collection point: the next session gets a short note instead of the
whole history. [Board, Batons and Background Sessions](board-and-lanes.md) covers the runners in
detail.

## 🪢 Loops on a Leash

Most stage work happens in loops: clarify and analyze in Draft, red-green-refactor and
post-implementation analyze in Iterate, panel and bot rounds in Deliver. Every one of them runs
under the same budget.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart TB
    START(["round 1"]):::link --> F{"Any CRITICAL or<br/>HIGH finding left?"}:::gate
    F -->|"no"| EXIT(["exit early"]):::ok
    F -->|"yes"| CAP{"Is this round 3?"}:::gate
    CAP -->|"no"| FIX(["fix, then next round"]):::link --> F
    CAP -->|"yes"| MECH(["fix the mechanical<br/>leftovers directly"]):::link
    MECH --> PANEL[["panel rules once on<br/>each judgement left"]]:::panel
    PANEL -->|"leaving it makes the<br/>build wrong or untestable"| NOW(["fix now"]):::link
    PANEL -->|"acceptable"| NOTE[/"accept, with a note<br/>in the artifact"/]:::note
    PANEL -->|"worth doing later"| ITEM[/"file a follow-up<br/>work item"/]:::note
    PANEL -->|"cannot settle a<br/>CRITICAL or HIGH"| HUMAN{{"lane stops,<br/>a human decides"}}:::human
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef human fill:#C2185B,color:#FFFFFF,stroke:#FFD23F,stroke-width:3px
    classDef panel fill:#5B3F8C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef ok fill:#1E7B34,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

**Why three rounds?** Findings per round fall fast, then flatten out at the reviewer's noise floor
`[Inference, from observed round counts such as 24 → 22 → 13]`. Wording-level findings do not change
what gets built, and Iterate's red-green cycle catches a spec mistake more cheaply than another
analyze round. It is a timebox, and it never lowers a quality bar: the panel chooses how to meet a
bar, never whether to.

## 🧑‍⚖️ Who Decides What

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart TB
    Q(["a decision comes up"]):::link --> AUTO{"An automated gate:<br/>test, linter, scanner?"}:::gate
    AUTO -->|"yes, and it is red"| HALT(["halt and fix:<br/>nobody can bypass it"]):::stop
    AUTO -->|"no"| IRR{"irreversible or<br/>outward-facing?"}:::gate
    IRR -->|"yes: publish, delete,<br/>spend, grant access"| HUM{{"a human decides"}}:::human
    IRR -->|"no"| MERGE{"Is it the merge?"}:::gate
    MERGE -->|"yes, delivery.merge: human"| HUM
    MERGE -->|"yes, delivery.merge: auto"| DEL(["Deliver merges, only<br/>when everything is green"]):::ok
    MERGE -->|"no"| PANEL[["the practitioner panel,<br/>fresh and cited"]]:::panel
    PANEL -->|"grounded: at least two<br/>citing members"| RULE(["ruling recorded<br/>in decisions.md"]):::ok
    PANEL -->|"cannot ground after<br/>5 changed attempts"| HUM
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef human fill:#C2185B,color:#FFFFFF,stroke:#FFD23F,stroke-width:3px
    classDef panel fill:#5B3F8C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef ok fill:#1E7B34,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
```

**Why the merge is the gate.** It is the last reversible moment. It is the one decision no
citation can settle ("do I want this in my trunk now?"). And it batches your attention: ten lanes
give you ten green PRs and one repeated question. Trunk-based teams keep the trunk releasable at
all times ([Humble & Farley](sources.md#humble-farley-2010)), so what enters it deserves a human's
judgement. Teams that have earned the trust can set `delivery.merge: auto`.

## 🧩 When Not Every Stage Applies

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart LR
    W{"What are you shipping?"}:::gate
    W -->|"a whole board"| B(["Assemble, then one<br/>six-link lane per item"]):::duck
    W -->|"one item by hand"| O(["Ideate mode:B, or start<br/>at Draft; no Assemble"]):::link
    W -->|"docs only"| DOC(["Draft (minimal), Iterate,<br/>Deliver, Investigate (skim), Tidy"]):::link
    W -->|"emergency hotfix"| HOT(["Iterate, Deliver,<br/>Investigate (never skip), Tidy"]):::stop
    W -->|"dependency bump"| DEP(["Iterate, Deliver,<br/>Investigate the runtime, Tidy"]):::link
    W -->|"a spike"| SPK(["Iterate only:<br/>no spec, no retro"]):::note
    classDef duck fill:#FFD23F,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

Investigate is the stage people are most tempted to skip, and the worst one to skip. The changes
made in a hurry are the ones whose collateral damage nobody looked for.

## 🥡 Takeaways

- `A` assembles the lanes; each lane runs `I-DID-IT`, one fresh session per link.
- The handoff note is on disk before the next link starts. A handoff subtracts context.
- Every loop is capped at three rounds; whatever is left gets one panel ruling.
- Automated gates cannot be overruled. Irreversible actions and the merge belong to a human.
- Skip Assemble for one item, never skip Investigate.
