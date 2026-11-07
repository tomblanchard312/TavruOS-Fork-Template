# Tavru chat interface standard

Status: required for every Tavru chat surface, including Oqelith, embedded assistants, standalone clients and agent panels. Applies to new work and changes to existing chat interfaces. Existing implementations require an adoption review; this document is not evidence of compliance. MUST rules are release acceptance gates. No chat runtime is introduced by this policy.

## Interaction requirements

- **CHAT-01 — Layout.** Keep chat beside the working artifact in an IDE. Dock the composer without covering messages. Reflow narrow layouts; preserve readable text, code and tables. Distinguish speakers and expose conversation history for continuing chats.
- **CHAT-02 — States.** Represent queued, active, streaming, complete, stopped, failed and retrying states honestly. Acknowledge submission immediately. Preserve drafts and partial output; explain failures with a recovery action. Never invent progress or reasoning.
- **CHAT-03 — Streaming.** Render incrementally without broken Markdown or forced scroll jumps. Pause following when readers scroll up; offer return to latest. Retain focus in the composer and announce updates without token-by-token speech.
- **CHAT-04 — Recovery.** Keep Stop reachable throughout active work. Preserve earlier versions when editing or regenerating; make branching/context changes clear. Never silently replace a conversation.
- **CHAT-05 — Accessibility.** Every action needs keyboard access, visible focus and an accessible name. Use restrained polite announcements, logical reading order, sufficient contrast and reduced-motion support. Test zoom, high contrast and screen readers.
- **CHAT-06 — Transparency.** Show tool activity as concise readable steps with optional details. Stop must propagate cancellation to the backend and prevent subsequent tool steps. If cancellation is unconfirmed or a running operation cannot stop, say so; never present it as stopped.
- **CHAT-07 — Verification.** Place supporting source links beside grounded claims; open the relevant passage, file or record when available. Mark unavailable evidence and uncertainty. Never fabricate citations, confidence scores or successful tool outcomes.
- **CHAT-08 — Control.** Present the concrete effect before irreversible actions and obtain explicit confirmation. Keep bounded tasks available through buttons/forms. Offer useful example prompts, explain capabilities and provide an exit when chat cannot help.

## Tavru implementation requirements

These are local product requirements extending the references below, not claims about their specifications.

- **TAVRU-01 — Identity.** Use the correct Tavru application and Oqelith identity where applicable. Do not relabel another provider as Oqelith. Show the actual configured provider/model and connection state; hide unsupported actions. No Copilot sign-up promotions or third-party product branding on Tavru-owned surfaces. Preserve legal attribution and third-party identities.
- **TAVRU-02 — Visual system.** Reuse the host application's controls, typography, spacing and theme tokens. Default to dark surfaces, blue accents, readable controls and generous spacing; respect light, high-contrast and user-selected themes. Use text with safety/status icons; color alone is insufficient.
- **TAVRU-03 — Context and privacy.** Show which workspace/files/attachments are included and allow removal before sending. Disclose local versus remote processing and retention controls. Never send hidden workspace content, secrets or telemetry by default. Treat model output as untrusted; sanitize rendering and gate links, commands and file operations through existing security boundaries.
- **TAVRU-04 — Execution.** Respect Workspace Trust and ordinary-user execution. Generated changes require a reviewable diff and explicit apply action. Container/cluster actions must identify the target and effect. Cancellation does not undo completed side effects: report what happened and recovery options. Never expose private source or credentials in public workflows.

## Acceptance evidence required with each chat change

The review must map applicable rule IDs to evidence, record justified non-applicable items, and leave unmet requirements visibly pending. Include:

1. Screenshots of empty, active, stopped, failed and completed views at normal and narrow widths, including long code/table content and zoom.
2. Keyboard and screen-reader checks covering composer, Stop, tools, citations and focus after submit/error; verify reduced motion and high contrast.
3. A meaningful integration check proving backend cancellation, no later tool scheduling, preserved partial output, and honest handling of an uncancellable operation. Test disconnect, retry and stale response arrival without duplicate side effects.
4. Checks for context removal, untrusted output rendering, disabled/unconfigured AI, confirmation boundaries and truthful provider identity.

Do not substitute document/link checks for runtime acceptance. Existing interfaces remain unverified until this evidence is recorded. Do not add a new UI framework solely to satisfy these rules; desktop utilities must not use Tk/Tkinter and should follow the user's Rust egui/eframe preference where applicable.

## References and interpretation

Reviewed 2026-11-06. The interaction rules are a Tavru synthesis of these design references, not copied component specifications or endorsement of advertised UI kits. Setproduct informs CHAT-01 through CHAT-05; Shanti Infosoft informs CHAT-06 through CHAT-08 and the cancellation/recovery requirements. Numeric timing/layout suggestions are design targets, not promises of backend performance. Show truthful waiting states when streaming is unavailable. Expose operational summaries, never private model chain-of-thought.

- [Setproduct: AI chat interface design](https://www.setproduct.com/blog/ai-chat-interface-ui-design)
- [Shanti Infosoft: Designing AI chat interfaces](https://shantiinfosoft.com/blog/designing-ai-chat-interfaces/)
