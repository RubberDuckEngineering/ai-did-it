# 📚 Sources, Soundly Sourced

> "If I have seen further, it is by standing on the shoulders of giants." The giants in this case
> wrote books with very sensible titles and occasional cartoons.

Every claim in these docs that leans on someone else's work points here. Each entry has a stable
anchor (`sources.md#<id>`), and a test fails if any page cites an id that is not on this page.

**How these were checked.** Every web URL below returned HTTP 200 on 2026-11-05. Every DOI resolved
at doi.org on the same date, and its title, venue, volume and pages were read back from Crossref
metadata. The books are cited by edition and publisher. A link that works today can still rot
later, so treat the check date as part of the citation.

**What a citation here does and does not mean.** A citation means the source exists and argues
the idea we attribute to it. It does not mean the author endorses AI Did It. Where these docs go
further than a source says, the sentence is labelled `[Inference]`.

---

## The practitioner panel's shelf

These five sit on the default practitioner panel. The lanes look up their positions fresh, with
web citations, every time they make a decision.

<a id="beck-2002"></a>**[beck-2002]** Beck, K. (2002). *Test-Driven Development: By Example*.
Addison-Wesley. Red, green, refactor, and why you watch the test fail first.

<a id="beck-2004"></a>**[beck-2004]** Beck, K., & Andres, C. (2004). *Extreme Programming
Explained: Embrace Change* (2nd ed.). Addison-Wesley. The Planning Game, the on-site customer,
small releases, and practices that reinforce each other.

<a id="beck-2023"></a>**[beck-2023]** Beck, K. (2023). *Tidy First? A Personal Exercise in
Empirical Software Design*. O'Reilly. Small structural tidyings, and when to do them.

<a id="beck-desiderata"></a>**[beck-desiderata]** Beck, K. *Test Desiderata*.
<https://kentbeck.github.io/TestDesiderata/>. Twelve properties a good test trades off.

<a id="fowler-2018"></a>**[fowler-2018]** Fowler, M. (2018). *Refactoring: Improving the Design
of Existing Code* (2nd ed.). Addison-Wesley. Behaviour-preserving change in small, safe steps.

<a id="fowler-ci"></a>**[fowler-ci]** Fowler, M. *Continuous Integration*.
<https://martinfowler.com/articles/continuousIntegration.html>. Integrate often, keep the build
green, and fix a broken build immediately.

<a id="fowler-quality"></a>**[fowler-quality]** Fowler, M. (2019). *Is High Quality Software
Worth the Cost?* <https://martinfowler.com/articles/is-quality-worth-cost.html>. The argument that
internal quality makes delivery cheaper, not dearer.

<a id="fowler-mocks"></a>**[fowler-mocks]** Fowler, M. *Mocks Aren't Stubs*.
<https://martinfowler.com/articles/mocksArentStubs.html>. Test doubles and the assumptions they
encode.

<a id="fowler-yagni"></a>**[fowler-yagni]** Fowler, M. *Yagni*.
<https://martinfowler.com/bliki/Yagni.html>. Don't build a capability before you need it.

<a id="fowler-debt"></a>**[fowler-debt]** Fowler, M. *Technical Debt*.
<https://martinfowler.com/bliki/TechnicalDebt.html>. Cruft as interest you pay on every change.

<a id="humble-farley-2010"></a>**[humble-farley-2010]** Humble, J., & Farley, D. (2010).
*Continuous Delivery: Reliable Software Releases through Build, Test, and Deployment Automation*.
Addison-Wesley. The deployment pipeline, and "done" meaning releasable.

<a id="farley-2021"></a>**[farley-2021]** Farley, D. (2021). *Modern Software Engineering: Doing
What Works to Build Better Software Faster*. Addison-Wesley. Engineering as optimising for learning
and managing complexity, using short feedback loops.

<a id="martin-2008"></a>**[martin-2008]** Martin, R. C. (2008). *Clean Code: A Handbook of Agile
Software Craftsmanship*. Prentice Hall. Names, small functions, and the Boy Scout Rule.

<a id="martin-2011"></a>**[martin-2011]** Martin, R. C. (2011). *The Clean Coder: A Code of
Conduct for Professional Programmers*. Prentice Hall. Taking responsibility for what you ship.

<a id="martin-2017"></a>**[martin-2017]** Martin, R. C. (2017). *Clean Architecture: A
Craftsman's Guide to Software Structure and Design*. Prentice Hall. Boundaries and dependency
direction.

<a id="dahan-cqrs"></a>**[dahan-cqrs]** Dahan, U. (2009). *Clarified CQRS*.
<https://udidahan.com/2009/12/09/clarified-cqrs/>. Service boundaries and autonomy, which is
the panel seat Dahan fills.

## Agile, flow and the board

<a id="agile-manifesto"></a>**[agile-manifesto]** Beck, K., et al. (2001). *Manifesto for Agile
Software Development*. <https://agilemanifesto.org/>.

<a id="anderson-2010"></a>**[anderson-2010]** Anderson, D. J. (2010). *Kanban: Successful
Evolutionary Change for Your Technology Business*. Blue Hole Press. Visualise the work and limit
work in progress.

