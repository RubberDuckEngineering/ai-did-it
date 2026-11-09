# 🛠️ The CLI, Close Up

> The best installer is one you run twice without fear.

`aididit` is a small Python CLI with three verbs. Each verb is a vertical slice: its own folder,
its own tests, and no shared "services" layer to wade through. This page draws what each verb does,
step by step.

## 🧱 Sliced by Feature, Not by Layer

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart LR
    CLI(["cli.py<br/>parse arguments only"]):::duck
    subgraph FEATURES["features/: one folder per verb"]
        direction TB
        INS(["install/"]):::link
        UNI(["uninstall/"]):::link
        DOC(["doctor/"]):::link
    end
    subgraph SHARED["small shared kernel"]
        direction TB
        LOC(["_specify.py<br/>find Spec Kit"]):::persona
        PRO(["_process.py<br/>run, never via a shell"]):::persona
        PACK(["_pack.py<br/>pack paths and ids"]):::persona
    end
    CLI --> INS
    CLI --> UNI
    CLI --> DOC
    INS --> PRO
    UNI --> PRO
    INS --> PACK
    CLI --> LOC
    classDef duck fill:#FFD23F,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef persona fill:#1F5FA8,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
```

Organising by feature keeps everything one change needs in one place, and keeps unrelated
features from coupling to each other ([Bogard](sources.md#bogard-2018)). The idea is older than
the name: Parnas argued in 1972 for decomposing a system around the decisions likely to change, not
around the steps of a flowchart ([Parnas](sources.md#parnas-1972)). Each slice receives its
dependencies (a runner, a `say` function, the `specify` command) as arguments, so the tests can
swap in fakes without patching anything.

## 📦 `aididit install`: Idempotent by Design

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart TB
    START(["aididit install [PROJECT]<br/>--integration AGENT [--no-init]"]):::duck --> EX{"Project folder exists?"}:::gate
    EX -->|"no"| E2A(["exit 2"]):::stop
    EX -->|"yes"| SK{"Already a Spec Kit<br/>project (.specify/)?"}:::gate
    SK -->|"no, and --no-init"| E2B(["exit 2: drop --no-init<br/>to create one"]):::stop
    SK -->|"no"| INIT(["specify init --here --force<br/>--ignore-agent-tools --integration AGENT"]):::link
    SK -->|"yes"| ADD
    INIT -->|"fails"| E1(["exit 1: nothing<br/>after it runs"]):::stop
    INIT -->|"ok"| ADD(["specify extension add<br/>--dev pack --force"]):::link
    ADD -->|"fails"| E1
    ADD -->|"ok"| SEED{"board.md already there?"}:::gate
    SEED -->|"yes"| KEEP(["keep yours"]):::ok
    SEED -->|"no"| COPY[/"seed the starter board"/]:::note
    KEEP --> IGN[/"lanes/ git-ignored<br/>(unless you already have an ignore file)"/]:::note
    COPY --> IGN
    IGN --> WF(["specify workflow add<br/>aididit-lane.yml"]):::link
    WF -->|"fails"| WARN(["warning only: every<br/>stage command still works"]):::gate
    WF -->|"ok"| CON{"constitution still<br/>Spec Kit's template?"}:::gate
    WARN --> CON
    CON -->|"yes"| CWARN(["warning: write it with<br/>/speckit.constitution"]):::gate
    CON -->|"no"| DONE(["exit 0: tell your agent<br/>Agents Assemble"]):::ok
    CWARN --> DONE
    classDef duck fill:#FFD23F,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef ok fill:#1E7B34,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

Run it again any time to upgrade. Spec Kit keeps your `aididit-config.yml`, and the installer keeps
your board and your ignore file. `--ignore-agent-tools` matters more than it looks: without it Spec
Kit refuses to initialise when the agent's own CLI is not on `PATH`. That describes most CI runners
and every IDE-only assistant. This repo's own CI caught the problem on the first push
(see [the kill-test ledger](kill-tests.md), row 20).

The constitution check is a warning, not a stop. The practitioner panel judges scope against
`.specify/memory/constitution.md`, so a constitution that still reads `[PROJECT_NAME]` makes every
one of those checks empty. A fresh `specify init` leaves exactly that template, so expect the warning
on a new project until you write it.

## 🧹 `aididit uninstall`: Leave the Furniture

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart LR
    U(["aididit uninstall [PROJECT]<br/>[--keep-config]"]):::duck --> SK{"A Spec Kit project?"}:::gate
    SK -->|"no"| E2(["exit 2: nothing to remove"]):::stop
    SK -->|"yes"| W(["specify workflow remove<br/>aididit-lane"]):::link
    W -->|"fails: warn, continue"| X
    W -->|"ok"| X(["specify extension remove<br/>aididit --force"]):::link
    X -->|"fails"| E1(["exit 1"]):::stop
    X -->|"ok"| K[/".specify/aididit/ kept:<br/>your board, retros, lane notes"/]:::note
    classDef duck fill:#FFD23F,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef link fill:#0F6B5C,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

Uninstall removes the pack and never touches your work. The board and lane history are yours. They
also outlive a reinstall, so `uninstall` followed by `install` is a clean upgrade path.

## 🩺 `aididit doctor`: Check Before You Wreck

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart TB
    D(["aididit doctor"]):::duck --> PY{"Python 3.11 or newer?"}:::gate
    D --> SPK{"Spec Kit found?"}:::gate
    D --> GIT{"git on PATH?"}:::gate
    D --> GH{"gh on PATH?"}:::gate
    D --> CLA{"claude on PATH?"}:::gate
    PY -->|"no"| MISS(["MISSING: required"]):::stop
    SPK -->|"no"| MISS
    GIT -->|"no"| MISS
    GH -->|"no"| OPT(["optional: needed for the<br/>github board and PRs"]):::note
    CLA -->|"no"| OPT2(["optional: needed for the<br/>claude and claude-remote runners"]):::note
    PY -->|"yes"| OK(["ok"]):::ok
    SPK -->|"yes"| OK
    GIT -->|"yes"| OK
    classDef duck fill:#FFD23F,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef ok fill:#1E7B34,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef note fill:#FFF4D6,color:#1B2A41,stroke:#1B2A41,stroke-width:1px
```