<a id="little-1961"></a>**[little-1961]** Little, J. D. C. (1961). A proof for the queuing
formula L = λW. *Operations Research*, 9(3), 383–387. <https://doi.org/10.1287/opre.9.3.383>.
For a stable system, items in progress = arrival rate × time in system. Fewer things in flight
means each finishes sooner.

<a id="reinertsen-2009"></a>**[reinertsen-2009]** Reinertsen, D. G. (2009). *The Principles of
Product Development Flow: Second Generation Lean Product Development*. Celeritas. Batch size,
queues, and the economics of small batches.

<a id="poppendieck-2003"></a>**[poppendieck-2003]** Poppendieck, M., & Poppendieck, T. (2003).
*Lean Software Development: An Agile Toolkit*. Addison-Wesley. ISBN 978-0-321-15078-3. Seven lean
principles for software, starting with eliminating waste. Publisher listing checked 2026-11-06.

<a id="ohno-1988"></a>**[ohno-1988]** Ohno, T. (1988). *Toyota Production System: Beyond
Large-Scale Production*. Productivity Press. The source of "ask why five times".

<a id="brooks-1975"></a>**[brooks-1975]** Brooks, F. P. (1975). *The Mythical Man-Month: Essays
on Software Engineering*. Addison-Wesley. Communication overhead grows faster than the team does.

<a id="forsgren-2018"></a>**[forsgren-2018]** Forsgren, N., Humble, J., & Kim, G. (2018).
*Accelerate: The Science of Lean Software and DevOps*. IT Revolution. Measured links between
small batches, fast feedback and delivery performance.

<a id="dora"></a>**[dora]** DORA (DevOps Research and Assessment). <https://dora.dev/>. The
ongoing research programme behind *Accelerate*.

<a id="wake-2003"></a>**[wake-2003]** Wake, B. (2003). *INVEST in Good Stories, and SMART
Tasks*. <https://xp123.com/articles/invest-in-good-stories-and-smart-tasks/>. Independent,
Negotiable, Valuable, Estimable, Small, Testable.

<a id="three-amigos"></a>**[three-amigos]** Agile Alliance. *Three Amigos* (glossary).
<https://www.agilealliance.org/glossary/three-amigos/>. Business, development and testing
perspectives reviewing a story together before it is built.

## Specs, tests and evidence

<a id="spec-kit"></a>**[spec-kit]** GitHub. *Spec Kit*. <https://github.com/github/spec-kit>.
The toolkit this pack extends (MIT).

<a id="spec-driven"></a>**[spec-driven]** GitHub. *Specification-Driven Development (SDD)*.
<https://github.com/github/spec-kit/blob/main/spec-driven.md>. Spec Kit's own account of why the
spec comes first.

<a id="north-2006"></a>**[north-2006]** North, D. (2006). *Introducing BDD*.
<https://dannorth.net/introducing-bdd/>. Given-When-Then, and behaviour as the unit of a test name.

<a id="demillo-1978"></a>**[demillo-1978]** DeMillo, R. A., Lipton, R. J., & Sayward, F. G.
(1978). Hints on test data selection: Help for the practicing programmer. *Computer*, 11(4),
34–41. <https://doi.org/10.1109/C-M.1978.218136>. The founding paper of mutation testing: a test
suite is judged by the faults it can detect.

<a id="dijkstra-1970"></a>**[dijkstra-1970]** Dijkstra, E. W. (1970). *Notes on Structured
Programming* (EWD 249). <https://www.cs.utexas.edu/~EWD/ewd02xx/EWD249.PDF>. Where testing is
said to show the presence of bugs, never their absence.

<a id="popper-1959"></a>**[popper-1959]** Popper, K. (1959). *The Logic of Scientific
Discovery*. Hutchinson. A claim is worth something only if it could be shown false.

<a id="nygard-2011"></a>**[nygard-2011]** Nygard, M. (2011). *Documenting Architecture
Decisions*. <https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions>. The
original lightweight ADR.

## Decisions, teams and learning

<a id="tversky-kahneman-1974"></a>**[tversky-kahneman-1974]** Tversky, A., & Kahneman, D.
(1974). Judgment under uncertainty: Heuristics and biases. *Science*, 185(4157), 1124–1131.
<https://doi.org/10.1126/science.185.4157.1124>. Anchoring: an earlier number drags later
estimates toward it.

<a id="surowiecki-2004"></a>**[surowiecki-2004]** Surowiecki, J. (2004). *The Wisdom of Crowds*.
Doubleday. Independent judgements aggregate well; judgements that copy each other do not.

<a id="kerth-2001"></a>**[kerth-2001]** Kerth, N. L. (2001). *Project Retrospectives: A Handbook
for Team Reviews*. Dorset House. The retrospective as a routine, blameless practice.

<a id="derby-larsen-2006"></a>**[derby-larsen-2006]** Derby, E., & Larsen, D. (2006). *Agile
Retrospectives: Making Good Teams Great*. Pragmatic Bookshelf. A retro that ends in actions.