## 🔎 Finding Spec Kit

`uv tool install` puts Spec Kit's `specify` next to the `aididit` interpreter, so the CLI looks
there before it trusts whatever happens to be first on `PATH`
([uv](sources.md#uv)).

```mermaid
%%{init: {"theme": "base", "themeVariables": {"fontSize": "15px", "primaryColor": "#FFF4D6", "primaryTextColor": "#1B2A41", "primaryBorderColor": "#1B2A41", "textColor": "#1B2A41", "lineColor": "#7C8BA1", "edgeLabelBackground": "#FFF4D6", "clusterBkg": "#1B2A41", "clusterBorder": "#FFD23F", "titleColor": "#FFD23F"}}}%%
flowchart LR
    A{"AIDIDIT_SPECIFY set?"}:::gate -->|"yes"| USE1(["use it"]):::ok
    A -->|"no"| B{"specify beside the<br/>Python interpreter?"}:::gate
    B -->|"yes"| USE2(["use the bundled one"]):::ok
    B -->|"no"| C{"specify on PATH?"}:::gate
    C -->|"yes"| USE3(["use that"]):::ok
    C -->|"no"| NONE(["not found: doctor says<br/>how to install it"]):::stop
    classDef gate fill:#F5A142,color:#1B2A41,stroke:#1B2A41,stroke-width:2px
    classDef stop fill:#B3261E,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
    classDef ok fill:#1E7B34,color:#FFFFFF,stroke:#FFD23F,stroke-width:2px
```

## 🔢 Exit Codes

| Code | Meaning |
|---|---|
| `0` | done |
| `1` | a step failed and nothing after it ran, or `doctor` found a required tool missing |
| `2` | a precondition failed before anything ran: a missing folder, `--no-init` on a folder that is not a Spec Kit project, or `uninstall` on one |

## 🥡 Takeaways

- Three verbs, three slices, one tiny shared kernel.
- `install` is safe to repeat: it never overwrites your board, config or ignore file.
- `uninstall` removes the pack and keeps your work.
- `doctor` separates what is required from what is merely useful.