<a id="deming-1986"></a>**[deming-1986]** Deming, W. E. (1986). *Out of the Crisis*. MIT Press.
Plan, do, study, act: the loop is only closed by acting.

<a id="sre-postmortem"></a>**[sre-postmortem]** Beyer, B., Jones, C., Petoff, J., & Murphy, N. R.
(Eds.). (2016). Postmortem culture: Learning from failure. In *Site Reliability Engineering*.
O'Reilly. <https://sre.google/sre-book/postmortem-culture/>.

<a id="cunningham-1992"></a>**[cunningham-1992]** Cunningham, W. (1992). The WyCash portfolio
management system. *OOPSLA '92 Addendum* (experience report). The first "technical debt" metaphor.

## Agents and context

<a id="liu-2024"></a>**[liu-2024]** Liu, N. F., Lin, K., Hewitt, J., Paranjape, A., Bevilacqua, M.,
Petroni, F., & Liang, P. (2024). Lost in the middle: How language models use long contexts.
*Transactions of the Association for Computational Linguistics*, 12, 157–173.
<https://doi.org/10.1162/tacl_a_00638>. Preprint: <https://arxiv.org/abs/2307.03172>. Models use
information in the middle of a long input less reliably than information at either end.

<a id="hong-2025"></a>**[hong-2025]** Hong, K., Troynikov, A., & Huber, J. (2025, July 14).
*Context Rot: How Increasing Input Tokens Impacts LLM Performance*. Chroma.
<https://www.trychroma.com/research/context-rot>. Measured performance falls as input length
grows, even on simple tasks and well inside the context window.

## Structure and architecture

<a id="parnas-1972"></a>**[parnas-1972]** Parnas, D. L. (1972). On the criteria to be used in
decomposing systems into modules. *Communications of the ACM*, 15(12), 1053–1058.
<https://doi.org/10.1145/361598.361623>. Split by the decisions likely to change, not by the
steps of the flowchart.

<a id="conway-1968"></a>**[conway-1968]** Conway, M. E. (1968). How do committees invent?
*Datamation*, 14(4), 28–31. <http://www.melconway.com/Home/Committees_Paper.html>. Systems mirror
the communication structure of the teams that build them.

<a id="bogard-2018"></a>**[bogard-2018]** Bogard, J. (2018). *Vertical Slice Architecture*.
<https://www.jimmybogard.com/vertical-slice-architecture/>. Organise by feature, minimise coupling
between slices, and maximise coupling within one.

<a id="hunt-thomas-1999"></a>**[hunt-thomas-1999]** Hunt, A., & Thomas, D. (1999). *The Pragmatic
Programmer*. Addison-Wesley. Source of the rubber-duck debugging story; see also
[Rubber duck debugging](https://en.wikipedia.org/wiki/Rubber_duck_debugging).

## Standards, formats and platforms

<a id="conventional-commits"></a>**[conventional-commits]** *Conventional Commits 1.0.0*.
<https://www.conventionalcommits.org/en/v1.0.0/>.

<a id="conventional-comments"></a>**[conventional-comments]** *Conventional Comments*.
<https://conventionalcomments.org/>.

<a id="semver"></a>**[semver]** Preston-Werner, T. *Semantic Versioning 2.0.0*.
<https://semver.org/>.

<a id="owasp-top10"></a>**[owasp-top10]** OWASP Foundation. *OWASP Top Ten*.
<https://owasp.org/www-project-top-ten/>.

<a id="wcag-22"></a>**[wcag-22]** W3C. (2023). *Web Content Accessibility Guidelines (WCAG) 2.2*.
<https://www.w3.org/TR/WCAG22/>. SC 1.4.3 (text contrast, 4.5:1) and SC 1.4.11 (non-text
contrast, 3:1) are the bars the diagram tests enforce.

<a id="mermaid-theming"></a>**[mermaid-theming]** Mermaid. *Theme Configuration*.
<https://mermaid.js.org/config/theming.html>. The `base` theme and the `themeVariables` the house
header sets.

<a id="github-diagrams"></a>**[github-diagrams]** GitHub Docs. *Creating diagrams*.
<https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams>.
And the launch post: [Include diagrams in your Markdown files with Mermaid](https://github.blog/2022-02-14-include-diagrams-markdown-files-mermaid/)
(GitHub Blog, 2022).

<a id="github-pulls-api"></a>**[github-pulls-api]** GitHub Docs. *REST API endpoints for pull
requests*, "Get a pull request". <https://docs.github.com/en/rest/pulls/pulls#get-a-pull-request>.
Before a merge, `merge_commit_sha` holds the SHA of GitHub's test merge commit, so it is no proof
of a merge. Checked 2026-11-06.

<a id="primer"></a>**[primer]** GitHub. *Primer Primitives* (design tokens).
<https://github.com/primer/primitives>. `bgColor.default` per theme gives the page backgrounds the
contrast tests measure against.

<a id="uv"></a>**[uv]** Astral. *uv*. <https://docs.astral.sh/uv/>. The installer behind
`uv tool install`.
